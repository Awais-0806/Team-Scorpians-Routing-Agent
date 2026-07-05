"""
Team Scorpians - Streamlit Demo UI
Addresses judge feedback: "No UI/UX - it's just an API"

Shows the routing decision LIVE and visually: which model answered,
whether it escalated to cloud, tokens spent, and cost -- this is the
single most convincing thing you can show a judge in 30 seconds.

Run:  streamlit run streamlit_app.py
(Assumes the agent's /route endpoint is reachable -- set API_URL if it's
not on localhost:8080, e.g. when running this on your own laptop against
the deployed Droplet.)
"""

import os
import requests
import streamlit as st

API_URL = os.getenv("API_URL", "http://localhost:8080")

st.set_page_config(page_title="Team Scorpians - Routing Agent", page_icon="🦂", layout="centered")

st.title("🦂 Team Scorpians — Hybrid Token-Efficient Routing Agent")
st.caption("Local-first Gemma cascade — free by default, cloud only when needed.")

query = st.text_area("Ask a question:", placeholder="e.g. What is the capital of Pakistan?", height=100)

col1, col2 = st.columns([1, 4])
with col1:
    submit = st.button("Route Query", type="primary")

if submit and query.strip():
    with st.spinner("Routing through the local-first cascade..."):
        try:
            resp = requests.post(f"{API_URL}/route", json={"query": query}, timeout=60)
            resp.raise_for_status()
            result = resp.json()
        except Exception as e:
            st.error(f"Could not reach the agent at {API_URL}: {e}")
            st.stop()

    escalated = result.get("escalated", False)

    if escalated:
        st.markdown("### 🔴 Routed to **CLOUD** (Fireworks — Gemma 4 31B IT)")
        st.caption("Local model wasn't confident enough, so this cost real tokens.")
    else:
        st.markdown("### 🟢 Answered **LOCALLY** (Gemma 4 E4B on ROCm)")
        st.caption("Zero tokens counted on the leaderboard — this is the free path.")

    st.write(result.get("answer", ""))

    st.divider()
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Model used", result.get("model_used", "-").split("/")[-1])
    m2.metric("Confidence", f"{result.get('confidence', 0):.2f}" if result.get("confidence") is not None else "-")
    m3.metric("Cloud tokens", result.get("cloud_tokens", 0))
    m4.metric("Latency", f"{result.get('latency_s', 0):.2f}s")

    if result.get("cloud_cost_usd"):
        st.caption(f"Estimated cloud cost for this query: ${result['cloud_cost_usd']:.6f}")

    with st.expander("Raw response (for debugging / judges who want to see the JSON)"):
        st.json(result)

elif submit:
    st.warning("Type a question first.")

st.divider()
st.caption("AMD Developer Hackathon: ACT II — Track 1 + Best Use of Gemma")
