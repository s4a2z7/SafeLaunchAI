"""
SafeLaunch AI — 데이터베이스 매니저 v2.0
core/database.py

SQLite 기반 관계형 데이터베이스 관리 모듈 (v2.0 간결판)
- schema.sql v2.0 기반 (11개 테이블)
- CRUD 헬퍼 메서드
- JSON 컬럼으로 프로젝트 하위 데이터 단순화
- 기존 JSON 벡터 스토어와 병행 운영 가능

사용법:
    from core.database import db

    # 프로젝트 생성
    project = db.create_project(user_id, name="My App", ...)

    # 분석 결과 조회
    analysis = db.get_latest_analysis(project_id)
"""

import sqlite3
import os
import uuid
import json
import logging
from datetime import datetime, timezone
from typing import Optional
from contextlib import contextmanager

logger = logging.getLogger("database")
if not logger.handlers:
    _handler = logging.StreamHandler()
    _handler.setFormatter(logging.Formatter("[%(name)s] %(levelname)s: %(message)s"))
    logger.addHandler(_handler)
    logger.setLevel(logging.INFO)

# ─────────────────────────────────────────────────────────────
# 설정
# ─────────────────────────────────────────────────────────────

DATABASE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "database")
DATABASE_PATH = os.path.join(DATABASE_DIR, "safelaunch.db")
SCHEMA_PATH = os.path.join(DATABASE_DIR, "schema.sql")


def _new_id() -> str:
    """UUID v4 생성"""
    return str(uuid.uuid4())


def _now() -> str:
    """UTC ISO 8601 타임스탬프"""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ─────────────────────────────────────────────────────────────
# 데이터베이스 매니저
# ─────────────────────────────────────────────────────────────

class DatabaseManager:
    """SafeLaunch AI SQLite 데이터베이스 매니저 v2.0"""

    def __init__(self, db_path: str = DATABASE_PATH):
        self.db_path = db_path
        self._ensure_database()

    def _ensure_database(self) -> None:
        """데이터베이스 파일 및 스키마 존재 확인, 없으면 생성"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

        if not os.path.exists(self.db_path) or os.path.getsize(self.db_path) == 0:
            logger.info(f"데이터베이스 초기화: {self.db_path}")
            self._init_schema()
        else:
            with self.connection() as conn:
                cursor = conn.execute(
                    "SELECT count(*) FROM sqlite_master WHERE type='table'"
                )
                table_count = cursor.fetchone()[0]
                if table_count < 5:
                    logger.info("테이블이 부족합니다. 스키마를 재초기화합니다.")
                    self._init_schema()

    def _init_schema(self) -> None:
        """schema.sql 파일을 실행하여 테이블 생성"""
        if not os.path.exists(SCHEMA_PATH):
            raise FileNotFoundError(
                f"스키마 파일을 찾을 수 없습니다: {SCHEMA_PATH}\n"
                "database/schema.sql 파일이 필요합니다."
            )

        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            schema_sql = f.read()

        with self.connection() as conn:
            conn.executescript(schema_sql)
            logger.info("데이터베이스 스키마 초기화 완료")

    @contextmanager
    def connection(self):
        """SQLite 연결 컨텍스트 매니저"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    # ─────────────────────────────────────────────────────────
    # A. 사용자
    # ─────────────────────────────────────────────────────────

    def create_user(
        self,
        email: str,
        password_hash: str,
        display_name: Optional[str] = None,
        role: str = "user",
        company_name: Optional[str] = None,
    ) -> dict:
        """사용자 생성"""
        user_id = _new_id()
        now = _now()

        with self.connection() as conn:
            conn.execute(
                """INSERT INTO users
                   (id, email, password_hash, display_name, role, company_name, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (user_id, email, password_hash, display_name, role, company_name, now, now),
            )

        logger.info(f"사용자 생성: {email} (id={user_id})")
        return {"id": user_id, "email": email, "role": role}

    def get_user_by_email(self, email: str) -> Optional[dict]:
        """이메일로 사용자 조회"""
        with self.connection() as conn:
            row = conn.execute(
                "SELECT * FROM users WHERE email = ?", (email,)
            ).fetchone()
            return dict(row) if row else None

    def get_user(self, user_id: str) -> Optional[dict]:
        """ID로 사용자 조회"""
        with self.connection() as conn:
            row = conn.execute(
                "SELECT * FROM users WHERE id = ?", (user_id,)
            ).fetchone()
            return dict(row) if row else None

    # ─────────────────────────────────────────────────────────
    # A. 프로젝트 (JSON 컬럼 방식)
    # ─────────────────────────────────────────────────────────

    def create_project(
        self,
        user_id: str,
        name: str,
        description: Optional[str] = None,
        app_category: Optional[str] = None,
        platforms: Optional[list[str]] = None,
        regions: Optional[list[str]] = None,
        features: Optional[dict] = None,
    ) -> dict:
        """프로젝트 생성 (JSON 컬럼으로 하위 데이터 저장)"""
        project_id = _new_id()
        now = _now()

        with self.connection() as conn:
            conn.execute(
                """INSERT INTO projects
                   (id, user_id, name, description, app_category,
                    platforms, regions, features, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    project_id, user_id, name, description, app_category,
                    json.dumps(platforms or [], ensure_ascii=False),
                    json.dumps(regions or [], ensure_ascii=False),
                    json.dumps(features or {}, ensure_ascii=False),
                    now, now,
                ),
            )

        logger.info(f"프로젝트 생성: {name} (id={project_id})")
        return {
            "id": project_id,
            "name": name,
            "user_id": user_id,
            "platforms": platforms or [],
            "regions": regions or [],
        }

    def get_project(self, project_id: str) -> Optional[dict]:
        """프로젝트 상세 조회 (JSON 파싱 포함)"""
        with self.connection() as conn:
            row = conn.execute(
                "SELECT * FROM projects WHERE id = ?", (project_id,)
            ).fetchone()
            if not row:
                return None

            project = dict(row)
            project["platforms"] = json.loads(project.get("platforms") or "[]")
            project["regions"] = json.loads(project.get("regions") or "[]")
            project["features"] = json.loads(project.get("features") or "{}")
            return project

    def list_projects(self, user_id: str) -> list[dict]:
        """사용자의 프로젝트 목록 조회"""
        with self.connection() as conn:
            rows = conn.execute(
                """SELECT p.*,
                          (SELECT count(*) FROM compliance_analyses ca WHERE ca.project_id = p.id) as analysis_count
                   FROM projects p
                   WHERE p.user_id = ?
                   ORDER BY p.updated_at DESC""",
                (user_id,),
            ).fetchall()
            return [dict(r) for r in rows]

    # ─────────────────────────────────────────────────────────
    # B. 법률 데이터 카탈로그
    # ─────────────────────────────────────────────────────────

    def upsert_law(
        self,
        law_id: str,
        law_name: str,
        raw_content: Optional[str] = None,
        **kwargs,
    ) -> str:
        """법령 추가/갱신 (upsert)"""
        now = _now()

        with self.connection() as conn:
            existing = conn.execute(
                "SELECT id FROM laws WHERE law_id = ?", (law_id,)
            ).fetchone()

            if existing:
                db_id = existing["id"]
                conn.execute(
                    """UPDATE laws SET law_name=?, raw_content=COALESCE(?, raw_content),
                       proclamation_date=COALESCE(?, proclamation_date),
                       enforcement_date=COALESCE(?, enforcement_date),
                       source_url=COALESCE(?, source_url),
                       updated_at=?
                       WHERE id=?""",
                    (
                        law_name, raw_content,
                        kwargs.get("proclamation_date"),
                        kwargs.get("enforcement_date"),
                        kwargs.get("source_url"),
                        now, db_id,
                    ),
                )
                return db_id
            else:
                db_id = _new_id()
                conn.execute(
                    """INSERT INTO laws
                       (id, law_id, law_name, law_type, proclamation_date,
                        enforcement_date, source_url, raw_content, created_at, updated_at)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        db_id, law_id, law_name,
                        kwargs.get("law_type"),
                        kwargs.get("proclamation_date"),
                        kwargs.get("enforcement_date"),
                        kwargs.get("source_url"),
                        raw_content,
                        now, now,
                    ),
                )
                return db_id

    def upsert_precedent(
        self,
        precedent_seq: str,
        case_name: str,
        raw_content: Optional[str] = None,
        **kwargs,
    ) -> str:
        """판례 추가/갱신 (upsert)"""
        now = _now()

        with self.connection() as conn:
            existing = conn.execute(
                "SELECT id FROM precedents WHERE precedent_seq = ?", (precedent_seq,)
            ).fetchone()

            if existing:
                db_id = existing["id"]
                conn.execute(
                    """UPDATE precedents SET case_name=?, raw_content=COALESCE(?, raw_content),
                       court_name=COALESCE(?, court_name),
                       judgment_date=COALESCE(?, judgment_date),
                       case_number=COALESCE(?, case_number),
                       case_type=COALESCE(?, case_type),
                       source_url=COALESCE(?, source_url),
                       updated_at=?
                       WHERE id=?""",
                    (
                        case_name, raw_content,
                        kwargs.get("court_name"),
                        kwargs.get("judgment_date"),
                        kwargs.get("case_number"),
                        kwargs.get("case_type"),
                        kwargs.get("source_url"),
                        now, db_id,
                    ),
                )
                return db_id
            else:
                db_id = _new_id()
                conn.execute(
                    """INSERT INTO precedents
                       (id, precedent_seq, case_name, court_name,
                        judgment_date, case_number, case_type, source_url, raw_content,
                        created_at, updated_at)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        db_id, precedent_seq, case_name,
                        kwargs.get("court_name"),
                        kwargs.get("judgment_date"),
                        kwargs.get("case_number"),
                        kwargs.get("case_type"),
                        kwargs.get("source_url"),
                        raw_content,
                        now, now,
                    ),
                )
                return db_id

    def upsert_store_policy(
        self,
        store: str,
        section: str,
        subsection: str,
        content: str,
        **kwargs,
    ) -> str:
        """스토어 정책 추가/갱신"""
        now = _now()

        with self.connection() as conn:
            existing = conn.execute(
                "SELECT id FROM store_policies WHERE store=? AND section=? AND COALESCE(subsection,'')=?",
                (store, section, subsection or ""),
            ).fetchone()

            if existing:
                db_id = existing["id"]
                conn.execute(
                    """UPDATE store_policies SET content=?,
                       effective_date=COALESCE(?, effective_date), updated_at=?
                       WHERE id=?""",
                    (content, kwargs.get("effective_date"), now, db_id),
                )
                return db_id
            else:
                db_id = _new_id()
                conn.execute(
                    """INSERT INTO store_policies
                       (id, store, policy_name, section, subsection,
                        content, effective_date, created_at, updated_at)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        db_id, store,
                        kwargs.get("policy_name", f"{store.title()} Policy"),
                        section, subsection, content,
                        kwargs.get("effective_date"),
                        now, now,
                    ),
                )
                return db_id

    # ─────────────────────────────────────────────────────────
    # C. RAG 검색
    # ─────────────────────────────────────────────────────────

    def upsert_chunk(
        self,
        chunk_hash: str,
        source_type: str,
        source_id: str,
        chunk_index: int,
        content: str,
        metadata: Optional[dict] = None,
    ) -> str:
        """문서 청크 추가/갱신"""
        with self.connection() as conn:
            existing = conn.execute(
                "SELECT id FROM document_chunks WHERE chunk_hash = ?", (chunk_hash,)
            ).fetchone()

            if existing:
                return existing["id"]

            chunk_id = _new_id()
            conn.execute(
                """INSERT INTO document_chunks
                   (id, chunk_hash, source_type, source_id, chunk_index,
                    content, content_length, metadata_json, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    chunk_id, chunk_hash, source_type, source_id,
                    chunk_index, content, len(content),
                    json.dumps(metadata, ensure_ascii=False) if metadata else None,
                    _now(),
                ),
            )
            return chunk_id

    def log_search(
        self,
        query_text: str,
        result_count: int,
        user_id: Optional[str] = None,
        project_id: Optional[str] = None,
        top_score: Optional[float] = None,
        duration_ms: Optional[int] = None,
    ) -> str:
        """검색 이력 기록"""
        log_id = _new_id()
        with self.connection() as conn:
            conn.execute(
                """INSERT INTO search_logs
                   (id, user_id, project_id, query_text,
                    result_count, top_score, search_duration_ms, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    log_id, user_id, project_id, query_text,
                    result_count, top_score, duration_ms, _now(),
                ),
            )
        return log_id

    # ─────────────────────────────────────────────────────────
    # D. 분석 결과
    # ─────────────────────────────────────────────────────────

    def create_analysis(
        self,
        project_id: str,
        user_id: str,
        analysis_type: str = "full",
    ) -> str:
        """컴플라이언스 분석 생성"""
        analysis_id = _new_id()
        now = _now()

        with self.connection() as conn:
            conn.execute(
                """INSERT INTO compliance_analyses
                   (id, project_id, user_id, analysis_type, status, started_at, created_at)
                   VALUES (?, ?, ?, ?, 'in_progress', ?, ?)""",
                (analysis_id, project_id, user_id, analysis_type, now, now),
            )
            conn.execute(
                "UPDATE projects SET status='analyzing', updated_at=? WHERE id=?",
                (now, project_id),
            )

        logger.info(f"분석 생성: project={project_id}, type={analysis_type}")
        return analysis_id

    def add_finding(
        self,
        analysis_id: str,
        finding_type: str,
        severity: str,
        category: str,
        title: str,
        description: str,
        recommendation: Optional[str] = None,
        affected_platform: Optional[str] = None,
    ) -> str:
        """분석 발견 사항 추가"""
        finding_id = _new_id()
        with self.connection() as conn:
            conn.execute(
                """INSERT INTO analysis_findings
                   (id, analysis_id, finding_type, severity, category,
                    title, description, recommendation, affected_platform, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    finding_id, analysis_id, finding_type, severity,
                    category, title, description, recommendation,
                    affected_platform, _now(),
                ),
            )
        return finding_id

    def add_finding_reference(
        self,
        finding_id: str,
        reference_type: str,
        reference_id: str,
        chunk_id: Optional[str] = None,
        relevance_score: Optional[float] = None,
        cited_text: Optional[str] = None,
    ) -> str:
        """발견 사항에 근거 자료 연결"""
        ref_id = _new_id()
        with self.connection() as conn:
            conn.execute(
                """INSERT INTO finding_references
                   (id, finding_id, reference_type, reference_id, chunk_id,
                    relevance_score, cited_text, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (ref_id, finding_id, reference_type, reference_id,
                 chunk_id, relevance_score, cited_text, _now()),
            )
        return ref_id

    def complete_analysis(
        self,
        analysis_id: str,
        overall_risk_level: str,
        summary: Optional[str] = None,
        ai_model_used: Optional[str] = None,
    ) -> None:
        """분석 완료 처리"""
        now = _now()
        with self.connection() as conn:
            counts = conn.execute(
                """SELECT
                    count(*) as total,
                    sum(CASE WHEN severity='critical' THEN 1 ELSE 0 END) as critical_count,
                    sum(CASE WHEN severity='high' THEN 1 ELSE 0 END) as high_count,
                    sum(CASE WHEN severity='medium' THEN 1 ELSE 0 END) as medium_count,
                    sum(CASE WHEN severity='low' THEN 1 ELSE 0 END) as low_count
                   FROM analysis_findings WHERE analysis_id = ?""",
                (analysis_id,),
            ).fetchone()

            conn.execute(
                """UPDATE compliance_analyses SET
                   status='completed', overall_risk_level=?, summary=?, ai_model_used=?,
                   total_findings=?, critical_count=?, high_count=?, medium_count=?,
                   low_count=?, completed_at=?
                   WHERE id=?""",
                (
                    overall_risk_level, summary, ai_model_used,
                    counts["total"], counts["critical_count"],
                    counts["high_count"], counts["medium_count"],
                    counts["low_count"],
                    now, analysis_id,
                ),
            )

            project = conn.execute(
                "SELECT project_id FROM compliance_analyses WHERE id=?",
                (analysis_id,),
            ).fetchone()
            if project:
                conn.execute(
                    "UPDATE projects SET status='completed', updated_at=? WHERE id=?",
                    (now, project["project_id"]),
                )

        logger.info(f"분석 완료: id={analysis_id}, risk={overall_risk_level}")

    def get_analysis(self, analysis_id: str) -> Optional[dict]:
        """분석 결과 상세 조회 (발견 사항 + 근거 포함)"""
        with self.connection() as conn:
            analysis = conn.execute(
                "SELECT * FROM compliance_analyses WHERE id = ?",
                (analysis_id,),
            ).fetchone()
            if not analysis:
                return None

            analysis = dict(analysis)

            findings = conn.execute(
                """SELECT * FROM analysis_findings
                   WHERE analysis_id = ?
                   ORDER BY
                       CASE severity
                           WHEN 'critical' THEN 1
                           WHEN 'high' THEN 2
                           WHEN 'medium' THEN 3
                           WHEN 'low' THEN 4
                       END""",
                (analysis_id,),
            ).fetchall()

            analysis["findings"] = []
            for finding in findings:
                f = dict(finding)
                refs = conn.execute(
                    "SELECT * FROM finding_references WHERE finding_id = ?",
                    (f["id"],),
                ).fetchall()
                f["references"] = [dict(r) for r in refs]
                analysis["findings"].append(f)

            return analysis

    def get_latest_analysis(self, project_id: str) -> Optional[dict]:
        """프로젝트의 최신 분석 결과 조회"""
        with self.connection() as conn:
            row = conn.execute(
                """SELECT id FROM compliance_analyses
                   WHERE project_id = ?
                   ORDER BY created_at DESC LIMIT 1""",
                (project_id,),
            ).fetchone()
            if not row:
                return None
            return self.get_analysis(row["id"])

    # ─────────────────────────────────────────────────────────
    # E. 동기화
    # ─────────────────────────────────────────────────────────

    def start_sync(
        self,
        sync_type: str,
        queries: Optional[list[str]] = None,
        **kwargs,
    ) -> str:
        """동기화 시작 기록"""
        sync_id = _new_id()
        now = _now()
        with self.connection() as conn:
            conn.execute(
                """INSERT INTO sync_logs
                   (id, sync_type, queries_used, status, started_at)
                   VALUES (?, ?, ?, 'started', ?)""",
                (
                    sync_id, sync_type,
                    json.dumps(queries or [], ensure_ascii=False),
                    now,
                ),
            )
        return sync_id

    def complete_sync(
        self,
        sync_id: str,
        items_added: int = 0,
        items_failed: int = 0,
        chunks_created: int = 0,
        error_message: Optional[str] = None,
        **kwargs,
    ) -> None:
        """동기화 완료 기록"""
        status = "failed" if error_message else "completed"
        with self.connection() as conn:
            conn.execute(
                """UPDATE sync_logs SET
                   status=?, items_added=?, items_failed=?,
                   chunks_created=?, error_message=?, completed_at=?
                   WHERE id=?""",
                (
                    status, items_added, items_failed,
                    chunks_created, error_message, _now(), sync_id,
                ),
            )

    # ─────────────────────────────────────────────────────────
    # 통계
    # ─────────────────────────────────────────────────────────

    def get_stats(self) -> dict:
        """전체 시스템 통계"""
        with self.connection() as conn:
            stats = {}
            for table in ("users", "projects", "laws", "precedents",
                          "store_policies", "document_chunks",
                          "compliance_analyses", "analysis_findings"):
                stats[table] = conn.execute(f"SELECT count(*) FROM {table}").fetchone()[0]
            return stats


# ─────────────────────────────────────────────────────────────
# 싱글톤 인스턴스 (import 시 자동 초기화)
# ─────────────────────────────────────────────────────────────

db = DatabaseManager()


# ─────────────────────────────────────────────────────────────
# CLI 테스트
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("SafeLaunch AI — Database Manager v2.0 테스트")
    print("=" * 60)

    # 1. 사용자 생성
    print("\n[1] 사용자 생성")
    user = db.create_user(
        email="test@safelaunch.ai",
        password_hash="hashed_password_here",
        display_name="테스트 사용자",
        company_name="SafeLaunch Inc.",
    )
    print(f"    생성됨: {user}")

    # 2. 프로젝트 생성 (JSON 컬럼 방식)
    print("\n[2] 프로젝트 생성")
    project = db.create_project(
        user_id=user["id"],
        name="SafeChat App",
        description="소셜 채팅 앱 - UGC + 결제 기능 포함",
        app_category="소셜",
        platforms=["ios", "android"],
        regions=["KR", "US"],
        features={
            "has_ugc": True,
            "has_social": True,
            "has_payment": True,
            "has_login": True,
        },
    )
    print(f"    생성됨: {project}")

    # 3. 프로젝트 조회
    print("\n[3] 프로젝트 상세 조회")
    detail = db.get_project(project["id"])
    print(f"    이름: {detail['name']}")
    print(f"    플랫폼: {detail['platforms']}")
    print(f"    지역: {detail['regions']}")
    print(f"    기능: {detail['features']}")

    # 4. 시스템 통계
    print("\n[4] 시스템 통계")
    stats = db.get_stats()
    for key, val in stats.items():
        print(f"    {key}: {val}")

    print("\n" + "=" * 60)
    print("테스트 완료")
    print("=" * 60)
