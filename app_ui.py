"""
🦂 Team Scorpians — 3D Crystal Clear UI
AMD Developer Hackathon: ACT II — Track 1 + Best Use of Gemma
"""

import streamlit as st
import requests
import time
import json
from datetime import datetime

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="Team Scorpians - 3D Hybrid Router",
    page_icon="🦂",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# 3D SCORPION LOGO — CSS ANIMATION
# ============================================================
st.markdown("""
<style>
    /* ===== GLOBAL ===== */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;900&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        background: radial-gradient(ellipse at 20% 50%, #0D1117 0%, #161B22 100%);
        min-height: 100vh;
    }
    
    /* ===== 3D SCORPION LOGO ===== */
    .scorpion-3d {
        width: 120px;
        height: 120px;
        margin: 0 auto 10px auto;
        display: block;
        animation: floatScorpion 4s ease-in-out infinite, rotateScorpion 8s linear infinite;
        filter: drop-shadow(0 0 40px rgba(237, 28, 36, 0.4));
        transform-style: preserve-3d;
        perspective: 800px;
    }
    
    @keyframes floatScorpion {
        0%, 100% { transform: translateY(0px) rotateY(0deg); }
        50% { transform: translateY(-15px) rotateY(180deg); }
    }
    
    @keyframes rotateScorpion {
        0% { transform: rotateY(0deg); }
        100% { transform: rotateY(360deg); }
    }
    
    .scorpion-3d svg {
        width: 100%;
        height: 100%;
        display: block;
        filter: drop-shadow(0 0 30px rgba(237, 28, 36, 0.3));
    }
    
    /* ===== GLASSMORPHISM CARDS ===== */
    .glass {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 24px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
        padding: 24px;
        transition: all 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94);
        transform-style: preserve-3d;
        perspective: 800px;
    }
    
    .glass:hover {
        transform: translateY(-6px) rotateX(2deg);
        box-shadow: 0 16px 48px rgba(237, 28, 36, 0.15);
        border-color: rgba(237, 28, 36, 0.2);
    }
    
    /* ===== TITLE WITH GLOW ===== */
    .scorpians-title {
        color: #ED1C24;
        font-size: 52px;
        font-weight: 900;
        text-align: center;
        text-shadow: 0 0 60px rgba(237, 28, 36, 0.3), 0 0 120px rgba(237, 28, 36, 0.1);
        letter-spacing: 4px;
        animation: glowPulse 3s ease-in-out infinite;
    }
    
    @keyframes glowPulse {
        0%, 100% { text-shadow: 0 0 60px rgba(237, 28, 36, 0.3); }
        50% { text-shadow: 0 0 80px rgba(237, 28, 36, 0.6), 0 0 160px rgba(237, 28, 36, 0.2); }
    }
    
    .scorpians-subtitle {
        color: #FFFFFF;
        font-size: 20px;
        text-align: center;
        opacity: 0.8;
        font-weight: 300;
        letter-spacing: 2px;
    }
    
    .scorpians-tagline {
        color: #ED1C24;
        font-size: 14px;
        text-align: center;
        letter-spacing: 6px;
        font-weight: 600;
        text-transform: uppercase;
        opacity: 0.9;
    }
    
    /* ===== STAT CARDS ===== */
    .stat-card {
        background: linear-gradient(145deg, rgba(255,255,255,0.05), rgba(255,255,255,0.01));
        border-radius: 16px;
        padding: 20px;
        text-align: center;
        border: 1px solid rgba(255,255,255,0.05);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
        transform-style: preserve-3d;
        perspective: 500px;
    }
    
    .stat-card::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle at 30% 30%, rgba(237, 28, 36, 0.05), transparent 70%);
        animation: rotateGlow 8s linear infinite;
    }
    
    @keyframes rotateGlow {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    .stat-card:hover {
        transform: translateY(-8px) scale(1.02) rotateX(2deg);
        border-color: rgba(237, 28, 36, 0.3);
        box-shadow: 0 12px 40px rgba(237, 28, 36, 0.15);
    }
    
    .stat-number {
        font-size: 38px;
        font-weight: 900;
        background: linear-gradient(135deg, #FFFFFF, #AAAAAA);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        position: relative;
        z-index: 1;
    }
    
    .stat-number.green {
        background: linear-gradient(135deg, #00C853, #00E676);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .stat-number.red {
        background: linear-gradient(135deg, #ED1C24, #FF3B3B);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .stat-label {
        color: #AAAAAA;
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 2px;
        position: relative;
        z-index: 1;
    }
    
    /* ===== CHAT BUBBLES ===== */
    .user-bubble {
        background: linear-gradient(135deg, rgba(45, 45, 68, 0.9), rgba(26, 26, 46, 0.9));
        backdrop-filter: blur(10px);
        border: 1px solid rgba(237, 28, 36, 0.2);
        border-radius: 18px 18px 18px 4px;
        padding: 16px 20px;
        margin: 12px 0;
        color: #FFFFFF;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        animation: slideInRight 0.5s ease;
    }
    
    .assistant-bubble {
        background: linear-gradient(135deg, rgba(26, 26, 46, 0.9), rgba(13, 17, 23, 0.9));
        backdrop-filter: blur(10px);
        border: 1px solid rgba(0, 200, 83, 0.2);
        border-radius: 18px 18px 4px 18px;
        padding: 16px 20px;
        margin: 12px 0;
        color: #FFFFFF;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        animation: slideInLeft 0.5s ease;
    }
    
    @keyframes slideInRight {
        from { opacity: 0; transform: translateX(20px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    @keyframes slideInLeft {
        from { opacity: 0; transform: translateX(-20px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    /* ===== SAVINGS DISPLAY ===== */
    .savings-display {
        background: linear-gradient(145deg, rgba(0, 200, 83, 0.08), rgba(0, 200, 83, 0.02));
        border: 2px solid rgba(0, 200, 83, 0.2);
        border-radius: 20px;
        padding: 24px;
        text-align: center;
        backdrop-filter: blur(10px);
        box-shadow: 0 0 60px rgba(0, 200, 83, 0.05);
        transition: all 0.3s ease;
    }
    
    .savings-display:hover {
        border-color: rgba(0, 200, 83, 0.4);
        box-shadow: 0 0 80px rgba(0, 200, 83, 0.1);
    }
    
    .savings-number {
        font-size: 48px;
        font-weight: 900;
        background: linear-gradient(135deg, #00C853, #00E676);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0 0 60px rgba(0, 200, 83, 0.2);
        animation: savingsPulse 2s ease-in-out infinite;
    }
    
    @keyframes savingsPulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.02); }
    }
    
    /* ===== ROUTING FLOW ===== */
    .routing-flow {
        background: rgba(255,255,255,0.03);
        backdrop-filter: blur(10px);
        border-radius: 16px;
        padding: 16px;
        border: 1px solid rgba(255,255,255,0.05);
        text-align: center;
    }
    
    .flow-step {
        display: inline-block;
        padding: 6px 16px;
        margin: 4px;
        border-radius: 30px;
        font-weight: 600;
        font-size: 12px;
        transition: all 0.3s ease;
    }
    
    .flow-step:hover {
        transform: scale(1.05);
    }
    
    .flow-local { background: linear-gradient(135deg, #00C853, #00E676); color: white; box-shadow: 0 4px 20px rgba(0, 200, 83, 0.3); }
    .flow-cloud { background: linear-gradient(135deg, #ED1C24, #FF3B3B); color: white; box-shadow: 0 4px 20px rgba(237, 28, 36, 0.3); }
    .flow-gate { background: linear-gradient(135deg, #FF6D00, #FF9100); color: white; box-shadow: 0 4px 20px rgba(255, 109, 0, 0.3); }
    .flow-query { background: linear-gradient(135deg, #2D2D44, #3D3D5C); color: white; box-shadow: 0 4px 20px rgba(45, 45, 68, 0.3); }
    
    /* ===== BADGES ===== */
    .badge-short { background: linear-gradient(135deg, #00C853, #00E676); color: white; padding: 2px 14px; border-radius: 20px; font-size: 11px; font-weight: 600; }
    .badge-medium { background: linear-gradient(135deg, #FF6D00, #FF9100); color: white; padding: 2px 14px; border-radius: 20px; font-size: 11px; font-weight: 600; }
    .badge-detailed { background: linear-gradient(135deg, #ED1C24, #FF3B3B); color: white; padding: 2px 14px; border-radius: 20px; font-size: 11px; font-weight: 600; }
    
    /* ===== SIDEBAR ===== */
    .sidebar-brand {
        text-align: center;
        padding: 20px 0;
        border-bottom: 2px solid rgba(237, 28, 36, 0.2);
        margin-bottom: 20px;
    }
    
    .sidebar-brand h2 {
        background: linear-gradient(135deg, #ED1C24, #FF3B3B);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 28px;
        font-weight: 900;
    }
    
    /* ===== BUTTONS ===== */
    .stButton button {
        background: linear-gradient(135deg, #ED1C24, #FF3B3B) !important;
        color: white !important;
        border: none !important;
        border-radius: 30px !important;
        padding: 10px 28px !important;
        font-weight: 700 !important;
        font-size: 15px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 30px rgba(237, 28, 36, 0.3) !important;
    }
    
    .stButton button:hover {
        transform: scale(1.05) !important;
        box-shadow: 0 8px 40px rgba(237, 28, 36, 0.5) !important;
    }
    
    /* ===== FOOTER ===== */
    .footer {
        text-align: center;
        color: #555555;
        font-size: 11px;
        padding: 20px 0;
        border-top: 1px solid rgba(255,255,255,0.05);
        margin-top: 30px;
    }
    
    .footer span { color: #ED1C24; }
    
    /* ===== INPUT ===== */
    .stTextInput input {
        background: rgba(255,255,255,0.05) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 30px !important;
        padding: 12px 20px !important;
        color: #FFFFFF !important;
        font-size: 15px !important;
        transition: all 0.3s ease !important;
    }
    
    .stTextInput input:focus {
        border-color: #ED1C24 !important;
        box-shadow: 0 0 30px rgba(237, 28, 36, 0.1) !important;
    }
    
    /* ===== TABS ===== */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        background: rgba(255,255,255,0.03);
        border-radius: 16px;
        padding: 4px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 12px !important;
        padding: 6px 20px !important;
        color: #AAAAAA !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
    }
    
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: linear-gradient(135deg, rgba(237, 28, 36, 0.2), rgba(237, 28, 36, 0.05)) !important;
        color: #FFFFFF !important;
        border: 1px solid rgba(237, 28, 36, 0.2) !important;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# 3D SCORPION LOGO (HTML + CSS)
# ============================================================
st.markdown("""
<div style="display: flex; justify-content: center; align-items: center; margin: 0 auto;">
    <div class="scorpion-3d" style="width: 140px; height: 140px;">
        <svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
            <defs>
                <linearGradient id="scorpionGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" style="stop-color:#ED1C24;stop-opacity:1" />
                    <stop offset="50%" style="stop-color:#FF3B3B;stop-opacity:0.8" />
                    <stop offset="100%" style="stop-color:#ED1C24;stop-opacity:1" />
                </linearGradient>
                <filter id="glow">
                    <feGaussianBlur stdDeviation="4" result="coloredBlur"/>
                    <feMerge>
                        <feMergeNode in="coloredBlur"/>
                        <feMergeNode in="SourceGraphic"/>
                    </feMerge>
                </filter>
            </defs>
            <!-- Scorpion Body -->
            <ellipse cx="100" cy="120" rx="35" ry="20" fill="url(#scorpionGrad)" filter="url(#glow)"/>
            <!-- Scorpion Head -->
            <circle cx="100" cy="95" r="18" fill="url(#scorpionGrad)" filter="url(#glow)"/>
            <!-- Scorpion Eyes -->
            <circle cx="92" cy="88" r="4" fill="#FFFFFF" opacity="0.9"/>
            <circle cx="108" cy="88" r="4" fill="#FFFFFF" opacity="0.9"/>
            <!-- Scorpion Tail Segments -->
            <ellipse cx="100" cy="148" rx="18" ry="10" fill="url(#scorpionGrad)" filter="url(#glow)"/>
            <ellipse cx="100" cy="165" rx="14" ry="8" fill="url(#scorpionGrad)" filter="url(#glow)"/>
            <ellipse cx="100" cy="178" rx="10" ry="6" fill="url(#scorpionGrad)" filter="url(#glow)"/>
            <!-- Scorpion Tail Stinger -->
            <ellipse cx="100" cy="190" rx="6" ry="8" fill="#ED1C24" filter="url(#glow)"/>
            <!-- Scorpion Legs (Left) -->
            <line x1="70" y1="115" x2="45" y2="105" stroke="#ED1C24" stroke-width="4" stroke-linecap="round" filter="url(#glow)"/>
            <line x1="70" y1="125" x2="40" y2="125" stroke="#ED1C24" stroke-width="4" stroke-linecap="round" filter="url(#glow)"/>
            <line x1="70" y1="135" x2="45" y2="145" stroke="#ED1C24" stroke-width="4" stroke-linecap="round" filter="url(#glow)"/>
            <!-- Scorpion Legs (Right) -->
            <line x1="130" y1="115" x2="155" y2="105" stroke="#ED1C24" stroke-width="4" stroke-linecap="round" filter="url(#glow)"/>
            <line x1="130" y1="125" x2="160" y2="125" stroke="#ED1C24" stroke-width="4" stroke-linecap="round" filter="url(#glow)"/>
            <line x1="130" y1="135" x2="155" y2="145" stroke="#ED1C24" stroke-width="4" stroke-linecap="round" filter="url(#glow)"/>
            <!-- Scorpion Claws -->
            <ellipse cx="80" cy="95" rx="12" ry="6" fill="url(#scorpionGrad)" filter="url(#glow)"/>
            <ellipse cx="120" cy="95" rx="12" ry="6" fill="url(#scorpionGrad)" filter="url(#glow)"/>
        </svg>
    </div>
</div>
""", unsafe_allow_html=True)

# ============================================================
# HEADER
# ============================================================
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown('<p class="scorpians-title">🦂 TEAM SCORPIANS</p>', unsafe_allow_html=True)
    st.markdown('<p class="scorpians-subtitle">Hybrid Token-Efficient Routing Agent</p>', unsafe_allow_html=True)
    st.markdown('<p class="scorpians-tagline">⚡ CODE. COLLABORATE. CONQUER. ⚡</p>', unsafe_allow_html=True)
    st.markdown("---")

# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown("""
    <div class="sidebar-brand">
        <h2>🦂 SCORPIANS</h2>
        <p style="color:#AAAAAA; font-size:13px;">AMD Hackathon ACT II</p>
        <p style="color:#ED1C24; font-size:11px; font-weight:600;">Track 1 + Gemma Bonus</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Stats
    if "total_queries" not in st.session_state:
        st.session_state.total_queries = 0
        st.session_state.local_count = 0
        st.session_state.cloud_count = 0
    
    st.markdown("### 📊 LIVE STATS")
    c1, c2, c3 = st.columns(3)
    c1.metric("Total", st.session_state.total_queries)
    c2.metric("🏠 Local", st.session_state.local_count)
    c3.metric("☁️ Cloud", st.session_state.cloud_count)
    
    # Savings
    savings_pct = 0
    if st.session_state.total_queries > 0:
        savings_pct = (st.session_state.local_count / st.session_state.total_queries) * 100
    
    st.markdown(f"""
    <div class="savings-display">
        <div style="color:#AAAAAA; font-size:13px;">💰 TOKENS SAVED</div>
        <div class="savings-number">{savings_pct:.0f}%</div>
        <div style="color:#AAAAAA; font-size:11px;">Local = Zero Tokens ✅</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("### ⚙️ HOW IT WORKS")
    st.markdown("""
    1. **Local Model** — Gemma 3 1B / Phi-3 Mini  
    2. **Asked TWICE** — Self-Consistency  
    3. **Confidence Gate** — Confident → FREE!  
    4. **Cloud Fallback** — Only if unsure
    """)
    
    st.markdown("---")
    
    st.markdown("""
    <div style="text-align:center; color:#555; font-size:10px;">
        🦂 Team Scorpians<br>
        Code. Collaborate. Conquer.
    </div>
    """, unsafe_allow_html=True)

# ============================================================
# TABS
# ============================================================
tab1, tab2, tab3 = st.tabs(["💬 Chat", "📊 Benchmark", "📈 About"])

# ============================================================
# TAB 1: CHAT
# ============================================================
with tab1:
    col1, col2 = st.columns([3, 1])
    with col1:
        API_URL = st.text_input(
            "🔗 Agent URL",
            value="http://localhost:8081/chat",
            help="FastAPI agent endpoint"
        )
    with col2:
        API_KEY = st.text_input(
            "🔑 API Key",
            value="myHackathonKey2026",
            type="password"
        )
    
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "🦂 Welcome to Team Scorpians! I'll try local first (FREE), and only escalate to cloud when needed."}
        ]
    
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f'<div class="user-bubble">🧑 <b>You</b><br>{msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="assistant-bubble">🦂 <b>Agent</b><br>{msg["content"]}</div>', unsafe_allow_html=True)
    
    with st.container():
        c1, c2 = st.columns([5, 1])
        with c1:
            user_query = st.text_input(
                "💬 Type your question...",
                placeholder="e.g., What is the capital of Pakistan?",
                key="query_input",
                label_visibility="collapsed"
            )
        with c2:
            submit = st.button("🚀 ASK", use_container_width=True)
    
    if submit and user_query:
        st.session_state.messages.append({"role": "user", "content": user_query})
        st.session_state.total_queries += 1
        
        with st.spinner("🦂 Routing..."):
            try:
                resp = requests.post(API_URL, json={"query": user_query, "api_key": API_KEY}, timeout=120)
                
                if resp.status_code == 200:
                    data = resp.json()
                    answer = data.get("answer", "No answer")
                    source = data.get("source", "unknown")
                    confidence = data.get("confidence", 0)
                    latency_ms = data.get("latency_ms", 0)
                    
                    if source == "local":
                        st.session_state.local_count += 1
                    elif source == "cloud":
                        st.session_state.cloud_count += 1
                    
                    source_emoji = "🏠" if source == "local" else "☁️" if source == "cloud" else "⚠️"
                    source_label = "LOCAL (FREE!)" if source == "local" else "CLOUD" if source == "cloud" else "ERROR"
                    source_color = "#00C853" if source == "local" else "#ED1C24" if source == "cloud" else "#FF6D00"
                    
                    answer_words = len(answer.split())
                    if answer_words <= 5:
                        answer_type = "⚡ Short (Direct)"
                        answer_badge = "badge-short"
                    elif answer_words <= 20:
                        answer_type = "📝 Medium (Concise)"
                        answer_badge = "badge-medium"
                    else:
                        answer_type = "📖 Detailed (Full)"
                        answer_badge = "badge-detailed"
                    
                    st.markdown("""
                    <div class="routing-flow">
                        <span class="flow-step flow-query">📩 Query</span>
                        <span style="color:#555;"> → </span>
                        <span class="flow-step flow-local">🏠 Local</span>
                        <span style="color:#555;"> → </span>
                        <span class="flow-step flow-gate">⚡ Confidence Gate</span>
                        <span style="color:#555;"> → </span>
                        <span class="flow-step {}">{}</span>
                    </div>
                    """.format("flow-local" if source == "local" else "flow-cloud", source_emoji + " " + source_label), unsafe_allow_html=True)
                    
                    display_text = f"""
**Answer:** {answer}

---
**📊 Routing Decision:**
- **Source:** {source_emoji} <span style="color:{source_color}; font-weight:700;">{source_label}</span>
- **Answer Type:** <span class="{answer_badge}">{answer_type}</span>
- **Confidence:** `{confidence:.2f}` {'✅' if confidence > 0.7 else '⚠️' if confidence > 0.4 else '❌'}
- **Latency:** `{latency_ms:.0f} ms`
                    """
                    
                    st.session_state.messages.append({"role": "assistant", "content": display_text})
                else:
                    st.session_state.messages.append({"role": "assistant", "content": f"❌ Error: {resp.status_code}"})
            except Exception as e:
                st.session_state.messages.append({"role": "assistant", "content": f"❌ Error: {str(e)}"})
        st.rerun()

# ============================================================
# TAB 2: BENCHMARK
# ============================================================
with tab2:
    st.markdown("### 📊 TOKEN SAVINGS BENCHMARK")
    st.markdown("---")
    
    if st.session_state.total_queries > 0:
        local_pct = (st.session_state.local_count / st.session_state.total_queries) * 100
        cloud_pct = (st.session_state.cloud_count / st.session_state.total_queries) * 100
        
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-number">{st.session_state.total_queries}</div>
                <div class="stat-label">Total Queries</div>
            </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-number green">{local_pct:.0f}%</div>
                <div class="stat-label">🏠 Local (FREE)</div>
            </div>
            """, unsafe_allow_html=True)
        with c3:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-number red">{cloud_pct:.0f}%</div>
                <div class="stat-label">☁️ Cloud</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="savings-display" style="margin-top:20px;">
            <div style="color:#AAAAAA; font-size:16px;">💰 TOTAL TOKEN SAVINGS</div>
            <div class="savings-number">{local_pct:.0f}%</div>
            <div style="color:#00C853; font-size:13px;">✅ {st.session_state.local_count} queries answered FREE</div>
            <div style="color:#ED1C24; font-size:13px;">❌ {st.session_state.cloud_count} queries used cloud tokens</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("🤖 Ask some questions first to see benchmark data!")

# ============================================================
# TAB 3: ABOUT
# ============================================================
with tab3:
    st.markdown("### 🦂 TEAM SCORPIANS")
    st.markdown("#### Hybrid Token-Efficient Routing Agent")
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div style="background: rgba(255,255,255,0.03); padding: 20px; border-radius: 16px; border: 1px solid rgba(255,255,255,0.08);">
            <h4 style="color: #ED1C24; margin-bottom: 14px;">📋 Project Details</h4>
            <p style="color: #E0E0E0; margin: 6px 0; font-size: 13px;">
                <b style="color: #FFFFFF;">Track:</b> Track 1 — Hybrid Token-Efficient
            </p>
            <p style="color: #E0E0E0; margin: 6px 0; font-size: 13px;">
                <b style="color: #FFFFFF;">Bonus:</b> Best Use of Gemma Models
            </p>
            <p style="color: #E0E0E0; margin: 6px 0; font-size: 13px;">
                <b style="color: #FFFFFF;">Local Model:</b> Gemma 3 1B / Phi-3 Mini (FREE!)
            </p>
            <p style="color: #E0E0E0; margin: 6px 0; font-size: 13px;">
                <b style="color: #FFFFFF;">Cloud Model:</b> Fireworks AI (Only when needed)
            </p>
            <p style="color: #E0E0E0; margin: 6px 0; font-size: 13px;">
                <b style="color: #FFFFFF;">Confidence Gate:</b> Self-Consistency (ask twice)
            </p>
            <p style="color: #E0E0E0; margin: 6px 0; font-size: 13px;">
                <b style="color: #FFFFFF;">Cost Savings:</b> 80%+ tokens saved
            </p>
            <p style="color: #E0E0E0; margin: 6px 0; font-size: 13px;">
                <b style="color: #FFFFFF;">Architecture:</b> FastAPI + Streamlit
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background: rgba(255,255,255,0.03); padding: 20px; border-radius: 16px; border: 1px solid rgba(255,255,255,0.08);">
            <h4 style="color: #ED1C24; margin-bottom: 14px;">👥 Team</h4>
            <p style="color: #E0E0E0; margin: 6px 0; font-size: 13px;">
                <b style="color: #FFFFFF;">Muhammad Awais</b> — Captain / Backend / UI
            </p>
            <p style="color: #E0E0E0; margin: 6px 0; font-size: 13px;">
                <b style="color: #FFFFFF;">Muhammad Ekremah</b> — AI/ML Engineer
            </p>
            <br>
            <h4 style="color: #ED1C24; margin-bottom: 14px;">🏆 Why We Win</h4>
            <p style="color: #E0E0E0; margin: 6px 0; font-size: 13px;">
                ✅ Local = 0 tokens → Optimal Track 1 strategy
            </p>
            <p style="color: #E0E0E0; margin: 6px 0; font-size: 13px;">
                ✅ Self-consistency confidence gate — simple & effective
            </p>
            <p style="color: #E0E0E0; margin: 6px 0; font-size: 13px;">
                ✅ Complete UI with live metrics
            </p>
            <p style="color: #E0E0E0; margin: 6px 0; font-size: 13px;">
                ✅ Real cost savings demonstrated
            </p>
        </div>
        """, unsafe_allow_html=True)

# ============================================================
# FOOTER
# ============================================================
st.markdown("""
<div class="footer">
    🦂 <span>Team Scorpians</span> | Code. Collaborate. Conquer.<br>
    AMD Developer Hackathon: ACT II — Track 1 + Best Use of Gemma
</div>
""", unsafe_allow_html=True)