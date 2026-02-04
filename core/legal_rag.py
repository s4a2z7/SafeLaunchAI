"""
벡터 검색 모듈 — 법령·판례·스토어 정책 RAG
core/legal_rag.py

SafeLaunch AI 프로젝트용
- 국가법령정보 Open API 데이터를 TF-IDF 벡터로 임베딩 저장
- 쿼리 기반 코사인 유사도 검색으로 분석 근거 제공
- database/ 경로에 JSON으로 영속 저장

※ Python 3.14 환경에서 ChromaDB가 미지원(pydantic v1 호환 이슈)되므로
  scikit-learn TF-IDF + cosine_similarity 기반으로 구현.
  API명세서 3.2 인터페이스(search_legal_context)를 동일하게 유지하여
  향후 ChromaDB 전환 시 호출부 변경 없이 교체 가능.
"""

import json
import os
import re
import hashlib
import logging
import numpy as np
from typing import Optional
from datetime import datetime, timezone
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from core.law_api import (
    search_laws,
    search_precedents,
    get_law_detail,
    get_precedent_detail,
)

# DB 연동 (SQLite — database.py와 이중 적재)
try:
    from core.database import db as _db
except Exception:
    _db = None
    logger.warning("database 모듈 로드 실패 — JSON VectorStore 단독 모드로 동작합니다.")

# ─────────────────────────────────────────────────────────────
# 로깅 설정
# ─────────────────────────────────────────────────────────────
logger = logging.getLogger("legal_rag")
if not logger.handlers:
    _handler = logging.StreamHandler()
    _handler.setFormatter(logging.Formatter("[%(name)s] %(levelname)s: %(message)s"))
    logger.addHandler(_handler)
    logger.setLevel(logging.INFO)


# ─────────────────────────────────────────────────────────────
# 상수
# ─────────────────────────────────────────────────────────────

DATABASE_PATH = "./database"

COLLECTION_LAWS = "laws"
COLLECTION_PRECEDENTS = "precedents"
COLLECTION_POLICIES = "store_policies"

ALL_COLLECTIONS = [COLLECTION_LAWS, COLLECTION_PRECEDENTS, COLLECTION_POLICIES]

# 노이즈 감지용 패턴 (Red Team #1, #4)
NOISE_PATTERNS = re.compile(
    r"/DRF/|"
    r"\.css\b|"
    r"\.js\b|"
    r"\.jpg\b|"
    r"\.png\b|"
    r"\.gif\b|"
    r"font-family:|"
    r"font-size:|"
    r"text-align:|"
    r"margin-top:|"
    r"padding:|"
    r"background-color:|"
    r"border:|"
    r"<script|"
    r"<style|"
    r"jquery|"
    r"ext-all|"
    r"resources/css",
    re.IGNORECASE,
)

# 법률 문서 최소 유효성 키워드
LEGAL_KEYWORDS_LAW = ["제", "조", "항", "호", "법", "규정", "시행"]
LEGAL_KEYWORDS_PRECEDENT = [
    "판시사항", "판결요지", "판례", "원고", "피고", "법원", "선고",
    "판결", "사건", "청구", "항소", "상고", "위반", "침해",
]
LEGAL_KEYWORDS_POLICY = ["앱", "정책", "가이드", "심사", "콘텐츠", "데이터", "사용자"]


# ─────────────────────────────────────────────────────────────
# Step 1: 벡터 스토어 (JSON 기반 영속 저장)
# ─────────────────────────────────────────────────────────────

class VectorStore:
    """
    TF-IDF 기반 벡터 스토어

    - database/<collection>.json 파일에 문서·메타데이터를 저장
    - 검색 시 TF-IDF 벡터라이저를 즉시 생성하여 코사인 유사도 계산
    - upsert로 중복 방지 (문서 ID 기반)
    """

    def __init__(self, name: str, db_path: str = DATABASE_PATH):
        self.name = name
        self.db_path = db_path
        self._file_path = os.path.join(db_path, f"{name}.json")
        self._docs: dict[str, dict] = {}  # id → {"text", "metadata"}
        self._load()

    def _load(self) -> None:
        """JSON 파일에서 기존 데이터 로드"""
        if os.path.exists(self._file_path):
            try:
                with open(self._file_path, "r", encoding="utf-8") as f:
                    self._docs = json.load(f)
            except (json.JSONDecodeError, OSError):
                self._docs = {}

    def _save(self) -> None:
        """현재 데이터를 JSON 파일에 저장"""
        os.makedirs(self.db_path, exist_ok=True)
        with open(self._file_path, "w", encoding="utf-8") as f:
            json.dump(self._docs, f, ensure_ascii=False, indent=2)

    def upsert(
        self,
        ids: list[str],
        documents: list[str],
        metadatas: list[dict],
    ) -> None:
        """문서 추가/갱신 (ID 기반 중복 방지)"""
        for doc_id, text, meta in zip(ids, documents, metadatas):
            self._docs[doc_id] = {"text": text, "metadata": meta}
        self._save()

    def count(self) -> int:
        return len(self._docs)

    def query(
        self,
        query_text: str,
        n_results: int = 5,
    ) -> list[dict]:
        """
        TF-IDF 코사인 유사도 기반 하이브리드 검색 (Red Team #5 개선)

        char_wb + word 두 벡터라이저의 점수를 가중 합산하여
        문자 매칭과 단어 매칭을 동시에 활용합니다.

        Returns:
            [{"text": str, "metadata": dict, "score": float}, ...]
            score가 높을수록 유사 (0~1)
        """
        if not self._docs:
            return []

        doc_ids = list(self._docs.keys())
        doc_texts = [self._docs[d]["text"] for d in doc_ids]

        # 1) 문자 단위 벡터라이저 (한글 부분 매칭에 강점)
        char_vectorizer = TfidfVectorizer(
            analyzer="char_wb",
            ngram_range=(2, 4),
            max_features=15000,
            sublinear_tf=True,
        )

        # 2) 단어 단위 벡터라이저 (의미 단위 매칭에 강점)
        word_vectorizer = TfidfVectorizer(
            analyzer="word",
            ngram_range=(1, 2),
            max_features=15000,
            sublinear_tf=True,
        )

        try:
            char_matrix = char_vectorizer.fit_transform(doc_texts)
            char_query = char_vectorizer.transform([query_text])
            char_sim = cosine_similarity(char_query, char_matrix).flatten()
        except ValueError:
            char_sim = np.zeros(len(doc_ids))

        try:
            word_matrix = word_vectorizer.fit_transform(doc_texts)
            word_query = word_vectorizer.transform([query_text])
            word_sim = cosine_similarity(word_query, word_matrix).flatten()
        except ValueError:
            word_sim = np.zeros(len(doc_ids))

        # 하이브리드 점수: 단어 60% + 문자 40%
        similarities = (word_sim * 0.6) + (char_sim * 0.4)

        # 상위 n_results 인덱스 (내림차순)
        top_indices = np.argsort(similarities)[::-1][:n_results]

        results = []
        for idx in top_indices:
            score = float(similarities[idx])
            if score <= 0:
                continue
            did = doc_ids[idx]
            results.append(
                {
                    "text": self._docs[did]["text"],
                    "metadata": self._docs[did]["metadata"],
                    "score": round(score, 4),
                }
            )

        return results

    def clear(self) -> None:
        """컬렉션 초기화"""
        self._docs = {}
        if os.path.exists(self._file_path):
            os.remove(self._file_path)


# 컬렉션 캐시 (싱글톤)
_stores: dict[str, VectorStore] = {}


def get_or_create_collection(name: str) -> VectorStore:
    """컬렉션(VectorStore) 반환 — 없으면 생성"""
    if name not in _stores:
        _stores[name] = VectorStore(name)
    return _stores[name]


# ─────────────────────────────────────────────────────────────
# Step 2: 데이터 청킹 (Context-aware Chunking)
# ─────────────────────────────────────────────────────────────

def _is_noise_text(text: str) -> bool:
    """CSS/JS/HTML 노이즈 텍스트인지 판별 (Red Team #1, #4)"""
    if not text or len(text.strip()) < 10:
        return True
    # 노이즈 패턴 매칭 횟수가 전체 문장 대비 과다하면 노이즈
    matches = NOISE_PATTERNS.findall(text)
    if len(matches) >= 3:
        return True
    # 텍스트 대비 경로 구분자(/) 비율이 높으면 노이즈
    slash_ratio = text.count("/") / max(len(text), 1)
    if slash_ratio > 0.05:
        return True
    return False


def validate_legal_document(text: str, source_type: str) -> bool:
    """
    법률 문서 유효성 검증 (Red Team #6)

    Args:
        text: 정제된 문서 텍스트
        source_type: "law" | "precedent" | "store_policy"

    Returns:
        True면 유효한 법률 문서
    """
    if not text or not text.strip():
        return False

    # 1. 노이즈 패턴 탐지 (CSS/JS 등)
    if _is_noise_text(text):
        return False

    # 2. 소스 타입별 최소 길이 검증
    min_lengths = {"law": 100, "precedent": 80, "store_policy": 50}
    min_len = min_lengths.get(source_type, 50)
    if len(text.strip()) < min_len:
        return False

    # 3. 소스 타입별 법률 키워드 포함 여부
    keyword_map = {
        "law": LEGAL_KEYWORDS_LAW,
        "precedent": LEGAL_KEYWORDS_PRECEDENT,
        "store_policy": LEGAL_KEYWORDS_POLICY,
    }
    keywords = keyword_map.get(source_type, LEGAL_KEYWORDS_LAW)
    keyword_hits = sum(1 for kw in keywords if kw in text)
    if keyword_hits < 2:
        return False

    return True


def _clean_html(text: str) -> str:
    """HTML 태그 및 노이즈 제거"""
    # 스크립트/스타일 블록 전체 제거
    text = re.sub(r"<script[^>]*>.*?</script>", "", text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<style[^>]*>.*?</style>", "", text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"&[a-zA-Z]+;", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _generate_chunk_id(source_id: str, chunk_index: int) -> str:
    """청크 고유 ID 생성 (중복 적재 방지용)"""
    raw = f"{source_id}_chunk_{chunk_index}"
    return hashlib.md5(raw.encode()).hexdigest()


def chunk_law_text(
    text: str,
    metadata: dict,
    chunk_size: int = 800,
    overlap: int = 150,
) -> list[dict]:
    """
    법령·판례 텍스트를 문맥 단위로 청킹

    조·항 경계를 우선 분할 기준으로 사용하고,
    경계가 없거나 단일 조문이 chunk_size를 초과하면 글자 수 기반으로 분할합니다.

    Args:
        text: 원문 텍스트 (HTML 포함 가능)
        metadata: 원천 메타데이터
        chunk_size: 청크 최대 글자 수 (권장 500~1000)
        overlap: 청크 간 겹침 글자 수

    Returns:
        [{"id": str, "text": str, "metadata": dict}, ...]
    """
    cleaned = _clean_html(text)
    if not cleaned:
        return []

    source_id = metadata.get("source_id", "unknown")

    # 조문 경계(제N조) 기준 분할 시도
    segments = re.split(r"(?=제\d+조[\s(])", cleaned)
    segments = [s.strip() for s in segments if s.strip()]

    # 경계 분할 결과가 없으면 원본을 그대로 사용
    if not segments:
        segments = [cleaned]

    chunks: list[dict] = []
    current = ""

    for segment in segments:
        # 현재 버퍼 + 세그먼트가 한도 내이면 합치기
        if len(current) + len(segment) + 1 <= chunk_size:
            current += (" " if current else "") + segment
            continue

        # 버퍼가 찼으면 청크로 확정
        if current:
            _append_chunk(chunks, current, metadata, source_id)

        # 세그먼트 자체가 한도 초과이면 글자 수 기반 분할
        if len(segment) > chunk_size:
            for i in range(0, len(segment), chunk_size - overlap):
                sub = segment[i : i + chunk_size].strip()
                if sub:
                    _append_chunk(chunks, sub, metadata, source_id)
            current = ""
        else:
            current = segment

    # 마지막 잔여 버퍼
    if current.strip():
        _append_chunk(chunks, current.strip(), metadata, source_id)

    return chunks


def _append_chunk(
    chunks: list[dict], text: str, metadata: dict, source_id: str
) -> None:
    """청크 리스트에 새 청크를 추가하는 내부 헬퍼"""
    idx = len(chunks)
    chunks.append(
        {
            "id": _generate_chunk_id(source_id, idx),
            "text": text,
            "metadata": {**metadata, "chunk_index": idx},
        }
    )


def chunk_precedent_text(
    text: str,
    metadata: dict,
    chunk_size: int = 1200,
    overlap: int = 300,
) -> list[dict]:
    """
    판례 텍스트 전용 청킹 (Red Team #10)

    판례는 [판시사항], [판결요지] 등의 섹션 헤더를 기준으로 분할합니다.
    조문 경계(제N조)가 없는 판례 특성에 맞게:
    - 섹션 헤더 기반 분할 우선
    - chunk_size를 1200자로 확대 (법률 문맥 유지)
    - overlap을 300자로 확대 (문맥 손실 방지)

    Args:
        text: 판례 원문 텍스트
        metadata: 원천 메타데이터
        chunk_size: 청크 최대 글자 수
        overlap: 청크 간 겹침 글자 수

    Returns:
        [{"id": str, "text": str, "metadata": dict}, ...]
    """
    cleaned = _clean_html(text)
    if not cleaned:
        return []

    source_id = metadata.get("source_id", "unknown")

    # 판례 섹션 헤더 기반 분할 (판시사항, 판결요지, 참조조문, 판례내용 등)
    section_pattern = r"(?=\[(판시사항|판결요지|참조조문|참조판례|판례내용|이유|주문|청구취지)\])"
    segments = re.split(section_pattern, cleaned)
    # re.split with group captures: merge header + content pairs
    merged_segments: list[str] = []
    i = 0
    while i < len(segments):
        seg = segments[i].strip()
        if seg in ("판시사항", "판결요지", "참조조문", "참조판례", "판례내용", "이유", "주문", "청구취지"):
            # 이 헤더는 다음 세그먼트 앞에 붙여야 함
            if i + 1 < len(segments):
                merged_segments.append(f"[{seg}] {segments[i + 1].strip()}")
                i += 2
            else:
                merged_segments.append(f"[{seg}]")
                i += 1
        else:
            if seg:
                merged_segments.append(seg)
            i += 1

    # 섹션 분할 결과가 없으면 원본 사용
    if not merged_segments:
        merged_segments = [cleaned]

    chunks: list[dict] = []
    current = ""

    for segment in merged_segments:
        if len(current) + len(segment) + 1 <= chunk_size:
            current += (" " if current else "") + segment
            continue

        if current:
            _append_chunk(chunks, current, metadata, source_id)

        # 세그먼트가 한도 초과 시 글자 수 기반 분할
        if len(segment) > chunk_size:
            for j in range(0, len(segment), chunk_size - overlap):
                sub = segment[j : j + chunk_size].strip()
                if sub:
                    _append_chunk(chunks, sub, metadata, source_id)
            current = ""
        else:
            current = segment

    if current.strip():
        _append_chunk(chunks, current.strip(), metadata, source_id)

    return chunks


# ─────────────────────────────────────────────────────────────
# Step 3: 데이터 적재 (Ingestion)
# ─────────────────────────────────────────────────────────────

def _extract_law_text(detail: dict) -> str:
    """법령 상세 응답(XML→dict)에서 본문 텍스트 추출"""
    law = detail.get("법령", {})
    if not law:
        law = detail.get("LawService", {})

    parts: list[str] = []

    # 조문 단위 추출
    articles_wrap = law.get("조문", {})
    articles = articles_wrap.get("조문단위", [])
    if not isinstance(articles, list):
        articles = [articles] if articles else []

    for art in articles:
        title = art.get("조문제목", "")
        content = art.get("조문내용", "")
        if title:
            parts.append(title)
        if content:
            parts.append(content)

        # 항 내용
        paras = art.get("항", [])
        if not isinstance(paras, list):
            paras = [paras] if paras else []
        for p in paras:
            p_text = p.get("항내용", "")
            if p_text:
                parts.append(p_text)

    # 구조화된 조문이 없으면 긴 문자열 필드를 수집
    if not parts:
        for value in law.values():
            if isinstance(value, str) and len(value) > 50:
                parts.append(value)

    return "\n".join(parts)


def _extract_precedent_text(detail: dict) -> str:
    """
    판례 상세 응답에서 본문 텍스트 추출 (Red Team #1, #4 개선)

    1. 구조화된 XML 필드(판시사항, 판결요지 등)를 우선 추출
    2. dict/OrderedDict 중첩 구조 재귀 탐색
    3. CSS/JS 노이즈 필터링 강화
    4. 유효성 검증 후 반환
    """
    # API 응답 키: XML type → "PrecService", 구버전 → "판례"
    prec = detail.get("PrecService", {})
    if not prec:
        prec = detail.get("판례", {})
    if not prec:
        # 최상위에 직접 필드가 있는 경우도 탐색
        prec = detail

    parts: list[str] = []
    field_keys = ["판시사항", "판결요지", "참조조문", "참조판례", "판례내용"]

    for key in field_keys:
        value = prec.get(key, "")
        # dict/OrderedDict인 경우 내부 텍스트 재귀 추출
        if isinstance(value, dict):
            extracted = _extract_text_recursive(value)
            if extracted and not _is_noise_text(extracted):
                parts.append(f"[{key}]\n{extracted}")
        elif isinstance(value, str):
            cleaned = _clean_html(value)
            if cleaned and len(cleaned) > 20 and not _is_noise_text(cleaned):
                parts.append(f"[{key}]\n{cleaned}")

    # 구조화 필드 실패 시: 모든 값에서 유효 텍스트 수집
    if not parts:
        for key, value in prec.items():
            if isinstance(value, str) and len(value) > 50:
                cleaned = _clean_html(value)
                if cleaned and not _is_noise_text(cleaned):
                    parts.append(cleaned)
            elif isinstance(value, dict):
                extracted = _extract_text_recursive(value)
                if extracted and len(extracted) > 50 and not _is_noise_text(extracted):
                    parts.append(extracted)

    # HTML 응답 폴백 (노이즈 검증 강화)
    if not parts and "html" in detail:
        html_text = _extract_text_from_html_dict(detail["html"])
        if html_text and not _is_noise_text(html_text):
            parts.append(html_text)

    result = "\n\n".join(parts)

    # 최종 노이즈 검증
    if _is_noise_text(result):
        return ""

    return result


def _extract_text_recursive(obj: object) -> str:
    """dict/list 구조에서 텍스트를 재귀적으로 추출"""
    texts: list[str] = []

    if isinstance(obj, str):
        cleaned = _clean_html(obj)
        if cleaned and len(cleaned) > 10 and not _is_noise_text(cleaned):
            texts.append(cleaned)
    elif isinstance(obj, dict):
        # #text 키는 XML 텍스트 노드
        if "#text" in obj:
            val = obj["#text"]
            if isinstance(val, str):
                cleaned = _clean_html(val)
                if cleaned and not _is_noise_text(cleaned):
                    texts.append(cleaned)
        for v in obj.values():
            texts.append(_extract_text_recursive(v))
    elif isinstance(obj, list):
        for item in obj:
            texts.append(_extract_text_recursive(item))

    return " ".join(t for t in texts if t.strip())


def _extract_text_from_html_dict(html_dict: dict) -> str:
    """
    HTML dict 구조에서 텍스트 콘텐츠 추출 (Red Team #4 개선)

    노이즈 필터링을 강화하여 CSS/JS 경로가 저장되지 않도록 합니다.
    """
    texts: list[str] = []

    def _walk(obj: object) -> None:
        if isinstance(obj, str):
            cleaned = _clean_html(obj)
            # 최소 길이 + 노이즈 패턴 검증
            if cleaned and len(cleaned) > 30 and not _is_noise_text(cleaned):
                texts.append(cleaned)
        elif isinstance(obj, dict):
            if "#text" in obj:
                val = obj["#text"]
                if isinstance(val, str):
                    cleaned = _clean_html(val)
                    if cleaned and len(cleaned) > 30 and not _is_noise_text(cleaned):
                        texts.append(cleaned)
            for v in obj.values():
                _walk(v)
        elif isinstance(obj, list):
            for item in obj:
                _walk(item)

    _walk(html_dict)
    return "\n".join(texts)


def ingest_laws(query: str, max_items: int = 100) -> int:
    """
    법령 검색 → 상세 조회 → 품질 검증 → 청킹 → 벡터 스토어 저장

    Args:
        query: 검색 키워드
        max_items: 최대 적재 법령 수

    Returns:
        저장된 청크 수
    """
    store = get_or_create_collection(COLLECTION_LAWS)
    total_chunks = 0
    failed_items: list[dict] = []

    try:
        result = search_laws(query, display=min(max_items, 100))
        laws = result.get("LawSearch", {}).get("law", [])
        if not isinstance(laws, list):
            laws = [laws] if laws else []
    except Exception as e:
        logger.error(f"법령 검색 실패: {e}")
        return 0

    for law in laws[:max_items]:
        law_id = law.get("법령일련번호", "")
        law_name = law.get("법령명한글", "")
        if not law_id:
            continue

        try:
            detail = get_law_detail(law_id)
            law_content = _extract_law_text(detail)
            if not law_content:
                continue

            # Red Team #6: 데이터 품질 검증
            if not validate_legal_document(law_content, "law"):
                logger.warning(f"법령 품질 검증 실패 (스킵): {law_name}")
                failed_items.append({"id": law_id, "name": law_name, "reason": "validation_failed"})
                continue

            metadata = {
                "source_type": "law",
                "source_id": f"law_{law_id}",
                "law_id": str(law_id),
                "law_name": str(law_name),
                "proclamation_date": str(law.get("공포일자", "")),
                "enforcement_date": str(law.get("시행일자", "")),
                "source_url": f"https://www.law.go.kr/법령/{law_name}",
            }

            chunks = chunk_law_text(law_content, metadata)
            if chunks:
                store.upsert(
                    ids=[c["id"] for c in chunks],
                    documents=[c["text"] for c in chunks],
                    metadatas=[c["metadata"] for c in chunks],
                )
                total_chunks += len(chunks)

                # SQLite DB 동시 적재
                if _db:
                    try:
                        db_law_id = _db.upsert_law(
                            law_id=str(law_id),
                            law_name=str(law_name),
                            raw_content=law_content,
                            proclamation_date=metadata.get("proclamation_date"),
                            enforcement_date=metadata.get("enforcement_date"),
                            source_url=metadata.get("source_url"),
                        )
                        for chunk in chunks:
                            _db.upsert_chunk(
                                chunk_hash=chunk["id"],
                                source_type="law",
                                source_id=db_law_id,
                                chunk_index=chunk["metadata"].get("chunk_index", 0),
                                content=chunk["text"],
                                metadata=chunk["metadata"],
                            )
                    except Exception as db_err:
                        logger.warning(f"법령 DB 적재 실패 ({law_name}): {db_err}")

                logger.info(f"법령 적재: {law_name} ({len(chunks)}청크)")

        except Exception as e:
            logger.error(f"법령 상세 조회 실패 ({law_name}): {e}")
            failed_items.append({"id": law_id, "name": law_name, "reason": str(e)})
            continue

    if failed_items:
        logger.warning(f"법령 적재 실패 {len(failed_items)}건: {[f['name'] for f in failed_items]}")

    return total_chunks


def ingest_precedents(query: str, max_items: int = 50) -> int:
    """
    판례 검색 → 상세 조회 → 품질 검증 → 청킹 → 벡터 스토어 저장

    Red Team #1, #4, #6, #7 개선 반영

    Args:
        query: 검색 키워드
        max_items: 최대 적재 판례 수

    Returns:
        저장된 청크 수
    """
    store = get_or_create_collection(COLLECTION_PRECEDENTS)
    total_chunks = 0
    failed_items: list[dict] = []
    skipped_noise = 0

    try:
        result = search_precedents(query, display=min(max_items, 100))
        precs = result.get("PrecSearch", {}).get("prec", [])
        if not isinstance(precs, list):
            precs = [precs] if precs else []
    except Exception as e:
        logger.error(f"판례 검색 실패: {e}")
        return 0

    for prec in precs[:max_items]:
        prec_seq = prec.get("판례일련번호", "")
        case_name = prec.get("사건명", "")
        if not prec_seq:
            continue

        try:
            detail = get_precedent_detail(prec_seq)
            prec_content = _extract_precedent_text(detail)

            # Red Team #1: 빈 내용 또는 노이즈만 추출된 경우 스킵
            if not prec_content:
                skipped_noise += 1
                logger.warning(f"판례 본문 추출 실패 (노이즈/빈 내용): {case_name} (seq={prec_seq})")
                failed_items.append({"seq": prec_seq, "name": case_name, "reason": "empty_or_noise"})
                continue

            # Red Team #6: 데이터 품질 검증
            if not validate_legal_document(prec_content, "precedent"):
                skipped_noise += 1
                logger.warning(f"판례 품질 검증 실패 (스킵): {case_name} (seq={prec_seq})")
                failed_items.append({"seq": prec_seq, "name": case_name, "reason": "validation_failed"})
                continue

            # Red Team #7: 메타데이터 보강
            prec_detail = detail.get("PrecService", {}) or detail.get("판례", {}) or {}
            metadata = {
                "source_type": "precedent",
                "source_id": f"prec_{prec_seq}",
                "precedent_seq": str(prec_seq),
                "case_name": str(case_name),
                "court_name": str(prec.get("법원명", "")),
                "judgment_date": str(prec.get("선고일자", "")),
                "case_number": str(prec.get("사건번호", prec_detail.get("사건번호", ""))),
                "case_type": str(prec.get("사건종류명", prec_detail.get("사건종류명", ""))),
                "source_url": f"https://www.law.go.kr/판례/{case_name}",
            }

            # 판례용 청킹 (Red Team #10)
            chunks = chunk_precedent_text(prec_content, metadata)
            if chunks:
                store.upsert(
                    ids=[c["id"] for c in chunks],
                    documents=[c["text"] for c in chunks],
                    metadatas=[c["metadata"] for c in chunks],
                )
                total_chunks += len(chunks)

                # SQLite DB 동시 적재
                if _db:
                    try:
                        db_prec_id = _db.upsert_precedent(
                            precedent_seq=str(prec_seq),
                            case_name=str(case_name),
                            raw_content=prec_content,
                            court_name=metadata.get("court_name"),
                            judgment_date=metadata.get("judgment_date"),
                            case_number=metadata.get("case_number"),
                            case_type=metadata.get("case_type"),
                            source_url=metadata.get("source_url"),
                        )
                        for chunk in chunks:
                            _db.upsert_chunk(
                                chunk_hash=chunk["id"],
                                source_type="precedent",
                                source_id=db_prec_id,
                                chunk_index=chunk["metadata"].get("chunk_index", 0),
                                content=chunk["text"],
                                metadata=chunk["metadata"],
                            )
                    except Exception as db_err:
                        logger.warning(f"판례 DB 적재 실패 ({case_name}): {db_err}")

                logger.info(f"판례 적재: {case_name} ({len(chunks)}청크)")

        except Exception as e:
            logger.error(f"판례 상세 조회 실패 ({case_name}): {e}")
            failed_items.append({"seq": prec_seq, "name": case_name, "reason": str(e)})
            continue

    if skipped_noise > 0:
        logger.warning(f"판례 노이즈/품질 실패로 {skipped_noise}건 스킵")
    if failed_items:
        logger.warning(f"판례 적재 실패 총 {len(failed_items)}건")

    return total_chunks


def ingest_store_policies(
    policies: list[dict],
    force_refresh: bool = False,
) -> int:
    """
    스토어 정책 데이터 적재

    외부 API가 없으므로 구조화된 정책 데이터를 직접 받아 청킹 후 저장합니다.

    Args:
        policies: 정책 데이터 리스트
            [{"text": str, "metadata": {"store": str, "section": str, ...}}, ...]
        force_refresh: True면 기존 컬렉션 삭제 후 재적재

    Returns:
        저장된 청크 수
    """
    store = get_or_create_collection(COLLECTION_POLICIES)

    if force_refresh:
        store.clear()
        print("[LegalRAG] store_policies 컬렉션 초기화")

    total_chunks = 0

    for idx, policy in enumerate(policies):
        text = policy.get("text", "")
        metadata = policy.get("metadata", {})
        if not text:
            continue

        metadata.setdefault("source_type", "store_policy")
        source_id = metadata.get(
            "source_id",
            f"{metadata.get('store', 'unknown')}"
            f"_{metadata.get('section', 'unknown')}"
            f"_{metadata.get('subsection', str(idx))}",
        )
        metadata["source_id"] = source_id

        chunks = chunk_law_text(text, metadata)
        if chunks:
            store.upsert(
                ids=[c["id"] for c in chunks],
                documents=[c["text"] for c in chunks],
                metadatas=[c["metadata"] for c in chunks],
            )
            total_chunks += len(chunks)
            section = metadata.get("section", "?")
            store_name = metadata.get("store", "?")

            # SQLite DB 동시 적재
            if _db:
                try:
                    db_policy_id = _db.upsert_store_policy(
                        store=metadata.get("store", "unknown"),
                        section=metadata.get("section", ""),
                        subsection=metadata.get("subsection", ""),
                        content=text,
                        policy_name=metadata.get("policy_name", ""),
                        effective_date=metadata.get("effective_date"),
                    )
                    for chunk in chunks:
                        _db.upsert_chunk(
                            chunk_hash=chunk["id"],
                            source_type="store_policy",
                            source_id=db_policy_id,
                            chunk_index=chunk["metadata"].get("chunk_index", 0),
                            content=chunk["text"],
                            metadata=chunk["metadata"],
                        )
                except Exception as db_err:
                    logger.warning(f"스토어 정책 DB 적재 실패 ([{store_name}] {section}): {db_err}")

            logger.info(f"스토어 정책 적재: [{store_name}] {section} ({len(chunks)}청크)")

    return total_chunks


# ─────────────────────────────────────────────────────────────
# Step 4: 유사도 검색 (API명세서 3.2 준수)
# ─────────────────────────────────────────────────────────────

def search_legal_context(
    query: str,
    top_k: int = 5,
    score_threshold: float = 0.7,
    user_id: Optional[str] = None,
    project_id: Optional[str] = None,
) -> list[dict]:
    """
    쿼리와 유사한 법령·판례·정책 청크 반환

    Args:
        query: 검색문
        top_k: 상위 결과 개수
        score_threshold: 유사도 하한 (미달 결과 제외 — 카더라 방지)
        user_id: (선택) 검색 로그에 기록할 사용자 ID
        project_id: (선택) 검색 로그에 기록할 프로젝트 ID

    Returns:
        [{"text": str, "metadata": dict, "score": float}, ...]
    """
    import time as _time
    _start = _time.perf_counter()

    results: list[dict] = []

    for col_name in ALL_COLLECTIONS:
        try:
            store = get_or_create_collection(col_name)
            if store.count() == 0:
                continue

            hits = store.query(query_text=query, n_results=top_k)

            for hit in hits:
                # 임계치 미달 결과 제외 (개발명세서 4.3 제약)
                if hit["score"] >= score_threshold:
                    results.append(hit)

        except Exception as e:
            logger.error(f"{col_name} 검색 오류: {e}")
            continue

    # 유사도 내림차순 정렬 → top_k 제한
    results.sort(key=lambda x: x["score"], reverse=True)
    results = results[:top_k]

    # 검색 로그를 DB에 기록
    duration_ms = int((_time.perf_counter() - _start) * 1000)
    if _db:
        try:
            _db.log_search(
                query_text=query,
                result_count=len(results),
                user_id=user_id,
                project_id=project_id,
                top_score=results[0]["score"] if results else None,
                duration_ms=duration_ms,
            )
        except Exception as db_err:
            logger.warning(f"검색 로그 DB 기록 실패: {db_err}")

    return results


# ─────────────────────────────────────────────────────────────
# Step 5: 데이터 동기화 (F-6)
# ─────────────────────────────────────────────────────────────

def _save_sync_metadata(summary: dict, queries: list[str]) -> None:
    """
    동기화 메타데이터를 database/metadata.json에 저장 (Red Team #8)
    """
    metadata_path = os.path.join(DATABASE_PATH, "metadata.json")
    existing: dict = {}
    if os.path.exists(metadata_path):
        try:
            with open(metadata_path, "r", encoding="utf-8") as f:
                existing = json.load(f)
        except (json.JSONDecodeError, OSError):
            existing = {}

    # 버전 자동 증가
    version = existing.get("version", "1.0.0")
    parts = version.split(".")
    try:
        parts[-1] = str(int(parts[-1]) + 1)
        new_version = ".".join(parts)
    except ValueError:
        new_version = "1.0.1"

    # 컬렉션 현재 상태
    collections_status = {}
    for name in ALL_COLLECTIONS:
        try:
            store = get_or_create_collection(name)
            collections_status[name] = store.count()
        except Exception:
            collections_status[name] = 0

    metadata = {
        "last_sync": datetime.now(timezone.utc).isoformat(),
        "version": new_version,
        "sync_queries": queries,
        "sync_result": summary,
        "collections": collections_status,
        "sync_history": existing.get("sync_history", []) + [
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "queries": queries,
                "result": summary,
            }
        ],
    }

    os.makedirs(DATABASE_PATH, exist_ok=True)
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    logger.info(f"동기화 메타데이터 저장: version={new_version}, path={metadata_path}")


def sync_legal_data(
    queries: list[str],
    force_refresh: bool = False,
) -> dict:
    """
    Vector DB 데이터 동기화 (Red Team #8: 버전 관리 추가)

    Args:
        queries: 동기화할 검색 키워드 목록
        force_refresh: True면 기존 컬렉션 삭제 후 재적재

    Returns:
        {"laws_added": int, "precedents_added": int, "total_chunks": int}
    """
    # DB sync_logs 기록 시작
    sync_id = None
    if _db:
        try:
            sync_id = _db.start_sync(sync_type="full", queries=queries)
        except Exception as db_err:
            logger.warning(f"sync_logs 시작 기록 실패: {db_err}")

    if force_refresh:
        for name in [COLLECTION_LAWS, COLLECTION_PRECEDENTS]:
            store = get_or_create_collection(name)
            store.clear()
            logger.info(f"컬렉션 초기화: {name}")

    laws_total = 0
    precs_total = 0
    sync_error = None

    try:
        for q in queries:
            logger.info(f"동기화 쿼리: '{q}'")
            laws_total += ingest_laws(q, max_items=50)
            precs_total += ingest_precedents(q, max_items=30)
    except Exception as e:
        sync_error = str(e)
        logger.error(f"동기화 중 오류: {e}")

    summary = {
        "laws_added": laws_total,
        "precedents_added": precs_total,
        "total_chunks": laws_total + precs_total,
    }

    # JSON 메타데이터 저장 (호환성 유지)
    _save_sync_metadata(summary, queries)

    # DB sync_logs 완료 기록
    if _db and sync_id:
        try:
            _db.complete_sync(
                sync_id=sync_id,
                items_added=laws_total + precs_total,
                chunks_created=laws_total + precs_total,
                error_message=sync_error,
            )
        except Exception as db_err:
            logger.warning(f"sync_logs 완료 기록 실패: {db_err}")

    logger.info(f"동기화 완료: {summary}")
    return summary


# ─────────────────────────────────────────────────────────────
# 테스트 실행
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("SafeLaunch AI — Vector DB (legal_rag.py) 테스트")
    print("=" * 60)

    # 1. 법령 적재 테스트
    print("\n[1] 법령 적재: '저작권'")
    law_count = ingest_laws("저작권", max_items=5)
    print(f"    저장된 청크: {law_count}")

    # 2. 판례 적재 테스트
    print("\n[2] 판례 적재: '저작권 침해'")
    prec_count = ingest_precedents("저작권 침해", max_items=3)
    print(f"    저장된 청크: {prec_count}")

    # 3. 검색 테스트
    print("\n[3] 검색: '앱 저작권 침해 기준'")
    results = search_legal_context("앱 저작권 침해 기준", top_k=3, score_threshold=0.1)
    if results:
        for r in results:
            print(f"    [{r['score']:.3f}] {r['metadata'].get('source_type', '?')}"
                  f" | {r['text'][:80]}...")
    else:
        print("    결과 없음 (임계치 미달 또는 데이터 부족)")

    # 4. 컬렉션 상태
    print("\n[4] 컬렉션 상태:")
    for name in ALL_COLLECTIONS:
        store = get_or_create_collection(name)
        print(f"    {name}: {store.count()}건")

    print("\n" + "=" * 60)
    print("테스트 완료")
    print("=" * 60)
