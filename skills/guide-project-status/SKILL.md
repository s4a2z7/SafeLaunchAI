---
name: guide-project-status
description: This skill should be used when the user asks "프로젝트 진행 상황", "현재 개발 상태", "무엇을 해야 하나요", "다음 단계가 뭔가요", "작업 우선순위", "프로젝트 점검", or needs guidance on SafeLaunch AI project progress and next steps.
version: 0.1.0
---

# SafeLaunch AI 프로젝트 진행 가이드

## 목적

사용자가 SafeLaunch AI 프로젝트의 현재 상태를 파악하고, 다음에 무엇을 해야 하는지 명확하게 안내받을 수 있도록 대화형으로 가이드를 제공합니다.

---

## 안내 흐름

### Phase 1: 현재 상태 파악

사용자에게 다음 질문을 통해 현재 상태를 파악합니다:

1. **역할 확인**: "어떤 역할(팀원 A/B/C)로 작업 중이신가요?"
2. **진행 단계 확인**: "현재 어느 모듈/기능을 개발 중이신가요?"
3. **이슈 확인**: "막히거나 고민되는 부분이 있으신가요?"

**상태 파악 시 확인할 파일:**
- `기획안.md` — 전체 프로젝트 정의 및 팀 역할
- `개발명세서.md` — 기능/기술/모듈 명세
- `개발일지/*.md` — 최근 작업 기록
- `core/*.py` — 구현된 코드 현황

---

### Phase 2: 목표 설정

파악된 상태에 따라 다음 가이드를 제공합니다:

| 상황 | 가이드 |
|------|--------|
| **팀원 A (Builder)** 작업 중 | → Vector DB, 스크래핑, UI 관련 `references/team-a-guide.md` 참조 |
| **팀원 B (Strategy)** 작업 중 | → AI 분석, 리스크 로직 관련 가이드 제공 |
| **팀원 C (UI/UX)** 작업 중 | → Streamlit UI, 시각화 관련 가이드 제공 |
| **전체 진행 상황 파악** 원함 | → 프로젝트 체크리스트 및 우선순위 안내 |
| **특정 기능 구현** 필요 | → 해당 모듈 명세 및 구현 가이드 제공 |

---

### Phase 3: 단계별 실행

#### Step 1: 현재 구현 상태 점검

**점검 방법:**
```bash
# 구현된 파일 확인
ls core/
```

**구현해야 할 핵심 모듈:**
- [ ] `app.py` — Streamlit 메인 대시보드
- [ ] `core/benchmarker.py` — 타겟 URL 스크래핑
- [ ] `core/legal_rag.py` — ChromaDB 검색
- [ ] `core/analyzer.py` — RS 점수 계산 및 LLM 연동
- [ ] `core/strategist.py` — 우회 전략 생성
- [ ] `utils/prompts.py` — 페르소나 프롬프트
- [ ] `utils/ui_helper.py` — 시각화 헬퍼

---

#### Step 2: 우선순위에 따른 작업 선택

**우선순위 (Must → Should → Could):**

1. **Must (필수 기능)**
   - F-1: URL 입력 및 벤치마킹
   - F-2: 리스크 분석 (RS 점수)
   - F-3: AI 사전 심사 리포트
   - F-4: 법률 RAG 검색
   - F-5: 출시 준비도 표시

2. **Should (권장 기능)**
   - F-6: 법률 데이터 동기화

3. **Could (선택 기능)**
   - F-7: 수정 예상 시간 표시
   - F-8: 유료 모델 연동

---

#### Step 3: 모듈별 구현 가이드

**각 모듈 구현 시 참조할 명세:**

| 모듈 | 참조 문서 | 핵심 포인트 |
|------|-----------|-------------|
| `benchmarker.py` | 개발명세서 4.2 | Selenium/BS4, 메타데이터 추출 |
| `legal_rag.py` | 개발명세서 4.3 | ChromaDB 쿼리, 유사도 임계치 |
| `analyzer.py` | 개발명세서 4.4 | RS 공식, M-2 JSON 형식 |
| `strategist.py` | 개발명세서 4.5 | Fix_Guide, 7단계 체크리스트 |

---

### Phase 4: 완료 확인

**기능 완료 기준:**

- [ ] 모듈이 Type Hint와 예외 처리를 포함하여 구현됨
- [ ] 개발명세서의 입출력 형식을 준수함
- [ ] `test_*.py`로 단위 테스트 통과
- [ ] 개발일지에 작업 내용 기록

**전체 프로젝트 완료 기준:**

- [ ] `streamlit run app.py`로 대시보드 실행 가능
- [ ] URL 입력 → 분석 결과 출력 전체 플로우 동작
- [ ] 응답 시간 60초 이내

---

## 자주 묻는 질문

**Q: 어떤 모듈부터 시작해야 하나요?**

A: 의존성 순서로 진행하는 것을 권장합니다:
1. `core/legal_rag.py` (Vector DB 기반)
2. `core/benchmarker.py` (데이터 수집)
3. `core/analyzer.py` (분석 로직)
4. `core/strategist.py` (리포트 생성)
5. `app.py` (UI 통합)

---

**Q: RS 점수는 어떻게 계산하나요?**

A: 공식은 다음과 같습니다:
```
RS = (C × 0.4) + (P × 0.2) + (L × 0.2) + (O × 0.2)
```
- C: 저작권 유사도 (40%)
- P: 정책 위반 가능성 (20%)
- L: 법령 엄격성 (20%)
- O: 기획 차별성 (20%)

---

**Q: 개발일지는 어떻게 작성하나요?**

A: `개발일지/YYYY-MM-DD.md` 형식으로 작성합니다. 작업 내용, 발생한 이슈, 다음 할 일을 기록하면 됩니다.

---

## 추가 리소스

### Reference Files

상세 가이드가 필요한 경우:
- **`references/project-overview.md`** — 프로젝트 전체 구조 및 현황
- **`references/module-checklist.md`** — 모듈별 구현 체크리스트

### 프로젝트 핵심 문서

- `기획안.md` — 비즈니스 모델, 팀 역할, 아키텍처
- `개발명세서.md` — 기능/기술/모듈/데이터/UI 명세
- `API명세서.md` — API 입출력 스키마
