"""
SafeLaunch AI -- REST API (FastAPI)
api.py

엔드포인트:
  - /api/health             시스템 상태
  - /api/stats              시스템 통계
  - /api/auth/register      사용자 등록
  - /api/laws               법령 목록 / 상세
  - /api/precedents         판례 목록 / 상세
  - /api/projects           프로젝트 CRUD
  - /api/search             FTS5 / RAG 검색
  - /api/analyses           분석 결과

실행:
  uvicorn api:app --reload --port 8000
"""

import os
import sys
import hashlib
import logging
from typing import Optional

from fastapi import FastAPI, HTTPException, Query, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# 프로젝트 루트를 경로에 추가
sys.path.insert(0, os.path.dirname(__file__))

from core.database import db
from core.legal_rag import search_legal_context

logger = logging.getLogger("api")

# ─────────────────────────────────────────────────────────────
# FastAPI 앱
# ─────────────────────────────────────────────────────────────

app = FastAPI(
    title="SafeLaunch AI API",
    version="2.0.0",
    description="앱 컴플라이언스 분석 API",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─────────────────────────────────────────────────────────────
# 요청/응답 모델
# ─────────────────────────────────────────────────────────────

class UserRegister(BaseModel):
    email: str
    password: str
    display_name: Optional[str] = None
    company_name: Optional[str] = None


class UserLogin(BaseModel):
    email: str
    password: str


class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    app_category: Optional[str] = None
    platforms: Optional[list[str]] = None
    regions: Optional[list[str]] = None
    features: Optional[dict] = None


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    app_category: Optional[str] = None
    status: Optional[str] = None
    platforms: Optional[list[str]] = None
    regions: Optional[list[str]] = None
    features: Optional[dict] = None


class AnalysisCreate(BaseModel):
    analysis_type: str = "full"


# ─────────────────────────────────────────────────────────────
# 헬퍼
# ─────────────────────────────────────────────────────────────

def _hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def _get_user_id(x_user_id: Optional[str] = Header(None)) -> str:
    """개발용 헤더 인증 (X-User-Id). 프로덕션에서는 JWT로 교체."""
    if not x_user_id:
        raise HTTPException(status_code=401, detail="X-User-Id 헤더가 필요합니다.")
    user = db.get_user(x_user_id)
    if not user:
        raise HTTPException(status_code=401, detail="유효하지 않은 사용자입니다.")
    return x_user_id


# ─────────────────────────────────────────────────────────────
# 시스템
# ─────────────────────────────────────────────────────────────

@app.get("/api/health")
def health():
    return {"status": "ok", "version": "2.0.0"}


@app.get("/api/stats")
def stats():
    return db.get_stats()


# ─────────────────────────────────────────────────────────────
# 인증
# ─────────────────────────────────────────────────────────────

@app.post("/api/auth/register")
def register(body: UserRegister):
    existing = db.get_user_by_email(body.email)
    if existing:
        raise HTTPException(status_code=409, detail="이미 등록된 이메일입니다.")

    user = db.create_user(
        email=body.email,
        password_hash=_hash_password(body.password),
        display_name=body.display_name,
        company_name=body.company_name,
    )
    return {"user_id": user["id"], "email": user["email"]}


@app.post("/api/auth/login")
def login(body: UserLogin):
    user = db.get_user_by_email(body.email)
    if not user:
        raise HTTPException(status_code=401, detail="이메일 또는 비밀번호가 틀립니다.")

    if user["password_hash"] != _hash_password(body.password):
        raise HTTPException(status_code=401, detail="이메일 또는 비밀번호가 틀립니다.")

    return {"user_id": user["id"], "email": user["email"], "role": user["role"]}


# ─────────────────────────────────────────────────────────────
# 법령
# ─────────────────────────────────────────────────────────────

@app.get("/api/laws")
def list_laws(
    keyword: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    laws = db.list_laws(limit=limit, offset=offset, keyword=keyword)
    return {"items": laws, "count": len(laws), "limit": limit, "offset": offset}


@app.get("/api/laws/{law_db_id}")
def get_law(law_db_id: str):
    law = db.get_law(law_db_id)
    if not law:
        raise HTTPException(status_code=404, detail="법령을 찾을 수 없습니다.")
    return law


# ─────────────────────────────────────────────────────────────
# 판례
# ─────────────────────────────────────────────────────────────

@app.get("/api/precedents")
def list_precedents(
    keyword: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    precs = db.list_precedents(limit=limit, offset=offset, keyword=keyword)
    return {"items": precs, "count": len(precs), "limit": limit, "offset": offset}


@app.get("/api/precedents/{prec_db_id}")
def get_precedent(prec_db_id: str):
    prec = db.get_precedent(prec_db_id)
    if not prec:
        raise HTTPException(status_code=404, detail="판례를 찾을 수 없습니다.")
    return prec


# ─────────────────────────────────────────────────────────────
# 프로젝트
# ─────────────────────────────────────────────────────────────

@app.get("/api/projects")
def list_projects(
    x_user_id: str = Header(...),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    user_id = _get_user_id(x_user_id)
    projects = db.list_projects(user_id=user_id, limit=limit, offset=offset)
    return {"items": projects, "count": len(projects)}


@app.post("/api/projects", status_code=201)
def create_project(body: ProjectCreate, x_user_id: str = Header(...)):
    user_id = _get_user_id(x_user_id)
    project = db.create_project(
        user_id=user_id,
        name=body.name,
        description=body.description,
        app_category=body.app_category,
        platforms=body.platforms,
        regions=body.regions,
        features=body.features,
    )
    return project


@app.get("/api/projects/{project_id}")
def get_project(project_id: str, x_user_id: str = Header(...)):
    _get_user_id(x_user_id)
    project = db.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="프로젝트를 찾을 수 없습니다.")
    return project


@app.put("/api/projects/{project_id}")
def update_project(project_id: str, body: ProjectUpdate, x_user_id: str = Header(...)):
    _get_user_id(x_user_id)
    updates = body.model_dump(exclude_none=True)
    if not updates:
        raise HTTPException(status_code=400, detail="수정할 내용이 없습니다.")
    db.update_project(project_id, **updates)
    return db.get_project(project_id)


@app.delete("/api/projects/{project_id}")
def delete_project(project_id: str, x_user_id: str = Header(...)):
    _get_user_id(x_user_id)
    deleted = db.delete_project(project_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="프로젝트를 찾을 수 없습니다.")
    return {"deleted": True}


# ─────────────────────────────────────────────────────────────
# 검색
# ─────────────────────────────────────────────────────────────

@app.get("/api/search")
def fts_search(
    q: str = Query(..., min_length=1),
    source_type: Optional[str] = Query(None, pattern="^(law|precedent|store_policy)$"),
    limit: int = Query(10, ge=1, le=50),
):
    """FTS5 전문 검색"""
    results = db.fts_search(query=q, source_type=source_type, limit=limit)
    return {"query": q, "count": len(results), "items": results}


@app.get("/api/search/rag")
def rag_search(
    q: str = Query(..., min_length=1),
    top_k: int = Query(5, ge=1, le=20),
    threshold: float = Query(0.1, ge=0.0, le=1.0),
    x_user_id: Optional[str] = Header(None),
):
    """RAG 벡터 검색 (TF-IDF 코사인 유사도)"""
    results = search_legal_context(
        query=q,
        top_k=top_k,
        score_threshold=threshold,
        user_id=x_user_id,
    )
    return {"query": q, "count": len(results), "items": results}


# ─────────────────────────────────────────────────────────────
# 분석
# ─────────────────────────────────────────────────────────────

@app.post("/api/projects/{project_id}/analyses", status_code=201)
def create_analysis(
    project_id: str,
    body: AnalysisCreate,
    x_user_id: str = Header(...),
):
    user_id = _get_user_id(x_user_id)
    project = db.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="프로젝트를 찾을 수 없습니다.")

    analysis_id = db.create_analysis(
        project_id=project_id,
        user_id=user_id,
        analysis_type=body.analysis_type,
    )
    return {"analysis_id": analysis_id, "status": "in_progress"}


@app.get("/api/projects/{project_id}/analyses")
def list_analyses(
    project_id: str,
    x_user_id: str = Header(...),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    _get_user_id(x_user_id)
    analyses = db.list_analyses(project_id=project_id, limit=limit, offset=offset)
    return {"items": analyses, "count": len(analyses)}


@app.get("/api/analyses/{analysis_id}")
def get_analysis(analysis_id: str, x_user_id: str = Header(...)):
    _get_user_id(x_user_id)
    analysis = db.get_analysis(analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="분석 결과를 찾을 수 없습니다.")
    return analysis


# ─────────────────────────────────────────────────────────────
# 엔트리포인트
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
