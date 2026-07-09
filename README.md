🦂 Team Scorpians — Hybrid Token-Efficient Routing Agent

[![AMD](https://img.shields.io/badge/AMD-ED1C24?style=for-the-badge&logo=amd&logoColor=white)](https://www.amd.com)
[![ROCm](https://img.shields.io/badge/ROCm-ED1C24?style=for-the-badge&logo=amd&logoColor=white)](https://www.amd.com/en/developer/rocm.html)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://docker.com)
[![Ollama](https://img.shields.io/badge/Ollama-000000?style=for-the-badge&logo=ollama&logoColor=white)](https://ollama.com)
[![Hackathon](https://img.shields.io/badge/AMD_Hackathon_ACT_II-ED1C24?style=for-the-badge&logo=amd&logoColor=white)](https://lablab.ai)

**Built for the AMD Developer Hackathon: ACT II (July 6–11, 2026)**  
**Track 1 — Hybrid Token-Efficient Routing Agent**  
**Bonus Target — Best Use of Gemma Models**

---

## 🎯 What This Does

Answers every query with a small **Gemma 3 model running locally via Ollama** first. Local tokens count as **zero** toward Track 1's score, so the agent only pays for the cloud model on **Fireworks AI** when the local model is genuinely unsure.

> **The result:** Up to **80% token cost savings** without sacrificing accuracy.

---

## 🏗️ Architecture
User Query
│
▼
Heuristic Pre-Filter ──(obviously hard?)──► Escalate to Cloud
│
▼
Local Gemma 3 1B (Ollama) ── asked TWICE at temperature 0.3
│
▼
Self-Consistency Check (Compare both answers)
│
├─── Answers AGREE ───► Return Local Answer ── (COST: 0 TOKENS) ✅
│
└─── Answers DISAGREE ───► Escalate to Fireworks AI
│
▼
Phi-3 Mini (Cloud)
│
▼
Return Cloud Answer (COST: REAL TOKENS)

text

**Why this wins:** Track 1's scoring rule states local tokens count as **zero**. The optimal strategy: **try free first, only pay when you absolutely must.**

---

## 📖 Our Journey: Challenges & How We Overcame Them

Every hackathon project has a story. This is ours.

**We were a team of two — until kickoff.** Awais and Muhammad Ekremah handled everything: infrastructure, code, documentation, slides, and deployment.

**The AMD Cloud credits almost broke us.** We requested our $100 credits, only to learn they required a 2-business-day approval. The hackathon started in 24 hours. We pivoted, used **Ollama + Gemma 3 locally**, and stayed ready.

**Hugging Face's gated model was a trap.** Ekremah caught it early, accepted the agreement, and generated the READ token we needed.

**Fireworks AI 404 errors haunted us.** We tried multiple model IDs — Gemma 4, Gemma 2, Llama, Mistral — all failed. Finally, **Phi-3 Mini** worked.

**We turned AI into a teammate.** With only two people, we used **Claude** and **DeepSeek** strategically — for code review, debugging, and documentation acceleration.

**Windows had no GPU.** We used **Ollama CPU mode** — slower (4-8 seconds), but works perfectly for demo.

> **We didn't just build a project. We fought for it.** Every line of code, every API key, every slide was earned through grit, smart decision-making, and unwavering belief in our vision.

---

## 🛠️ Tech Stack

| Layer | Tool |
|-------|------|
| **Local Inference** | Ollama + Gemma 3 1B (CPU) |
| **Cloud Inference** | Fireworks AI — Phi-3 Mini |
| **Agent** | Python + FastAPI (`app/` folder) |
| **Frontend (Demo)** | Streamlit (`streamlit_app.py`) |
| **Cache** | In-memory (Redis optional) |
| **AI Assistants** | Claude + DeepSeek |

---

## 👥 Team

| Name | Role |
|------|------|
| **Muhammad Awais** | Team Captain / Backend / UI / DevOps |
| **Muhammad Ekremah** | AI / ML Engineer / API Keys |

---

## 📦 Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/Awais-0806/Team-Scorpians-Routing-Agent.git
cd Team-Scorpians-Routing-Agent
2. Install Ollama (Local Model)
Windows:

Download from: https://ollama.com/download/windows

Install and run: ollama serve

Pull Gemma 3 1B (Fast):

bash
ollama pull gemma3:1b
Test:

bash
ollama run gemma3:1b "What is the capital of Pakistan?"
3. Create Environment File
bash
cp .env.example .env
Then fill in:

env
HOST=0.0.0.0
PORT=8080
LOCAL_LLM_URL=http://localhost:11434/api/generate
LOCAL_LLM_API_KEY=
FIREWORKS_API_URL=https://api.fireworks.ai/inference/v1/chat/completions
FIREWORKS_API_KEY=your_fireworks_key_here
FIREWORKS_MODEL=accounts/fireworks/models/phi-3-mini-4k-instruct
API_KEY=myHackathonKey2026
RATE_LIMIT=100/minute
CONFIDENCE_THRESHOLD=0.6
SELF_CONSISTENCY_SAMPLES=2
Where to get them:

FIREWORKS_API_KEY: Fireworks AI → Dashboard → API Keys

HF_TOKEN: Hugging Face Settings → Generate "Read" token

4. Install Python Dependencies
bash
pip install -r requirements.txt
5. Run the Agent (Backend)
bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8080
6. Run Streamlit UI (Frontend)
bash
streamlit run streamlit_app.py --server.port 8501
7. Open Browser
text
http://localhost:8501
🔧 Test the API
Health Check
bash
curl http://localhost:8080/health
Simple Query (Local Response)
bash
curl -X POST http://localhost:8080/chat -H "Content-Type: application/json" -d "{\"query\": \"What is the capital of Pakistan?\", \"api_key\": \"myHackathonKey2026\"}"
Hard Query (Escalates to Cloud)
bash
curl -X POST http://localhost:8080/chat -H "Content-Type: application/json" -d "{\"query\": \"Derive why merge sort has O(n log n) time complexity, step by step.\", \"api_key\": \"myHackathonKey2026\"}"
🧠 Confidence Gate — The Secret Sauce
"Instead of guessing whether a question is 'easy' or 'hard' in advance, we let the local model tell us. We ask it the same question twice, with a bit of randomness turned on. If a model actually knows the answer, it gives the same answer both times. If it's guessing, the two answers drift apart. Two answers that agree = confident, keep it local and free. Two answers that disagree = unsure, send it to the bigger cloud model. "

The Math: agreement_score = (matching answers) / (total answers sampled)

With 2 samples: either 1.0 (both matched) or 0.5 (they didn't).

Want a more graduated score? Set SELF_CONSISTENCY_SAMPLES=3 → scores can be 1.0, 0.67, or 0.33.

📁 Repository Structure
text
.
├── app/
│   ├── __init__.py
│   ├── cache.py
│   ├── classifier.py
│   ├── clients.py
│   ├── confidence.py
│   ├── config.py
│   ├── logger.py
│   ├── main.py
│   ├── metrics.py
│   ├── models.py
│   ├── prompts.py
│   ├── router.py
│   ├── security.py
│   └── utils.py
├── streamlit_app.py          # Streamlit UI
├── requirements.txt
├── .env.example
├── .gitignore
├── LICENSE
└── README.md
📋 Submission Checklist
Public GitHub Repository — github.com/Awais-0806/Team-Scorpians-Routing-Agent

Live Demo URL — Deployed on AMD Developer Cloud with Streamlit UI

5-Minute Video Presentation — Covers problem, solution, demo, and results

PDF Slide Deck — 9 professional slides (Title → Architecture → Results → Team)

Cover Image — 16:9 thumbnail for project submission

MIT License — Added to repository

Project Description — Clear problem-solution narrative on lablab.ai

Technology Tags — ROCm, vLLM, Fireworks AI, Gemma, Docker, FastAPI, Ollama

🏆 Hackathon Details
Detail	Info
Event	AMD Developer Hackathon: ACT II
Platform	lablab.ai
Dates	July 6–11, 2026
Track	Track 1 — Hybrid Token-Efficient Routing Agent
Bonus Target	Best Use of Gemma Models
Judging Criteria	Creativity, Originality, Technical Complexity, Product/Market Potential, Presentation Quality
📝 License
This project is licensed under the MIT License. See the LICENSE file for details.

🙏 Acknowledgments
AMD — For ROCm, Developer Cloud credits, and AI Academy resources

Fireworks AI — For cloud inference credits and API access

Hugging Face — For hosting the Gemma models

Ollama — For local model inference on CPU

lablab.ai — For organizing the hackathon and providing a platform to compete

Claude & DeepSeek — Our AI teammates who accelerated our development

🦂 Why We Will Win
We didn't just build a hybrid router. We built a story — of grit, smart decision-making, and relentless execution. Our local-first cascade is not just clever; it's mathematically optimal for Track 1's scoring. Our use of Gemma end-to-end is not just a feature; it's a coherent, judge-friendly narrative for the bonus prize. And our challenges — fought and overcome by just two people — prove that we have what it takes to win.

"Code. Collaborate. Conquer." — Team Scorpians 🦂

📬 Contact
Team Scorpians

GitHub: github.com/Awais-0806/Team-Scorpians-Routing-Agent

Lablab: team-scorpians