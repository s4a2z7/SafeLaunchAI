# Red Team 리뷰: DB 담당자(팀원 A) 자료 개선점 10가지

**작성일:** 2026-02-01  
**리뷰어:** Red Team  
**대상 브랜치:** [db_deisgner](https://github.com/s4a2z7/startup-legal-helper/tree/db_deisgner)  
**참고 자료:** `logit_study.md` (법률 리스크 분석)

---

## 개요

`logit_study.md`에서 제시한 **핵심 법률 리스크**(저작권법, 부정경쟁방지법 카목, 개인정보보호법, 전자상거래법)를 기준으로 현재 DB 인프라의 심각한 문제점을 Red Team 관점에서 분석하였습니다.

---

## 🚨 Critical Issues (치명적 문제)

### 1. 판례 데이터 오염 — 실제 판례 내용 0%

**현상:**
```json
{
  "text": "/DRF/js/ext/resources/css/ext-all.css /DRF/js/common/jquery/jquery.js ...",
  "case_name": "저작권침해금지등"
}
```

**문제점:**
- `precedents.json`의 **77건 전체**가 CSS/JS 경로 문자열로 오염
- 판시사항, 판결요지, 참조조문 등 **핵심 법률 근거가 전무**
- 이 상태로 RAG 검색 시 **"카더라" 수준의 응답**만 생성됨

**영향:**
- `logit_study.md`에서 언급한 "야놀자-여기어때", "잡코리아-사람인" 판례 검색 불가
- 사용자에게 **잘못된 법률 근거** 제공 → 서비스 신뢰도 0

---

### 2. 핵심 법령 미수집 — 서비스 목적 달성 불가

**logit_study.md에서 요구하는 법령:**
| 법령 | 수집 여부 | 중요도 |
|------|:--------:|:------:|
| 저작권법 | ✅ | Critical |
| **부정경쟁방지법** | ❌ | Critical |
| **개인정보보호법** | ❌ | Critical |
| **전자상거래법** | ❌ | Critical |
| 정보통신망법 | ❌ | High |

**문제점:**
- 현재 `laws.json`에는 **저작권법만** 존재
- `logit_study.md`의 핵심인 **부정경쟁방지법 제2조 제1호 카목**(성과물 도용) 검색 불가
- 개인정보보호법 제15조, 제22조 — **광고성 정보 전송 동의** 조항 누락
- 전자상거래법 제17조, 제18조 — **청약철회/환불** 조항 누락

---

### 3. 스토어 정책 컬렉션 완전 공백

**현상:**
- `store_policies.json` 파일 자체가 존재하지 않거나 비어있음
- `ingest_store_policies()` 함수는 구현되어 있으나 **호출된 적 없음**

**문제점:**
- App Store Review Guidelines, Google Play Developer Policy 미수집
- **"스토어 정책 위반 가능성(P 점수)"** 계산이 불가능
- RS 공식의 4요소 중 **P(Policy) 요소가 작동하지 않음**

---

## ⚠️ High Priority Issues (우선 개선 필요)

### 4. 판례 본문 추출 로직 결함

**`_extract_precedent_text()` 함수 분석:**
```python
field_keys = ["판시사항", "판결요지", "참조조문", "참조판례", "판례내용"]
for key in field_keys:
    value = prec.get(key, "")  # 항상 빈 문자열 반환
```

**문제점:**
- 국가법령정보 API의 판례 응답이 **HTML 형식**일 때 파싱 실패
- `_extract_text_from_html_dict()` 함수가 HTML 노이즈를 그대로 저장
- **30자 이상**이면 무조건 저장하는 로직 → CSS 경로도 저장됨

**개선안:**
```python
# HTML 노이즈 필터링 강화
NOISE_PATTERNS = [
    r"/DRF/js/",
    r"\.css",
    r"\.js",
    r"font-family:",
    r"font-size:",
]
```

---

### 5. TF-IDF 기반 검색의 의미론적 한계

**현재 구현:**
```python
vectorizer = TfidfVectorizer(
    analyzer="char_wb",
    ngram_range=(1, 3),
    max_features=10000,
)
```

**문제점:**
- **문자 단위(char_wb)** 벡터화 → 법률 용어의 의미를 이해하지 못함
- "저작권 침해"와 "저작물 도용"의 **의미적 유사성** 인식 불가
- `logit_study.md`의 "성과물 도용" 개념을 검색하려면 **정확히 같은 단어**가 필요

**권장 대안:**
- OpenAI Embedding API 또는 HuggingFace의 `sentence-transformers` 도입
- 최소한 **형태소 분석기(Mecab, Okt)** 적용 필요

---

### 6. 데이터 품질 검증 로직 부재

**현재 상태:**
- 수집된 데이터가 **"유효한 법률 문서"인지 검증하지 않음**
- 빈 문자열, HTML 노이즈, 중복 데이터가 그대로 저장됨

**필요한 검증:**
```python
def validate_legal_document(text: str, source_type: str) -> bool:
    """법률 문서 유효성 검증"""
    # 1. 최소 길이 검증 (법률 문서는 보통 500자 이상)
    if len(text) < 500:
        return False
    
    # 2. 법률 용어 포함 여부
    LEGAL_KEYWORDS = ["제", "조", "항", "호", "법", "규정", "위반"]
    if not any(kw in text for kw in LEGAL_KEYWORDS):
        return False
    
    # 3. 노이즈 패턴 탐지
    if re.search(r"\.(css|js|jpg|png)", text):
        return False
    
    return True
```

---

### 7. 메타데이터 불완전 — 출처 추적 곤란

**현재 메타데이터:**
```json
{
  "source_type": "precedent",
  "precedent_seq": "608359",
  "case_name": "저작권침해금지등",
  "court_name": "서울고등법원",
  "judgment_date": "2024.12.12"
}
```

**누락된 필수 정보:**
- `case_number` (사건번호: 2024나12345)
- `parties` (당사자: 원고 vs 피고)
- `key_issues` (쟁점 요약)
- `related_laws` (관련 법조문 리스트)
- `source_url` (원문 링크)

**중요성:**
- `logit_study.md`의 "야놀자-여기어때" 판례를 검색해도 **사건번호로 식별 불가**
- 사용자에게 **"어떤 판례인지"** 명확히 안내 불가능

---

## 📋 Medium Priority Issues (중기 개선)

### 8. 동기화 주기 및 버전 관리 부재

**현재 상태:**
- `sync_legal_data()` 함수가 **수동 호출** 방식
- 데이터 갱신 시점, 버전 정보 기록 없음

**문제점:**
- 법령 개정 시 **자동 반영 불가**
- 저작권법이 "2025-09-26 시행"인데 현재 수집 데이터가 최신인지 불명

**권장:**
```python
# database/metadata.json
{
  "last_sync": "2026-02-01T10:30:00Z",
  "version": "1.0.3",
  "laws_count": 5,
  "precedents_count": 77,
  "sync_queries": ["저작권", "부정경쟁", "개인정보"]
}
```

---

### 9. 에러 핸들링 및 재시도 로직 미흡

**현재 코드:**
```python
except Exception as e:
    print(f"[LegalRAG] 법령 상세 조회 실패 ({law_name}): {e}")
    continue  # 그냥 건너뜀
```

**문제점:**
- API 일시 장애 시 **데이터 누락** 발생
- 실패 건에 대한 **재시도 로직 없음**
- 실패 로그가 **파일로 저장되지 않아** 추적 불가

---

### 10. 청킹 전략의 법률 문맥 손실

**현재 청킹:**
```python
# 조문 경계(제N조) 기준 분할
segments = re.split(r"(?=제\d+조[\s(])", cleaned)
```

**문제점:**
- 판례의 경우 **"제N조" 패턴이 없어** 청킹 실패 → 문서 전체가 하나의 청크
- `chunk_size=800`이 법률 문맥 유지에 **너무 작을 수 있음**
- 조문 간 **연관성**(예: 제2조 정의 → 제30조 적용)이 청킹 시 분리됨

**권장:**
- 판례용 별도 청킹 전략 필요 (쟁점별, 판시사항별 분리)
- Overlap을 현재 150자에서 **300자 이상**으로 확대

---

## 📊 개선 우선순위 요약

| 순위 | 이슈 | 심각도 | 예상 공수 |
|:----:|------|:------:|:---------:|
| 1 | 판례 데이터 오염 | 🔴 Critical | 1일 |
| 2 | 핵심 법령 미수집 | 🔴 Critical | 0.5일 |
| 3 | 스토어 정책 공백 | 🔴 Critical | 1일 |
| 4 | 판례 추출 로직 결함 | 🟠 High | 0.5일 |
| 5 | TF-IDF 의미론적 한계 | 🟠 High | 2일 |
| 6 | 데이터 품질 검증 | 🟠 High | 0.5일 |
| 7 | 메타데이터 불완전 | 🟡 Medium | 0.5일 |
| 8 | 동기화/버전 관리 | 🟡 Medium | 0.5일 |
| 9 | 에러 핸들링 | 🟡 Medium | 0.5일 |
| 10 | 청킹 전략 개선 | 🟡 Medium | 1일 |

---

## 결론

**현재 DB 인프라는 서비스 목적 달성에 심각한 장애가 있습니다.**

`logit_study.md`에서 분석한 4대 법률 리스크(저작권, 부정경쟁, 개인정보, 전자상거래) 중 **저작권법만 부분적으로 수집**되었고, 판례는 **사실상 사용 불가 상태**입니다.

**즉시 조치 필요:**
1. 판례 수집 로직 전면 재작업
2. 부정경쟁방지법, 개인정보보호법, 전자상거래법 수집
3. 스토어 정책(App Store, Google Play) 데이터 확보

---

## 대응 완료 현황 (2026-02-02 업데이트)

| 순위 | 이슈 | 심각도 | 대응 상태 | 변경 파일 |
|:----:|------|:------:|:---------:|----------|
| 1 | 판례 데이터 오염 | Critical | **해결** | `legal_rag.py`, `clean_precedents.py` |
| 2 | 핵심 법령 미수집 | Critical | **해결** (01-31) | `laws.json` (46개 법령) |
| 3 | 스토어 정책 공백 | Critical | **해결** (02-01) | `store_policies.json` (36건) |
| 4 | 판례 추출 로직 결함 | High | **해결** | `legal_rag.py` — 노이즈 필터링 + 재귀 추출 |
| 5 | TF-IDF 의미론적 한계 | High | **개선** | `legal_rag.py` — 하이브리드 검색(word 60% + char 40%) |
| 6 | 데이터 품질 검증 | High | **해결** | `legal_rag.py` — `validate_legal_document()` |
| 7 | 메타데이터 불완전 | Medium | **해결** | `legal_rag.py` — case_number, source_url 추가 |
| 8 | 동기화/버전 관리 | Medium | **해결** | `legal_rag.py` — `database/metadata.json` |
| 9 | 에러 핸들링 | Medium | **해결** | `law_api.py` — 지수 백오프 재시도 (3회) |
| 10 | 청킹 전략 개선 | Medium | **해결** | `legal_rag.py` — `chunk_precedent_text()` |

> **판례 데이터 현황:** 기존 71건 전체 오염 확인 → 정화 완료 (백업 보존).
> 개선된 추출 로직으로 재수집 필요.

---

*Red Team Review 완료*
*대응 완료: 2026-02-02*
