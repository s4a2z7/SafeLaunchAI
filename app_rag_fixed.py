"""
SafeLaunch AI - RAG 기반 완전 통합 웹서비스 (수정 버전)
프론트엔드(Streamlit) + 백엔드(RAG Engine) 통합

기존 startup-legal-helper 프로젝트의 RAG 엔진을 활용
"""

import streamlit as st
import json
import sys
import os
from datetime import datetime
import time
from typing import Dict, List, Optional

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'startup-legal-helper-main'))

# RAG 엔진 import
RAG_AVAILABLE = False
try:
    from core.legal_rag import (
        search_legal_context,
        get_or_create_collection,
        ALL_COLLECTIONS
    )
    RAG_AVAILABLE = True
except ImportError as e:
    print(f"RAG 엔진 로드 실패: {e}")
    RAG_AVAILABLE = False

# 페이지 설정
st.set_page_config(
    page_title="SafeLaunch AI - RAG Edition",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 커스텀 CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .main-header {
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    
    .rag-badge {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 0.3rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.9rem;
        display: inline-block;
        margin: 0.5rem;
    }
    
    .law-card {
        background: white;
        border-left: 4px solid #3B82F6;
        padding: 1.5rem;
        margin: 1rem 0;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    .precedent-card {
        background: white;
        border-left: 4px solid #F59E0B;
        padding: 1.5rem;
        margin: 1rem 0;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    .policy-card {
        background: white;
        border-left: 4px solid #10B981;
        padding: 1.5rem;
        margin: 1rem 0;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    .similarity-score {
        display: inline-block;
        background: #667eea;
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-size: 0.85rem;
        font-weight: 600;
    }
    
    .risk-indicator {
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        text-align: center;
        font-weight: 600;
    }
    
    .risk-high {
        background: #FEE2E2;
        color: #991B1B;
        border: 2px solid #EF4444;
    }
    
    .risk-medium {
        background: #FEF3C7;
        color: #92400E;
        border: 2px solid #F59E0B;
    }
    
    .risk-low {
        background: #D1FAE5;
        color: #065F46;
        border: 2px solid #10B981;
    }
    
    .analysis-section {
        background: #F9FAFB;
        padding: 2rem;
        border-radius: 15px;
        margin: 2rem 0;
    }
    
    .stat-box {
        background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        margin: 0.5rem;
    }
    
    .stat-number {
        font-size: 2.5rem;
        font-weight: bold;
        color: #667eea;
    }
    
    .stat-label {
        font-size: 0.9rem;
        color: #6B7280;
        margin-top: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# 세션 상태 초기화
if 'rag_initialized' not in st.session_state:
    st.session_state.rag_initialized = False
if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = None
if 'search_history' not in st.session_state:
    st.session_state.search_history = []

# RAG 초기화 (수정된 버전)
@st.cache_resource
def init_rag_system():
    """RAG 시스템 초기화 및 통계 반환"""
    if not RAG_AVAILABLE:
        return None, "RAG 엔진을 사용할 수 없습니다."
    
    try:
        # 컬렉션 통계 가져오기
        stats = {}
        for collection_name in ALL_COLLECTIONS:
            try:
                collection = get_or_create_collection(collection_name)
                stats[collection_name] = collection.count()
            except Exception as e:
                stats[collection_name] = 0
        
        return stats, None
    except Exception as e:
        return None, f"RAG 초기화 실패: {str(e)}"

# 리스크 분석 함수
def analyze_service_risk(
    service_description: str,
    service_type: str,
    top_k: int = 5
) -> Dict:
    """RAG 기반 서비스 리스크 분석"""
    
    try:
        # RAG 검색 실행 (수정된 함수 사용)
        search_results = search_legal_context(
            query=service_description,
            top_k=top_k,
            score_threshold=0.0  # 모든 결과 표시
        )
        
        # 결과 구조 변환
        formatted_results = {
            "laws": [],
            "precedents": [],
            "policies": []
        }
        
        if search_results:
            for result in search_results:
                source_type = result.get("metadata", {}).get("source_type", "unknown")
                
                formatted_item = {
                    "text": result.get("text", ""),
                    "metadata": result.get("metadata", {}),
                    "similarity": result.get("score", 0.0)
                }
                
                if source_type == "law":
                    formatted_results["laws"].append(formatted_item)
                elif source_type == "precedent":
                    formatted_results["precedents"].append(formatted_item)
                elif source_type == "policy":
                    formatted_results["policies"].append(formatted_item)
        
        # 리스크 점수 계산
        risk_score = calculate_risk_score(formatted_results, service_description)
        
        # 결과 구조화
        analysis = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "query": service_description,
            "service_type": service_type,
            "risk_score": risk_score,
            "risk_level": get_risk_level(risk_score),
            "search_results": formatted_results,
            "recommendations": generate_recommendations(formatted_results, risk_score)
        }
        
        return analysis
        
    except Exception as e:
        st.error(f"분석 중 오류 발생: {str(e)}")
        import traceback
        st.code(traceback.format_exc())
        return None

def calculate_risk_score(search_results: Dict, query: str) -> float:
    """검색 결과 기반 리스크 점수 계산 (0-100)"""
    
    laws = search_results.get("laws", [])
    precedents = search_results.get("precedents", [])
    policies = search_results.get("policies", [])
    
    # 가중치
    law_weight = 0.4
    precedent_weight = 0.4
    policy_weight = 0.2
    
    # 각 카테고리별 평균 유사도
    law_avg = sum([doc.get("similarity", 0) for doc in laws]) / len(laws) if laws else 0
    prec_avg = sum([doc.get("similarity", 0) for doc in precedents]) / len(precedents) if precedents else 0
    policy_avg = sum([doc.get("similarity", 0) for doc in policies]) / len(policies) if policies else 0
    
    # 리스크 점수 (유사도가 높을수록 리스크 높음)
    risk_score = (law_avg * law_weight + prec_avg * precedent_weight + policy_avg * policy_weight) * 100
    
    return round(risk_score, 1)

def get_risk_level(risk_score: float) -> str:
    """리스크 점수를 등급으로 변환"""
    if risk_score >= 70:
        return "높음"
    elif risk_score >= 40:
        return "중간"
    else:
        return "낮음"

def generate_recommendations(search_results: Dict, risk_score: float) -> List[Dict]:
    """검색 결과 기반 권장사항 생성"""
    
    recommendations = []
    
    # 법률 관련 권장사항
    laws = search_results.get("laws", [])
    if laws and len(laws) > 0:
        top_law = laws[0]
        recommendations.append({
            "category": "법률 준수",
            "priority": "높음" if risk_score >= 70 else "중간",
            "action": f"{top_law['metadata'].get('law_name', '관련 법률')} 검토 필요",
            "detail": "상위 유사 법조문과의 충돌 가능성을 검토하고, 필요시 법률 자문을 받으세요."
        })
    
    # 판례 관련 권장사항
    precedents = search_results.get("precedents", [])
    if precedents and len(precedents) > 0:
        recommendations.append({
            "category": "판례 분석",
            "priority": "높음",
            "action": "유사 분쟁 사례 검토",
            "detail": f"{len(precedents)}건의 유사 판례가 발견되었습니다. 과거 분쟁 패턴을 분석하세요."
        })
    
    # 스토어 정책 관련 권장사항
    policies = search_results.get("policies", [])
    if policies and len(policies) > 0:
        recommendations.append({
            "category": "스토어 정책",
            "priority": "중간",
            "action": "플랫폼 가이드라인 확인",
            "detail": "Google Play 및 App Store 정책을 사전에 검토하여 리젝을 방지하세요."
        })
    
    # 리스크 레벨별 기본 권장사항
    if risk_score >= 70:
        recommendations.insert(0, {
            "category": "긴급 조치",
            "priority": "긴급",
            "action": "즉시 전문가 상담 필요",
            "detail": "법적 리스크가 매우 높습니다. 출시 전 반드시 IT 전문 변호사와 상담하세요."
        })
    
    return recommendations

# ============ UI 렌더링 ============

# 헤더
st.markdown('<div class="main-header">🛡️ SafeLaunch AI - RAG Edition</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    st.markdown('<div class="rag-badge">📚 실제 법률 DB</div>', unsafe_allow_html=True)
with col2:
    st.markdown('<div class="rag-badge">🔍 벡터 검색</div>', unsafe_allow_html=True)
with col3:
    st.markdown('<div class="rag-badge">⚡ 실시간 분석</div>', unsafe_allow_html=True)

st.markdown("---")

# RAG 시스템 상태 확인
if not st.session_state.rag_initialized:
    with st.spinner("🔄 RAG 시스템 초기화 중..."):
        stats, error = init_rag_system()
        
        if error:
            st.error(f"⚠️ {error}")
            st.info("💡 데모 모드로 실행됩니다. 실제 RAG 기능은 사용할 수 없습니다.")
            stats = None
        else:
            st.session_state.rag_initialized = True
            st.success("✅ RAG 시스템 초기화 완료!")
        
        # 통계 표시
        if stats:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown(f"""
                <div class="stat-box">
                    <div class="stat-number">{stats.get('laws', 0):,}</div>
                    <div class="stat-label">법률 조항</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="stat-box">
                    <div class="stat-number">{stats.get('precedents', 0):,}</div>
                    <div class="stat-label">판례</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div class="stat-box">
                    <div class="stat-number">{stats.get('store_policies', 0):,}</div>
                    <div class="stat-label">스토어 정책</div>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("---")

# 사이드바
with st.sidebar:
    st.header("🔍 서비스 분석")
    
    service_type = st.selectbox(
        "서비스 유형",
        [
            "뉴스/미디어",
            "전자상거래",
            "콘텐츠 큐레이션",
            "소셜 네트워크",
            "게임",
            "헬스케어",
            "핀테크",
            "교육",
            "기타"
        ]
    )
    
    service_description = st.text_area(
        "서비스 설명",
        placeholder="예: AI가 여러 뉴스를 종합해 3줄 요약하고, 찬반 의견을 정리해주는 앱",
        height=150,
        help="구체적으로 작성할수록 정확한 분석이 가능합니다"
    )
    
    top_k = st.slider(
        "검색 결과 수",
        min_value=3,
        max_value=10,
        value=5,
        help="검색할 문서 개수 (많을수록 정확하지만 느림)"
    )
    
    st.markdown("---")
    
    analyze_button = st.button(
        "🛡️ 리스크 분석 시작",
        type="primary",
        use_container_width=True,
        disabled=not RAG_AVAILABLE
    )
    
    if analyze_button and service_description:
        with st.spinner("🔍 RAG 검색 및 분석 중..."):
            progress = st.progress(0)
            
            # 진행률 시뮬레이션
            for i in range(100):
                time.sleep(0.01)
                progress.progress(i + 1)
            
            # 실제 분석 실행
            result = analyze_service_risk(service_description, service_type, top_k)
            
            if result:
                st.session_state.analysis_result = result
                st.session_state.search_history.append({
                    "timestamp": result["timestamp"],
                    "query": service_description[:50] + "...",
                    "risk_level": result["risk_level"]
                })
                st.success("✅ 분석 완료!")
                time.sleep(0.5)
                st.rerun()
    
    if not service_description and analyze_button:
        st.error("서비스 설명을 입력해주세요!")
    
    # 검색 히스토리
    if st.session_state.search_history:
        st.markdown("---")
        st.markdown("### 📜 검색 기록")
        
        for idx, item in enumerate(reversed(st.session_state.search_history[-5:])):
            risk_emoji = "🔴" if item["risk_level"] == "높음" else "🟡" if item["risk_level"] == "중간" else "🟢"
            st.caption(f"{risk_emoji} {item['timestamp']}")
            st.caption(f"   {item['query']}")
    
    st.markdown("---")
    st.markdown("### 💡 RAG Edition")
    st.caption("""
    - ✅ 실제 법률 DB 연동
    - ✅ TF-IDF 벡터 검색
    - ✅ 판례 유사도 매칭
    - ✅ 실시간 리스크 계산
    """)

# 메인 콘텐츠
if st.session_state.analysis_result:
    result = st.session_state.analysis_result
    
    # 종합 리스크 점수
    st.markdown("## 📊 종합 분석 결과")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        risk_level = result["risk_level"]
        risk_class = "risk-high" if risk_level == "높음" else "risk-medium" if risk_level == "중간" else "risk-low"
        
        st.markdown(f"""
        <div class="risk-indicator {risk_class}">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">
                {"🔴" if risk_level == "높음" else "🟡" if risk_level == "중간" else "🟢"}
            </div>
            <div style="font-size: 1.5rem;">리스크 등급: {risk_level}</div>
            <div style="font-size: 2.5rem; font-weight: bold; margin-top: 0.5rem;">
                {result["risk_score"]}점
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.metric("서비스 유형", result["service_type"])
        st.metric("분석 시각", result["timestamp"])
    
    with col3:
        search_results = result["search_results"]
        total_results = (
            len(search_results.get("laws", [])) +
            len(search_results.get("precedents", [])) +
            len(search_results.get("policies", []))
        )
        st.metric("검색된 문서", f"{total_results}건")
    
    st.markdown("---")
    
    # 탭 구성
    tab1, tab2, tab3, tab4 = st.tabs([
        "📚 법률 조항",
        "⚖️ 판례",
        "🏪 스토어 정책",
        "💡 권장사항"
    ])
    
    # 탭 1: 법률 조항
    with tab1:
        st.markdown("### 📚 관련 법률 조항 (유사도 순)")
        
        laws = search_results.get("laws", [])
        
        if laws:
            for idx, law in enumerate(laws, 1):
                similarity = law.get("similarity", 0)
                metadata = law.get("metadata", {})
                text = law.get("text", "")
                
                st.markdown(f"""
                <div class="law-card">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                        <h4 style="margin: 0;">#{idx} {metadata.get('law_name', '법률명 불명')}</h4>
                        <span class="similarity-score">유사도: {similarity:.1%}</span>
                    </div>
                    <p style="color: #6B7280; font-size: 0.9rem; margin-bottom: 0.5rem;">
                        공포일: {metadata.get('proclamation_date', 'N/A')} | 
                        시행일: {metadata.get('enforcement_date', 'N/A')}
                    </p>
                    <div style="background: #F9FAFB; padding: 1rem; border-radius: 8px; margin-top: 1rem;">
                        <p style="margin: 0; line-height: 1.6;">{text[:500]}{"..." if len(text) > 500 else ""}</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("💡 관련 법률 조항이 검색되지 않았습니다. 더 구체적인 키워드로 검색해보세요.")
    
    # 탭 2: 판례
    with tab2:
        st.markdown("### ⚖️ 유사 판례 (유사도 순)")
        
        precedents = search_results.get("precedents", [])
        
        if precedents:
            for idx, prec in enumerate(precedents, 1):
                similarity = prec.get("similarity", 0)
                metadata = prec.get("metadata", {})
                text = prec.get("text", "")
                
                st.markdown(f"""
                <div class="precedent-card">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                        <h4 style="margin: 0;">#{idx} {metadata.get('case_number', '사건번호 불명')}</h4>
                        <span class="similarity-score">유사도: {similarity:.1%}</span>
                    </div>
                    <p style="color: #6B7280; font-size: 0.9rem; margin-bottom: 0.5rem;">
                        법원: {metadata.get('court', 'N/A')} | 
                        선고일: {metadata.get('judgment_date', 'N/A')}
                    </p>
                    <div style="background: #FFFBEB; padding: 1rem; border-radius: 8px; margin-top: 1rem;">
                        <p style="margin: 0; line-height: 1.6;">{text[:500]}{"..." if len(text) > 500 else ""}</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("💡 관련 판례가 검색되지 않았습니다.")
    
    # 탭 3: 스토어 정책
    with tab3:
        st.markdown("### 🏪 스토어 정책 (유사도 순)")
        
        policies = search_results.get("policies", [])
        
        if policies:
            for idx, policy in enumerate(policies, 1):
                similarity = policy.get("similarity", 0)
                metadata = policy.get("metadata", {})
                text = policy.get("text", "")
                
                st.markdown(f"""
                <div class="policy-card">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                        <h4 style="margin: 0;">#{idx} {metadata.get('platform', '플랫폼 불명')} 정책</h4>
                        <span class="similarity-score">유사도: {similarity:.1%}</span>
                    </div>
                    <p style="color: #6B7280; font-size: 0.9rem; margin-bottom: 0.5rem;">
                        카테고리: {metadata.get('category', 'N/A')}
                    </p>
                    <div style="background: #ECFDF5; padding: 1rem; border-radius: 8px; margin-top: 1rem;">
                        <p style="margin: 0; line-height: 1.6;">{text[:500]}{"..." if len(text) > 500 else ""}</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("💡 관련 스토어 정책이 검색되지 않았습니다.")
    
    # 탭 4: 권장사항
    with tab4:
        st.markdown("### 💡 권장 조치사항")
        
        recommendations = result.get("recommendations", [])
        
        if recommendations:
            for idx, rec in enumerate(recommendations, 1):
                priority = rec["priority"]
                priority_color = "#EF4444" if priority == "긴급" else "#F59E0B" if priority == "높음" else "#10B981"
                
                st.markdown(f"""
                <div style="background: white; border-left: 4px solid {priority_color}; padding: 1.5rem; margin: 1rem 0; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                        <h4 style="margin: 0; color: #1F2937;">{rec['category']}</h4>
                        <span style="background: {priority_color}; color: white; padding: 0.3rem 0.8rem; border-radius: 15px; font-size: 0.85rem; font-weight: 600;">
                            {priority}
                        </span>
                    </div>
                    <p style="font-weight: 600; color: #374151; margin: 0.5rem 0;">✓ {rec['action']}</p>
                    <p style="color: #6B7280; margin: 0.5rem 0; line-height: 1.6;">{rec['detail']}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("권장사항을 생성할 수 없습니다.")
    
    # 액션 버튼
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # JSON 다운로드
        result_json = json.dumps(result, ensure_ascii=False, indent=2)
        st.download_button(
            label="📥 분석 결과 다운로드 (JSON)",
            data=result_json,
            file_name=f"safelaunch_analysis_{result['timestamp'].replace(':', '-').replace(' ', '_')}.json",
            mime="application/json",
            use_container_width=True
        )
    
    with col2:
        if st.button("📧 결과 공유", use_container_width=True):
            st.info("이메일 공유 기능은 향후 추가 예정입니다.")
    
    with col3:
        if st.button("🔄 새로운 분석", use_container_width=True):
            st.session_state.analysis_result = None
            st.rerun()

else:
    # 초기 화면
    st.markdown("### 👋 SafeLaunch AI RAG Edition에 오신 것을 환영합니다!")
    
    st.markdown("""
<div class="analysis-section">
    <h3>🎯 이 서비스는 무엇을 하나요?</h3>
    <p>실제 법률 데이터베이스를 기반으로 귀하의 서비스가 가진 법적 리스크를 분석합니다.</p>
    
    <h4 style="margin-top: 2rem;">📚 데이터 소스</h4>
    <ul>
        <li><strong>법률 조항</strong>: 저작권법, 개인정보보호법, 정보통신망법 등</li>
        <li><strong>판례</strong>: 과거 IT 서비스 관련 분쟁 사례</li>
        <li><strong>스토어 정책</strong>: Google Play, App Store 가이드라인</li>
    </ul>
    
    <h4 style="margin-top: 2rem;">🔍 분석 방법</h4>
    <ol>
        <li><strong>벡터 검색</strong>: TF-IDF 기반 유사도 계산</li>
        <li><strong>리스크 평가</strong>: 검색 결과 기반 점수 산정</li>
        <li><strong>권장사항 생성</strong>: 실행 가능한 조치 제시</li>
    </ol>
</div>
""", unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("### 📝 사용 예시")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **🎬 뉴스 요약 앱**
        
        "AI가 여러 뉴스 기사를 분석해 핵심 쟁점을 3줄로 요약하고, 
        찬반 의견을 정리해주는 앱"
        
        → 저작권법, 판례 검색
        → 리스크 평가 및 대안 제시
        """)
    
    with col2:
        st.markdown("""
        **🎮 게임 앱**
        
        "사용자가 업로드한 사진을 AI가 분석해 캐릭터를 생성하고, 
        다른 유저와 대전할 수 있는 게임"
        
        → 개인정보보호법, 스토어 정책 검색
        → 생체정보 처리 가이드 제공
        """)
    
    st.markdown("---")
    st.info("👈 왼쪽 사이드바에서 **서비스 설명**을 입력하고 **리스크 분석**을 시작하세요!")

# 푸터
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #6B7280; padding: 2rem;">
    <p style="font-size: 1.3rem; font-weight: 600;">🛡️ SafeLaunch AI - RAG Edition</p>
    <p style="font-size: 1rem; margin: 0.5rem 0;">실제 법률 DB 기반 리스크 분석</p>
    <p style="font-size: 0.85rem; margin-top: 1rem; color: #9CA3AF;">
        본 서비스는 사전 검토 도구입니다. 중요한 법률 결정은 반드시 전문 변호사와 상담하세요.
    </p>
</div>
""", unsafe_allow_html=True)
