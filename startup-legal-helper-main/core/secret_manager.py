"""
SecretManager Module
API 키 및 보안 설정을 안전하게 관리하는 중앙화된 시크릿 관리 모듈.

우선순위:
1. Streamlit Secrets (.streamlit/secrets.toml) - 🏆 권장 (가장 안전)
2. OS 환경변수 (ANTHROPIC_API_KEY)
3. .env 파일 (로컬 개발용)
"""

import os
from typing import Optional


class SecretManager:
    """
    API 키와 보안 설정을 안전하게 로드·제공하는 싱글톤 클래스.
    UI 입력 방식 없이 시스템 레벨에서만 키를 관리합니다.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def get_api_key(self, key_name: str = "ANTHROPIC_API_KEY") -> Optional[str]:
        """
        지정된 API 키를 안전한 우선순위로 로드합니다.

        Returns:
            str: API 키 값, 없으면 None
        """
        # 1순위: Streamlit Secrets (배포 환경 권장)
        try:
            import streamlit as st
            if key_name in st.secrets:
                return st.secrets[key_name]
        except Exception:
            pass  # secrets.toml이 없는 경우 무시

        # 2순위: OS 환경변수 (서버 환경 또는 시스템 설정)
        value = os.getenv(key_name)
        if value:
            return value

        # 3순위: .env 파일 (로컬 개발용)
        try:
            from dotenv import load_dotenv
            load_dotenv()
            value = os.getenv(key_name)
            if value:
                return value
        except ImportError:
            pass

        return None

    def get_anthropic_key(self) -> Optional[str]:
        """Anthropic API 키를 반환합니다."""
        return self.get_api_key("ANTHROPIC_API_KEY")

    def is_api_available(self, key_name: str = "ANTHROPIC_API_KEY") -> bool:
        """API 키가 사용 가능한지 확인합니다."""
        return self.get_api_key(key_name) is not None

    def get_status_message(self) -> dict:
        """
        보안 상태 정보를 반환합니다.

        Returns:
            dict: {"has_key": bool, "source": str, "message": str}
        """
        # 소스 판별
        try:
            import streamlit as st
            if "ANTHROPIC_API_KEY" in st.secrets:
                return {
                    "has_key": True,
                    "source": "Streamlit Secrets",
                    "message": "✅ 보안 연결 활성화 (Streamlit Secrets)"
                }
        except Exception:
            pass

        if os.getenv("ANTHROPIC_API_KEY"):
            return {
                "has_key": True,
                "source": "OS Environment",
                "message": "✅ 보안 연결 활성화 (OS 환경변수)"
            }

        return {
            "has_key": False,
            "source": None,
            "message": "⚠️ API 키 미설정 (에이전트 기능 비활성)"
        }

    @staticmethod
    def print_setup_guide():
        """API 키 설정 가이드를 출력합니다."""
        guide = """
🔒 API 키 보안 설정 가이드
─────────────────────────────
1. [권장] Streamlit Secrets 사용
   - .streamlit/secrets.toml 파일을 생성 후 아래 내용 입력:
   
   [secrets]
   ANTHROPIC_API_KEY = "your_api_key_here"

2. OS 환경변수 설정 (Windows)
   - 시스템 속성 > 환경변수 > 새로 만들기
   - 변수명: ANTHROPIC_API_KEY
   - 변수값: your_api_key_here

** UI에 직접 API 키를 입력하는 방식은 보안상 권장되지 않습니다. **
─────────────────────────────
"""
        print(guide)


# 모듈 수준 싱글톤 인스턴스
secret_manager = SecretManager()
