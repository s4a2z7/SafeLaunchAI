"""
SafeLaunch AI -- database.py 단위 테스트
tests/test_database.py

실행: pytest tests/test_database.py -v
"""

import os
import sys
import tempfile
import shutil

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.database import DatabaseManager


@pytest.fixture()
def tmp_db():
    """테스트용 임시 DB — 테스트 종료 후 자동 삭제"""
    tmp_dir = tempfile.mkdtemp()
    db_path = os.path.join(tmp_dir, "test.db")

    # schema.sql 경로를 복사
    src_schema = os.path.join(os.path.dirname(__file__), "..", "database", "schema.sql")
    dst_schema = os.path.join(tmp_dir, "schema.sql")
    shutil.copy(src_schema, dst_schema)

    # DatabaseManager가 스키마를 찾을 수 있도록 monkey-patch
    import core.database as dbmod
    original_schema = dbmod.SCHEMA_PATH
    dbmod.SCHEMA_PATH = dst_schema

    db = DatabaseManager(db_path=db_path)

    yield db

    dbmod.SCHEMA_PATH = original_schema
    shutil.rmtree(tmp_dir, ignore_errors=True)


# ──────────────────────────────────────────────
# A. Users
# ──────────────────────────────────────────────

class TestUsers:
    def test_create_and_get_user(self, tmp_db):
        user = tmp_db.create_user(email="a@b.com", password_hash="hash")
        assert user["email"] == "a@b.com"
        assert user["id"]

        fetched = tmp_db.get_user(user["id"])
        assert fetched is not None
        assert fetched["email"] == "a@b.com"

    def test_get_user_by_email(self, tmp_db):
        tmp_db.create_user(email="find@me.com", password_hash="h")
        result = tmp_db.get_user_by_email("find@me.com")
        assert result is not None
        assert result["email"] == "find@me.com"

    def test_update_user(self, tmp_db):
        user = tmp_db.create_user(email="upd@t.com", password_hash="h")
        tmp_db.update_user(user["id"], display_name="Updated Name")
        fetched = tmp_db.get_user(user["id"])
        assert fetched["display_name"] == "Updated Name"

    def test_delete_user(self, tmp_db):
        user = tmp_db.create_user(email="del@t.com", password_hash="h")
        assert tmp_db.delete_user(user["id"]) is True
        assert tmp_db.get_user(user["id"]) is None

    def test_duplicate_email_fails(self, tmp_db):
        tmp_db.create_user(email="dup@t.com", password_hash="h")
        with pytest.raises(Exception):
            tmp_db.create_user(email="dup@t.com", password_hash="h2")


# ──────────────────────────────────────────────
# A. Projects
# ──────────────────────────────────────────────

class TestProjects:
    def test_create_and_get_project(self, tmp_db):
        user = tmp_db.create_user(email="p@t.com", password_hash="h")
        proj = tmp_db.create_project(
            user_id=user["id"],
            name="TestApp",
            platforms=["ios", "android"],
            regions=["KR"],
            features={"has_ugc": True},
        )
        assert proj["name"] == "TestApp"

        detail = tmp_db.get_project(proj["id"])
        assert detail["platforms"] == ["ios", "android"]
        assert detail["regions"] == ["KR"]
        assert detail["features"]["has_ugc"] is True

    def test_list_projects_pagination(self, tmp_db):
        user = tmp_db.create_user(email="list@t.com", password_hash="h")
        for i in range(5):
            tmp_db.create_project(user_id=user["id"], name=f"App{i}")

        page1 = tmp_db.list_projects(user["id"], limit=3, offset=0)
        page2 = tmp_db.list_projects(user["id"], limit=3, offset=3)

        assert len(page1) == 3
        assert len(page2) == 2

    def test_update_project(self, tmp_db):
        user = tmp_db.create_user(email="u@t.com", password_hash="h")
        proj = tmp_db.create_project(user_id=user["id"], name="Old")
        tmp_db.update_project(proj["id"], name="New", platforms=["ios"])

        updated = tmp_db.get_project(proj["id"])
        assert updated["name"] == "New"
        assert updated["platforms"] == ["ios"]

    def test_delete_project(self, tmp_db):
        user = tmp_db.create_user(email="d@t.com", password_hash="h")
        proj = tmp_db.create_project(user_id=user["id"], name="Gone")
        assert tmp_db.delete_project(proj["id"]) is True
        assert tmp_db.get_project(proj["id"]) is None


# ──────────────────────────────────────────────
# B. Laws / Precedents
# ──────────────────────────────────────────────

class TestLegalData:
    def test_upsert_law_insert_and_update(self, tmp_db):
        law_id = tmp_db.upsert_law(law_id="L001", law_name="테스트법")
        assert law_id

        # 같은 law_id로 upsert → 업데이트
        law_id2 = tmp_db.upsert_law(law_id="L001", law_name="테스트법 개정", raw_content="본문")
        assert law_id2 == law_id

        fetched = tmp_db.get_law(law_id)
        assert fetched["law_name"] == "테스트법 개정"
        assert fetched["raw_content"] == "본문"

    def test_list_laws_keyword(self, tmp_db):
        tmp_db.upsert_law(law_id="L1", law_name="저작권법")
        tmp_db.upsert_law(law_id="L2", law_name="개인정보보호법")
        tmp_db.upsert_law(law_id="L3", law_name="전자상거래법")

        result = tmp_db.list_laws(keyword="저작권")
        assert len(result) == 1
        assert result[0]["law_name"] == "저작권법"

    def test_upsert_precedent(self, tmp_db):
        prec_id = tmp_db.upsert_precedent(
            precedent_seq="P001", case_name="테스트 판례",
            court_name="대법원", case_type="민사",
        )
        assert prec_id

        fetched = tmp_db.get_precedent_by_seq("P001")
        assert fetched["case_name"] == "테스트 판례"
        assert fetched["court_name"] == "대법원"

    def test_list_precedents(self, tmp_db):
        tmp_db.upsert_precedent(precedent_seq="P1", case_name="판례A")
        tmp_db.upsert_precedent(precedent_seq="P2", case_name="판례B")
        result = tmp_db.list_precedents(limit=10)
        assert len(result) == 2


# ──────────────────────────────────────────────
# C. RAG / Chunks
# ──────────────────────────────────────────────

class TestChunks:
    def test_upsert_chunk_dedup(self, tmp_db):
        law_id = tmp_db.upsert_law(law_id="L1", law_name="법")
        c1 = tmp_db.upsert_chunk("hash1", "law", law_id, 0, "텍스트1")
        c2 = tmp_db.upsert_chunk("hash1", "law", law_id, 0, "텍스트1")  # 중복
        assert c1 == c2  # 같은 ID 반환

    def test_search_chunks(self, tmp_db):
        law_id = tmp_db.upsert_law(law_id="L1", law_name="법")
        tmp_db.upsert_chunk("h1", "law", law_id, 0, "개인정보 보호법 관련 내용")
        tmp_db.upsert_chunk("h2", "law", law_id, 1, "저작권 침해 관련 내용")

        result = tmp_db.search_chunks("개인정보")
        assert len(result) == 1
        assert "개인정보" in result[0]["content"]

    def test_log_search(self, tmp_db):
        log_id = tmp_db.log_search(query_text="테스트 쿼리", result_count=5, duration_ms=100)
        assert log_id


# ──────────────────────────────────────────────
# D. Analysis
# ──────────────────────────────────────────────

class TestAnalysis:
    def test_full_analysis_lifecycle(self, tmp_db):
        user = tmp_db.create_user(email="a@a.com", password_hash="h")
        proj = tmp_db.create_project(user_id=user["id"], name="App")

        # 분석 생성
        analysis_id = tmp_db.create_analysis(proj["id"], user["id"], "full")
        assert analysis_id

        # 발견 사항 추가
        f1 = tmp_db.add_finding(analysis_id, "violation", "high", "privacy", "제목1", "설명1")
        f2 = tmp_db.add_finding(analysis_id, "warning", "medium", "content", "제목2", "설명2")

        # 근거 연결
        tmp_db.add_finding_reference(f1, "law", "some_law_id", cited_text="법조문")

        # 분석 완료
        tmp_db.complete_analysis(analysis_id, "high", summary="위험도 높음")

        # 조회
        result = tmp_db.get_analysis(analysis_id)
        assert result["status"] == "completed"
        assert result["overall_risk_level"] == "high"
        assert result["total_findings"] == 2
        assert result["high_count"] == 1
        assert result["medium_count"] == 1
        assert len(result["findings"]) == 2
        assert len(result["findings"][0]["references"]) == 1

    def test_list_analyses(self, tmp_db):
        user = tmp_db.create_user(email="l@a.com", password_hash="h")
        proj = tmp_db.create_project(user_id=user["id"], name="App")

        for _ in range(3):
            tmp_db.create_analysis(proj["id"], user["id"])

        result = tmp_db.list_analyses(proj["id"])
        assert len(result) == 3


# ──────────────────────────────────────────────
# E. Sync
# ──────────────────────────────────────────────

class TestSync:
    def test_sync_lifecycle(self, tmp_db):
        sync_id = tmp_db.start_sync("laws", queries=["저작권"])
        assert sync_id

        tmp_db.complete_sync(sync_id, items_added=10, chunks_created=50)

        with tmp_db.connection() as conn:
            row = conn.execute("SELECT * FROM sync_logs WHERE id=?", (sync_id,)).fetchone()
            assert row["status"] == "completed"
            assert row["items_added"] == 10


# ──────────────────────────────────────────────
# 통계
# ──────────────────────────────────────────────

class TestStats:
    def test_get_stats(self, tmp_db):
        stats = tmp_db.get_stats()
        assert "users" in stats
        assert "laws" in stats
        assert "document_chunks" in stats
