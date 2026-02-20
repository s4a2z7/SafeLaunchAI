# SafeLaunch AI API 명세서 (API Specification)

**프로젝트명:** SafeLaunch AI  
**문서 버전:** 1.0  
**기준일:** 2026-01-31  
**참조:** 기획안.md, 개발명세서.md

---

## 1. 문서 개요

본 문서는 다음을 정의합니다.

1. **외부 API:** 국가법령정보 Open API 연동 사양  
2. **내부 모듈 인터페이스:** core·utils 간 함수 시그니처 및 입출력  
3. **애플리케이션 출력 표준:** M-2 JSON 스키마 (AI 리포트·대시보드 데이터)

---

## 2. 외부 API — 국가법령정보 Open API

### 2.1 기본 정보

- **공식 안내:** [국가법령정보 공동활용](https://open.law.go.kr), [공공데이터포털](https://www.data.go.kr)
- **인증:** API Key 또는 OC(사용자 이메일 ID) — 포털 신청 후 발급
- **제한:** Rate Limit·일일 호출 한도는 포털 및 서비스별 상이 (문서 확인 필요)

### 2.2 법령체계도 목록 조회 (예시)

| 항목 | 내용 |
|------|------|
| **Base URL** | `http://www.law.go.kr/DRF/lawSearch.do` |
| **Method** | GET |
| **필수 파라미터** | |

| 파라미터 | 타입 | 필수 | 설명 |
|----------|------|------|------|
| OC | string | O | 사용자 이메일 ID (예: g4c → g4c@korea.kr) |
| target | string | O | 서비스 대상 (예: lsStmd 법령체계도 목록) |
| type | string | O | 출력 형태: `XML` \| `JSON` \| `HTML` |

**선택 파라미터 (예시)**

| 파라미터 | 타입 | 설명 |
|----------|------|------|
| query | string | 법령명 검색 질의 |
| display | int | 검색 결과 개수 (기본 20, 최대 100) |
| page | int | 페이지 (기본 1) |
| sort | string | 정렬 (법령순, 공포일자순 등) |
| efYd, ancYd | string | 시행/공포 일자 범위 |
| org | string | 소관부처 |
| knd | string | 법령종류 |

**응답:** `type=JSON` 시 JSON 객체 (필드 구조는 공식 API 문서 참조)

### 2.3 연동 시 유의사항 (개발명세서 반영)

- **Error Handling:** Rate Limit·네트워크 오류 시 재시도(Retry)·로깅
- **데이터 보존:** 원천 ID, 법령번호, 공포일, 시행일 등 메타데이터 유지 후 ChromaDB 저장
- **정제:** HTML 태그·노이즈 제거 후 임베딩 (utils 또는 core 파이프라인에서 처리)

---

## 3. 내부 모듈 인터페이스 (Python)

아래는 **함수 시그니처 및 입출력 타입** 요약입니다. 구현 시 Type Hint 필수.

### 3.1 core/benchmarker.py

```text
def fetch_target_metadata(url: str) -> dict
```
- **입력:** `url` — 분석 대상 페이지 URL
- **출력:** `dict` — 기능 목록, 문구 샘플, 결제/개인정보 관련 텍스트 등 (키는 개발명세서·analyzer 요구에 맞게 정의)

### 3.2 core/legal_rag.py

```text
def search_legal_context(
    query: str,
    top_k: int = 5,
    score_threshold: float = 0.7
) -> list[dict]
```
- **입력:** `query` 검색문, `top_k` 상위 개수, `score_threshold` 유사도 하한
- **출력:** `list[dict]` — 각 항목 `{"text": str, "metadata": dict, "score": float}` 형태

### 3.3 core/analyzer.py

```text
def run_risk_analysis(
    benchmark_result: dict,
    rag_results: list[dict]
) -> dict
```
- **입력:** benchmarker 출력, legal_rag 검색 결과
- **출력:** M-2 호환 `dict` (아래 §4 스키마 준수)

### 3.4 core/strategist.py

```text
def build_fix_guide_and_checklist(analysis_result: dict) -> dict
```
- **입력:** analyzer 출력 (M-2 형식)
- **출력:** `dict` — `fix_guide: list[str]`, `checklist_7_steps: list[str]`, 기타 UX용 필드

### 3.5 utils/prompts.py

- **역할:** 시스템/유저 프롬프트 문자열, JSON 스키마 설명 문자열 반환
- **예시:** `get_analyzer_system_prompt() -> str`, `get_m2_schema_instruction() -> str`

### 3.6 utils/ui_helper.py

- **역할:** Streamlit용 시각화 (게이지, 신호등, 카드)
- **예시:** `render_readiness_gauge(score: int) -> None`, `render_status_badge(status: str) -> None`

---

## 4. 애플리케이션 출력 표준 — M-2 JSON 스키마

AI 분석 결과 및 대시보드가 공통으로 사용하는 JSON 구조입니다.

### 4.1 최상위 필드

| 필드명 | 타입 | 필수 | 설명 |
|--------|------|------|------|
| launch_readiness_score | number | O | 0~100 출시 준비도 |
| status | string | O | `Ready` \| `Needs Fix` \| `Blocker` |
| summary_for_user | string | O | 코치 톤 요약 (1~3문단) |
| fix_guide | array of string | O | “이렇게 바꾸면 가능하다” 대안 목록 |
| risk_breakdown | object | O | C, P, L, O 세부 점수 (아래) |
| checklist_7_steps | array of string | 권장 | 출시 전 7단계 체크리스트 |

### 4.2 risk_breakdown 객체

| 필드명 | 타입 | 설명 |
|--------|------|------|
| C | number | Copyright 유사도 (0~1) |
| P | number | Policy 위반 가능성 (0~1) |
| L | number | Legal 엄격성 (0~1) |
| O | number | Originality 차별성 (0~1) |
| RS | number | 종합 리스크 지수 (M-1 공식) |

### 4.3 JSON 예시 (요약)

```json
{
  "launch_readiness_score": 78,
  "status": "Needs Fix",
  "summary_for_user": "전반적으로 런칭 가능한 수준입니다. 다만 결제 정책 문구를 앱스토어 가이드에 맞게 한 곳만 보완하면 더 안전합니다.",
  "fix_guide": [
    "인앱 결제 안내 문구에 '구독 해지 방법' 링크를 명시하세요.",
    "개인정보 처리방침 링크를 앱 내 설정 메뉴에 노출하세요."
  ],
  "risk_breakdown": {
    "C": 0.2,
    "P": 0.4,
    "L": 0.1,
    "O": 0.7,
    "RS": 0.31
  },
  "checklist_7_steps": [
    "1. 결제 정책 문구 보완",
    "2. 개인정보처리방침 링크 노출",
    "..."
  ]
}
```

### 4.4 Status 판단 기준 (가이드)

| Status | 조건 (예시) |
|--------|-------------|
| Ready | launch_readiness_score ≥ 80, 치명적 리스크 없음 |
| Needs Fix | 50 ≤ score < 80 또는 수정 권장 항목 존재 |
| Blocker | score < 50 또는 즉시 수정 필요 항목 존재 |

※ 실제 임계치는 기획·운영 정책에 따라 조정 가능.

---

## 5. 버전 및 변경 추적

- API 명세 변경 시 본 문서의 **문서 버전**과 **기준일**을 갱신합니다.
- 외부 API 파라미터·URL은 공식 포털 개정 시 맞춰 수정합니다.
- M-2 스키마 필드 추가·삭제 시 개발명세서·analyzer/strategist 구현과 동기화합니다.

---

*문서 끝.*
