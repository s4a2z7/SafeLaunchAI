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
import numpy as np
from typing import Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from core.law_api import (
    search_laws,
    search_precedents,
    get_law_detail,
    get_precedent_detail,
)


# ─────────────────────────────────────────────────────────────
# 상수
# ─────────────────────────────────────────────────────────────

DATABASE_PATH = "./database"

COLLECTION_LAWS = "laws"
COLLECTION_PRECEDENTS = "precedents"
COLLECTION_POLICIES = "store_policies"

ALL_COLLECTIONS = [COLLECTION_LAWS, COLLECTION_PRECEDENTS, COLLECTION_POLICIES]


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
        TF-IDF 코사인 유사도 기반 검색

        Returns:
            [{"text": str, "metadata": dict, "score": float}, ...]
            score가 높을수록 유사 (0~1)
        """
        if not self._docs:
            return []

        doc_ids = list(self._docs.keys())
        doc_texts = [self._docs[d]["text"] for d in doc_ids]

        # TF-IDF 벡터라이저 (한글 1~3글자 단위 + 공백 토큰)
        vectorizer = TfidfVectorizer(
            analyzer="char_wb",
            ngram_range=(1, 3),
            max_features=10000,
        )

        try:
            tfidf_matrix = vectorizer.fit_transform(doc_texts)
            query_vec = vectorizer.transform([query_text])
        except ValueError:
            # 문서가 비어있거나 벡터화 실패
            return []

        similarities = cosine_similarity(query_vec, tfidf_matrix).flatten()

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

def _clean_html(text: str) -> str:
    """HTML 태그 및 노이즈 제거"""
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
    """판례 상세 응답에서 본문 텍스트 추출"""
    # 구조화된 XML 응답 시도
    prec = detail.get("판례", {})
    if not prec:
        prec = detail.get("PrecService", {})

    parts: list[str] = []
    field_keys = ["판시사항", "판결요지", "참조조문", "참조판례", "판례내용"]

    for key in field_keys:
        value = prec.get(key, "")
        if value and isinstance(value, str):
            parts.append(f"[{key}]\n{value}")

    # 필드 매칭 실패 시 긴 문자열 수집
    if not parts:
        for value in prec.values():
            if isinstance(value, str) and len(value) > 50:
                parts.append(value)

    # HTML 응답인 경우 (API가 HTML로 반환할 때)
    if not parts and "html" in detail:
        html_text = _extract_text_from_html_dict(detail["html"])
        if html_text:
            parts.append(html_text)

    return "\n\n".join(parts)


def _extract_text_from_html_dict(html_dict: dict) -> str:
    """HTML dict 구조에서 텍스트 콘텐츠 추출"""
    texts: list[str] = []

    def _walk(obj: object) -> None:
        if isinstance(obj, str):
            cleaned = _clean_html(obj)
            if cleaned and len(cleaned) > 30:
                texts.append(cleaned)
        elif isinstance(obj, dict):
            # #text 키는 직접 텍스트 노드
            if "#text" in obj:
                val = obj["#text"]
                if isinstance(val, str):
                    cleaned = _clean_html(val)
                    if cleaned and len(cleaned) > 30:
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
    법령 검색 → 상세 조회 → 청킹 → 벡터 스토어 저장

    Args:
        query: 검색 키워드
        max_items: 최대 적재 법령 수

    Returns:
        저장된 청크 수
    """
    store = get_or_create_collection(COLLECTION_LAWS)
    total_chunks = 0

    try:
        result = search_laws(query, display=min(max_items, 100))
        laws = result.get("LawSearch", {}).get("law", [])
        if not isinstance(laws, list):
            laws = [laws] if laws else []
    except Exception as e:
        print(f"[LegalRAG] 법령 검색 실패: {e}")
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

            metadata = {
                "source_type": "law",
                "source_id": f"law_{law_id}",
                "law_id": str(law_id),
                "law_name": str(law_name),
                "proclamation_date": str(law.get("공포일자", "")),
                "enforcement_date": str(law.get("시행일자", "")),
            }

            chunks = chunk_law_text(law_content, metadata)
            if chunks:
                store.upsert(
                    ids=[c["id"] for c in chunks],
                    documents=[c["text"] for c in chunks],
                    metadatas=[c["metadata"] for c in chunks],
                )
                total_chunks += len(chunks)
                print(f"[LegalRAG] 법령 적재: {law_name} ({len(chunks)}청크)")

        except Exception as e:
            print(f"[LegalRAG] 법령 상세 조회 실패 ({law_name}): {e}")
            continue

    return total_chunks


def ingest_precedents(query: str, max_items: int = 50) -> int:
    """
    판례 검색 → 상세 조회 → 청킹 → 벡터 스토어 저장

    Args:
        query: 검색 키워드
        max_items: 최대 적재 판례 수

    Returns:
        저장된 청크 수
    """
    store = get_or_create_collection(COLLECTION_PRECEDENTS)
    total_chunks = 0

    try:
        result = search_precedents(query, display=min(max_items, 100))
        precs = result.get("PrecSearch", {}).get("prec", [])
        if not isinstance(precs, list):
            precs = [precs] if precs else []
    except Exception as e:
        print(f"[LegalRAG] 판례 검색 실패: {e}")
        return 0

    for prec in precs[:max_items]:
        prec_seq = prec.get("판례일련번호", "")
        case_name = prec.get("사건명", "")
        if not prec_seq:
            continue

        try:
            detail = get_precedent_detail(prec_seq)
            prec_content = _extract_precedent_text(detail)
            if not prec_content:
                continue

            metadata = {
                "source_type": "precedent",
                "source_id": f"prec_{prec_seq}",
                "precedent_seq": str(prec_seq),
                "case_name": str(case_name),
                "court_name": str(prec.get("법원명", "")),
                "judgment_date": str(prec.get("선고일자", "")),
            }

            chunks = chunk_law_text(prec_content, metadata)
            if chunks:
                store.upsert(
                    ids=[c["id"] for c in chunks],
                    documents=[c["text"] for c in chunks],
                    metadatas=[c["metadata"] for c in chunks],
                )
                total_chunks += len(chunks)
                print(f"[LegalRAG] 판례 적재: {case_name} ({len(chunks)}청크)")

        except Exception as e:
            print(f"[LegalRAG] 판례 상세 조회 실패 ({case_name}): {e}")
            continue

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
            print(
                f"[LegalRAG] 스토어 정책 적재: [{store_name}] {section}"
                f" ({len(chunks)}청크)"
            )

    return total_chunks


# ─────────────────────────────────────────────────────────────
# Step 4: 유사도 검색 (API명세서 3.2 준수)
# ─────────────────────────────────────────────────────────────

def search_legal_context(
    query: str,
    top_k: int = 5,
    score_threshold: float = 0.7,
) -> list[dict]:
    """
    쿼리와 유사한 법령·판례·정책 청크 반환

    Args:
        query: 검색문
        top_k: 상위 결과 개수
        score_threshold: 유사도 하한 (미달 결과 제외 — 카더라 방지)

    Returns:
        [{"text": str, "metadata": dict, "score": float}, ...]
    """
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
            print(f"[LegalRAG] {col_name} 검색 오류: {e}")
            continue

    # 유사도 내림차순 정렬 → top_k 제한
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:top_k]


# ─────────────────────────────────────────────────────────────
# Step 5: 데이터 동기화 (F-6)
# ─────────────────────────────────────────────────────────────

def sync_legal_data(
    queries: list[str],
    force_refresh: bool = False,
) -> dict:
    """
    Vector DB 데이터 동기화

    Args:
        queries: 동기화할 검색 키워드 목록
        force_refresh: True면 기존 컬렉션 삭제 후 재적재

    Returns:
        {"laws_added": int, "precedents_added": int, "total_chunks": int}
    """
    if force_refresh:
        for name in [COLLECTION_LAWS, COLLECTION_PRECEDENTS]:
            store = get_or_create_collection(name)
            store.clear()
            print(f"[LegalRAG] 컬렉션 초기화: {name}")

    laws_total = 0
    precs_total = 0

    for q in queries:
        print(f"\n[LegalRAG] 동기화 쿼리: '{q}'")
        laws_total += ingest_laws(q, max_items=50)
        precs_total += ingest_precedents(q, max_items=30)

    summary = {
        "laws_added": laws_total,
        "precedents_added": precs_total,
        "total_chunks": laws_total + precs_total,
    }
    print(f"\n[LegalRAG] 동기화 완료: {summary}")
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
