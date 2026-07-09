"""
Team Scorpians — Hybrid Token-Efficient Routing Agent
Streamlit UI for V2 (FastAPI + Ollama)
"""

import streamlit as st
import requests
import json
import time
import os

# Page Config
st.set_page_config(
    page_title="Team Scorpians - Hybrid Router V2",
    page_icon="🦂",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .stApp {
        background-color: #0D1117;
    }
    
    .main-title {
        color: #ED1C24;
        font-size: 42px;
        font-weight: 700;
        text-align: center;
        font-family: 'Inter', sans-serif;
    }
    
    .sub-title {
        color: #FFFFFF;
        font-size: 20px;
        text-align: center;
        font-family: 'Inter', sans-serif;
        opacity: 0.8;
    }
    
    .user-bubble {
        background-color: #2D2D44;
        color: #FFFFFF;
        padding: 12px 16px;
        border-radius: 12px;
        border-left: 4px solid #ED1C24;
        margin: 8px 0;
        font-family: 'Inter', sans-serif;
    }
    
    .assistant-bubble {
        background-color: #1A1A2E;
        color: #FFFFFF;
        padding: 12px 16px;
        border-radius: 12px;
        border-left: 4px solid #00C853;
        margin: 8px 0;
        font-family: 'Inter', sans-serif;
    }
    
    .metric-card {
        background-color: #1A1A2E;
        border: 1px solid #ED1C24;
        border-radius: 8px;
        padding: 12px 16px;
        margin: 4px 0;
        color: #FFFFFF;
    }
    
    .metric-label {
        color: #AAAAAA;
        font-size: 12px;
        font-weight: 400;
    }
    
    .metric-value {
        color: #FFFFFF;
        font-size: 18px;
        font-weight: 700;
    }
    
    .metric-value.local {
        color: #00C853;
    }
    
    .metric-value.cloud {
        color: #ED1C24;
    }
    
    .stTextInput input {
        background-color: #1A1A2E;
        border: 1px solid #ED1C24;
        border-radius: 8px;
        padding: 12px;
        color: #FFFFFF;
        font-size: 16px;
    }
    
    .stButton button {
        background-color: #ED1C24;
        color: #FFFFFF;
        border: none;
        border-radius: 8px;
        padding: 10px 24px;
        font-weight: 600;
        font-size: 16px;
    }
    
    .stButton button:hover {
        background-color: #FF3B3B;
        color: #FFFFFF;
    }
    
    hr {
        border-color: #2D2D44;
        margin: 20px 0;
    }
</style>
""", unsafe_allow_html=True)

# Header
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown('<p class="main-title">🦂 Team Scorpians</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Hybrid Token-Efficient Routing Agent V2</p>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center; color:#AAAAAA; font-size:14px;">Powered by Ollama + Fireworks AI</p>', unsafe_allow_html=True)
    st.markdown("---")

# API Configuration
API_URL = st.text_input(
    "Agent API URL",
    value="http://localhost:8080/chat",
    help="The URL where your FastAPI agent is running"
)

API_KEY = st.text_input(
    "API Key",
    value="myHackathonKey2026",
    type="password",
    help="API key for authentication"
)

# Session State
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! 👋 I'm your AI router. Ask me anything, and I'll use the cheapest model that can answer accurately."}
    ]

if "total_queries" not in st.session_state:
    st.session_state.total_queries = 0

# Sidebar
with st.sidebar:
    st.markdown("### 📊 Live Stats")
    st.metric("Total Queries", st.session_state.total_queries)
    
    st.markdown("---")
    
    st.markdown("### ⚙️ How It Works")
    st.markdown("""
    1. Query goes to **Local Gemma 3 4B** (Ollama)
    2. Asked **TWICE** (Self-Consistency)
    3. **Confidence Check**:
       - ✅ **Match** → Local Answer (FREE!)
       - ❌ **Differ** → Escalate to **Cloud** (Fireworks)
    """)
    
    st.markdown("---")
    
    st.markdown("### 🚀 Tech Stack")
    st.markdown("""
    - **Local Model:** Gemma 3 4B (Ollama)
    - **Cloud Model:** Fireworks AI (Gemma 2/Phi)
    - **Framework:** FastAPI + Ollama
    - **Container:** Uvicorn
    """)

# Chat Display
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f'<div class="user-bubble">🧑 <b>You:</b><br>{msg["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="assistant-bubble">🦂 <b>Agent:</b><br>{msg["content"]}</div>', unsafe_allow_html=True)

# Input
with st.container():
    col1, col2 = st.columns([4, 1])
    with col1:
        user_query = st.text_input(
            "Type your question here...",
            placeholder="e.g., What is the capital of Pakistan?",
            key="query_input",
            label_visibility="collapsed"
        )
    with col2:
        submit = st.button("🚀 Ask", use_container_width=True)

# Handle Submission
if submit and user_query:
    st.session_state.messages.append({"role": "user", "content": user_query})
    st.session_state.total_queries += 1
    
    with st.spinner("🧠 Thinking..."):
        try:
            response = requests.post(
                API_URL,
                json={"query": user_query, "api_key": API_KEY},
                timeout=120
            )
            
            if response.status_code == 200:
                data = response.json()
                
                answer = data.get("answer", "No answer received.")
                source = data.get("source", "unknown")
                confidence = data.get("confidence", 0)
                category = data.get("category", "general")
                cached = data.get("cached", False)
                request_id = data.get("request_id", "N/A")
                latency_ms = data.get("latency_ms", 0)
                
                # Emoji for source
                source_emoji = "🏠" if source == "local" else "☁️" if source == "cloud" else "⚠️"
                
                # Confidence color
                conf_color = "#00C853" if confidence > 0.7 else "#FF6D00" if confidence > 0.4 else "#ED1C24"
                
                display_text = f"""
**Answer:** {answer}

---
**📊 Routing Metadata:**
- **Source:** {source_emoji} `{source}` {'✅ (FREE!)' if source == 'local' else '💰 (Cost applies)'}
- **Confidence:** `{confidence:.2f}` {'✅' if confidence > 0.7 else '⚠️' if confidence > 0.4 else '❌'}
- **Category:** `{category}`
- **Cached:** `{'✅' if cached else '❌'}`
- **Latency:** `{latency_ms:.0f} ms`
- **Request ID:** `{request_id[:8]}...`
                """
                
                st.session_state.messages.append({"role": "assistant", "content": display_text})
                
            elif response.status_code == 401:
                st.session_state.messages.append({"role": "assistant", "content": f"❌ **Authentication Error:** Invalid API Key. Please check your API_KEY."})
            elif response.status_code == 404:
                st.session_state.messages.append({"role": "assistant", "content": f"❌ **Not Found:** The agent is not responding. Make sure `app.main` is running on `{API_URL}`"})
            else:
                st.session_state.messages.append({"role": "assistant", "content": f"❌ **Error:** {response.status_code} - {response.text[:200]}"})
                
        except requests.exceptions.ConnectionError:
            st.session_state.messages.append({"role": "assistant", "content": f"❌ **Connection Error:** Cannot reach the agent at `{API_URL}`\n\nMake sure `uvicorn app.main:app` is running."})
        except Exception as e:
            st.session_state.messages.append({"role": "assistant", "content": f"❌ **Unexpected Error:** {str(e)}"})
    
    st.rerun()

# Footer
st.markdown("---")
st.markdown(
    '<p style="text-align:center; color:#555555; font-size:12px;">'
    '🦂 Team Scorpians | Code. Collaborate. Conquer. | AMD Developer Hackathon: ACT II'
    '</p>',
    unsafe_allow_html=True
)