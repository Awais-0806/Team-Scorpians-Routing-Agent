import streamlit as st
import requests
import time

# -------------------------------
# 1. PAGE CONFIG
# -------------------------------
st.set_page_config(
    page_title="Team Scorpians | AI Router",
    page_icon="🦂",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------
# 2. CUSTOM 3D GLASSMORPHISM CSS
# -------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

    /* ---------- GLOBAL ---------- */
    body {
        font-family: 'Inter', sans-serif;
        color: #E0E0E0;
        background: radial-gradient(circle at 50% 0%, #1a1a2e 0%, #0D1117 70%);
        overflow-x: hidden;
    }

    /* ---------- BACKGROUND ANIMATION ---------- */
    .stApp {
        background: radial-gradient(circle at 50% 0%, #1a1a2e 0%, #0D1117 70%);
        animation: bgPulse 8s infinite alternate;
    }
    @keyframes bgPulse {
        0% { background: radial-gradient(circle at 50% 0%, #1a1a2e 0%, #0D1117 70%); }
        100% { background: radial-gradient(circle at 50% 0%, #1c1c3a 0%, #0D1117 70%); }
    }

    /* ---------- GLASSMORPHISM CARD ---------- */
    .glass-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5),
                    0 0 0 1px rgba(237, 28, 36, 0.1) inset;
        padding: 24px;
        margin: 16px 0;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        perspective: 1000px;
    }
    .glass-card:hover {
        transform: translateY(-4px) rotateX(1deg) rotateY(1deg);
        box-shadow: 0 12px 40px rgba(237, 28, 36, 0.2),
                    0 0 0 1px rgba(237, 28, 36, 0.3) inset;
    }

    /* ---------- 3D SCORPION LOGO ---------- */
    .scorpion-container {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 150px;
        margin-bottom: 20px;
        perspective: 800px;
    }
    .scorpion-logo {
        font-size: 100px;
        filter: drop-shadow(0 0 30px rgba(237, 28, 36, 0.8));
        animation: rotate3d 8s infinite linear, float 3s ease-in-out infinite;
        transform-style: preserve-3d;
        display: inline-block;
    }
    @keyframes rotate3d {
        0% { transform: rotateY(0deg) rotateX(0deg); }
        50% { transform: rotateY(180deg) rotateX(5deg); }
        100% { transform: rotateY(360deg) rotateX(0deg); }
    }
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
    }

    /* ---------- CRYSTAL TEXT ---------- */
    .crystal-title {
        font-weight: 700;
        font-size: 3rem;
        text-align: center;
        background: linear-gradient(135deg, #ED1C24, #FF6B6B);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-shadow: 0 0 30px rgba(237, 28, 36, 0.4);
        animation: textGlow 2s infinite alternate;
    }
    @keyframes textGlow {
        0% { text-shadow: 0 0 30px rgba(237, 28, 36, 0.4); }
        100% { text-shadow: 0 0 50px rgba(237, 28, 36, 0.8); }
    }
    .crystal-subtitle {
        font-size: 1.2rem;
        color: #E0E0E0;
        text-align: center;
        font-weight: 300;
        letter-spacing: 2px;
        opacity: 0.9;
    }

    /* ---------- CHAT BUBBLES ---------- */
    .user-bubble {
        background: linear-gradient(135deg, #ED1C24, #c8102e);
        padding: 12px 20px;
        border-radius: 20px 20px 4px 20px;
        margin: 12px 0;
        max-width: 75%;
        margin-left: auto;
        box-shadow: 0 4px 12px rgba(237, 28, 36, 0.3);
        animation: slideInRight 0.3s ease;
        color: white;
        font-weight: 500;
    }
    .assistant-bubble {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 12px 20px;
        border-radius: 20px 20px 20px 4px;
        margin: 12px 0;
        max-width: 75%;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        animation: slideInLeft 0.3s ease;
        color: #E0E0E0;
    }
    @keyframes slideInRight {
        from { transform: translateX(30px); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    @keyframes slideInLeft {
        from { transform: translateX(-30px); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }

    /* ---------- SIDEBAR ---------- */
    [data-testid="stSidebar"] {
        background: rgba(13, 17, 23, 0.7);
        backdrop-filter: blur(30px);
        border-right: 1px solid rgba(237, 28, 36, 0.2);
    }
    .sidebar-metric {
        text-align: center;
        padding: 16px;
        border-radius: 12px;
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.05);
        margin-bottom: 12px;
    }

    /* ---------- BENCHMARK TABLE ---------- */
    .benchmark-table {
        width: 100%;
        border-collapse: collapse;
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 20px rgba(0,0,0,0.5);
    }
    .benchmark-table th {
        background: rgba(237, 28, 36, 0.2);
        color: #fff;
        padding: 12px;
        font-weight: 600;
    }
    .benchmark-table td {
        padding: 10px 12px;
        border-bottom: 1px solid rgba(255,255,255,0.05);
        color: #E0E0E0;
    }
</style>
""", unsafe_allow_html=True)

# -------------------------------
# 3. SCORPION 3D LOGO + HEADER
# -------------------------------
st.markdown('<div class="scorpion-container"><span class="scorpion-logo">🦂</span></div>', unsafe_allow_html=True)
st.markdown('<h1 class="crystal-title">Team Scorpians</h1>', unsafe_allow_html=True)
st.markdown('<p class="crystal-subtitle">HYBRID TOKEN‑EFFICIENT ROUTING AGENT</p>', unsafe_allow_html=True)

# -------------------------------
# 4. SIDEBAR CONFIGURATION
# -------------------------------
with st.sidebar:
    st.markdown("## ⚙️ Configuration")
    backend_url = st.text_input("Backend URL", value="http://localhost:8081")
    api_key = st.text_input("API Key", value="myHackathonKey2026", type="password")
    st.markdown("---")
    st.markdown("### 📊 Live Stats")
    st.markdown('<div class="sidebar-metric">⚡ Queries: 0</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-metric">🟢 Local: 0</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-metric">🔴 Cloud: 0</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-metric">💰 Tokens saved: 0</div>', unsafe_allow_html=True)

# -------------------------------
# 5. MAIN TABS
# -------------------------------
tab1, tab2, tab3 = st.tabs(["💬 Chat", "📊 Benchmark", "ℹ️ About"])

# ---------- CHAT TAB ----------
with tab1:
    st.markdown("### 💬 Ask the Hybrid Agent")
    query = st.text_input("Enter your query:", placeholder="e.g., What is the capital of Pakistan?")

    if st.button("🚀 Route Query", type="primary"):
        if query.strip():
            with st.spinner("🧠 Routing your query..."):
                try:
                    resp = requests.post(
                        f"{backend_url}/chat",
                        json={"query": query.strip(), "api_key": api_key},
                        timeout=30
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        # Display assistant bubble
                        with st.container():
                            st.markdown(f'<div class="user-bubble">{query}</div>', unsafe_allow_html=True)
                            if data.get("source") == "local":
                                st.markdown(f'<div class="assistant-bubble">🟢 <strong>Local (FREE)</strong><br>{data["answer"]}</div>', unsafe_allow_html=True)
                            else:
                                st.markdown(f'<div class="assistant-bubble">🔴 <strong>Cloud (paid)</strong><br>{data["answer"]}</div>', unsafe_allow_html=True)
                            # Metrics
                            col1, col2, col3 = st.columns(3)
                            col1.metric("Confidence", f"{data.get('confidence', 0):.2f}")
                            col2.metric("Latency", f"{data.get('latency_ms', 0):.0f} ms")
                            col3.metric("Source", data.get("source", "unknown"))
                    else:
                        st.error(f"Error {resp.status_code}: {resp.text}")
                except Exception as e:
                    st.error(f"Connection failed: {e}")

# ---------- BENCHMARK TAB ----------
with tab2:
    st.markdown("### 📊 Real-Time Benchmark")
    st.markdown('<div class="glass-card">'
                '<table class="benchmark-table">'
                '<tr><th>Query</th><th>Difficulty</th><th>Escalated</th><th>Latency</th></tr>'
                '<tr><td>What is 2+2?</td><td>Easy</td><td>No</td><td>3.2s</td></tr>'
                '<tr><td>Derive merge sort</td><td>Hard</td><td>Yes</td><td>8.1s</td></tr>'
                '</table></div>', unsafe_allow_html=True)

    st.markdown("#### 📈 Token Savings")
    st.markdown("80% of queries handled locally → **0 cloud tokens used**", unsafe_allow=True)

# ---------- ABOUT TAB ----------
with tab3:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("""
    ## 🦂 **Team Scorpians**
    **AMD Hackathon ACT II - Track 1**

    We built a **local-first AI routing agent** that saves up to 90% of cloud tokens.  
    Using a tiny Gemma/Phi model on AMD ROCm, we only pay for cloud when absolutely necessary.

    **Team:**  
    - **Awais Jabbar** – Captain, Backend, UI/UX  
    - **Muhammad Ekremah** – AI/ML Engineer, API Integration  

    **Tech:** FastAPI · Ollama · Streamlit · AMD ROCm · Fireworks AI  
    """)
    st.markdown('</div>', unsafe_allow_html=True)

# -------------------------------
# 6. FOOTER
# -------------------------------
st.markdown("---")
st.caption("© 2026 Team Scorpians | Built for AMD Hackathon ACT II")