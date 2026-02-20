# SafeLaunch AI - Advanced Legal Risk Analysis (v3.1)

SafeLaunch AI는 스타트업의 규제 리스크를 지능적으로 분석하고, 기술적 우회 전략(Bypass)을 제안하는 프리미엄 법률 RAG 시스템입니다.

## 🌟 주요 업데이트 (v3.1 Advanced)

- **Semantic Vector DB**: TF-IDF를 넘어 `ko-sroberta` 임베딩 기반의 고성능 시맨틱 검색 엔진 탑재
- **Multi-Agent Orchestration**: 법률 전문가, 기술 전략가, 리스크 분석가로 구성된 Claude 3.5 에이전트 팀의 협업 분석
- **Bypass Strategy Engine**: 리스크 패턴별 12가지 기술적 대안(Design Around) 자동 매핑
- **AI Legal Coach**: 분석 결과에 대해 실시간 질문이 가능한 멀티-턴(Multi-turn) 채팅 인터페이스
- **High Performance**: 최적화된 Numpy 엔진으로 기존 대비 검색 속도 75% 향상 (0.45s)

## 📊 데이터베이스 현항 (Total: 18,300+)

| 데이터 유형 | 수량 | 특징 |
|------------|----------|----------|
| **법률 조항** | 17,458개 | IT, 저작권, 개인정보 연관 법령 전수 |
| **IT 판례** | 712건 | 대법원 및 하급심 주요 분쟁 사례 |
| **플랫폼 정책** | 156개 | Google/App Store 가이드라인 |

## 🚀 시작하기

### 설치 및 환경 설정

1. **저장소 클론**
```bash
git clone https://github.com/s4a2z7/SafeLaunchAI.git
cd SafeLaunchAI
```

2. **패키지 설치**
```bash
pip install -r requirements_rag.txt
```

3. **API 키 설정 (선택)**
- `.streamlit/secrets.toml` 생성 후 `ANTHROPIC_API_KEY = "your_key"` 입력 (에이전트 기능용)

### 실행

```bash
# Advanced v3.1 실행 (권장)
$env:PYTHONPATH="startup-legal-helper-main"; python -m streamlit run app_rag_v3_advanced.py
```

## 📁 프로젝트 구조 (v3.1)

```
SafeLaunchAI/
├── app_rag_v3_advanced.py       # [NEW] 멀티턴 채팅 통합 대시보드
├── app_rag_clean_white.py       # [UI] KBO 스타일 화이트 테마 버전
│
├── startup-legal-helper-main/   # CORE 엔진
│   └── core/
│       ├── legal_rag_advanced.py # Numpy 기반 시맨틱 검색 엔진
│       ├── agent_orchestrator.py # Claude 멀티 에이전트 관리
│       └── solution_engine.py    # 우회 전략 매핑 엔진
│
└── startup-legal-helper-db/     # DB 및 인덱스
    └── vector_cache/            # [NEW] 임베딩 벡터 캐시
```

## 🛠️ 기술 스택

- **Backend**: Python 3.14 (Numpy Optimized)
- **AI/ML**: `jhgan/ko-sroberta-multitask`, Claude 3.5 Sonnet
- **UI**: Streamlit (Premium Aesthetic)
- **Database**: Custom Numpy Vector Store

---
**SafeLaunch AI - "Safe Tech, Safe Launch"**
