# SafeLaunch AI 프로젝트 전체 개요

## 프로젝트 정보

- **프로젝트명:** SafeLaunch AI — 수익형 앱 저작권 및 정책 매니저
- **슬로건:** "딱딱한 법률 검사 도구가 아닌, 출시 전 함께 점검해주는 'AI 런칭 코치'"
- **타겟 사용자:** 법률 지식이 부족한 1인 개발자 및 소규모 스타트업

---

## 핵심 가치

1. **벤치마킹 URL 분석**을 통한 리스크 수치화
2. **AI 사전 심사 리포트** 제공
3. **"이렇게 바꾸면 가능하다"** 관점의 대안 제시

---

## 기술 스택

| 구분 | 기술 | 용도 |
|------|------|------|
| Frontend | Streamlit | 출시 준비 대시보드 UI |
| Data Collection | Selenium / BeautifulSoup4 | 벤치마킹 대상 페이지 스크래핑 |
| Vector DB | ChromaDB | 법령·판례·스토어 정책 임베딩 저장·검색 |
| AI Engine | Claude 3.5 Sonnet (JSON Mode) | 정형화된 분석·리포트 생성 |
| Language | Python 3.9+ | 전 모듈 공통 |

---

## 팀 구성 및 역할

### 팀원 A: 법률 데이터 아키텍트 (The Foundation)

> "정확한 법률 데이터가 곧 서비스의 신뢰도입니다."

**담당 영역:**
- 데이터 파이프라인 구축 (국가법령정보 Open API)
- Vector DB 마스터 (ChromaDB 관리)
- 데이터 무결성 책임

**담당 모듈:**
- `core/benchmarker.py`
- `core/legal_rag.py`
- `database/`

---

### 팀원 B: AI 전략 및 로직 설계자 (The Brain)

> "단순한 비평을 넘어, 규제를 뚫고 나갈 '우회 전략'을 설계합니다."

**담당 영역:**
- AI 오케스트레이션 (RAG 로직 설계)
- 리스크 엔진 개발 (RS 알고리즘)
- 페르소나 프롬프트 설계

**담당 모듈:**
- `core/analyzer.py`
- `core/strategist.py`
- `utils/prompts.py`

---

### 팀원 C: UI/UX 경험 설계자 (The Face)

> "복잡하고 무거운 법률 정보를 누구나 이해하기 쉬운 직관적 경험으로 바꿉니다."

**담당 영역:**
- 프론트엔드 개발 (Streamlit)
- 리스크 시각화 (게이지 차트, 신호등 UI)
- UX 라이팅

**담당 모듈:**
- `app.py`
- `utils/ui_helper.py`

---

## 디렉토리 구조

```
/safelaunch-ai
├── app.py                  # Streamlit 메인 진입점
├── core/
│   ├── benchmarker.py      # 타겟 URL 스크래핑
│   ├── legal_rag.py        # ChromaDB 검색·판례 추출
│   ├── analyzer.py         # RS 계산·LLM 연동
│   └── strategist.py       # 우회 전략·리포트 생성
├── database/               # ChromaDB 로컬 저장소
├── utils/
│   ├── prompts.py          # 페르소나·UX 프롬프트
│   └── ui_helper.py        # 차트·카드 시각화
├── .env                    # API Key (미커밋)
├── requirements.txt
└── docs/
    ├── 개발명세서.md
    ├── API명세서.md
    └── dev-logs/
```

---

## 리스크 판별 로직 (RS)

**공식:**
```
RS = (C × 0.4) + (P × 0.2) + (L × 0.2) + (O × 0.2)
```

| 요소 | 설명 | 가중치 |
|------|------|--------|
| C (Copyright) | 타겟과의 기능/문구 유사도 | 40% |
| P (Policy) | 스토어 정책 위반 가능성 | 20% |
| L (Legal) | 관련 법령·판례의 엄격성 | 20% |
| O (Originality) | 제안 기획의 차별성 | 20% |

---

## UX 출력 표준 (M-2)

| 필드 | 설명 |
|------|------|
| `Launch_Readiness_Score` | 출시 준비도 점수 (0~100) |
| `Status` | Ready / Needs Fix / Blocker |
| `Summary_For_User` | 코치 톤의 친근한 요약 |
| `Fix_Guide` | 대안 제시 목록 |

---

## 협업 흐름

```
팀원 A (데이터) → Vector DB 업데이트
        ↓
사용자 URL 입력 → 팀원 B (AI 분석) → 리스크 분석 + 대안 전략
        ↓
팀원 C (UI) → 대시보드에 시각화 결과 표시
```
