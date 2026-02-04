-- ============================================================
-- SafeLaunch AI -- 관계형 데이터베이스 스키마 v2.0
-- 호환: SQLite (개발) / PostgreSQL (프로덕션)
-- 날짜: 2026-02-03
-- ============================================================
--
-- v2.0 변경: 21개 -> 11개 테이블 (YAGNI 원칙 적용)
--
-- 도메인 (4개):
--   A. 사용자 + 프로젝트   (users, projects)
--   B. 법률 데이터 카탈로그 (laws, precedents, store_policies)
--   C. RAG 검색            (document_chunks, search_logs)
--   D. 분석 결과           (compliance_analyses, analysis_findings, finding_references)
--   E. 동기화              (sync_logs)
--
-- ============================================================


-- ============================================================
-- A. 사용자 + 프로젝트
-- ============================================================

CREATE TABLE IF NOT EXISTS users (
    id              TEXT PRIMARY KEY,
    email           TEXT UNIQUE NOT NULL,
    password_hash   TEXT NOT NULL,
    display_name    TEXT,
    role            TEXT NOT NULL DEFAULT 'user' CHECK (role IN ('user', 'admin')),
    company_name    TEXT,
    is_active       INTEGER NOT NULL DEFAULT 1,
    created_at      TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    updated_at      TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);


CREATE TABLE IF NOT EXISTS projects (
    id              TEXT PRIMARY KEY,
    user_id         TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name            TEXT NOT NULL,
    description     TEXT,
    app_category    TEXT,
    status          TEXT NOT NULL DEFAULT 'draft' CHECK (status IN ('draft', 'analyzing', 'completed', 'archived')),
    -- JSON 컬럼으로 복잡한 하위 데이터를 단순화
    platforms       TEXT DEFAULT '[]',        -- JSON: ["ios","android"]
    regions         TEXT DEFAULT '[]',        -- JSON: ["KR","US"]
    features        TEXT DEFAULT '{}',        -- JSON: {"has_ugc":true,"has_payment":true,...}
    created_at      TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    updated_at      TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);

CREATE INDEX IF NOT EXISTS idx_projects_user ON projects(user_id);
CREATE INDEX IF NOT EXISTS idx_projects_status ON projects(status);


-- ============================================================
-- B. 법률 데이터 카탈로그 (마스터 데이터)
-- ============================================================

CREATE TABLE IF NOT EXISTS laws (
    id                TEXT PRIMARY KEY,
    law_id            TEXT UNIQUE NOT NULL,     -- 법령일련번호 (API 원본)
    law_name          TEXT NOT NULL,
    law_type          TEXT,                     -- 법률/대통령령/부령
    proclamation_date TEXT,
    enforcement_date  TEXT,
    source_url        TEXT,
    raw_content       TEXT,
    is_active         INTEGER NOT NULL DEFAULT 1,
    created_at        TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    updated_at        TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);

CREATE INDEX IF NOT EXISTS idx_laws_law_id ON laws(law_id);
CREATE INDEX IF NOT EXISTS idx_laws_name ON laws(law_name);


CREATE TABLE IF NOT EXISTS precedents (
    id              TEXT PRIMARY KEY,
    precedent_seq   TEXT UNIQUE NOT NULL,       -- 판례일련번호 (API 원본)
    case_name       TEXT NOT NULL,
    court_name      TEXT,
    judgment_date   TEXT,
    case_number     TEXT,
    case_type       TEXT,                       -- 민사/형사/행정
    source_url      TEXT,
    raw_content     TEXT,
    is_active       INTEGER NOT NULL DEFAULT 1,
    created_at      TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    updated_at      TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);

CREATE INDEX IF NOT EXISTS idx_precedents_seq ON precedents(precedent_seq);
CREATE INDEX IF NOT EXISTS idx_precedents_name ON precedents(case_name);


CREATE TABLE IF NOT EXISTS store_policies (
    id              TEXT PRIMARY KEY,
    store           TEXT NOT NULL CHECK (store IN ('apple', 'google')),
    policy_name     TEXT NOT NULL,
    section         TEXT NOT NULL,
    subsection      TEXT,
    content         TEXT NOT NULL,
    effective_date  TEXT,
    is_current      INTEGER NOT NULL DEFAULT 1,
    created_at      TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    updated_at      TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);

CREATE INDEX IF NOT EXISTS idx_store_policies_store ON store_policies(store);
CREATE INDEX IF NOT EXISTS idx_store_policies_section ON store_policies(section);


-- ============================================================
-- C. RAG 검색
-- ============================================================

CREATE TABLE IF NOT EXISTS document_chunks (
    id              TEXT PRIMARY KEY,
    chunk_hash      TEXT UNIQUE NOT NULL,
    source_type     TEXT NOT NULL CHECK (source_type IN ('law', 'precedent', 'store_policy')),
    source_id       TEXT NOT NULL,              -- laws.id / precedents.id / store_policies.id
    chunk_index     INTEGER NOT NULL,
    content         TEXT NOT NULL,
    content_length  INTEGER NOT NULL DEFAULT 0,
    metadata_json   TEXT,                       -- JSON: 유연한 메타데이터
    created_at      TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);

CREATE INDEX IF NOT EXISTS idx_chunks_hash ON document_chunks(chunk_hash);
CREATE INDEX IF NOT EXISTS idx_chunks_source ON document_chunks(source_type, source_id);


CREATE TABLE IF NOT EXISTS search_logs (
    id                  TEXT PRIMARY KEY,
    user_id             TEXT REFERENCES users(id) ON DELETE SET NULL,
    project_id          TEXT REFERENCES projects(id) ON DELETE SET NULL,
    query_text          TEXT NOT NULL,
    result_count        INTEGER NOT NULL DEFAULT 0,
    top_score           REAL,
    search_duration_ms  INTEGER,
    created_at          TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);

CREATE INDEX IF NOT EXISTS idx_search_logs_date ON search_logs(created_at);


-- ============================================================
-- D. 분석 결과 (핵심 비즈니스)
-- ============================================================

CREATE TABLE IF NOT EXISTS compliance_analyses (
    id                  TEXT PRIMARY KEY,
    project_id          TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    user_id             TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    analysis_type       TEXT NOT NULL DEFAULT 'full' CHECK (analysis_type IN ('full', 'quick', 'targeted')),
    status              TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'in_progress', 'completed', 'failed')),
    overall_risk_level  TEXT CHECK (overall_risk_level IN ('low', 'medium', 'high', 'critical') OR overall_risk_level IS NULL),
    total_findings      INTEGER NOT NULL DEFAULT 0,
    critical_count      INTEGER NOT NULL DEFAULT 0,
    high_count          INTEGER NOT NULL DEFAULT 0,
    medium_count        INTEGER NOT NULL DEFAULT 0,
    low_count           INTEGER NOT NULL DEFAULT 0,
    summary             TEXT,                   -- AI 종합 요약
    ai_model_used       TEXT,
    started_at          TEXT,
    completed_at        TEXT,
    created_at          TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);

CREATE INDEX IF NOT EXISTS idx_analyses_project ON compliance_analyses(project_id);
CREATE INDEX IF NOT EXISTS idx_analyses_status ON compliance_analyses(status);


CREATE TABLE IF NOT EXISTS analysis_findings (
    id                  TEXT PRIMARY KEY,
    analysis_id         TEXT NOT NULL REFERENCES compliance_analyses(id) ON DELETE CASCADE,
    finding_type        TEXT NOT NULL CHECK (finding_type IN ('violation', 'warning', 'recommendation', 'pass')),
    severity            TEXT NOT NULL DEFAULT 'medium' CHECK (severity IN ('low', 'medium', 'high', 'critical')),
    category            TEXT NOT NULL,          -- privacy/content/payment/ip/safety/children/ads
    title               TEXT NOT NULL,
    description         TEXT NOT NULL,
    recommendation      TEXT,
    affected_platform   TEXT,                   -- ios/android/both
    is_resolved         INTEGER NOT NULL DEFAULT 0,
    created_at          TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);

CREATE INDEX IF NOT EXISTS idx_findings_analysis ON analysis_findings(analysis_id);
CREATE INDEX IF NOT EXISTS idx_findings_severity ON analysis_findings(severity);


CREATE TABLE IF NOT EXISTS finding_references (
    id                  TEXT PRIMARY KEY,
    finding_id          TEXT NOT NULL REFERENCES analysis_findings(id) ON DELETE CASCADE,
    reference_type      TEXT NOT NULL CHECK (reference_type IN ('law', 'precedent', 'store_policy')),
    reference_id        TEXT NOT NULL,          -- 원천 테이블 id
    chunk_id            TEXT REFERENCES document_chunks(id) ON DELETE SET NULL,
    relevance_score     REAL,
    cited_text          TEXT,
    created_at          TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);

CREATE INDEX IF NOT EXISTS idx_finding_refs_finding ON finding_references(finding_id);


-- ============================================================
-- E. 동기화
-- ============================================================

CREATE TABLE IF NOT EXISTS sync_logs (
    id              TEXT PRIMARY KEY,
    sync_type       TEXT NOT NULL CHECK (sync_type IN ('laws', 'precedents', 'policies', 'full')),
    status          TEXT NOT NULL DEFAULT 'started' CHECK (status IN ('started', 'completed', 'failed')),
    queries_used    TEXT,                       -- JSON: 검색 키워드
    items_added     INTEGER NOT NULL DEFAULT 0,
    items_failed    INTEGER NOT NULL DEFAULT 0,
    chunks_created  INTEGER NOT NULL DEFAULT 0,
    error_message   TEXT,
    started_at      TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    completed_at    TEXT
);

CREATE INDEX IF NOT EXISTS idx_sync_logs_type ON sync_logs(sync_type);


-- ============================================================
-- 뷰 (View)
-- ============================================================

-- ============================================================
-- FTS5 전문 검색 인덱스 (document_chunks용)
-- ============================================================

CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts USING fts5(
    content,
    source_type,
    content='document_chunks',
    content_rowid='rowid'
);

-- FTS 동기화 트리거: INSERT
CREATE TRIGGER IF NOT EXISTS chunks_fts_insert AFTER INSERT ON document_chunks
BEGIN
    INSERT INTO chunks_fts(rowid, content, source_type)
    VALUES (NEW.rowid, NEW.content, NEW.source_type);
END;

-- FTS 동기화 트리거: DELETE
CREATE TRIGGER IF NOT EXISTS chunks_fts_delete BEFORE DELETE ON document_chunks
BEGIN
    INSERT INTO chunks_fts(chunks_fts, rowid, content, source_type)
    VALUES ('delete', OLD.rowid, OLD.content, OLD.source_type);
END;

-- FTS 동기화 트리거: UPDATE
CREATE TRIGGER IF NOT EXISTS chunks_fts_update AFTER UPDATE OF content ON document_chunks
BEGIN
    INSERT INTO chunks_fts(chunks_fts, rowid, content, source_type)
    VALUES ('delete', OLD.rowid, OLD.content, OLD.source_type);
    INSERT INTO chunks_fts(rowid, content, source_type)
    VALUES (NEW.rowid, NEW.content, NEW.source_type);
END;


-- ============================================================
-- 뷰 (View)
-- ============================================================

-- 발견 사항 + 근거 자료 통합 뷰
CREATE VIEW IF NOT EXISTS v_findings_detail AS
SELECT
    af.id AS finding_id,
    af.analysis_id,
    af.finding_type,
    af.severity,
    af.category,
    af.title,
    af.description,
    af.recommendation,
    af.affected_platform,
    af.is_resolved,
    fr.reference_type,
    fr.cited_text,
    fr.relevance_score,
    CASE
        WHEN fr.reference_type = 'law' THEN l.law_name
        WHEN fr.reference_type = 'precedent' THEN prec.case_name
        WHEN fr.reference_type = 'store_policy' THEN sp.section || ' - ' || COALESCE(sp.subsection, '')
    END AS reference_name
FROM analysis_findings af
LEFT JOIN finding_references fr ON fr.finding_id = af.id
LEFT JOIN laws l ON fr.reference_type = 'law' AND fr.reference_id = l.id
LEFT JOIN precedents prec ON fr.reference_type = 'precedent' AND fr.reference_id = prec.id
LEFT JOIN store_policies sp ON fr.reference_type = 'store_policy' AND fr.reference_id = sp.id;
