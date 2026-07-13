"""
Team Scorpians - Hybrid Token-Efficient Routing Agent
Smart UI with Live Stats & Token Counter
"""

import streamlit as st
import requests
import time

# ========== PAGE CONFIG ==========
st.set_page_config(
    page_title="Scorpians - AI Router",
    page_icon="🦂",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ========== INITIALIZE SESSION STATE ==========
if 'total_queries' not in st.session_state:
    st.session_state.total_queries = 0
    st.session_state.local_count = 0
    st.session_state.cloud_count = 0
    st.session_state.tokens_saved = 0
    st.session_state.history = []  # store recent interactions (max 5)

# ========== CUSTOM CSS ==========
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    * { font-family: 'Inter', sans-serif; }
    .main-header { text-align: center; padding: 2rem 0 1rem 0; }
    .gradient-text {
        background: linear-gradient(135deg, #000000 0%, #6b7280 50%, #9ca3af 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 600;
    }
    .glass-card {
        background: rgba(255, 255, 255, 0.7);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.3);
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 8px 32px rgba(0,0,0,0.05);
        transition: all 0.3s ease;
        text-align: center;
    }
    .glass-card:hover { transform: translateY(-2px); box-shadow: 0 12px 40px rgba(0,0,0,0.08); }
    .stat-number { font-size: 2.5rem; font-weight: 700; color: #1a1a1a; margin: 0; }
    .stat-label { font-size: 0.85rem; color: #6b7280; font-weight: 500; }
    .badge-local { background: #10b981; color: white; padding: 4px 12px; border-radius: 20px; font-size: 0.8rem; font-weight: 600; }
    .badge-cloud { background: #ef4444; color: white; padding: 4px 12px; border-radius: 20px; font-size: 0.8rem; font-weight: 600; }
    .answer-box {
        background: white;
        border-radius: 12px;
        padding: 1rem 1.5rem;
        border-left: 4px solid #10b981;
        margin: 0.5rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }
    .answer-box.cloud { border-left-color: #ef4444; }
    .video-wrapper {
        border-radius: 20px;
        overflow: hidden;
        position: relative;
        height: 400px;
        background: #000;
        margin: 1.5rem 0;
    }
    .video-wrapper video { width: 100%; height: 100%; object-fit: cover; }
    .overlay-card {
        position: absolute;
        bottom: 20px;
        left: 50%;
        transform: translateX(-50%);
        background: rgba(255, 255, 255, 0.92);
        backdrop-filter: blur(8px);
        padding: 1.5rem 2rem;
        border-radius: 16px;
        width: 90%;
        max-width: 500px;
        text-align: center;
        box-shadow: 0 8px 32px rgba(0,0,0,0.15);
    }
    .overlay-card h4 { color: #1a1a1a !important; margin: 0; font-weight: 600; }
    .overlay-card p { color: #4b5563 !important; margin: 0.25rem 0 0 0; font-size: 0.9rem; }
    .footer-logos {
        display: flex;
        flex-wrap: wrap;
        justify-content: center;
        gap: 2rem 3rem;
        padding: 2rem 0;
        color: #9ca3af;
        font-weight: 500;
        font-size: 1.1rem;
        letter-spacing: 0.5px;
    }
    @media (max-width: 768px) {
        .stat-number { font-size: 1.8rem; }
        .overlay-card { padding: 1rem; }
        .video-wrapper { height: 280px; }
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
    <h1 style="font-size:3.5rem; font-weight:400; letter-spacing:-0.02em; margin-bottom:0.5rem;">
        Work Smarter.<br>
        <span class="gradient-text" style="font-weight:400;">AI Routes Intelligently.</span>
    </h1>
    <p style="color:#6b7280; font-size:1.15rem; max-width:600px; margin:0 auto 1rem auto;">
        Local-first AI routing — save tokens, reduce costs, and get answers faster.
    </p>
</div>
""", unsafe_allow_html=True)

# ========== LIVE STATS (Accurate Counts) ==========
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
    saved_percent = 0
    if st.session_state.total_queries > 0:
        saved_percent = int((st.session_state.local_count / st.session_state.total_queries) * 100)
    st.markdown(f"""
    <div class="glass-card">
        <div class="stat-number" style="color:#f59e0b;">{saved_percent}%</div>
        <div class="stat-label">💰 Tokens Saved</div>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# ========== REMOVE NON-FUNCTIONAL TABS ==========
# Instead of visual tabs, just a heading
st.markdown("### 🧠 Smart Routing Engine")

# ========== VIDEO + OVERLAY ==========
st.markdown("""
<div class="video-wrapper">
    <video autoplay loop muted playsinline>
        <source src="https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260319_165750_358b1e72-c921-48b7-aaac-f200994f32fb.mp4" type="video/mp4">
    </video>
    <div class="overlay-card">
        <h4>⚡ Ask me anything</h4>
        <p>I'll try local first (FREE) and escalate to cloud only if unsure.</p>
    </div>
</div>
""", unsafe_allow_html=True)

# ========== LIVE INTERACTION ==========
st.markdown("### 💬 Live Interaction")
query = st.text_area("", placeholder="Type your question here...", height=80, label_visibility="collapsed")

if st.button("🚀 Route Query", type="primary"):
    if not query.strip():
        st.warning("Please enter a query.")
    else:
        with st.spinner("⏳ Routing your query..."):
            try:
                # Check backend
                health = requests.get(f"{BACKEND_URL}/health", timeout=3)
                if health.status_code != 200:
                    st.error("❌ Backend not healthy.")
                    st.stop()
                
                # Send query
                start_time = time.time()
                response = requests.post(
                    f"{BACKEND_URL}/route",
                    json={"query": query},
                    timeout=30
                )
                latency_ms = (time.time() - start_time) * 1000
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # --- UPDATE STATS (ONLY ON SUCCESS) ---
                    st.session_state.total_queries += 1
                    
                    # Determine source from response
                    source = data.get("source", "unknown").lower()
                    if source == "cloud":
                        st.session_state.cloud_count += 1
                        badge_class = "cloud"
                        badge_text = "☁️ CLOUD"
                    else:
                        st.session_state.local_count += 1
                        badge_class = ""
                        badge_text = "🟢 LOCAL (FREE)"
                    
                    # Update tokens saved (only if local)
                    tokens_saved = data.get("tokens_saved", 0)
                    if source == "local":
                        st.session_state.tokens_saved += tokens_saved
                    
                    # Store history (keep last 5)
                    st.session_state.history.append({
                        "query": query,
                        "answer": data.get('content', 'No answer'),  # our router returns 'content'
                        "source": source.upper(),
                        "confidence": data.get('confidence', 0),
                        "latency": f"{latency_ms:.0f} ms"
                    })
                    if len(st.session_state.history) > 5:
                        st.session_state.history.pop(0)
                    
                    # Display answer
                    st.markdown(f"""
                    <div class="answer-box {badge_class}">
                        <span class="badge-{badge_class if badge_class else 'local'}">{badge_text}</span>
                        <p style="margin-top:0.5rem;"><strong>Answer:</strong> {data.get('content', 'No answer')}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Routing details
                    col_a, col_b, col_c, col_d = st.columns(4)
                    confidence = data.get('confidence', 0)
                    col_a.metric("Source", source.upper())
                    col_b.metric("Confidence", f"{confidence:.2f}" if confidence else "N/A")
                    col_c.metric("Tokens Saved", tokens_saved, delta="FREE" if source=="local" else None)
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

# ========== RECENT INTERACTIONS (EXACTLY 5 OR NONE) ==========
if st.session_state.history:
    st.markdown("### 📋 Recent Interactions")
    for log in reversed(st.session_state.history):
        badge = "🟢 LOCAL (FREE)" if log["source"] == "LOCAL" else "🔴 CLOUD"
        st.markdown(f"""
        <div style="background:#f9fafb; padding:0.8rem 1rem; border-radius:10px; margin-bottom:0.5rem; border-left:3px solid {'#10b981' if log['source']=='LOCAL' else '#ef4444'};">
            <span style="font-weight:500;">❓ {log['query']}</span><br>
            <span style="font-size:0.9rem; color:#6b7280;">{badge} | Confidence: {log['confidence']:.2f} | Latency: {log['latency']}</span>
            <p style="margin:0.3rem 0 0 0; font-size:0.95rem;"><strong>Answer:</strong> {log['answer'][:100]}{'...' if len(log['answer'])>100 else ''}</p>
        </div>
        """, unsafe_allow_html=True)

# ========== FOOTER ==========
st.markdown("""
<div style="text-align: center; padding: 1rem 0; border-top: 1px solid #e5e7eb; margin-top: 1.5rem;">
    <div style="font-weight: 700; color: #ED1C24; font-size: 1.1rem;">🦂 Team Scorpians</div>
    <div style="margin-top: 0.3rem;">
        <a href="https://github.com/Awais-0806/Team-Scorpians-Routing-Agent" target="_blank" style="color: #6b7280; text-decoration: none;">
            🔗 GitHub: Awais-0806/Team-Scorpians-Routing-Agent
        </a>
    </div>
    <div style="color: #9ca3af; font-size: 0.85rem;">AMD Hackathon ACT II · Track 1 · July 2026</div>
</div>
""", unsafe_allow_html=True)

st.divider()
st.caption("Built with ❤️ by Team Scorpians | AMD Hackathon 2026")