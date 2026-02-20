# SafeLaunch AI RAG 고도화 구현 완료 보고서

## 구현 일시
2026-02-13

## 구현 개요

SafeLaunch AI의 RAG 파이프라인을 다음 4가지 기능으로 고도화하였습니다:

1. **Hybrid Search** - 벡터 검색 + 법제처 API 병합
2. **Reranking** - BGE-reranker를 이용한 상위 결과 재정렬
3. **Self-healing RAG** - LLM 기반 context 적합도 평가 및 재검색
4. **RAGAS 평가** - RAG 품질 정량 평가 시스템

---

## 1. Hybrid Search 구현

### 파일
- `core/legal_rag.py`

### 추가된 함수
- `_reciprocal_rank_fusion()`: RRF 알고리즘 구현
- `hybrid_search_laws()`: 법령 하이브리드 검색
- `hybrid_search_precedents()`: 판례 하이브리드 검색

### 동작 방식
1. **벡터 검색**: 기존 TF-IDF VectorStore 사용
2. **API 검색**: `search_laws()`, `search_precedents()` 실시간 호출
3. **RRF 병합**: 두 결과를 Reciprocal Rank Fusion으로 병합 (k=60)
4. **결과**: 상위 20건 반환 (리랭킹 전 단계)

### 특징
- 법제처 API Rate Limit 대응 (기존 재시도 로직 활용)
- API 실패 시 벡터 검색 결과만 사용 (폴백)
- 스토어 정책은 API 없으므로 벡터 검색만 사용

---

## 2. Reranking 구현

### 파일
- `core/reranker.py` (신규)

### 클래스
- `BaseReranker`: 리랭커 기본 인터페이스
- `BGEReranker`: BGE-reranker-v2-m3 기반 (로컬, 무료)
- `CohereReranker`: Cohere Rerank API 기반 (유료, 선택)

### 통합
- `search_legal_context()`에서 하이브리드 모드 시 자동으로 리랭킹 적용
- 상위 20건 → BGE 모델로 재정렬 → 상위 5건 선별

### 특징
- Cross-Encoder 방식으로 Query-Document 유사도 정밀 계산
- GPU 사용 시 성능 향상
- 리랭킹 실패 시 원본 점수로 폴백

---

## 3. Self-healing RAG 구현

### 파일
- `core/self_healing_rag.py` (신규)

### Pydantic 모델
- `ContextFitnessOutput`: 적합도 평가 결과 (0~1 실수)
- `QueryExpansionOutput`: 쿼리 확장 결과

### 주요 함수
- `evaluate_context_fitness()`: LLM으로 context 적합도 평가
- `expand_query()`: 검색 쿼리 확장
- `self_healing_search()`: 검색 → 평가 → 재검색 루프

### 동작 방식
1. 검색 실행
2. LLM으로 context 적합도 평가 (0~1)
3. 임계치 미달 시:
   - 쿼리 확장 (동의어, 관련 용어 추가)
   - 검색 파라미터 조정 (top_k 확대, threshold 완화)
   - 재검색 (최대 2회)
4. 임계치 통과 또는 최대 재시도 시 결과 반환

### 특징
- Anthropic Claude 및 OpenAI 지원
- Pydantic으로 출력 형식 강제 (0~1 실수 보장)
- Tool use / Function calling 활용

---

## 4. RAGAS 평가 구현

### 파일
- `eval/ragas_eval.py` (신규)

### 평가 메트릭
- **Context Precision**: 검색된 문서의 질문 적합도
- **Faithfulness**: 답변의 context 근거도
- **Answer Relevancy**: 답변의 질문 관련성

### 평가 데이터셋
- 법률/판례 관련 Q&A 10건 포함
- 저작권, 개인정보, 상표, 위치정보, 오픈소스 등 다양한 주제

### 실행 방법
```bash
# 기본 실행
python eval/ragas_eval.py

# OpenAI 사용
python eval/ragas_eval.py --llm openai

# 하이브리드 비활성화
python eval/ragas_eval.py --no-hybrid
```

### 결과 저장
- `eval/ragas_evaluation_result.json`에 평가 점수 저장

---

## 파일 변경 요약

| 파일 | 상태 | 설명 |
|------|------|------|
| `core/legal_rag.py` | 수정 | 하이브리드 검색, 리랭킹, Self-healing 통합 |
| `core/reranker.py` | 신규 | BGE/Cohere 리랭커 구현 |
| `core/self_healing_rag.py` | 신규 | LLM 기반 적합도 평가 및 재검색 |
| `eval/ragas_eval.py` | 신규 | RAGAS 평가 스크립트 |
| `requirements.txt` | 수정 | 필요 패키지 추가 |
| `RAG_UPGRADE_README.md` | 신규 | 사용 가이드 |

---

## 의존성 추가

### 필수
- `sentence-transformers>=2.3.0` - BGE Reranker
- `langchain>=0.1.0` - RAGAS 연동
- `langchain-anthropic>=0.1.0` - Anthropic LLM
- `langchain-openai>=0.0.5` - OpenAI LLM
- `ragas>=0.1.0` - RAG 평가
- `datasets>=2.14.0` - RAGAS 데이터셋
- `pydantic>=2.0.0` - 구조화 출력

### 선택
- `cohere>=4.0.0` - Cohere Rerank API (유료)

---

## 환경변수 설정

`.env` 파일에 추가 필요:

```bash
# Self-healing 및 RAGAS용 LLM API 키
ANTHROPIC_API_KEY=your_key
# 또는
OPENAI_API_KEY=your_key

# Cohere Rerank 사용 시 (선택)
COHERE_API_KEY=your_key
```

---

## 사용 예시

### 1. 기본 하이브리드 검색 (리랭킹 포함)

```python
from core.legal_rag import search_legal_context

results = search_legal_context(
    query="앱 저작권 침해",
    top_k=5,
    use_hybrid=True,  # 기본값
)
```

### 2. Self-healing RAG

```python
results = search_legal_context(
    query="앱 저작권 침해",
    top_k=5,
    use_hybrid=True,
    use_self_healing=True,
    fitness_threshold=0.6,
)
```

### 3. RAGAS 평가

```bash
python eval/ragas_eval.py --llm anthropic --top-k 5
```

---

## 성능 고려사항

### 하이브리드 검색
- **장점**: 벡터 + API 병합으로 검색 품질 향상
- **단점**: API 호출로 인한 지연 (1~3초)
- **최적화**: 법제처 API Rate Limit 대응 (재시도 로직)

### 리랭킹
- **장점**: 상위 결과 정밀도 향상
- **단점**: BGE 모델 로드 시간 (첫 실행 시 ~5초)
- **최적화**: GPU 사용 권장, 모델 캐싱

### Self-healing
- **장점**: 저품질 결과 자동 개선
- **단점**: LLM 호출 비용 및 지연 (재검색 시 추가 시간)
- **최적화**: 임계치 조정, 재시도 횟수 제한

---

## 테스트 결과

### 하이브리드 검색
- 법령 검색: 벡터 10건 + API 10건 → RRF 병합 → 20건
- 판례 검색: 벡터 10건 + API 10건 → RRF 병합 → 20건
- 스토어 정책: 벡터 20건

### 리랭킹
- 입력: 20건
- 출력: 5건 (BGE 점수 기준 재정렬)

### Self-healing
- 적합도 평가: 0~1 실수 (Pydantic 강제)
- 재검색: 임계치 미달 시 최대 2회

### RAGAS
- 평가 데이터: 10건
- 메트릭: Context Precision, Faithfulness, Answer Relevancy
- 결과: JSON 파일 저장

---

## 향후 개선 사항

1. **하이브리드 검색 캐싱**: API 결과 캐싱으로 지연 감소
2. **리랭커 모델 선택**: 도메인 특화 모델 파인튜닝
3. **Self-healing 임계치 자동 조정**: 피드백 기반 학습
4. **RAGAS 데이터셋 확장**: 50~100건으로 확대

---

## 문의 및 지원

- 구현 관련 문의: `RAG_UPGRADE_README.md` 참조
- 문제 해결: GitHub Issues

---

**구현 완료일**: 2026-02-13  
**구현자**: AI Assistant (Claude)  
**프로젝트**: SafeLaunch AI
