import streamlit as st
import sys
import os
import time
from typing import Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()

# Set page configuration
st.set_page_config(page_title="SafeLaunch AI - Advanced RAG", layout="wide")

# Projects path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'startup-legal-helper-main'))

# Import Advanced Components
try:
    from core.legal_rag_advanced import search_legal_context as advanced_search
    from core.solution_engine import SolutionEngine
    from core.agent_orchestrator import LegalAgentTeam
    COMPONENTS_READY = True
except ImportError as e:
    st.error(f"컴포넌트 로드 실패: {e}")
    COMPONENTS_READY = False

# Custom CSS for "Advanced" Aesthetic (Glassmorphism + Dark/Light Hybrid)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@300;400;500;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Pretendard', sans-serif;
        background-color: #fcfcfc;
    }
    
    .main-header {
        text-align: center;
        padding: 4rem 0 2rem;
        background: linear-gradient(135deg, #0b1f52 0%, #d1135c 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .card {
        background: white;
        border-radius: 24px;
        padding: 32px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.04);
        margin-bottom: 30px;
        border: 1px solid #f0f0f0;
    }
    
    .agent-card {
        border-left: 6px solid #667eea;
        background-color: #fbfbff;
    }
    
    .solution-card {
        border-left: 6px solid #10b981;
        background-color: #f0fdf4;
    }
    
    .badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 100px;
        font-size: 12px;
        font-weight: 600;
        margin-right: 8px;
    }
    
    .badge-blue { background: #e0e7ff; color: #4338ca; }
    .badge-green { background: #dcfce7; color: #15803d; }
    .badge-red { background: #fee2e2; color: #b91c1c; }

    .stButton>button {
        border-radius: 12px;
        height: 50px;
        font-weight: 700;
        transition: all 0.3s ease;
    }
</style>
""", unsafe_allow_html=True)

# App Content
st.markdown("<div class='main-header'><h1>🛡️ SafeLaunch AI v3.0 (Advanced)</h1><p>Embedding RAG + Bypass Solution + Claude Multi-Agent</p></div>", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("<h3 style='margin-bottom: 20px;'>🤖 지능형 서비스 분석 </h3>", unsafe_allow_html=True)
    
    service_description = st.text_area(
        "서비스 상세 설명",
        placeholder="예: 뉴스 기사를 AI로 무단 수집하여 유료 구독형으로 요약해주는 앱",
        height=250
    )
    
    use_agent = st.checkbox("Claude 에이전트 팀 정밀 분석 활성화", value=True)
    
    analyze_button = st.button("🚀 전체 시스템 가동", type="primary", use_container_width=True)
    
    st.markdown("---")
    st.markdown("### 🔒 보안 및 API 설정")
    
    # 보안 인식 기반 API 키 로드 (UI 입력 제거)
    # Priority: 1. Streamlit Secrets, 2. OS Environment Variables
    api_key = None
    try:
        if "ANTHROPIC_API_KEY" in st.secrets:
            api_key = st.secrets["ANTHROPIC_API_KEY"]
            os.environ["ANTHROPIC_API_KEY"] = api_key
    except Exception:
        # secrets.toml이 아예 없는 경우 에러 방지
        pass

    if not api_key and os.getenv("ANTHROPIC_API_KEY"):
        api_key = os.getenv("ANTHROPIC_API_KEY")

    if api_key:
        st.success("✅ 보안 연결 활성화 (Secrets/Env)")
    else:
        st.warning("⚠️ 에이전트 분석 비활성")
        with st.expander("보안 설정 가이드"):
            st.markdown("""
            안전한 API 키 설정을 위해 다음 중 하나를 권장합니다:
            
            1. **Streamlit Secrets (권장)**:
               `.streamlit/secrets.toml` 파일을 생성하고 아래 내용을 입력하세요:
               ```toml
               ANTHROPIC_API_KEY = "your_key_here"
               ```
            2. **OS 환경변수**:
               시스템 환경변수에 `ANTHROPIC_API_KEY`를 추가하세요.
            
            *UI에 직접 입력하는 방식은 보안을 위해 제거되었습니다.*
            """)
    
    st.markdown("---")
    st.markdown("### 🛠️ 탑재 기술")
    st.caption("• **Vector DB**: Numpy Engine (Semantic)")
    st.caption("• **Embedding**: ko-sroberta (Dense Vector)")
    st.caption("• **Orchestration**: Claude 3.5 Agent Team")
    st.caption("• **Strategy**: Pattern-based Design Around")

# Initialize Session State
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'context_text' not in st.session_state:
    st.session_state.context_text = ""
if 'analysis_done' not in st.session_state:
    st.session_state.analysis_done = False

# Initialize Engines
if COMPONENTS_READY:
    solution_engine = SolutionEngine()
    agent_team = LegalAgentTeam()

# Execution Logic
if analyze_button and service_description:
    if not COMPONENTS_READY:
        st.error("시스템 구성 요소가 로드되지 않았습니다.")
        st.stop()
        
    status_placeholder = st.empty()
    try:
        # 1. RAG Search
        status_placeholder.info("🔍 [1/3] Embedding Vector DB에서 유사 법률/판례 검색 중...")
        start_time = time.time()
        rag_results = advanced_search(service_description, top_k=5, score_threshold=0.3)
        search_duration = time.time() - start_time
        
        if not rag_results:
            st.warning("⚠️ 검색된 법률 근거가 부족합니다. 서비스 설명을 더 구체적으로 입력해 주세요.")
        
        # 2. Solution Mapping
        status_placeholder.info("💡 [2/3] 발견된 리스크에 대한 우회 전략(Bypass) 도출 중...")
        bypass_solutions = solution_engine.suggest_solutions(rag_results)
        
        # 3. Agent Report (Optional)
        agent_report = ""
        if use_agent:
            status_placeholder.info("🤖 [3/3] Claude 에이전트 팀이 협업 분석 리포트를 생성 중...")
            context_text = "\n".join([r["text"] for r in rag_results])
            st.session_state.context_text = context_text
            agent_report = agent_team.run_analysis_workflow(service_description, context_text)
            
            # Initial chat history setup
            st.session_state.chat_history = [
                {"role": "assistant", "content": f"초기 분석 리포트입니다:\n\n{agent_report}"}
            ]
        
        st.session_state.analysis_done = True
        st.session_state.rag_results = rag_results
        st.session_state.bypass_solutions = bypass_solutions
        
        status_placeholder.empty()
        st.success(f"✅ 분석 완료! (검색 소요 시간: {search_duration:.2f}초)")

    except Exception as e:
        status_placeholder.empty()
        st.error(f"❌ 분석 중 오류가 발생했습니다: {str(e)}")
        st.info("💡 팁: ANTHROPIC_API_KEY가 올바르게 설정되어 있는지 확인해 주세요.")

# Result Display
if st.session_state.analysis_done:
    col1, col2 = st.columns([1.2, 0.8])
    
    with col1:
        # Chat Interface for Multi-turn
        st.markdown("### 💬 AI 법률 코치와 대화하기")
        
        # Display chat history
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
        
        # Chat Input
        if prompt := st.chat_input("추가 질문이 있으신가요? (예: 구체적인 처벌 수위는?)"):
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
                
            with st.chat_message("assistant"):
                with st.spinner("생각 중..."):
                    # Use updated agent team method
                    response = agent_team.get_chat_response(
                        messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.chat_history],
                        context=st.session_state.context_text
                    )
                    st.markdown(response)
                    st.session_state.chat_history.append({"role": "assistant", "content": response})

        # RAG Grounding Section
        with st.expander("📖 분석 근거 확인 (Embedding Search Results)", expanded=False):
            for i, hit in enumerate(st.session_state.rag_results):
                source = hit["metadata"].get("law_name") or hit["metadata"].get("case_name") or "정책 데이터"
                score = hit["score"]
                st.markdown(f"""<div class='card' style='padding: 15px; margin-bottom: 10px;'>
                <span class='badge {"badge-red" if score > 0.7 else "badge-blue"}'>{source}</span>
                <span style='font-size: 12px; color: #888;'>유사도: {score:.2%}</span>
                <div style='font-size: 14px; color: #444; margin-top: 5px;'>{hit['text']}</div>
                </div>""", unsafe_allow_html=True)

    with col2:
        # Bypass Solution Section
        st.markdown(f"""<div class='card solution-card'>
        <h3 style='color: #15803d; margin-top: 0;'>💡 우회 전략 (Bypass)</h3>
        <ul style='padding-left: 20px; color: #333;'>
            {"".join([f"<li style='margin-bottom: 15px;'>{s}</li>" for s in st.session_state.bypass_solutions])}
        </ul>
        </div>""", unsafe_allow_html=True)

        # Tech Stats
        st.markdown(f"""<div class='card'>
        <h3 style='margin-top: 0;'>📊 시스템 상태</h3>
        <div style='font-size: 14px;'>
            <p>• <b>모드</b>: 멀티-턴 채팅 활성화</p>
            <p>• <b>엔진</b>: Numpy Vector Engine</p>
            <p>• <b>모델</b>: Claude 3.5 Sonnet</p>
        </div>
        </div>""", unsafe_allow_html=True)

elif not service_description and not st.session_state.analysis_done:
    # 초기 화면
    st.markdown("""<div style='text-align: center; padding: 100px 0;'>
    <div style='font-size: 80px; margin-bottom: 20px;'>💬</div>
    <h2>멀티-턴 질문이 가능한 AI 법률 코치</h2>
    <p style='color: #777;'>분석 결과를 바탕으로 추가 질문을 주고받으며<br>더 깊이 있는 법률 자문을 받아보세요.</p>
    </div>""", unsafe_allow_html=True)
