#!/bin/bash

echo "🛡️ SafeLaunch AI - RAG Edition 실행"
echo ""

# 가상환경 확인 (선택사항)
if [ -d "venv" ]; then
    echo "✅ 가상환경 발견"
    source venv/bin/activate
fi

# Streamlit 설치 확인
if ! command -v streamlit &> /dev/null
then
    echo "⚠️  Streamlit이 설치되지 않았습니다."
    echo "📦 설치 중..."
    pip install -r requirements_rag.txt
fi

# startup-legal-helper-main 폴더 확인
if [ ! -d "startup-legal-helper-main" ]; then
    echo "❌ startup-legal-helper-main 폴더를 찾을 수 없습니다."
    echo "💡 해결 방법:"
    echo "   1. startup-legal-helper-main.zip 파일을 프로젝트 루트에 압축 해제"
    echo "   2. 또는 GitHub에서 클론"
    exit 1
fi

# database 폴더 확인
if [ ! -d "startup-legal-helper-main/database" ]; then
    echo "❌ database 폴더를 찾을 수 없습니다."
    exit 1
fi

echo ""
echo "🌐 브라우저에서 앱을 여는 중..."
echo "📍 URL: http://localhost:8501"
echo ""
echo "⏹️  종료하려면 Ctrl+C를 누르세요"
echo ""

# Streamlit 실행
streamlit run app_rag.py
