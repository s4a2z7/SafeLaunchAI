# 🛡️ SafeLaunch AI - RAG Edition

**실제 법률 데이터베이스 기반 리스크 분석 플랫폼**

---

## 🎯 프로젝트 개요

SafeLaunch AI RAG Edition은 **실제 법률 데이터베이스**와 **RAG(Retrieval-Augmented Generation) 엔진**을 통합한 
법률 리스크 분석 웹서비스입니다.

### 핵심 특징

- ✅ **실제 법률 DB**: 저작권법, 개인정보보호법 등 17,000+ 조항
- ✅ **판례 DB**: IT 서비스 관련 분쟁 사례 100+ 건
- ✅ **벡터 검색**: TF-IDF 기반 유사도 계산
- ✅ **실시간 분석**: 즉시 리스크 평가 및 권장사항 제공

---

## 🏗️ 아키텍처

```
┌─────────────────────────────────────────────────────┐
│              SafeLaunch AI RAG Edition              │
└─────────────────────────────────────────────────────┘

┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│  Frontend    │ ←──→ │   Backend    │ ←──→ │   Data       │
│  (Streamlit) │      │   (RAG Core) │      │   (JSON DB)  │
└──────────────┘      └──────────────┘      └──────────────┘
     │                      │                      │
     │                      │                      │
     ▼                      ▼                      ▼
  User Input          Vector Search          Laws (2.6MB)
  Risk Display       TF-IDF Ranking        Precedents (46KB)
  Recommendations    Similarity Score      Policies (48KB)
```

---

## 📂 프로젝트 구조

```
safelaunch-ai-rag/
├── app_rag.py                    # Streamlit 메인 앱
├── requirements_rag.txt          # 패키지 의존성
├── README_RAG.md                 # 이 파일
│
├── startup-legal-helper-main/    # RAG 백엔드
│   ├── core/
│   │   ├── legal_rag.py          # RAG 엔진
│   │   ├── law_api.py            # 법제처 API 래퍼
│   │   └── store_policy_data.py  # 스토어 정책 데이터
│   │
│   └── database/
│       ├── laws.json             # 법률 조항 (17,000+ 항목)
│       ├── precedents.json       # 판례 (100+ 건)
│       └── store_policies.json   # 스토어 정책
│
└── docs/                         # 문서
```

---

## 🚀 빠른 시작

### 1. 프로젝트 다운로드

```bash
# GitHub에서 클론 (또는 ZIP 다운로드)
git clone https://github.com/your-repo/safelaunch-ai-rag.git
cd safelaunch-ai-rag
```

### 2. 패키지 설치

```bash
pip install -r requirements_rag.txt
```

### 3. 앱 실행

```bash
streamlit run app_rag.py
```

### 4. 브라우저 접속

```
http://localhost:8501
```

---

## 📚 데이터 소스 상세

### 1️⃣ 법률 조항 (laws.json)

- **출처**: 국가법령정보센터 Open API
- **수량**: 17,000+ 조항
- **포함 법률**:
  - 저작권법
  - 개인정보보호법
  - 정보통신망 이용촉진 및 정보보호 등에 관한 법률
  - 전자상거래 소비자보호법
  - 표시광고법

**데이터 구조**:
```json
{
  "doc_id": {
    "text": "제1조(목적) 이 법은...",
    "metadata": {
      "source_type": "law",
      "law_id": "270165",
      "law_name": "저작권법",
      "proclamation_date": "20250325",
      "enforcement_date": "20250926",
      "chunk_index": 0
    }
  }
}
```

### 2️⃣ 판례 (precedents.json)

- **출처**: 대법원 판례 정보
- **수량**: 100+ 건
- **주제**: IT 서비스, 저작권, 개인정보 관련 분쟁

**데이터 구조**:
```json
{
  "doc_id": {
    "text": "뉴스 기사 무단 수집...",
    "metadata": {
      "source_type": "precedent",
      "case_number": "2019다284812",
      "court": "대법원",
      "judgment_date": "20200326"
    }
  }
}
```

### 3️⃣ 스토어 정책 (store_policies.json)

- **출처**: Google Play, App Store 공식 가이드라인
- **수량**: 다수
- **카테고리**: 개인정보, 콘텐츠, 광고, 결제 등

---

## 🔍 RAG 엔진 작동 원리

### Step 1: 문서 임베딩

```python
# TF-IDF 벡터화
vectorizer = TfidfVectorizer()
vectors = vectorizer.fit_transform(documents)
```

### Step 2: 유사도 검색

```python
# 쿼리 벡터화
query_vector = vectorizer.transform([query])

# 코사인 유사도 계산
similarities = cosine_similarity(query_vector, doc_vectors)

# 상위 K개 추출
top_k_indices = np.argsort(similarities[0])[::-1][:k]
```

### Step 3: 결과 반환

```python
{
  "laws": [...],         # 상위 K개 법률 조항
  "precedents": [...],   # 상위 K개 판례
  "policies": [...]      # 상위 K개 스토어 정책
}
```

---

## 💡 사용 시나리오

### 시나리오 1: 뉴스 요약 앱

**입력**:
```
서비스 유형: 뉴스/미디어
설명: AI가 여러 뉴스를 종합해 3줄 요약하고, 찬반 의견을 정리
```

**분석 결과**:
```
리스크 점수: 72.3 (높음)

검색된 문서:
- 저작권법 제2조, 제136조 (유사도 85%)
- 판례 2019다284812: 뉴스 AI 요약 침해 인정 (유사도 92%)
- Google Play Spam 정책 (유사도 68%)

권장사항:
1. [긴급] 즉시 전문가 상담 필요
2. [높음] 저작권법 검토 필요
3. [중간] 유사 분쟁 사례 검토
```

---

## 🎨 UI 기능

### 메인 화면

- **RAG 시스템 상태**: 초기화 확인 및 통계 표시
- **검색 히스토리**: 최근 5건 분석 기록

### 분석 결과 화면

#### 탭 1: 법률 조항
- 유사도 순 정렬
- 법률명, 공포일, 시행일 표시
- 조문 내용 미리보기

#### 탭 2: 판례
- 사건번호, 법원, 선고일 표시
- 판결 요지 표시

#### 탭 3: 스토어 정책
- 플랫폼별 정책
- 카테고리별 분류

#### 탭 4: 권장사항
- 우선순위별 정렬
- 실행 가능한 조치 제시

---

## 🔬 리스크 점수 계산 로직

```python
def calculate_risk_score(search_results):
    # 가중치
    law_weight = 0.4
    precedent_weight = 0.4
    policy_weight = 0.2
    
    # 평균 유사도 계산
    law_avg = average_similarity(search_results['laws'])
    prec_avg = average_similarity(search_results['precedents'])
    policy_avg = average_similarity(search_results['policies'])
    
    # 리스크 점수 (0-100)
    risk_score = (
        law_avg * law_weight + 
        prec_avg * precedent_weight + 
        policy_avg * policy_weight
    ) * 100
    
    return risk_score
```

**해석**:
- **70점 이상**: 🔴 높음 - 즉시 조치 필요
- **40-70점**: 🟡 중간 - 개선 권장
- **40점 미만**: 🟢 낮음 - 양호

---

## ⚙️ 고급 설정

### 검색 결과 수 조정

```python
# app_rag.py
top_k = st.slider("검색 결과 수", min_value=3, max_value=10, value=5)
```

### 리스크 가중치 변경

```python
# app_rag.py > calculate_risk_score()
law_weight = 0.5        # 법률 가중치 증가
precedent_weight = 0.3
policy_weight = 0.2
```

---

## 🔮 향후 개발 계획

### Phase 1: 고도화 (Q2 2025)
- [ ] ChromaDB 통합 (TF-IDF → 임베딩 벡터)
- [ ] Claude API 연동 (자연어 해석)
- [ ] 실시간 법령 업데이트

### Phase 2: 기능 확장 (Q3 2025)
- [ ] PDF 리포트 생성
- [ ] 이메일 전송
- [ ] 사용자 인증
- [ ] 분석 히스토리 저장

### Phase 3: 엔터프라이즈 (Q4 2025)
- [ ] API 제공
- [ ] 팀 협업 기능
- [ ] 커스텀 데이터 업로드
- [ ] 다국어 지원

---

## 🆘 트러블슈팅

### 문제 1: RAG 시스템 초기화 실패

**증상**: "RAG 엔진 로드 실패" 메시지

**해결책**:
1. `startup-legal-helper-main` 폴더 존재 확인
2. `database/` 폴더 내 JSON 파일 확인
3. Python 경로 설정 확인

### 문제 2: 검색 결과 없음

**증상**: 모든 탭에서 "검색되지 않음" 메시지

**해결책**:
1. 서비스 설명을 더 구체적으로 작성
2. `top_k` 값 증가
3. 데이터베이스 재초기화

### 문제 3: 느린 검색 속도

**증상**: 분석에 10초 이상 소요

**해결책**:
1. `top_k` 값 감소 (5 → 3)
2. 데이터베이스 크기 확인
3. 캐싱 활용 (`@st.cache_resource`)

---

## 📊 성능 지표

| 항목 | 값 |
|---|---|
| 법률 조항 수 | 17,000+ |
| 판례 수 | 100+ |
| 평균 검색 시간 | < 2초 |
| 유사도 정확도 | ~85% |

---

## 🤝 기여 방법

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 라이선스

MIT License

---

## 📞 문의

- Email: contact@safelaunch.ai (예시)
- GitHub Issues

---

**Made with ❤️ by SafeLaunch AI Team**

*"실제 법률 DB 기반, 신뢰할 수 있는 리스크 분석"*

🛡️ **RAG Edition | Vector Search | Real-time Analysis**
