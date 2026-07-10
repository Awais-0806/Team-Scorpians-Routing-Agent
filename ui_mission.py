"""
Team Scorpians - Mission Log UI
AMD Hackathon ACT II - Track 1
Run: streamlit run ui_mission.py
"""

import streamlit as st
import datetime
import requests
import plotly.graph_objects as go

BACKEND_URL = "http://localhost:8080"
API_KEY = "myHackathonKey2026"

st.set_page_config(page_title="Scorpion Mission Log", page_icon="🦂", layout="wide")

# ---------- CSS (Dark Terminal + Glassmorphism) ----------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Inter:wght@400;600;700&display=swap');

    body, .stApp {
        background: #0A0A0A;
        color: #E0E0E0;
        font-family: 'Inter', sans-serif;
    }
    .stApp::before {
        content: "";
        position: fixed;
        top: 0; left: 0; right: 0; bottom: 0;
        background: repeating-linear-gradient(0deg, rgba(237,28,36,0.02) 0px, transparent 1px, transparent 40px),
                    repeating-linear-gradient(90deg, rgba(237,28,36,0.02) 0px, transparent 1px, transparent 40px);
        pointer-events: none;
    }

    [data-testid="stSidebar"] {
        background: #0A0A0A;
        border-right: 1px solid rgba(237,28,36,0.3);
    }

    .log-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 8px 12px;
        margin: 4px 0;
        background: rgba(18,18,18,0.8);
        border-left: 4px solid #00C853;
        border-radius: 4px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 13px;
        transition: background 0.2s;
    }
    .log-row.cloud { border-left-color: #FF6D00; }
    .log-row:hover { background: rgba(30,30,30,0.8); }

    .stat-box {
        text-align: center;
        margin-bottom: 16px;
    }
    .stat-value {
        font-family: 'JetBrains Mono', monospace;
        font-size: 28px;
        font-weight: 700;
        color: #00C853;
    }
    .stat-label {
        font-size: 10px;
        text-transform: uppercase;
        color: #888;
    }
    .cmd-field input {
        background: #0A0A0A !important;
        border: 1px solid #ED1C24 !important;
        color: #E0E0E0 !important;
        font-family: 'JetBrains Mono', monospace !important;
        border-radius: 4px !important;
    }
    .execute-btn {
        background: linear-gradient(135deg, #ED1C24, #c8102e) !important;
        color: white !important;
        font-weight: 700 !important;
        border-radius: 4px !important;
        letter-spacing: 1px;
    }
</style>
""", unsafe_allow_html=True)

# ---------- Session State ----------
if 'total' not in st.session_state:
    st.session_state.total = 0
    st.session_state.local_cnt = 0
    st.session_state.cloud_cnt = 0
    st.session_state.log = []
    st.session_state.saved_tokens = 0
    st.session_state.latency_sum = 0

def query_backend(query):
    try:
        resp = requests.post(f"{BACKEND_URL}/chat",
                             json={"query": query, "api_key": API_KEY},
                             timeout=120)
        if resp.status_code == 200:
            return resp.json()
    except:
        pass
    return {"answer": "Connection error", "source": "error", "confidence": 0.0,
            "tokens_saved": 0, "latency_ms": 0}

# ---------- Sidebar Stats ----------
with st.sidebar:
    st.markdown("# 🦂 SCORPIANS")
    st.markdown("**Mission Command**")
    st.divider()
    total = st.session_state.total
    local = st.session_state.local_cnt
    cloud = st.session_state.cloud_cnt
    saved = st.session_state.saved_tokens
    avg_lat = round(st.session_state.latency_sum / max(total, 1)) if total else 0

    st.markdown(f"<div class='stat-box'><div class='stat-value'>{total}</div><div class='stat-label'>Total Missions</div></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='stat-box'><div class='stat-value'>{round((local/max(total,1))*100)}%</div><div class='stat-label'>Local</div></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='stat-box'><div class='stat-value'>{round((local/max(total,1))*100)}%</div><div class='stat-label'>Tokens Saved</div></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='stat-box'><div class='stat-value'>{avg_lat} ms</div><div class='stat-label'>Avg Latency</div></div>", unsafe_allow_html=True)

    # Efficiency gauge
    eff = round((local / max(total, 1)) * 100)
    fig = go.Figure(go.Indicator(mode="gauge+number", value=eff, title={'text': "Efficiency"},
                                 gauge={'axis': {'range': [0,100]}, 'bar': {'color': "#00C853"},
                                        'steps': [{'range': [0,50], 'color': "rgba(255,109,0,0.3)"},
                                                  {'range': [50,80], 'color': "rgba(255,255,0,0.3)"},
                                                  {'range': [80,100], 'color': "rgba(0,200,83,0.3)"}],
                                        'threshold': {'line': {'color': "white"}, 'value': 90}}))
    fig.update_layout(height=200, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
    st.plotly_chart(fig, use_container_width=True)

# ---------- Main Mission Log ----------
st.markdown("## 🦂 MISSION LOG")
with st.form("query_form", clear_on_submit=True):
    cols = st.columns([5,1])
    with cols[0]:
        query = st.text_input("Enter query", placeholder=">_ type mission...", label_visibility="collapsed")
    with cols[1]:
        submit = st.form_submit_button("EXECUTE", type="primary")
if submit and query:
    with st.spinner("Routing..."):
        res = query_backend(query)
        # update counters
        st.session_state.total += 1
        st.session_state.latency_sum += res.get("latency_ms", 0)
        if res.get("source") == "local":
            st.session_state.local_cnt += 1
            st.session_state.saved_tokens += res.get("tokens_saved", 150)
        elif res.get("source") == "cloud":
            st.session_state.cloud_cnt += 1
        st.session_state.log.append({
            "time": datetime.datetime.now().strftime("%H:%M:%S"),
            "query": query,
            "answer": res.get("answer", ""),
            "source": res.get("source", "unknown"),
            "confidence": res.get("confidence", 0),
            "latency": res.get("latency_ms", 0),
            "tokens_saved": res.get("tokens_saved", 0)
        })
    st.rerun()

# Show log entries
if st.session_state.log:
    for entry in reversed(st.session_state.log):
        css = "log-row cloud" if entry['source'] == 'cloud' else "log-row"
        st.markdown(f"""
        <div class="{css}">
            <span style="flex:1">{entry['time']}</span>
            <span style="flex:3">> {entry['query'][:50]}</span>
            <span style="flex:1">{entry['source'].upper()}</span>
            <span style="flex:1">conf {entry['confidence']:.2f}</span>
            <span style="flex:1">{entry['latency']:.0f}ms</span>
        </div>
        """, unsafe_allow_html=True)
        with st.expander("See full response"):
            st.write(entry['answer'])
else:
    st.markdown("<span style='color:#888;'>Awaiting missions...</span>", unsafe_allow_html=True)