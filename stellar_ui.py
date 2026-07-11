"""
Team Scorpians - Hybrid Token-Efficient Routing Agent
AMD Hackathon ACT II - Track 1
"""
import streamlit as st
import requests
import time
import os

# ========== PAGE CONFIG ==========
st.set_page_config(
    page_title="Team Scorpians - AI Router",
    page_icon="🦂",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ========== SESSION STATE ==========
if 'total_queries' not in st.session_state:
    st.session_state.total_queries = 0
    st.session_state.local_count = 0
    st.session_state.cloud_count = 0
    st.session_state.history = []

# ========== CUSTOM CSS ==========
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .main-header {
        text-align: center;
        padding: 1.5rem 0 0.5rem 0;
    }
    
    .main-header h1 {
        font-size: 3.5rem;
        font-weight: 700;
        letter-spacing: -0.02em;
        margin-bottom: 0.2rem;
        color: #1a1a1a;
    }
    
    .main-header h1 .gradient-text {
        background: linear-gradient(135deg, #ED1C24 0%, #FF6D00 50%, #ED1C24 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .main-header p {
        color: #6b7280;
        font-size: 1.15rem;
        max-width: 600px;
        margin: 0 auto 0.5rem auto;
    }
    
    .glass-card {
        background: rgba(255, 255, 255, 0.7);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.3);
        border-radius: 16px;
        padding: 1.2rem;
        box-shadow: 0 8px 32px rgba(0,0,0,0.05);
        transition: all 0.3s ease;
        text-align: center;
    }
    
    .glass-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 40px rgba(0,0,0,0.08);
    }
    
    .stat-number {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1a1a1a;
        margin: 0;
    }
    
    .stat-label {
        font-size: 0.85rem;
        color: #6b7280;
        font-weight: 500;
    }
    
    .badge-local {
        background: #10b981;
        color: white;
        padding: 4px 14px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        display: inline-block;
    }
    
    .badge-cloud {
        background: #ef4444;
        color: white;
        padding: 4px 14px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        display: inline-block;
    }
    
    .answer-box {
        background: white;
        border-radius: 12px;
        padding: 1rem 1.5rem;
        border-left: 4px solid #10b981;
        margin: 0.5rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }
    
    .answer-box.cloud {
        border-left-color: #ef4444;
    }
    
    .tab-container {
        background: #f3f4f6;
        border-radius: 12px;
        padding: 4px;
        display: flex;
        gap: 4px;
        justify-content: center;
        margin: 1rem 0;
    }
    
    .tab-item {
        padding: 8px 24px;
        border-radius: 8px;
        font-size: 0.85rem;
        font-weight: 500;
        color: #6b7280;
        background: transparent;
        cursor: default;
    }
    
    .tab-item.active {
        background: white;
        color: #1a1a1a;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    .footer-scorpion {
        text-align: center;
        padding: 1.5rem 0 0.5rem 0;
        border-top: 1px solid #e5e7eb;
        margin-top: 2rem;
    }
    
    .footer-scorpion .team {
        font-weight: 700;
        font-size: 1.1rem;
        color: #ED1C24;
    }
    
    .footer-scorpion .github-link {
        color: #6b7280;
        text-decoration: none;
        font-size: 0.9rem;
    }
    
    .footer-scorpion .github-link:hover {
        color: #ED1C24;
        text-decoration: underline;
    }
    
    .footer-scorpion .hackathon {
        color: #9ca3af;
        font-size: 0.85rem;
        margin-top: 0.2rem;
    }
    
    @media (max-width: 768px) {
        .stat-number { font-size: 1.8rem; }
        .main-header h1 { font-size: 2.2rem; }
    }
</style>
""", unsafe_allow_html=True)

# ========== BACKEND URL ==========
BACKEND_URL = st.sidebar.text_input("⚙️ Backend URL", value="http://localhost:8080")
st.sidebar.markdown("---")
st.sidebar.caption("🦂 Team Scorpians | AMD Hackathon 2026")

# ========== HERO HEADER ==========
st.markdown("""
<div class="main-header">
    <h1>
        Work Smarter.<br>
        <span class="gradient-text">AI Routes Intelligently.</span>
    </h1>
    <p>Local-first AI routing — save tokens, reduce costs, and get answers faster.</p>
</div>
""", unsafe_allow_html=True)

# ========== STATS ==========
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="glass-card">
        <div class="stat-number">{st.session_state.total_queries}</div>
        <div class="stat-label">📊 Total Queries</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="glass-card">
        <div class="stat-number" style="color:#10b981;">{st.session_state.local_count}</div>
        <div class="stat-label">🟢 Local (FREE)</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="glass-card">
        <div class="stat-number" style="color:#ef4444;">{st.session_state.cloud_count}</div>
        <div class="stat-label">🔴 Cloud (PAID)</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    saved = 0
    if st.session_state.total_queries > 0:
        saved = int((st.session_state.local_count / st.session_state.total_queries) * 100)
    st.markdown(f"""
    <div class="glass-card">
        <div class="stat-number" style="color:#f59e0b;">{saved}%</div>
        <div class="stat-label">💰 Tokens Saved</div>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# ========== TABS ==========
st.markdown("""
<div class="tab-container">
    <span class="tab-item active">📊 Analyse</span>
    <span class="tab-item">📚 Train</span>
    <span class="tab-item">👥 Testing</span>
    <span class="tab-item">🚀 Deploy</span>
</div>
""", unsafe_allow_html=True)

# ========== QUERY INPUT ==========
st.markdown("### 💬 Live Interaction")

query = st.text_area("", placeholder="Type your question here...", height=80, label_visibility="collapsed")

if st.button("🚀 Route Query", type="primary"):
    if not query.strip():
        st.warning("Please enter a query.")
    else:
        with st.spinner("⏳ Routing..."):
            try:
                # Check backend health
                health = requests.get(f"{BACKEND_URL}/health", timeout=3)
                if health.status_code != 200:
                    st.error("❌ Backend not healthy.")
                    st.stop()
                
                start_time = time.time()
                response = requests.post(
                    f"{BACKEND_URL}/route",
                    json={"query": query},
                    timeout=30
                )
                latency_ms = (time.time() - start_time) * 1000
                
                if response.status_code == 200:
                    data = response.json()
                    
                    st.session_state.total_queries += 1
                    if data.get("escalated"):
                        st.session_state.cloud_count += 1
                        badge_class = "cloud"
                        badge_text = "☁️ CLOUD"
                    else:
                        st.session_state.local_count += 1
                        badge_class = ""
                        badge_text = "🟢 LOCAL (FREE)"
                    
                    # History
                    st.session_state.history.append({
                        "query": query,
                        "answer": data.get('answer', ''),
                        "source": "CLOUD" if data.get('escalated') else "LOCAL",
                        "confidence": data.get('confidence', 0),
                        "latency": f"{latency_ms:.0f} ms"
                    })
                    if len(st.session_state.history) > 5:
                        st.session_state.history.pop(0)
                    
                    # Display Answer
                    st.markdown(f"""
                    <div class="answer-box {badge_class}">
                        <span class="badge-{badge_class if badge_class else 'local'}">{badge_text}</span>
                        <p style="margin-top:0.5rem;"><strong>Answer:</strong> {data.get('answer', 'No answer')}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    col_a, col_b, col_c, col_d = st.columns(4)
                    confidence = data.get('confidence', 0)
                    col_a.metric("Source", "LOCAL" if not data.get('escalated') else "CLOUD")
                    col_b.metric("Confidence", f"{confidence:.2f}")
                    col_c.metric("Local Tokens", data.get('local_tokens', 0), delta="FREE" if not data.get('escalated') else None)
                    col_d.metric("Latency", f"{latency_ms:.0f} ms")
                    
                    if data.get('cloud_cost_usd', 0) > 0:
                        st.info(f"💰 Cloud cost: ${data.get('cloud_cost_usd', 0):.6f}")
                    if data.get('error'):
                        st.warning(f"⚠️ {data.get('error')}")
                else:
                    st.error(f"❌ Backend error: {response.status_code}")
                    
            except requests.exceptions.ConnectionError:
                st.error("❌ Cannot connect to backend. Make sure it's running.")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

# ========== RECENT INTERACTIONS ==========
if st.session_state.history:
    st.markdown("### 📋 Recent Interactions")
    for log in reversed(st.session_state.history):
        badge = "🟢 LOCAL (FREE)" if log["source"] == "LOCAL" else "🔴 CLOUD"
        st.markdown(f"""
        <div style="background:#f9fafb; padding:0.8rem 1rem; border-radius:10px; margin-bottom:0.5rem; border-left:3px solid {'#10b981' if log['source']=='LOCAL' else '#ef4444'};">
            <span style="font-weight:500;">❓ {log['query']}</span><br>
            <span style="font-size:0.9rem; color:#6b7280;">{badge} | Confidence: {log['confidence']:.2f} | Latency: {log['latency']}</span>
            <p style="margin:0.3rem 0 0 0; font-size:0.95rem;"><strong>Answer:</strong> {log['answer'][:150]}{'...' if len(log['answer'])>150 else ''}</p>
        </div>
        """, unsafe_allow_html=True)

# ========== TEAM SCORPIANS FOOTER (UPDATED) ==========
st.markdown("""
<div class="footer-scorpion">
    <div class="team">🦂 Team Scorpians</div>
    <div>
        <a class="github-link" href="https://github.com/Awais-0806/Team-Scorpians-Routing-Agent" target="_blank">
            🔗 GitHub: Awais-0806/Team-Scorpians-Routing-Agent
        </a>
    </div>
    <div class="hackathon">AMD Developer Hackathon ACT II · Track 1 · July 2026</div>
    <div style="margin-top:0.5rem; color:#d1d5db; font-size:0.75rem;">
        Built with ❤️ by Team Scorpians
    </div>
</div>
""", unsafe_allow_html=True)