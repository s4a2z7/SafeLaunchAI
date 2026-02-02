# 🚀 SafeLaunch AI - 통합 가이드

프론트엔드(Streamlit)와 백엔드(RAG Engine)를 통합한 완전한 웹서비스

---

## 📦 패키지 구성

```
safelaunch-ai-complete/
│
├── 📱 프론트엔드 (3가지 버전)
│   ├── app.py              # Basic - 간단한 데모
│   ├── app_pro.py          # Pro - URL 벤치마킹
│   ├── app_ultimate.py     # Ultimate - 4단계 워크플로우
│   └── app_rag.py          # RAG - 실제 DB 연동 ⭐
│
├── 🔧 백엔드 (RAG Engine)
│   └── startup-legal-helper-main/
│       ├── core/
│       │   ├── legal_rag.py          # RAG 엔진
│       │   ├── law_api.py            # API 래퍼
│       │   └── store_policy_data.py
│       └── database/
│           ├── laws.json             # 2.6MB
│           ├── precedents.json       # 46KB
│           └── store_policies.json   # 48KB
│
└── 📚 문서
    ├── README.md
    ├── README_PRO.md
    ├── README_ULTIMATE.md
    └── README_RAG.md
```

---

## 🎯 버전별 특징 비교

| 특징 | Basic | Pro | Ultimate | **RAG** ⭐ |
|---|:---:|:---:|:---:|:---:|
| Streamlit UI | ✅ | ✅ | ✅ | ✅ |
| 리스크 분석 | ✅ | ✅ | ✅ | ✅ |
| URL 벤치마킹 | ❌ | ✅ | ✅ | ❌ |
| 4단계 워크플로우 | ❌ | ❌ | ✅ | ❌ |
| 수학적 RS 지수 | ❌ | ❌ | ✅ | ✅ |
| **실제 법률 DB** | ❌ | ❌ | ❌ | ✅ |
| **벡터 검색** | ❌ | ❌ | ❌ | ✅ |
| **판례 매칭** | 시뮬 | 시뮬 | 시뮬 | ✅ |

---

## 🚀 빠른 시작 (RAG Edition 권장)

### 1. 프로젝트 구조 준비

```bash
# 프로젝트 루트 구조
safelaunch-ai/
├── app_rag.py
├── requirements_rag.txt
├── run_rag.sh
└── startup-legal-helper-main/  # 백엔드 폴더
    ├── core/
    └── database/
```

### 2. 의존성 설치

```bash
pip install -r requirements_rag.txt
```

**필수 패키지**:
- `streamlit` - 웹 인터페이스
- `scikit-learn` - TF-IDF 벡터화
- `numpy` - 수치 연산
- `pandas` - 데이터 처리

### 3. 앱 실행

```bash
# 방법 1: 직접 실행
streamlit run app_rag.py

# 방법 2: 스크립트 사용
./run_rag.sh
```

### 4. 브라우저 접속

```
http://localhost:8501
```

---

## 🏗️ 시스템 아키텍처

### 데이터 흐름

```
┌──────────────┐
│    사용자    │
└──────┬───────┘
       │ 서비스 설명 입력
       ▼
┌──────────────┐
│  Streamlit   │  app_rag.py
│  Frontend    │  - 입력 폼
└──────┬───────┘  - 결과 표시
       │
       │ analyze_service_risk()
       ▼
┌──────────────┐
│  RAG Engine  │  core/legal_rag.py
│              │  - search_legal_context()
└──────┬───────┘  - TF-IDF 벡터화
       │          - 코사인 유사도
       │
       │ query()
       ▼
┌──────────────┐
│  Vector DB   │  database/*.json
│              │  - laws.json (17K+ 항목)
└──────────────┘  - precedents.json (100+)
                  - policies.json
```

### 핵심 컴포넌트

#### 1️⃣ Frontend (app_rag.py)

**역할**:
- 사용자 입력 수집
- RAG 엔진 호출
- 결과 시각화

**주요 함수**:
```python
def analyze_service_risk(description, service_type, top_k):
    # RAG 검색
    results = search_legal_context(query=description, top_k=top_k)
    
    # 리스크 점수 계산
    risk_score = calculate_risk_score(results, description)
    
    # 권장사항 생성
    recommendations = generate_recommendations(results, risk_score)
    
    return {
        "risk_score": risk_score,
        "search_results": results,
        "recommendations": recommendations
    }
```

#### 2️⃣ Backend (core/legal_rag.py)

**역할**:
- 벡터 스토어 관리
- 유사도 검색
- 결과 필터링

**주요 클래스**:
```python
class VectorStore:
    def __init__(self, name, db_path):
        # JSON 파일에서 문서 로드
        
    def query(self, query_text, n_results):
        # TF-IDF 벡터화
        # 코사인 유사도 계산
        # 상위 N개 반환
```

#### 3️⃣ Database (database/*.json)

**구조**:
```json
{
  "doc_id": {
    "text": "실제 조문 내용...",
    "metadata": {
      "source_type": "law|precedent|policy",
      "law_name": "저작권법",
      "chunk_index": 0
    }
  }
}
```

---

## 🔍 RAG 검색 상세

### TF-IDF 벡터화

```python
from sklearn.feature_extraction.text import TfidfVectorizer

# 1. 문서 벡터화
vectorizer = TfidfVectorizer()
doc_vectors = vectorizer.fit_transform(documents)

# 2. 쿼리 벡터화
query_vector = vectorizer.transform([query])

# 3. 유사도 계산
from sklearn.metrics.pairwise import cosine_similarity
similarities = cosine_similarity(query_vector, doc_vectors)

# 4. 상위 K개 추출
top_k_indices = np.argsort(similarities[0])[::-1][:k]
```

### 검색 결과 구조

```python
{
  "laws": [
    {
      "text": "제1조(목적) ...",
      "metadata": {...},
      "similarity": 0.85
    }
  ],
  "precedents": [...],
  "policies": [...]
}
```

---

## 💡 커스터마이징

### 1. 리스크 가중치 조정

```python
# app_rag.py > calculate_risk_score()

# 기본값
law_weight = 0.4
precedent_weight = 0.4
policy_weight = 0.2

# 법률 중시
law_weight = 0.6
precedent_weight = 0.3
policy_weight = 0.1
```

### 2. 검색 결과 수 변경

```python
# app_rag.py > sidebar

top_k = st.slider(
    "검색 결과 수",
    min_value=3,
    max_value=20,  # 증가
    value=10       # 기본값 증가
)
```

### 3. UI 테마 변경

```python
# app_rag.py > st.markdown (CSS)

.main-header {
    background: linear-gradient(135deg, #FF6B6B 0%, #4ECDC4 100%);
    # 색상 변경
}
```

### 4. 추가 데이터 소스

```python
# core/legal_rag.py

COLLECTION_CUSTOM = "custom_data"
ALL_COLLECTIONS = [
    COLLECTION_LAWS,
    COLLECTION_PRECEDENTS,
    COLLECTION_POLICIES,
    COLLECTION_CUSTOM  # 추가
]
```

---

## 🧪 테스트

### 단위 테스트

```python
# test_rag.py
import sys
sys.path.insert(0, './startup-legal-helper-main')

from core.legal_rag import search_legal_context

def test_search():
    result = search_legal_context(
        query="AI 뉴스 요약",
        top_k=5
    )
    
    assert "laws" in result
    assert "precedents" in result
    assert len(result["laws"]) > 0

test_search()
print("✅ 테스트 통과")
```

### 통합 테스트

```bash
# 1. RAG 엔진 단독 테스트
cd startup-legal-helper-main
python test_api.py

# 2. Streamlit 앱 테스트
streamlit run app_rag.py --server.headless true
```

---

## 📊 성능 최적화

### 1. 캐싱 활용

```python
@st.cache_resource
def init_rag_system():
    # RAG 초기화는 한 번만
    initialize_vector_stores()
    return get_store_stats()

@st.cache_data(ttl=3600)
def search_cached(query, top_k):
    # 1시간 캐싱
    return search_legal_context(query, top_k)
```

### 2. 벡터 DB 최적화

```python
# core/legal_rag.py

class VectorStore:
    def __init__(self, name, db_path):
        self._vectorizer = None  # 지연 로딩
        self._doc_matrix = None
    
    def _build_index(self):
        # 최초 검색 시에만 인덱스 구축
        if self._vectorizer is None:
            # TF-IDF 벡터화
```

### 3. 병렬 처리

```python
from concurrent.futures import ThreadPoolExecutor

def search_all_collections(query, top_k):
    with ThreadPoolExecutor(max_workers=3) as executor:
        law_future = executor.submit(search_laws, query, top_k)
        prec_future = executor.submit(search_precedents, query, top_k)
        policy_future = executor.submit(search_policies, query, top_k)
        
        return {
            "laws": law_future.result(),
            "precedents": prec_future.result(),
            "policies": policy_future.result()
        }
```

---

## 🔮 확장 가능성

### Phase 1: AI 통합

```python
# Claude API 연동
import anthropic

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

def analyze_with_claude(search_results, query):
    prompt = f"""
    다음 법률 문서를 바탕으로 리스크를 분석하세요:
    
    {json.dumps(search_results, ensure_ascii=False)}
    
    질문: {query}
    """
    
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )
    
    return message.content
```

### Phase 2: ChromaDB 전환

```python
# core/legal_rag.py

import chromadb

class VectorStore:
    def __init__(self, name, db_path):
        self.client = chromadb.PersistentClient(path=db_path)
        self.collection = self.client.get_or_create_collection(name)
    
    def query(self, query_text, n_results):
        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results
        )
        return results
```

### Phase 3: 실시간 업데이트

```python
# 법제처 API 연동
import schedule

def update_laws():
    # API에서 최신 법령 가져오기
    new_laws = fetch_from_law_api()
    
    # 벡터 DB 업데이트
    vector_store.upsert(new_laws)

# 매일 자정 업데이트
schedule.every().day.at("00:00").do(update_laws)
```

---

## 🆘 트러블슈팅

### 문제 1: "core 모듈을 찾을 수 없음"

```bash
# 해결책
export PYTHONPATH="${PYTHONPATH}:./startup-legal-helper-main"
```

### 문제 2: JSON 파싱 오류

```bash
# database/*.json 파일 확인
cd startup-legal-helper-main/database
python -m json.tool laws.json > /dev/null
```

### 문제 3: 메모리 부족

```python
# app_rag.py
# top_k 값 감소
top_k = st.slider("검색 결과 수", min_value=1, max_value=5, value=3)
```

---

## 📞 지원

- GitHub Issues: [링크]
- Email: support@safelaunch.ai
- 문서: README_RAG.md

---

**🛡️ SafeLaunch AI - Complete Integration Guide**

*프론트엔드 + 백엔드 + RAG 엔진 = 완전한 법률 리스크 분석 플랫폼*
