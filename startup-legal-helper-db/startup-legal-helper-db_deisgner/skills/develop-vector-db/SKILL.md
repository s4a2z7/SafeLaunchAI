---
name: develop-vector-db
description: This skill should be used when the user asks "벡터DB 개발", "ChromaDB 구현", "legal_rag 만들기", "법률 RAG 구현", "벡터 검색 구현", "임베딩 저장", "법령 데이터 인덱싱", or needs guidance on building the ChromaDB-based legal vector search module for SafeLaunch AI.
version: 0.1.0
---

# SafeLaunch AI — 벡터 DB (legal_rag.py) 개발 가이드

## 목적

`core/legal_rag.py` 모듈을 구현합니다.
국가법령정보 Open API에서 수집한 법령·판례·스토어 정책 데이터를 ChromaDB에 임베딩 저장하고,
쿼리 기반 유사도 검색을 통해 분석 근거를 제공하는 RAG 파이프라인을 완성합니다.

---

## 선행 조건

구현을 시작하기 전 반드시 확인:

1. **`core/law_api.py`가 정상 동작하는지** — 이 모듈이 법령/판례 원천 데이터를 공급합니다
2. **`requirements.txt`의 `chromadb>=0.4.22`가 설치되었는지** — `pip install chromadb`
3. **프로젝트 루트에 `database/` 디렉토리가 존재하는지** — ChromaDB 로컬 저장소 경로

```bash
pip install chromadb
mkdir -p database
```

---

## 구현 단계

### Step 1: ChromaDB 클라이언트 초기화

`database/` 경로를 persist_directory로 사용하는 ChromaDB 클라이언트를 생성합니다.

**핵심 사항:**
- `chromadb.PersistentClient(path="./database")` 사용
- 컬렉션 3종 설계: `laws` (법령), `precedents` (판례), `store_policies` (스토어 정책)
- 또는 통합 컬렉션 1개 + metadata의 `source_type` 필드로 구분 (개발명세서 5.3 참조)

**구현할 함수:**
```python
def get_chroma_client() -> chromadb.ClientAPI:
    """ChromaDB 클라이언트 싱글톤 반환"""

def get_or_create_collection(name: str) -> chromadb.Collection:
    """컬렉션 반환 (없으면 생성)"""
```

**참조:** 개발명세서 5.3 — ChromaDB 컬렉션 설계

---

### Step 2: 데이터 청킹 (Chunking)

법령·판례 텍스트를 벡터 검색에 적합한 단위로 분할합니다.

**핵심 사항:**
- **법률 문맥 단위 청킹** (Context-aware Chunking) — 조문 단위, 판결요지 단위
- 단순 글자 수 분할이 아닌, 법률 문서의 구조적 경계(조, 항, 호)를 기준으로 분할
- 청크 크기 권장: 500~1000자, 오버랩 100~200자
- 각 청크에 메타데이터 필수 부착: 원천 ID, 법령번호, 공포일, 시행일, 출처 URL

**구현할 함수:**
```python
def chunk_law_text(
    text: str,
    metadata: dict,
    chunk_size: int = 800,
    overlap: int = 150
) -> list[dict]:
    """
    법령 텍스트를 문맥 단위로 청킹
    Returns: [{"text": str, "metadata": dict}, ...]
    """
```

**참조:** 개발명세서 5.3 — "문맥 유지형 청킹, 법률 문맥 단위"

---

### Step 3: 데이터 적재 (Ingestion)

`core/law_api.py`에서 가져온 법령·판례 데이터를 정제 후 ChromaDB에 저장합니다.

**핵심 사항:**
- HTML 태그·노이즈 제거 후 임베딩 (API명세서 2.3 참조)
- Source First 원칙 — 원천 메타데이터 반드시 보존
- 중복 적재 방지: document ID 기반 upsert
- ChromaDB 기본 임베딩 모델 사용 (all-MiniLM-L6-v2) 또는 프로젝트에 맞는 다국어 모델 검토

**구현할 함수:**
```python
def ingest_laws(query: str, max_items: int = 100) -> int:
    """
    법령 검색 → 상세 조회 → 청킹 → ChromaDB 저장
    Returns: 저장된 청크 수
    """

def ingest_precedents(query: str, max_items: int = 50) -> int:
    """
    판례 검색 → 상세 조회 → 청킹 → ChromaDB 저장
    Returns: 저장된 청크 수
    """
```

**데이터 흐름:**
```
law_api.search_laws() → law_api.get_law_detail() → 정제 → chunk_law_text() → collection.upsert()
```

---

### Step 4: 유사도 검색 (Query)

API 명세서 3.2에 정의된 인터페이스를 구현합니다.

**필수 인터페이스 (API명세서 준수):**
```python
def search_legal_context(
    query: str,
    top_k: int = 5,
    score_threshold: float = 0.7
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
```

**핵심 사항:**
- `score_threshold` 미달 결과는 반드시 필터링 (개발명세서 4.3 제약사항)
- ChromaDB의 `collection.query()` 결과를 프로젝트 표준 형식으로 변환
- distance → similarity score 변환 주의 (ChromaDB는 distance 반환, 낮을수록 유사)

---

### Step 5: 데이터 동기화 (F-6 기능)

법률 데이터의 주기적 갱신을 지원합니다.

**구현할 함수:**
```python
def sync_legal_data(
    queries: list[str],
    force_refresh: bool = False
) -> dict:
    """
    Vector DB 데이터 동기화
    Returns: {"laws_added": int, "precedents_added": int, "total_chunks": int}
    """
```

**참조:** 개발명세서 F-6 (Should 우선순위)

---

## 코드 품질 기준

구현 시 반드시 준수:

- [ ] 모든 함수에 **Type Hint** 적용
- [ ] 예외 처리: API 오류, ChromaDB 연결 실패, 빈 결과 등
- [ ] `core/law_api.py`의 코딩 스타일과 일관성 유지 (docstring, 에러 핸들링 패턴)
- [ ] 유사도 임계치 미달 결과 필터링 (카더라 방지)
- [ ] 메타데이터에 원천 정보 필수 포함 (Source First 원칙)

---

## 테스트 시나리오

구현 완료 후 검증:

1. **적재 테스트:** "저작권법" 검색 → 법령 상세 조회 → ChromaDB 저장 → 청크 수 확인
2. **검색 테스트:** "앱 저작권 침해" 쿼리 → 유사 법령/판례 반환 확인
3. **임계치 테스트:** `score_threshold=0.9` → 저품질 결과 필터링 확인
4. **중복 방지 테스트:** 동일 데이터 2회 적재 → 중복 없이 upsert 확인
5. **통합 테스트:** `search_legal_context()` 반환값이 `core/analyzer.py` 입력 형식과 호환 확인

```python
# 테스트 예시
if __name__ == "__main__":
    # 1. 적재
    count = ingest_laws("저작권", max_items=10)
    print(f"저장된 청크: {count}")

    # 2. 검색
    results = search_legal_context("앱 내 결제 정책 위반", top_k=3)
    for r in results:
        print(f"[{r['score']:.3f}] {r['text'][:100]}...")
```

---

## 참조 문서

| 문서 | 참조 섹션 |
|------|-----------|
| 개발명세서.md | 4.3 (모듈 명세), 5.3 (ChromaDB 컬렉션) |
| API명세서.md | 2.3 (연동 유의사항), 3.2 (함수 시그니처) |
| core/law_api.py | 데이터 공급 모듈 (구현 패턴 참조) |

---

## 다음 단계

`legal_rag.py` 완료 후:
- → `core/benchmarker.py` 구현 (타겟 URL 스크래핑)
- → `core/analyzer.py`에서 `search_legal_context()` 호출하여 RS 점수 산출
