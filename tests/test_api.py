"""
SafeLaunch AI -- API 엔드포인트 테스트
tests/test_api.py

실행: pytest tests/test_api.py -v
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi.testclient import TestClient
from api import app


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


@pytest.fixture()
def test_user(client):
    """테스트용 사용자 생성 → user_id 반환 → 종료 후 삭제"""
    import uuid
    email = f"test_{uuid.uuid4().hex[:8]}@test.com"
    r = client.post("/api/auth/register", json={
        "email": email,
        "password": "pw1234",
        "display_name": "Test",
    })
    user_id = r.json()["user_id"]
    yield user_id

    # cleanup
    from core.database import db
    db.delete_user(user_id)


# ──────────────────────────────────────────────
# System
# ──────────────────────────────────────────────

class TestSystem:
    def test_health(self, client):
        r = client.get("/api/health")
        assert r.status_code == 200
        assert r.json()["status"] == "ok"

    def test_stats(self, client):
        r = client.get("/api/stats")
        assert r.status_code == 200
        assert "laws" in r.json()


# ──────────────────────────────────────────────
# Auth
# ──────────────────────────────────────────────

class TestAuth:
    def test_register_and_login(self, client):
        import uuid
        email = f"auth_{uuid.uuid4().hex[:8]}@test.com"

        # Register
        r = client.post("/api/auth/register", json={
            "email": email,
            "password": "secret123",
        })
        assert r.status_code == 200
        user_id = r.json()["user_id"]

        # Login
        r = client.post("/api/auth/login", json={
            "email": email,
            "password": "secret123",
        })
        assert r.status_code == 200
        assert r.json()["user_id"] == user_id

        # Wrong password
        r = client.post("/api/auth/login", json={
            "email": email,
            "password": "wrong",
        })
        assert r.status_code == 401

        # Cleanup
        from core.database import db
        db.delete_user(user_id)

    def test_duplicate_register(self, client, test_user):
        from core.database import db
        user = db.get_user(test_user)
        r = client.post("/api/auth/register", json={
            "email": user["email"],
            "password": "pw",
        })
        assert r.status_code == 409


# ──────────────────────────────────────────────
# Laws / Precedents
# ──────────────────────────────────────────────

class TestLaws:
    def test_list_laws(self, client):
        r = client.get("/api/laws?limit=5")
        assert r.status_code == 200
        assert r.json()["count"] <= 5

    def test_list_laws_keyword(self, client):
        r = client.get("/api/laws?keyword=저작권")
        assert r.status_code == 200
        for item in r.json()["items"]:
            assert "저작권" in item["law_name"]


class TestPrecedents:
    def test_list_precedents(self, client):
        r = client.get("/api/precedents?limit=5")
        assert r.status_code == 200
        assert r.json()["count"] <= 5


# ──────────────────────────────────────────────
# Projects CRUD
# ──────────────────────────────────────────────

class TestProjects:
    def test_crud_lifecycle(self, client, test_user):
        headers = {"X-User-Id": test_user}

        # Create
        r = client.post("/api/projects", json={
            "name": "My App",
            "platforms": ["ios"],
        }, headers=headers)
        assert r.status_code == 201
        proj_id = r.json()["id"]

        # List
        r = client.get("/api/projects", headers=headers)
        assert r.status_code == 200
        assert r.json()["count"] >= 1

        # Get
        r = client.get(f"/api/projects/{proj_id}", headers=headers)
        assert r.status_code == 200
        assert r.json()["name"] == "My App"

        # Update
        r = client.put(f"/api/projects/{proj_id}", json={
            "name": "Updated App",
        }, headers=headers)
        assert r.status_code == 200
        assert r.json()["name"] == "Updated App"

        # Delete
        r = client.delete(f"/api/projects/{proj_id}", headers=headers)
        assert r.status_code == 200
        assert r.json()["deleted"] is True

    def test_unauthorized_access(self, client):
        r = client.get("/api/projects")
        assert r.status_code == 422  # Missing required header


# ──────────────────────────────────────────────
# Search
# ──────────────────────────────────────────────

class TestSearch:
    def test_fts_search(self, client):
        r = client.get("/api/search?q=개인정보")
        assert r.status_code == 200
        assert r.json()["count"] >= 1

    def test_fts_search_with_source_type(self, client):
        r = client.get("/api/search?q=개인정보&source_type=law")
        assert r.status_code == 200
        for item in r.json()["items"]:
            assert item["source_type"] == "law"

    def test_rag_search(self, client):
        r = client.get("/api/search/rag?q=앱 개인정보 수집&top_k=3&threshold=0.05")
        assert r.status_code == 200
        assert r.json()["count"] >= 0


# ──────────────────────────────────────────────
# Analysis
# ──────────────────────────────────────────────

class TestAnalysis:
    def test_create_and_list_analysis(self, client, test_user):
        headers = {"X-User-Id": test_user}

        # Create project
        r = client.post("/api/projects", json={"name": "AnalysisTest"}, headers=headers)
        proj_id = r.json()["id"]

        # Create analysis
        r = client.post(f"/api/projects/{proj_id}/analyses", json={
            "analysis_type": "quick",
        }, headers=headers)
        assert r.status_code == 201
        analysis_id = r.json()["analysis_id"]

        # List
        r = client.get(f"/api/projects/{proj_id}/analyses", headers=headers)
        assert r.status_code == 200
        assert r.json()["count"] >= 1

        # Get detail
        r = client.get(f"/api/analyses/{analysis_id}", headers=headers)
        assert r.status_code == 200
        assert r.json()["analysis_type"] == "quick"

        # Cleanup
        from core.database import db
        db.delete_project(proj_id)
