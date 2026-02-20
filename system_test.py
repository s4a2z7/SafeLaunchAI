
import os
import sys
import time
from dotenv import load_dotenv

# Path setup
sys.path.insert(0, os.path.join(os.getcwd(), 'startup-legal-helper-main'))

from core.legal_rag_advanced import search_legal_context
from core.solution_engine import SolutionEngine
from core.agent_orchestrator import LegalAgentTeam

def test_system_flow():
    load_dotenv()
    print("=== SafeLaunch AI v3.0 System Test ===")
    
    query = "AI를 사용하여 타사 뉴스 기사를 크롤링하고 요약하여 구독 서비스로 제공하는 모델"
    print(f"\n[1] 입력 쿼리: {query}")
    
    # 1. RAG Search
    print("\n[2] RAG 검색 중 (Embedding Search)...")
    results = search_legal_context(query, top_k=3)
    for i, res in enumerate(results):
        source = res['metadata'].get('law_name') or res['metadata'].get('case_name') or "데이터"
        print(f" - 결과 {i+1} [{source}]: {res['text'][:100]}... (Score: {res['score']:.4f})")
    
    # 2. Solution Engine
    print("\n[3] 우회 전략 도출 중 (Bypass Engine)...")
    engine = SolutionEngine()
    solutions = engine.suggest_solutions(results)
    for i, sol in enumerate(solutions):
        print(f" - 솔루션 {i+1}: {sol}")
        
    # 3. Agent Analysis (If API Key exists)
    if os.getenv("ANTHROPIC_API_KEY"):
        print("\n[4] Claude 에이전트 팀 분석 중 (Multi-Agent)...")
        team = LegalAgentTeam()
        context = "\n".join([r['text'] for r in results])
        report = team.run_analysis_workflow(query, context)
        print("\n--- 최종 에이전트 리포트 ---")
        print(report[:1000] + "...")
    else:
        print("\n[4] API 키가 없어 에이전트 분석은 생략합니다.")

if __name__ == "__main__":
    test_system_flow()
