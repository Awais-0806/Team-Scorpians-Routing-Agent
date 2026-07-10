"""
AMD Scorpion Command Center - Streamlit UI
Team Scorpians - AMD Hackathon ACT II - Track 1
Run: streamlit run ui_final.py
"""

import streamlit as st
import datetime
import requests
import plotly.graph_objects as go
import time

# -------------------------------------------------------------------
# BACKEND CONFIG
# -------------------------------------------------------------------
BACKEND_URL = "http://localhost:8080"
API_KEY = "myHackathonKey2026"

# -------------------------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------------------------
st.set_page_config(
    page_title="Scorpion Command Center",
    page_icon="🦂",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -------------------------------------------------------------------
# CUSTOM CSS – FULL THEME
# -------------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&family=Inter:wght@400;500;600;700&display=swap');

    /* ---- GLOBAL ---- */
    body, .stApp {
        font-family: 'Inter', sans-serif;
        background-color: #0B0E14;
        color: #FFFFFF;
    }
    .stApp {
        background-image: repeating-linear-gradient(0deg, rgba(237,28,36,0.03) 0px, rgba(237,28,36,0.03) 1px, transparent 1px, transparent 40px),
                          repeating-linear-gradient(90deg, rgba(237,28,36,0.03) 0px, rgba(237,28,36,0.03) 1px, transparent 1px, transparent 40px);
    }

    /* ---- SIDEBAR ---- */
    [data-testid="stSidebar"] {
        background-color: #0B0E14 !important;
        border-right: 1px solid rgba(237,28,36,0.2);
        min-width: 220px !important;
        max-width: 220px !important;
    }
    [data-testid="stSidebar"] > div:first-child {
        padding-top: 20px;
    }

    /* ---- GLASS CARDS ---- */
    .glass-card {
        background: rgba(18, 22, 28, 0.8);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(237,28,36,0.15);
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
        transition: all 0.3s ease;
    }
    .glass-card:hover {
        border-color: rgba(237,28,36,0.4);
        box-shadow: 0 0 15px rgba(237,28,36,0.15);
    }

    /* ---- SIDEBAR LOGO PULSE ---- */
    .logo-ring {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 80px;
        height: 80px;
        border-radius: 50%;
        border: 2px solid #ED1C24;
        margin: 0 auto;
        animation: pulse-ring 2s infinite;
        font-size: 40px;
    }
    @keyframes pulse-ring {
        0% { box-shadow: 0 0 0 0 rgba(237,28,36,0.6); }
        70% { box-shadow: 0 0 0 15px rgba(237,28,36,0); }
        100% { box-shadow: 0 0 0 0 rgba(237,28,36,0); }
    }

    /* ---- CONNECTION STATUS ---- */
    .status-dot {
        width: 10px;
        height: 10px;
        background-color: #00C853;
        border-radius: 50%;
        display: inline-block;
        margin-right: 6px;
        animation: blink 1.5s infinite;
    }
    @keyframes blink {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.3; }
    }

    /* ---- STAT NUMBERS ---- */
    .stat-value {
        font-family: 'JetBrains Mono', monospace;
        font-size: 24px;
        font-weight: 700;
        color: #00C853;
        text-align: center;
    }
    .stat-label {
        font-size: 11px;
        color: #AAAAAA;
        text-transform: uppercase;
        letter-spacing: 1px;
        text-align: center;
    }

    /* ---- TOKEN BURN BAR ---- */
    .burn-bar-container {
        background: rgba(255,255,255,0.05);
        border-radius: 8px;
        height: 12px;
        margin-top: 8px;
        overflow: hidden;
    }
    .burn-bar {
        height: 100%;
        width: 0%;
        background: linear-gradient(90deg, #00C853, #00E676);
        border-radius: 8px;
        transition: width 0.5s ease;
    }

    /* ---- COMMAND LINE INPUT ---- */
    .cmd-input {
        background: rgba(18,22,28,0.8);
        border: 1px solid rgba(237,28,36,0.3);
        border-radius: 8px;
        font-family: 'JetBrains Mono', monospace;
        color: #FFFFFF;
        padding: 12px 16px;
        width: 100%;
        caret-color: #ED1C24;
        animation: blink-cursor 1s infinite;
    }
    .cmd-input:focus {
        outline: none;
        border-color: #ED1C24;
        box-shadow: 0 0 10px rgba(237,28,36,0.2);
    }
    @keyframes blink-cursor {
        0%, 100% { caret-color: #ED1C24; }
        50% { caret-color: transparent; }
    }

    .execute-btn {
        background: linear-gradient(135deg, #ED1C24, #c8102e);
        border: none;
        color: white;
        padding: 12px 30px;
        border-radius: 8px;
        font-weight: 700;
        font-family: 'Inter', sans-serif;
        letter-spacing: 1px;
        cursor: pointer;
        transition: all 0.3s ease;
        text-transform: uppercase;
    }
    .execute-btn:hover {
        box-shadow: 0 0 20px rgba(237,28,36,0.5);
        transform: translateY(-2px);
    }

    /* ---- MISSION LOG ROW ---- */
    .log-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 10px 16px;
        border-radius: 8px;
        margin-bottom: 6px;
        background: rgba(18,22,28,0.6);
        border-left: 4px solid #00C853;
        animation: localPulse 0.6s ease;
    }
    .log-row.cloud {
        border-left-color: #FF6D00;
        animation: cloudPulse 0.6s ease;
    }
    @keyframes localPulse {
        0% { background: rgba(0,200,83,0.15); }
        100% { background: rgba(18,22,28,0.6); }
    }
    @keyframes cloudPulse {
        0% { background: rgba(255,109,0,0.15); }
        100% { background: rgba(18,22,28,0.6); }
    }
    .log-meta {
        font-family: 'JetBrains Mono', monospace;
        font-size: 12px;
        color: #AAAAAA;
    }

    /* ---- RADAR DONUT ---- */
    .radar-container {
        position: relative;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .radar-ring {
        position: absolute;
        width: 100px;
        height: 100px;
        border: 2px dashed rgba(237,28,36,0.3);
        border-radius: 50%;
        animation: rotate-ring 8s linear infinite;
    }
    @keyframes rotate-ring {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }

    /* ---- EFFICIENCY GAUGE ---- */
    .gauge-label {
        font-size: 14px;
        color: #AAAAAA;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------------
# SESSION STATE
# -------------------------------------------------------------------
if "total_queries" not in st.session_state:
    st.session_state.total_queries = 0
if "local_count" not in st.session_state:
    st.session_state.local_count = 0
if "cloud_count" not in st.session_state:
    st.session_state.cloud_count = 0
if "mission_log" not in st.session_state:
    st.session_state.mission_log = []
if "total_tokens_saved" not in st.session_state:
    st.session_state.total_tokens_saved = 0
if "total_latency" not in st.session_state:
    st.session_state.total_latency = 0

# -------------------------------------------------------------------
# HELPER: BACKEND CALL
# -------------------------------------------------------------------
def call_backend(query_text):
    try:
        resp = requests.post(
            f"{BACKEND_URL}/chat",
            json={"query": query_text, "api_key": API_KEY},
            timeout=120,
        )
        resp.raise_for_status()
        data = resp.json()
        return {
            "timestamp": datetime.datetime.now().strftime("%H:%M:%S"),
            "query": query_text,
            "answer": data.get("answer", ""),
            "source": data.get("source", "unknown"),
            "confidence": data.get("confidence", 0.0),
            "latency": data.get("latency_ms", 0),
            "tokens_saved": data.get("tokens_saved", 0),
        }
    except Exception as e:
        return {
            "timestamp": datetime.datetime.now().strftime("%H:%M:%S"),
            "query": query_text,
            "answer": f"[Error] {str(e)}",
            "source": "error",
            "confidence": 0.0,
            "latency": 0,
            "tokens_saved": 0,
        }

# -------------------------------------------------------------------
# SIDEBAR
# -------------------------------------------------------------------
with st.sidebar:
    # Logo
    st.markdown("<div class='logo-ring'>🦂</div>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; font-weight:700; font-size:18px; color:#ED1C24;'>SCORPIANS</p>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; font-size:12px; color:#AAAAAA;'>COMMAND CENTER</p>", unsafe_allow_html=True)
    st.markdown("---")

    # Connection status
    st.markdown("<span class='status-dot'></span> <span style='color:#00C853; font-weight:600;'>ONLINE</span>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # Quick stats
    total_q = st.session_state.total_queries
    local_percent = round((st.session_state.local_count / max(total_q, 1)) * 100) if total_q else 0
    tokens_saved_pct = round((st.session_state.local_count / max(total_q, 1)) * 100) if total_q else 0
    avg_lat = round(st.session_state.total_latency / total_q) if total_q else 0

    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown(f"<div class='stat-value'>{total_q}</div><div class='stat-label'>Total Queries</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='stat-value'>{local_percent}%</div><div class='stat-label'>Local</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='stat-value'>{tokens_saved_pct}%</div><div class='stat-label'>Tokens Saved</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='stat-value'>{avg_lat}ms</div><div class='stat-label'>Avg Latency</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Token Burn Rate
    st.markdown("<p style='font-weight:600; margin-top:20px;'>TOKEN BURN RATE</p>", unsafe_allow_html=True)
    # Simulate: without hybrid, each query would cost 100 tokens; with hybrid we saved tokens
    saved_tokens = st.session_state.local_count * 100  # 100 tokens saved per local query
    total_possible = total_q * 100 if total_q else 1
    burn_width = ((total_possible - saved_tokens) / total_possible) * 100 if total_q else 100
    st.markdown(f"""
        <div class='burn-bar-container'>
            <div class='burn-bar' style='width:{burn_width}%;'></div>
        </div>
        <div style='display:flex; justify-content:space-between; font-size:10px; color:#AAAAAA;'>
            <span>Actual</span><span>Without Hybrid</span>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("<p style='font-size:12px; color:#AAAAAA; text-align:center;'>AMD ROCm | Fireworks AI</p>", unsafe_allow_html=True)

# -------------------------------------------------------------------
# MAIN LAYOUT: CENTER + RIGHT PANEL
# -------------------------------------------------------------------
col_center, col_right = st.columns([3, 1])

# ======================== CENTER ========================
with col_center:
    st.markdown("<h2 style='margin-top:0;'>MISSION LOG</h2>", unsafe_allow_html=True)

    # Command input
    with st.form("query_form"):
        cmd_col, btn_col = st.columns([5, 1])
        with cmd_col:
            user_input = st.text_input(
                "QUERY",
                placeholder="Enter your mission query...",
                label_visibility="collapsed",
                key="cmd_input"
            )
        with btn_col:
            submitted = st.form_submit_button("EXECUTE", type="primary")

    if submitted and user_input.strip():
        with st.spinner("Processing..."):
            result = call_backend(user_input.strip())
        # Update stats
        st.session_state.total_queries += 1
        if result["source"] == "local":
            st.session_state.local_count += 1
            st.session_state.total_tokens_saved += result.get("tokens_saved", 100)
        elif result["source"] == "cloud":
            st.session_state.cloud_count += 1
        st.session_state.total_latency += result["latency"]
        # Add to mission log
        st.session_state.mission_log.append(result)
        st.rerun()

    # Display mission log
    if st.session_state.mission_log:
        for idx, entry in enumerate(reversed(st.session_state.mission_log)):
            is_local = entry["source"] == "local"
            css_class = "log-row" if is_local else "log-row cloud"
            decision = "LOCAL" if is_local else ("CLOUD" if entry["source"] == "cloud" else "ERROR")
            with st.expander(
                f"{entry['timestamp']}  |  {entry['query'][:40]}...  |  {decision}  |  {entry['confidence']:.2f}  |  {entry['latency']:.0f}ms",
                expanded=False,
            ):
                st.markdown(f"**Answer:** {entry['answer']}")
                st.markdown(f"**Confidence:** {entry['confidence']:.2f}  |  **Latency:** {entry['latency']:.0f}ms  |  **Tokens Saved:** ~{entry.get('tokens_saved',0)}")
    else:
        st.markdown("<p style='color:#AAAAAA;'>No missions executed yet. Enter a query above.</p>", unsafe_allow_html=True)

# ======================== RIGHT PANEL ========================
with col_right:
    # Radar donut chart
    local = st.session_state.local_count
    cloud = st.session_state.cloud_count
    if local + cloud == 0:
        local, cloud = 1, 0
    fig = go.Figure(data=[go.Pie(
        labels=["Local (FREE)", "Cloud (paid)"],
        values=[local, cloud],
        hole=0.7,
        marker_colors=["#00C853", "#FF6D00"],
        textinfo="none",
        hoverinfo="label+percent"
    )])
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="white",
        margin=dict(t=0, b=0, l=0, r=0),
        showlegend=False,
        height=200,
    )
    st.markdown("<div class='radar-container'>", unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    st.markdown("<div class='radar-ring'></div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; font-weight:600;'>ROUTING RADAR</p>", unsafe_allow_html=True)

    # Last route card
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("<p style='font-weight:600;'>LAST ROUTE</p>", unsafe_allow_html=True)
    if st.session_state.mission_log:
        last = st.session_state.mission_log[-1]
        st.markdown(f"**Query:** {last['query'][:50]}...")
        st.markdown(f"**Confidence:** {last['confidence']:.2f}")
        st.markdown(f"**Model:** {last['source']}")
        st.markdown(f"**Tokens Saved:** {last.get('tokens_saved', 0)}")
    else:
        st.markdown("<span style='color:#AAAAAA;'>No data yet</span>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Peak efficiency gauge
    efficiency_pct = round((st.session_state.local_count / max(total_q, 1)) * 100) if total_q else 0
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=efficiency_pct,
        title={'text': "PEAK EFFICIENCY"},
        gauge={
            'axis': {'range': [0, 100], 'tickcolor': "white"},
            'bar': {'color': "#00C853"},
            'steps': [
                {'range': [0, 50], 'color': "rgba(255,109,0,0.2)"},
                {'range': [50, 80], 'color': "rgba(255,255,0,0.2)"},
                {'range': [80, 100], 'color': "rgba(0,200,83,0.2)"}
            ],
            'threshold': {'line': {'color': "white", 'width': 2}, 'value': 90}
        },
        number={'font': {'color': 'white', 'family': 'JetBrains Mono'}},
    ))
    fig_gauge.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="white",
        height=180,
        margin=dict(t=20, b=0, l=0, r=0),
    )
    st.plotly_chart(fig_gauge, use_container_width=True, config={'displayModeBar': False})