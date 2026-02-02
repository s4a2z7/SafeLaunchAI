# SafeLaunch AI - Legal Risk Analysis System

스타트업을 위한 AI 기반 법률 리스크 분석 시스템입니다. RAG(Retrieval-Augmented Generation) 기술을 활용하여 실제 법률 데이터베이스를 기반으로 서비스의 법적 리스크를 분석합니다.

## 🎯 주요 기능

- **법률 조항 검색**: 저작권법, 개인정보보호법, 정보통신망법 등 1,458개 법률 조항
- **판례 검색**: IT 서비스 관련 분쟁 사례 712건
- **스토어 정책**: Google Play, App Store 가이드라인 36개
- **리스크 분석**: TF-IDF 기반 벡터 검색으로 관련 법률 자동 검색
- **리스크 점수**: 검색 결과 기반 자동 점수 산정
- **권장사항 생성**: 실행 가능한 조치 제시

## 📊 데이터베이스 현황

| 데이터 유형 | 파일 크기 | 데이터 수 |
|------------|----------|----------|
| 법률 조항 | 2.51 MB | 1,458개 |
| 판례 | 2.08 MB | 712개 |
| 스토어 정책 | 0.05 MB | 36개 |
| **총합** | **4.64 MB** | **2,206개** |

## 🚀 시작하기

### 필수 요구사항

- Python 3.8 이상
- pip

### 설치

1. 저장소 클론
```bash
git clone https://github.com/YOUR_USERNAME/SafeLaunchAI.git
cd SafeLaunchAI
```

2. 가상환경 생성 및 활성화 (선택사항)
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

3. 필요한 패키지 설치
```bash
pip install -r requirements_rag.txt
```

### 실행

```bash
streamlit run app_rag_v2.py
```

브라우저에서 `http://localhost:8501`로 접속하세요.

## 📁 프로젝트 구조

```
SafeLaunchAI/
├── app_rag_v2.py                    # Streamlit 메인 앱
├── requirements_rag.txt             # 패키지 의존성
├── README.md                        # 이 파일
├── README_RAG.md                    # 상세 기술 문서
│
├── startup-legal-helper-main/       # RAG 백엔드
│   └── core/
│       ├── legal_rag.py            # RAG 엔진
│       ├── law_api.py              # 법제처 API 래퍼
│       └── store_policy_data.py    # 스토어 정책 데이터
│
└── startup-legal-helper-db/         # 데이터베이스
    └── startup-legal-helper-db_deisgner/
        └── database/
            ├── laws.json           # 법률 조항 (1,458개)
            ├── precedents.json     # 판례 (712건)
            └── store_policies.json # 스토어 정책 (36개)
```

## 🔍 사용 방법

1. **서비스 설명 입력**: 분석하고자 하는 서비스의 설명을 입력합니다.
2. **분석 실행**: "분석 시작" 버튼을 클릭합니다.
3. **결과 확인**: 
   - 리스크 점수 (0-100)
   - 관련 법률 조항
   - 관련 판례
   - 스토어 정책
   - 권장사항

## 🛠️ 기술 스택

- **Frontend**: Streamlit
- **Backend**: Python
- **RAG Engine**: TF-IDF + Cosine Similarity
- **Data Source**: 국가법령정보센터 Open API

## 📝 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다.

## 🤝 기여

기여를 환영합니다! Pull Request를 보내주세요.

## 📧 문의

문제가 있거나 질문이 있으시면 Issue를 생성해주세요.
