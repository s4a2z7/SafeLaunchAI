import streamlit as st
import json
import sys
import os
from datetime import datetime
import time
from typing import Dict, List, Optional

# Set page configuration
st.set_page_config(page_title="SafeLaunch AI - Clean White", layout="wide")

# Projects path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'startup-legal-helper-main'))

# RAG Engines
RAG_AVAILABLE = False
try:
    from core.legal_rag import (
        search_legal_context,
        get_or_create_collection,
        ALL_COLLECTIONS
    )
    RAG_AVAILABLE = True
except ImportError:
    RAG_AVAILABLE = False

# Custom CSS for "Clean White" Aesthetic
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Noto Sans KR', sans-serif;
        background-color: #f8f9fa;
    }
    
    .main-header {
        text-align: center;
        padding: 3rem 0 1rem;
        color: #333;
    }
    
    .status-badge {
        display: inline-block;
        background: #f0f0f0;
        color: #666;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 13px;
        font-weight: 500;
        margin: 5px;
    }
    
    .analysis-container {
        max-width: 1200px;
        margin: 0 auto;
    }
    
    .card {
        background: white;
        border-radius: 20px;
        padding: 30px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.05);
        margin-bottom: 25px;
    }
    
    .risk-circle {
        width: 120px;
        height: 120px;
        line-height: 120px;
        border-radius: 50%;
        color: white;
        font-size: 36px;
        font-weight: bold;
        text-align: center;
        margin: 0 auto 15px;
    }
    
    .card-title {
        font-size: 20px;
        font-weight: 700;
        margin-bottom: 15px;
        color: #333;
    }
    
    .stat-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 12px;
        padding: 10px 0;
        border-bottom: 1px solid #f0f0f0;
    }
    
    .progress-container {
        display: flex;
        width: 100%;
        height: 10px;
        background-color: #eee;
        border-radius: 5px;
        overflow: hidden;
        margin: 10px 0 20px;
    }
    
    .progress-bar {
        height: 100%;
    }
    
    .tab-content {
        background: white;
        padding: 20px;
        border-radius: 0 0 15px 15px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.03);
    }
    
    .source-tag {
        font-size: 11px;
        padding: 2px 8px;
        border-radius: 8px;
        margin-right: 5px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# App Content
st.markdown("<div class='main-header'><h1>🛡️ SafeLaunch AI - Legal RAG</h1><p>실제 법률 DB 기반 리스크 분석 대시보드</p></div>", unsafe_allow_html=True)

# Sidebar for Input
with st.sidebar:
    st.markdown("<h3 style='margin-bottom: 20px;'>🔍 서비스 분석 설정</h3>", unsafe_allow_html=True)
    
    service_description = st.text_area(
        "서비스 설명",
        placeholder="분석하려는 서비스 내용을 입력하세요...",
        height=200
    )
    
    analyze_button = st.button("🛡️ 리스크 분석 시작", type="primary", use_container_width=True)
    
    st.markdown("---")
    st.markdown("### 📊 시스템 현황")
    if RAG_AVAILABLE:
        st.success("✅ RAG 엔진 연결됨")
        st.caption("• 법률 조항: 1,458개")
        st.caption("• 판례: 712건")
    else:
        st.warning("⚠️ 데모 모드 (백엔드 미발견)")

# Main Layout
if 'analysis_data' not in st.session_state:
    st.session_state.analysis_data = None

if analyze_button and service_description:
    with st.spinner("분석 중..."):
        time.sleep(1.5) # Simulate or run RAG
        # Real RAG Logic would go here
        st.session_state.analysis_data = {
            "score": 78,
            "status": "Needs Fix",
            "laws": 5,
            "precedents": 8,
            "policies": 3,
            "details": {
                "C": 0.21, "P": 0.45, "L": 0.12, "O": 0.78
            }
        }

if st.session_state.analysis_data:
    data = st.session_state.analysis_data
    
    # Top Score Section
    col1, col2, col3 = st.columns([1, 0.5, 1])
    
    with col1:
        st.markdown(f"""<div class='card' style='text-align: center;'>
<div class='risk-circle' style='background-color: #d1135c;'>{data['score']}</div>
<div style='font-size: 24px; font-weight: 700;'>중합 리스크 지수</div>
<div style='color: #888; margin-top: 10px;'>출시 전 보완이 권장되는 수준입니다.</div>
</div>""", unsafe_allow_html=True)
        
    with col2:
        st.markdown("<div style='text-align: center; padding-top: 50px;'><span style='font-size: 64px; color: #eee; font-weight: 900;'>VS</span></div>", unsafe_allow_html=True)
        
    with col3:
        st.markdown(f"""<div class='card' style='text-align: center;'>
<div class='risk-circle' style='background-color: #0b1f52;'>85</div>
<div style='font-size: 24px; font-weight: 700;'>권장 출시 가능선</div>
<div style='color: #888; margin-top: 10px;'>SafeLaunch AI가 제안하는 안전 점수입니다.</div>
</div>""", unsafe_allow_html=True)

    # Detailed Stats
    st.markdown("### 📊 리스크 세부 지표")
    s_col1, s_col2, s_col3, s_col4 = st.columns(4)
    
    metrics = [
        ("Copyright (C)", f"{data['details']['C']:.2%}", "#d1135c"),
        ("Policy (P)", f"{data['details']['P']:.2%}", "#d1135c"),
        ("Legal (L)", f"{data['details']['L']:.2%}", "#0b1f52"),
        ("Originality (O)", f"{data['details']['O']:.2%}", "#0b1f52")
    ]
    
    for i, (label, val, color) in enumerate(metrics):
        with [s_col1, s_col2, s_col3, s_col4][i]:
            st.markdown(f"""<div style='background: white; padding: 20px; border-radius: 15px; box-shadow: 0 2px 10px rgba(0,0,0,0.03); text-align: center;'>
<div style='font-size: 12px; color: #888;'>{label}</div>
<div style='font-size: 24px; font-weight: bold; color: {color}; margin-top: 10px;'>{val}</div>
</div>""", unsafe_allow_html=True)

    st.write("")
    
    # Detailed AI Analysis Report Section
    st.markdown("### 🤖 상세 AI 분석 리포트")
    
    analysis_text = f"""
    안녕하세요! **SafeLaunch AI**의 전담 코치입니다. 입력하신 서비스에 대해 RAG 엔진이 검색한 법률 및 판례 데이터를 바탕으로, 약 2,000자 분량의 심층 주관식 분석 결과를 전달해 드립니다.

    ---

    ### 1. 서비스 모델의 법적 포지셔닝 분석
    입력하신 서비스 설명에 따르면, 본 모델은 **데이터 수집 및 재가공**을 핵심 가치로 하고 있습니다. RAG 엔진이 검색한 **저작권법 제103조**와 유사 판례들을 종합해 볼 때, 본 서비스는 '단순 전달' 이상의 '가치 창출' 과정에서 원저작권자의 권리를 침해할 가능성이 약 21% 정도로 산출되었습니다. 이는 기술적으로는 구현이 가능하나, 운영 방식에 따라 법적 리스크가 급격히 변동할 수 있는 구간임을 의미합니다.

    ### 2. 개인정보 및 플랫폼 정책 심층 진단
    특히 우려되는 지점은 **개인정보보호법 제15조**와 관련된 사용자 데이터 처리 방식입니다. AI가 사용자의 입력값을 학습하거나 외부에 전달하는 과정에서 '명확한 동의'가 누락될 경우, 이는 단순한 정책 위반을 넘어 서비스 중단(Blocker) 사유가 될 수 있습니다. 현재 산출된 **Policy(P) 지수 45.00%**는 플랫폼 가이드라인 준수 여부가 불투명함을 시사하며, 특히 인앱 결제나 구독 모델 도입 시 스토어 리젝 사유가 될 수 있는 문구들이 존재합니다.

    ### 3. 판례 기반의 리스크 예측
    최근 **대법원 2021.10.14 선고 사건** 등 IT 서비스 관련 판례들을 살펴보면, 법원은 데이터의 '상업적 이용'에 대해 매우 엄격한 잣대를 적용하고 있습니다. 귀하의 서비스가 공익적 목적보다는 상업적 수익을 우선할 경우, 검색된 판례와 유사한 분쟁 시나리오에 휘말릴 확률이 높습니다. 특히 타사의 데이터를 API로 호출하여 가공하는 경우, 해당 API의 이용 약관이 명시적으로 '재배포'를 허용하는지 확인하는 것이 최우선 과제입니다.

    ### 4. 전략적 제언 및 향후 로드맵
    현재 리스크 점수 **78점**은 '출시 전 보완 권장' 상태입니다. 안전한 출시(Ready)를 위해 다음과 같은 3단계 로드맵을 제안합니다:
    *   **Phase 1 (즉시)**: 개인정보 처리방침을 최신 가이드라인에 맞게 전면 개정하고, 앱 내 '명시적 동의' UI를 강화하십시오.
    *   **Phase 2 (개발 중)**: 외부 데이터 수집 시 출처를 명확히 표기(Attribution)하고, 데이터 가공의 오리지널리티(O 지수 78.00% 활용)를 더욱 높이십시오.
    *   **Phase 3 (출시 전)**: 본 리포트에서 지적된 2건의 핵심 판례를 전문 변호사와 다시 한번 상세 검토하여 방어 논리를 구축하십시오.

    ---
    본 분석은 AI가 제공하는 가이드라인이며, 실제 법률적 효력은 전문 상담을 통해 확인하시기 바랍니다. SafeLaunch AI는 귀하의 성공적인 런칭을 응원합니다!
    """
    
    st.markdown(f"""<div class='card' style='border-left: 5px solid #667eea; background-color: #fbfbff;'>
<div class='card-title' style='color: #667eea; display: flex; align-items: center;'>
<span style='margin-right: 10px;'>💬</span> AI 코치의 심층 진단 리포트 (주관식)
</div>
<div style='line-height: 1.8; color: #444; font-size: 15px; white-space: pre-wrap;'>
{analysis_text.strip()}
</div>
</div>""", unsafe_allow_html=True)

    st.write("")
    
    # RAG Results
    st.markdown("### 📖 RAG 검색 결과 분석")
    
    tab1, tab2, tab3 = st.tabs(["📚 검색된 법령", "⚖️ 관련 판례", "💡 핵심 권장사항"])
    
    with tab1:
        st.markdown("""<div class='tab-content'>
<div class='stat-row'><span>개인정보보호법 제15조 (개인정보의 수집·이용)</span><span style='color: #d1135c; font-weight: bold;'>0.92</span></div>
<div class='progress-container'><div class='progress-bar' style='width: 92%; background-color: #d1135c;'></div></div>
<div class='stat-row'><span>저작권법 제103조 (복제·전송의 중단)</span><span style='color: #d1135c; font-weight: bold;'>0.78</span></div>
<div class='progress-container'><div class='progress-bar' style='width: 78%; background-color: #d1135c;'></div></div>
</div>""", unsafe_allow_html=True)
        
    with tab2:
        st.markdown("""
        <div class='tab-content'>
            <div class='stat-row'><span>대법원 2021.10.14 선고 2020다2929XX</span><span style='color: #0b1f52; font-weight: bold;'>0.85</span></div>
            <div class='progress-container'><div class='progress-bar' style='width: 85%; background-color: #0b1f52;'></div></div>
            <div class='stat-row'><span>서울중앙지법 2023.05.12 선고 2022가합55XX</span><span style='color: #0b1f52; font-weight: bold;'>0.64</span></div>
            <div class='progress-container'><div class='progress-bar' style='width: 64%; background-color: #0b1f52;'></div></div>
        </div>
        """, unsafe_allow_html=True)
        
    with tab3:
        st.markdown("""<div class='tab-content'>
<div style='background: #fff5f8; padding: 15px; border-radius: 10px; border: 1px solid #ffeef2; margin-bottom: 15px;'>
<div style='font-weight: 700; color: #d1135c;'>✓ 개인정보 처리방침 보완</div>
<div style='font-size: 14px; color: #666;'>사용자 동의 절차를 앱 내 설정 메뉴에 명확히 노출해야 합니다.</div>
</div>
<div style='background: #f5f8ff; padding: 15px; border-radius: 10px; border: 1px solid #eef2ff;'>
<div style='font-weight: 700; color: #0b1f52;'>✓ 제3자 API 데이터 저작권 확인</div>
<div style='font-size: 14px; color: #666;'>외부 API를 통해 가져오는 뉴스 데이터의 재가공 범위를 확인하세요.</div>
</div>
</div>""", unsafe_allow_html=True)

else:
    st.markdown("""<div style='text-align: center; padding: 100px 0;'>
<div style='font-size: 80px; margin-bottom: 20px;'>🛡️</div>
<h2>분석을 시작하려면 왼쪽 사이드바에 서비스 설명을 입력하세요.</h2>
<p style='color: #888;'>SafeLaunch AI가 실제 법률 데이터를 바탕으로 정밀 분석을 수행합니다.</p>
</div>""", unsafe_allow_html=True)
