"""
LangChain 기반 벡터 검색 모듈 - 법령·판례·스토어 정책 RAG
core/langchain_rag.py

SafeLaunch AI 프로젝트용
- OpenAI Embedding + FAISS 기반 벡터 스토어
- LangChain Document 구조 활용
- 데이터 품질 검증 + 법률 특화 청킹 + Hybrid Search

개선 이력:
- v2.0: 데이터 품질 검증, 법률 특화 청킹, Hybrid Search, Query Expansion, 캐싱 추가
"""

import json
import os
import re
import hashlib
import logging
import time
from typing import Optional
from functools import lru_cache
from dotenv import load_dotenv

from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

# 환경 변수 로드
load_dotenv()

# ─────────────────────────────────────────────────────────────
# 로깅 설정
# ─────────────────────────────────────────────────────────────

logger = logging.getLogger("langchain_rag")
if not logger.handlers:
    _handler = logging.StreamHandler()
    _handler.setFormatter(logging.Formatter("[%(name)s] %(levelname)s: %(message)s"))
    logger.addHandler(_handler)
    logger.setLevel(logging.INFO)


# ─────────────────────────────────────────────────────────────
# 상수
# ─────────────────────────────────────────────────────────────

FAISS_INDEX_PATH = "./faiss_index"
JSON_DATABASE_PATH = "./database"

COLLECTION_LAWS = "laws"
COLLECTION_PRECEDENTS = "precedents"
COLLECTION_POLICIES = "store_policies"

ALL_COLLECTIONS = [COLLECTION_LAWS, COLLECTION_PRECEDENTS, COLLECTION_POLICIES]

# OpenAI Embedding 모델
EMBEDDING_MODEL = "text-embedding-3-small"

# 캐시 설정
CACHE_TTL = 300  # 5분
_search_cache: dict = {}

# 출처별 신뢰도 가중치
SOURCE_WEIGHTS = {
    "law": 1.0,           # 법령 - 최우선
    "precedent": 0.9,     # 판례 - 높음
    "store_policy": 0.8,  # 스토어 정책 - 참고
}


# ─────────────────────────────────────────────────────────────
# [개선 #1] 데이터 품질 검증
# ─────────────────────────────────────────────────────────────

# 노이즈 감지용 패턴
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
LEGAL_KEYWORDS = {
    "law": ["제", "조", "항", "호", "법", "규정", "시행"],
    "precedent": [
        "판시사항", "판결요지", "판례", "원고", "피고", "법원", "선고",
        "판결", "사건", "청구", "항소", "상고", "위반", "침해",
    ],
    "store_policy": ["앱", "정책", "가이드", "심사", "콘텐츠", "데이터", "사용자"],
}


def is_noise_text(text: str) -> bool:
    """CSS/JS/HTML 노이즈 텍스트인지 판별"""
    if not text or len(text.strip()) < 10:
        return True

    # 노이즈 패턴 매칭 횟수가 과다하면 노이즈
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
    법률 문서 유효성 검증

    Args:
        text: 정제된 문서 텍스트
        source_type: "law" | "precedent" | "store_policy"

    Returns:
        True면 유효한 법률 문서
    """
    if not text or not text.strip():
        return False

    # 1. 노이즈 패턴 탐지
    if is_noise_text(text):
        return False

    # 2. 소스 타입별 최소 길이 검증
    min_lengths = {"law": 100, "precedent": 80, "store_policy": 50}
    min_len = min_lengths.get(source_type, 50)
    if len(text.strip()) < min_len:
        return False

    # 3. 소스 타입별 법률 키워드 포함 여부
    keywords = LEGAL_KEYWORDS.get(source_type, LEGAL_KEYWORDS["law"])
    keyword_hits = sum(1 for kw in keywords if kw in text)
    if keyword_hits < 2:
        return False

    return True


# ─────────────────────────────────────────────────────────────
# [개선 #4] Query Expansion - 동의어 사전
# ─────────────────────────────────────────────────────────────

LEGAL_SYNONYMS = {
    "인앱결제": ["앱 내 구매", "인앱 구매", "IAP"],
    "인앱 결제": ["앱 내 구매", "인앱 구매", "IAP"],
    "개인정보": ["개인 정보", "사용자 데이터", "프라이버시"],
    "저작권": ["저작물", "지적재산권", "IP", "copyright"],
    "어린이": ["아동", "미성년자", "키즈", "kids"],
    "아동": ["어린이", "미성년자", "키즈"],
    "구독": ["자동 갱신", "정기 결제", "subscription"],
    "환불": ["취소", "반품", "refund"],
    "광고": ["애드", "ad", "advertisement"],
    "결제": ["구매", "purchase", "payment"],
}


def expand_query(query: str) -> str:
    """쿼리 확장 - 동의어 추가"""
    expanded_terms = [query]

    for term, synonyms in LEGAL_SYNONYMS.items():
        if term in query:
            # 상위 2개 동의어만 추가
            expanded_terms.extend(synonyms[:2])

    return " ".join(expanded_terms)


# ─────────────────────────────────────────────────────────────
# 임베딩 설정
# ─────────────────────────────────────────────────────────────

def get_embeddings() -> OpenAIEmbeddings:
    """OpenAI 임베딩 객체 반환"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY 환경 변수가 설정되지 않았습니다. .env 파일을 확인하세요.")

    return OpenAIEmbeddings(
        model=EMBEDDING_MODEL,
        openai_api_key=api_key,
    )


# ─────────────────────────────────────────────────────────────
# FAISS 벡터 스토어 관리
# ─────────────────────────────────────────────────────────────

_vectorstores: dict[str, FAISS] = {}


def get_index_path(collection_name: str) -> str:
    """FAISS 인덱스 저장 경로 반환"""
    return os.path.join(FAISS_INDEX_PATH, collection_name)


def load_vectorstore(collection_name: str) -> Optional[FAISS]:
    """저장된 FAISS 인덱스 로드"""
    index_path = get_index_path(collection_name)

    if not os.path.exists(index_path):
        return None

    try:
        embeddings = get_embeddings()
        vectorstore = FAISS.load_local(
            index_path,
            embeddings,
            allow_dangerous_deserialization=True,
        )
        logger.debug(f"{collection_name} 인덱스 로드 완료")
        return vectorstore
    except Exception as e:
        logger.error(f"{collection_name} 인덱스 로드 실패: {e}")
        return None


def save_vectorstore(vectorstore: FAISS, collection_name: str) -> None:
    """FAISS 인덱스 저장"""
    index_path = get_index_path(collection_name)
    os.makedirs(index_path, exist_ok=True)
    vectorstore.save_local(index_path)
    logger.info(f"{collection_name} 인덱스 저장 완료")


def get_or_create_vectorstore(collection_name: str) -> Optional[FAISS]:
    """캐시된 벡터 스토어 반환 또는 로드"""
    if collection_name in _vectorstores:
        return _vectorstores[collection_name]

    vectorstore = load_vectorstore(collection_name)
    if vectorstore:
        _vectorstores[collection_name] = vectorstore

    return vectorstore


# ─────────────────────────────────────────────────────────────
# [개선 #2] 법률 특화 텍스트 전처리 및 청킹
# ─────────────────────────────────────────────────────────────

def _clean_html(text: str) -> str:
    """HTML 태그 및 노이즈 제거 (강화)"""
    # 스크립트/스타일 블록 전체 제거
    text = re.sub(r"<script[^>]*>.*?</script>", "", text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<style[^>]*>.*?</style>", "", text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"&[a-zA-Z]+;", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def get_legal_text_splitter(doc_type: str = "law") -> RecursiveCharacterTextSplitter:
    """
    법률 문서 유형별 특화 스플리터

    Args:
        doc_type: "law" | "precedent" | "store_policy"
    """
    if doc_type == "law":
        # 법령: 조문 경계 우선 분할
        return RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=150,
            separators=[
                "\n제",       # 조문 경계 (제N조)
                "\n\n",
                "\n",
                ".",
                " ",
                "",
            ],
            length_function=len,
        )

    elif doc_type == "precedent":
        # 판례: 섹션 헤더 기반 분할, 더 큰 청크
        return RecursiveCharacterTextSplitter(
            chunk_size=1200,
            chunk_overlap=300,
            separators=[
                "[판시사항]",
                "[판결요지]",
                "[참조조문]",
                "[참조판례]",
                "[판례내용]",
                "[이유]",
                "[주문]",
                "\n\n",
                "\n",
                ".",
                " ",
                "",
            ],
            length_function=len,
        )

    else:  # store_policy
        return RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=150,
            separators=[
                "\n\n",
                "\n",
                ".",
                " ",
                "",
            ],
            length_function=len,
        )


def chunk_law_text_advanced(text: str, metadata: dict) -> list[Document]:
    """
    법령 텍스트 특화 청킹 - 조문 경계 우선
    """
    cleaned = _clean_html(text)
    if not cleaned:
        return []

    source_id = metadata.get("source_id", "unknown")

    # 조문 경계(제N조) 기준 분할 시도
    segments = re.split(r"(?=제\d+조[\s(])", cleaned)
    segments = [s.strip() for s in segments if s.strip()]

    if not segments:
        segments = [cleaned]

    documents = []
    text_splitter = get_legal_text_splitter("law")

    for segment in segments:
        if len(segment) > 800:
            # 긴 세그먼트는 추가 분할
            chunks = text_splitter.split_text(segment)
        else:
            chunks = [segment]

        for i, chunk in enumerate(chunks):
            chunk_metadata = {
                **metadata,
                "chunk_index": len(documents),
                "source_type": "law",
            }
            documents.append(Document(page_content=chunk, metadata=chunk_metadata))

    return documents


def chunk_precedent_text_advanced(text: str, metadata: dict) -> list[Document]:
    """
    판례 텍스트 특화 청킹 - 섹션 헤더 기반
    """
    cleaned = _clean_html(text)
    if not cleaned:
        return []

    # 판례 섹션 헤더 기반 분할
    section_pattern = r"(?=\[(판시사항|판결요지|참조조문|참조판례|판례내용|이유|주문|청구취지)\])"
    segments = re.split(section_pattern, cleaned)

    # 헤더와 내용 병합
    merged_segments = []
    i = 0
    while i < len(segments):
        seg = segments[i].strip()
        if seg in ("판시사항", "판결요지", "참조조문", "참조판례", "판례내용", "이유", "주문", "청구취지"):
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

    if not merged_segments:
        merged_segments = [cleaned]

    documents = []
    text_splitter = get_legal_text_splitter("precedent")

    for segment in merged_segments:
        if len(segment) > 1200:
            chunks = text_splitter.split_text(segment)
        else:
            chunks = [segment]

        for chunk in chunks:
            chunk_metadata = {
                **metadata,
                "chunk_index": len(documents),
                "source_type": "precedent",
            }
            documents.append(Document(page_content=chunk, metadata=chunk_metadata))

    return documents


def _generate_doc_id(source_id: str, chunk_index: int) -> str:
    """문서 고유 ID 생성"""
    raw = f"{source_id}_chunk_{chunk_index}"
    return hashlib.md5(raw.encode()).hexdigest()


# ─────────────────────────────────────────────────────────────
# JSON 데이터 로드 유틸리티
# ─────────────────────────────────────────────────────────────

def load_json_data(filename: str) -> dict:
    """database/ 폴더에서 JSON 데이터 로드"""
    filepath = os.path.join(JSON_DATABASE_PATH, filename)
    if not os.path.exists(filepath):
        return {}

    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


# ─────────────────────────────────────────────────────────────
# 데이터 적재 (Ingestion) - 품질 검증 포함
# ─────────────────────────────────────────────────────────────

def ingest_store_policies_langchain(force_refresh: bool = False) -> int:
    """스토어 정책 데이터를 FAISS에 적재 (품질 검증 포함)"""
    collection_name = COLLECTION_POLICIES

    if force_refresh:
        index_path = get_index_path(collection_name)
        if os.path.exists(index_path):
            import shutil
            shutil.rmtree(index_path)
        if collection_name in _vectorstores:
            del _vectorstores[collection_name]
        logger.info(f"{collection_name} 인덱스 초기화")

    policies_data = load_json_data("store_policies.json")
    if not policies_data:
        logger.warning("store_policies.json 데이터가 없습니다.")
        return 0

    documents = []
    skipped = 0
    text_splitter = get_legal_text_splitter("store_policy")

    for doc_id, doc_data in policies_data.items():
        text = doc_data.get("text", "")
        metadata = doc_data.get("metadata", {})

        if not text:
            continue

        cleaned_text = _clean_html(text)

        # [개선 #1] 품질 검증
        if is_noise_text(cleaned_text):
            skipped += 1
            continue

        if not validate_legal_document(cleaned_text, "store_policy"):
            skipped += 1
            continue

        chunks = text_splitter.split_text(cleaned_text)

        for i, chunk in enumerate(chunks):
            chunk_metadata = {
                **metadata,
                "chunk_index": i,
                "original_doc_id": doc_id,
                "source_type": "store_policy",
            }
            documents.append(Document(page_content=chunk, metadata=chunk_metadata))

    if documents:
        embeddings = get_embeddings()
        vectorstore = FAISS.from_documents(documents, embeddings)
        save_vectorstore(vectorstore, collection_name)
        _vectorstores[collection_name] = vectorstore
        logger.info(f"스토어 정책 적재 완료: {len(documents)}개 청크 (스킵: {skipped})")

    return len(documents)


def ingest_laws_langchain(force_refresh: bool = False) -> int:
    """법령 데이터를 FAISS에 적재 (품질 검증 + 특화 청킹)"""
    collection_name = COLLECTION_LAWS

    if force_refresh:
        index_path = get_index_path(collection_name)
        if os.path.exists(index_path):
            import shutil
            shutil.rmtree(index_path)
        if collection_name in _vectorstores:
            del _vectorstores[collection_name]
        logger.info(f"{collection_name} 인덱스 초기화")

    laws_data = load_json_data("laws.json")
    if not laws_data:
        logger.warning("laws.json 데이터가 없습니다.")
        return 0

    documents = []
    skipped = 0

    for doc_id, doc_data in laws_data.items():
        text = doc_data.get("text", "")
        metadata = doc_data.get("metadata", {})

        if not text:
            continue

        cleaned_text = _clean_html(text)

        # [개선 #1] 품질 검증
        if is_noise_text(cleaned_text):
            skipped += 1
            logger.debug(f"노이즈 텍스트 스킵: {doc_id}")
            continue

        if not validate_legal_document(cleaned_text, "law"):
            skipped += 1
            logger.debug(f"품질 검증 실패: {doc_id}")
            continue

        # [개선 #2] 법령 특화 청킹
        metadata["original_doc_id"] = doc_id
        docs = chunk_law_text_advanced(cleaned_text, metadata)
        documents.extend(docs)

    if documents:
        embeddings = get_embeddings()
        vectorstore = FAISS.from_documents(documents, embeddings)
        save_vectorstore(vectorstore, collection_name)
        _vectorstores[collection_name] = vectorstore
        logger.info(f"법령 적재 완료: {len(documents)}개 청크 (스킵: {skipped})")

    return len(documents)


def ingest_precedents_langchain(force_refresh: bool = False) -> int:
    """판례 데이터를 FAISS에 적재 (품질 검증 + 특화 청킹)"""
    collection_name = COLLECTION_PRECEDENTS

    if force_refresh:
        index_path = get_index_path(collection_name)
        if os.path.exists(index_path):
            import shutil
            shutil.rmtree(index_path)
        if collection_name in _vectorstores:
            del _vectorstores[collection_name]
        logger.info(f"{collection_name} 인덱스 초기화")

    precedents_data = load_json_data("precedents.json")
    if not precedents_data:
        logger.warning("precedents.json 데이터가 없습니다.")
        return 0

    documents = []
    skipped = 0

    for doc_id, doc_data in precedents_data.items():
        text = doc_data.get("text", "")
        metadata = doc_data.get("metadata", {})

        if not text:
            continue

        cleaned_text = _clean_html(text)

        # [개선 #1] 품질 검증
        if is_noise_text(cleaned_text):
            skipped += 1
            continue

        if not validate_legal_document(cleaned_text, "precedent"):
            skipped += 1
            continue

        # [개선 #2] 판례 특화 청킹
        metadata["original_doc_id"] = doc_id
        docs = chunk_precedent_text_advanced(cleaned_text, metadata)
        documents.extend(docs)

    if documents:
        embeddings = get_embeddings()
        vectorstore = FAISS.from_documents(documents, embeddings)
        save_vectorstore(vectorstore, collection_name)
        _vectorstores[collection_name] = vectorstore
        logger.info(f"판례 적재 완료: {len(documents)}개 청크 (스킵: {skipped})")

    return len(documents)


def ingest_all_data(force_refresh: bool = False) -> dict:
    """모든 데이터 적재"""
    start_time = time.perf_counter()

    laws_count = ingest_laws_langchain(force_refresh)
    precedents_count = ingest_precedents_langchain(force_refresh)
    policies_count = ingest_store_policies_langchain(force_refresh)

    result = {
        "laws": laws_count,
        "precedents": precedents_count,
        "policies": policies_count,
        "total": laws_count + precedents_count + policies_count,
    }

    duration = time.perf_counter() - start_time
    logger.info(f"전체 적재 완료: {result} ({duration:.2f}초)")
    return result


# ─────────────────────────────────────────────────────────────
# [개선 #3] Hybrid Search + [개선 #5] 캐싱
# ─────────────────────────────────────────────────────────────

def _semantic_search(
    query: str,
    top_k: int = 5,
    collections: Optional[list[str]] = None,
) -> list[dict]:
    """FAISS 의미 기반 검색 (내부용)"""
    if collections is None:
        collections = ALL_COLLECTIONS

    results = []

    for col_name in collections:
        try:
            vectorstore = get_or_create_vectorstore(col_name)
            if vectorstore is None:
                continue

            docs_with_scores = vectorstore.similarity_search_with_score(
                query,
                k=top_k,
            )

            for doc, distance in docs_with_scores:
                # L2 distance -> 유사도 변환
                score = 1 / (1 + distance)
                results.append({
                    "text": doc.page_content,
                    "metadata": doc.metadata,
                    "score": round(score, 4),
                    "search_type": "semantic",
                })

        except Exception as e:
            logger.error(f"{col_name} 의미 검색 오류: {e}")
            continue

    return results


def _keyword_search(query: str, top_k: int = 5) -> list[dict]:
    """FTS5 키워드 검색 (SQLite DB 활용)"""
    try:
        from core.database import db

        # FTS5 검색
        fts_results = db.search_fts(query, limit=top_k)

        results = []
        for row in fts_results:
            results.append({
                "text": row.get("content", ""),
                "metadata": row.get("metadata", {}),
                "score": row.get("rank", 0.5),
                "search_type": "keyword",
            })
        return results

    except Exception as e:
        logger.debug(f"키워드 검색 실패 (DB 미사용): {e}")
        return []


def search_legal_context(
    query: str,
    top_k: int = 5,
    score_threshold: float = 0.3,
    collections: Optional[list[str]] = None,
    use_hybrid: bool = True,
    use_query_expansion: bool = True,
    use_cache: bool = True,
) -> list[dict]:
    """
    쿼리와 유사한 법령·판례·정책 청크 반환 (개선된 버전)

    Args:
        query: 검색문
        top_k: 상위 결과 개수
        score_threshold: 유사도 하한
        collections: 검색할 컬렉션 목록 (None이면 전체)
        use_hybrid: Hybrid Search 사용 여부
        use_query_expansion: Query Expansion 사용 여부
        use_cache: 캐시 사용 여부

    Returns:
        [{"text": str, "metadata": dict, "score": float}, ...]
    """
    start_time = time.perf_counter()

    # [개선 #5] 캐싱
    if use_cache:
        cache_key = hashlib.md5(f"{query}:{top_k}:{collections}".encode()).hexdigest()
        if cache_key in _search_cache:
            cached_time, cached_result = _search_cache[cache_key]
            if time.time() - cached_time < CACHE_TTL:
                logger.debug(f"캐시 히트: {query[:30]}...")
                return cached_result

    # [개선 #4] Query Expansion
    search_query = query
    if use_query_expansion:
        search_query = expand_query(query)
        if search_query != query:
            logger.debug(f"쿼리 확장: {query} -> {search_query[:50]}...")

    results = []

    # [개선 #3] Hybrid Search
    if use_hybrid:
        # 1. 의미 검색 (70% 가중치)
        semantic_results = _semantic_search(search_query, top_k=top_k * 2, collections=collections)

        # 2. 키워드 검색 (30% 가중치)
        keyword_results = _keyword_search(query, top_k=top_k)

        # 3. RRF (Reciprocal Rank Fusion) 점수 결합
        combined_scores: dict = {}
        result_data: dict = {}

        for rank, result in enumerate(semantic_results):
            doc_key = hashlib.md5(result["text"][:100].encode()).hexdigest()
            rrf_score = 0.7 / (60 + rank)  # 의미 검색 70% 가중치
            combined_scores[doc_key] = combined_scores.get(doc_key, 0) + rrf_score
            result_data[doc_key] = result

        for rank, result in enumerate(keyword_results):
            doc_key = hashlib.md5(result["text"][:100].encode()).hexdigest()
            rrf_score = 0.3 / (60 + rank)  # 키워드 검색 30% 가중치
            combined_scores[doc_key] = combined_scores.get(doc_key, 0) + rrf_score
            if doc_key not in result_data:
                result_data[doc_key] = result

        # 정렬 및 결과 구성
        sorted_keys = sorted(combined_scores.keys(), key=lambda k: combined_scores[k], reverse=True)
        for key in sorted_keys[:top_k * 2]:
            result = result_data[key]
            result["hybrid_score"] = round(combined_scores[key], 4)
            results.append(result)
    else:
        # Hybrid 미사용 시 의미 검색만
        results = _semantic_search(search_query, top_k=top_k * 2, collections=collections)

    # 출처별 가중치 적용
    for result in results:
        source_type = result["metadata"].get("source_type", "unknown")
        weight = SOURCE_WEIGHTS.get(source_type, 0.5)
        base_score = result.get("hybrid_score", result.get("score", 0))
        result["weighted_score"] = round(base_score * weight, 4)

    # 최종 정렬 및 필터링
    results.sort(key=lambda x: x.get("weighted_score", x.get("score", 0)), reverse=True)
    results = [r for r in results if r.get("score", 0) >= score_threshold][:top_k]

    # 로깅
    duration_ms = int((time.perf_counter() - start_time) * 1000)
    logger.info(f"검색 완료: query='{query[:30]}...', results={len(results)}, duration={duration_ms}ms")

    # 캐시 저장
    if use_cache:
        _search_cache[cache_key] = (time.time(), results)

    return results


def search_by_collection(
    query: str,
    collection_name: str,
    top_k: int = 5,
    score_threshold: float = 0.3,
) -> list[dict]:
    """특정 컬렉션에서만 검색"""
    return search_legal_context(
        query=query,
        top_k=top_k,
        score_threshold=score_threshold,
        collections=[collection_name],
    )


def search_store_policies(
    query: str,
    top_k: int = 5,
    store_filter: Optional[str] = None,
) -> list[dict]:
    """스토어 정책 검색 (Apple/Google 필터 지원)"""
    results = search_by_collection(
        query=query,
        collection_name=COLLECTION_POLICIES,
        top_k=top_k * 2 if store_filter else top_k,
        score_threshold=0.2,
    )

    if store_filter:
        store_filter = store_filter.lower()
        results = [
            r for r in results
            if r["metadata"].get("store", "").lower() == store_filter
        ]

    return results[:top_k]


# ─────────────────────────────────────────────────────────────
# 컬렉션 상태 확인
# ─────────────────────────────────────────────────────────────

def get_collection_stats() -> dict:
    """각 컬렉션의 문서 수 반환"""
    stats = {}

    for col_name in ALL_COLLECTIONS:
        try:
            vectorstore = get_or_create_vectorstore(col_name)
            if vectorstore:
                count = vectorstore.index.ntotal
                stats[col_name] = count
            else:
                stats[col_name] = 0
        except Exception as e:
            stats[col_name] = 0
            logger.error(f"{col_name} 상태 확인 오류: {e}")

    return stats


def clear_cache() -> None:
    """검색 캐시 초기화"""
    global _search_cache
    _search_cache = {}
    logger.info("검색 캐시 초기화 완료")


# ─────────────────────────────────────────────────────────────
# 테스트 실행
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("SafeLaunch AI - LangChain RAG v2.0 테스트")
    print("=" * 60)

    # 1. 컬렉션 상태 확인
    print("\n[1] 컬렉션 상태:")
    stats = get_collection_stats()
    for name, count in stats.items():
        print(f"    {name}: {count}건")

    # 2. 데이터가 없으면 적재
    if all(count == 0 for count in stats.values()):
        print("\n[2] 데이터 적재 시작...")
        ingest_all_data(force_refresh=True)

    # 3. 검색 테스트
    print("\n[3] 검색 테스트 (Hybrid Search + Query Expansion):")

    test_queries = [
        "앱 내 결제 인앱 구매 정책",
        "개인정보 수집 동의",
        "저작권 침해 기준",
        "어린이 앱 보호 정책",
    ]

    for query in test_queries:
        print(f"\n  Q: {query}")
        results = search_legal_context(query, top_k=3, score_threshold=0.2)

        if results:
            for r in results:
                source_type = r["metadata"].get("source_type", "?")
                store = r["metadata"].get("store", "")
                section = r["metadata"].get("section", "")
                score = r.get("weighted_score", r.get("score", 0))
                print(f"    [{score:.3f}] [{source_type}] {store} {section}")
                print(f"      {r['text'][:80]}...")
        else:
            print("    결과 없음")

    # 4. 캐시 테스트
    print("\n[4] 캐시 테스트:")
    start = time.perf_counter()
    search_legal_context("인앱 구매", top_k=3)
    first_time = time.perf_counter() - start

    start = time.perf_counter()
    search_legal_context("인앱 구매", top_k=3)
    second_time = time.perf_counter() - start

    print(f"    첫 번째 검색: {first_time*1000:.1f}ms")
    print(f"    두 번째 검색 (캐시): {second_time*1000:.1f}ms")

    print("\n" + "=" * 60)
    print("테스트 완료")
    print("=" * 60)
