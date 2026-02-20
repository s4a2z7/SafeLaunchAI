import streamlit as st
import pandas as pd

# Set page configuration
st.set_page_config(page_title="KBO 2024 시즌 선수 비교", layout="wide")

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
        padding: 2rem 0;
        color: #333;
    }
    
    .comparison-container {
        display: flex;
        justify-content: space-around;
        align-items: center;
        padding: 2rem;
        background: white;
        border-radius: 20px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.05);
        margin-bottom: 2rem;
    }
    
    .player-card {
        text-align: center;
        padding: 20px;
        width: 300px;
    }
    
    .player-number {
        width: 80px;
        height: 80px;
        line-height: 80px;
        border-radius: 50%;
        color: white;
        font-size: 32px;
        font-weight: bold;
        margin: 0 auto 20px;
    }
    
    .player-name {
        font-size: 24px;
        font-weight: 700;
        margin-bottom: 5px;
    }
    
    .player-sub {
        color: #888;
        font-size: 14px;
        margin-bottom: 15px;
    }
    
    .vs-text {
        font-size: 64px;
        font-weight: 900;
        color: #eee;
    }
    
    .stat-box {
        background: white;
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.03);
    }
    
    .stat-title {
        font-size: 18px;
        font-weight: 700;
        margin-bottom: 15px;
        display: flex;
        align-items: center;
    }
    
    .stat-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 10px;
    }
    
    .progress-container {
        display: flex;
        width: 100%;
        height: 8px;
        background-color: #eee;
        border-radius: 4px;
        overflow: hidden;
        margin: 10px 0;
    }
    
    .progress-bar-left {
        height: 100%;
        background-color: #d1135c;
    }
    
    .progress-bar-right {
        height: 100%;
        background-color: #0b1f52;
    }
</style>
""", unsafe_allow_html=True)

# App Content
st.markdown("<div class='main-header'><h1>⚾ KBO 2024 시즌 선수 비교</h1><p>폰세카 (LG 트윈스) vs 라일리 (두산 베어스)</p></div>", unsafe_allow_html=True)

# Top Comparison Cards
col1, col2, col3 = st.columns([1, 0.5, 1])

with col1:
    st.markdown("""
    <div class='player-card'>
        <div class='player-number' style='background-color: #d1135c;'>51</div>
        <div class='player-name'>폰세카</div>
        <div class='player-sub'>Austin Dean Fonseca</div>
        <div style='margin-bottom: 15px;'>
            <span style='background: #fce4ec; color: #d1135c; padding: 2px 8px; border-radius: 10px; font-size: 12px;'>LG 트윈스</span>
            <span style='background: #f0f0f0; color: #666; padding: 2px 8px; border-radius: 10px; font-size: 12px;'>좌익수</span>
        </div>
        <div class='player-sub'>우투우타 | 188cm / 95kg<br>1993.10.14 (31세)</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("<div style='text-align: center; padding-top: 50px;'><span class='vs-text'>VS</span></div>", unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class='player-card'>
        <div class='player-number' style='background-color: #0b1f52;'>27</div>
        <div class='player-name'>라일리</div>
        <div class='player-sub'>Austin Riley</div>
        <div style='margin-bottom: 15px;'>
            <span style='background: #e3f2fd; color: #0b1f52; padding: 2px 8px; border-radius: 10px; font-size: 12px;'>두산 베어스</span>
            <span style='background: #f0f0f0; color: #666; padding: 2px 8px; border-radius: 10px; font-size: 12px;'>3루수</span>
        </div>
        <div class='player-sub'>우투우타 | 191cm / 109kg<br>1997.04.02 (27세)</div>
    </div>
    """, unsafe_allow_html=True)

# Stats Section
st.markdown("### 📊 2024 시즌 주요 스탯")

# Key stats summary
s_col1, s_col2, s_col3, s_col4, s_col5 = st.columns(5)
stats_data = [
    ("타율 (AVG)", ".311", ".289"),
    ("홈런 (HR)", "28", "32"),
    ("타점 (RBI)", "102", "98"),
    ("OPS", ".931", ".905"),
    ("WAR", "4.8", "4.2")
]

for i, (label, v1, v2) in enumerate(stats_data):
    cols = [s_col1, s_col2, s_col3, s_col4, s_col5]
    with cols[i]:
        st.markdown(f"""
        <div style='text-align: center; background: white; padding: 15px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.02);'>
            <div style='font-size: 12px; color: #888;'>{label}</div>
            <div style='display: flex; justify-content: space-around; align-items: baseline; margin-top: 10px;'>
                <span style='font-size: 20px; font-weight: bold; color: #d1135c;'>{v1}</span>
                <span style='font-size: 20px; font-weight: bold; color: #0b1f52;'>{v2}</span>
            </div>
            <div style='font-size: 10px; color: #bbb; margin-top: 5px;'>폰세카  라일리</div>
        </div>
        """, unsafe_allow_html=True)

st.write("")

# Detailed comparison
c_col1, c_col2 = st.columns(2)

with c_col1:
    st.markdown("""
    <div class='stat-box'>
        <div class='stat-title'>🎯 타격 스탯 비교</div>
        <div class='stat-row'><span>출루율 (OBP)</span><div style='text-align: right;'><span style='color: #d1135c; font-weight: bold;'>.389</span> <span style='color: #0b1f52; font-weight: bold;'>.368</span></div></div>
        <div class='progress-container'><div class='progress-bar-left' style='width: 52%;'></div><div class='progress-bar-right' style='width: 48%;'></div></div>
        <div class='stat-row' style='margin-top: 20px;'><span>장타율 (SLG)</span><div style='text-align: right;'><span style='color: #d1135c; font-weight: bold;'>.542</span> <span style='color: #0b1f52; font-weight: bold;'>.537</span></div></div>
        <div class='progress-container'><div class='progress-bar-left' style='width: 51%;'></div><div class='progress-bar-right' style='width: 49%;'></div></div>
    </div>
    """, unsafe_allow_html=True)

with c_col2:
    st.markdown("""
    <div class='stat-box'>
        <div class='stat-title'>📈 세이버메트릭스</div>
        <div style='display: flex; gap: 10px;'>
            <div style='flex: 1; background: #fff5f8; padding: 15px; border-radius: 10px; border: 1px solid #ffeef2;'>
                <div style='font-size: 12px; color: #d1135c;'>wOBA</div>
                <div style='font-size: 24px; font-weight: bold; color: #d1135c;'>.385</div>
            </div>
            <div style='flex: 1; background: #f5f8ff; padding: 15px; border-radius: 10px; border: 1px solid #eef2ff;'>
                <div style='font-size: 12px; color: #0b1f52;'>wOBA</div>
                <div style='font-size: 24px; font-weight: bold; color: #0b1f52;'>.372</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
