"""
SafeLaunch AI - Agent Orchestrator
startup-legal-helper-main/core/agent_orchestrator.py

이 모듈은 Claude를 기반으로 세 명의 전문 에이전트(법률, 기술전략, 리스크분석)가 
협업하여 리스크를 분석하고 제보하는 Multi-Agent 워크플로우를 담당합니다.
"""

import os
from typing import List, Dict, Any
import anthropic
from core.secret_manager import secret_manager

class LegalAgentTeam:
    """
    Claude Multi-Agent 팀 관리 클래스
    """
    def __init__(self):
        # SecretManager를 통한 안전한 키 로드
        api_key = secret_manager.get_anthropic_key()
        if not api_key:
            print("[LegalAgentTeam] Warning: ANTHROPIC_API_KEY가 설정되지 않았습니다.")
            secret_manager.print_setup_guide()
            self.client = None
        else:
            self.client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-3-5-sonnet-latest"

    def run_analysis_workflow(self, service_description: str, rag_context: str) -> str:
        """
        1. 법률 전문가 분석 -> 2. 기술 전략가 우회 제안 -> 3. 리스크 분석가 종합 리포트
        """
        # Phase 1: Legal Researcher Analysis
        legal_prompt = f"당신은 상업 법률 전문가입니다. 다음 서비스 설명과 검색된 법률/판례 근거를 바탕으로 핵심 리스크 3가지를 도출하십시오.\n\n[서비스 설명]\n{service_description}\n\n[검색된 법률 근거]\n{rag_context}"
        legal_analysis = self._call_claude([{"role": "user", "content": legal_prompt}])
        
        # Phase 2: Technical Strategist Bypass Solution
        tech_prompt = f"당신은 기술 전략가입니다. 다음 리스크를 기술적으로 우회할 솔루션을 제안하십시오.\n\n[리스크]\n{legal_analysis}"
        tech_solutions = self._call_claude([{"role": "user", "content": tech_prompt}])
        
        # Phase 3: Final Synthesis
        summary_prompt = f"수석 리스크 분석가로서 다음 법률 분석과 기술 솔루션을 종합하여 최종 '출시 전략 리포트'를 작성하십시오.\n\n[법률]\n{legal_analysis}\n\n[기술]\n{tech_solutions}"
        final_report = self._call_claude([{"role": "user", "content": summary_prompt}])
        
        return final_report

    def get_chat_response(self, messages: List[Dict], context: str) -> str:
        """
        연속 질문 처리를 위한 멀티 턴 응답 생성
        """
        if not self.client:
            return "API 키가 설정되지 않았습니다. 사이드바의 안내를 확인해 주세요."
            
        system_prompt = f"당신은 SafeLaunch AI의 상담 전문가입니다. 다음 법률/판례 맥락을 바탕으로 사용자의 질문에 답변하십시오.\n\n[맥락]\n{context}"
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                system=system_prompt,
                messages=messages
            )
            return response.content[0].text
        except Exception as e:
            return f"응답 생성 중 오류가 발생했습니다: {str(e)}"

    def _call_claude(self, messages: List[Dict]) -> str:
        if not self.client:
            return "API 키가 설정되지 않아 에이전트 분석을 수행할 수 없습니다."
            
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                messages=messages
            )
            return message.content[0].text
        except Exception as e:
            return f"에러 발생: {str(e)}"

if __name__ == "__main__":
    # 간단한 테스트 실행
    team = LegalAgentTeam()
    sample_desc = "AI를 사용하여 뉴스 기사를 요약하고 구독형으로 제공하는 서비스"
    sample_context = "저작권법 제103조: 복제 및 전송의 중단 요청권..."
    
    # API 키가 있을 때만 실행 권장
    if os.getenv("ANTHROPIC_API_KEY"):
        report = team.run_analysis_workflow(sample_desc, sample_context)
        print(report)
    else:
        print("ANTHROPIC_API_KEY 환경변수가 설정되지 않았습니다.")
