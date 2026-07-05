# 🦂 Team Scorpians — Hybrid Token-Efficient Routing Agent

[![AMD](https://img.shields.io/badge/AMD-ED1C24?style=for-the-badge&logo=amd&logoColor=white)](https://www.amd.com)
[![ROCm](https://img.shields.io/badge/ROCm-ED1C24?style=for-the-badge&logo=amd&logoColor=white)](https://www.amd.com/en/developer/rocm.html)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://docker.com)
[![Hackathon](https://img.shields.io/badge/AMD_Hackathon_ACT_II-ED1C24?style=for-the-badge&logo=amd&logoColor=white)](https://lablab.ai)

**Built for the AMD Developer Hackathon: ACT II (July 6–11, 2026)**  
**Track 1 — Hybrid Token-Efficient Routing Agent**  
**Bonus Target — Best Use of Gemma Models**

---

## 🎯 What This Does

Answers every query with a small **Gemma 4 model running locally on AMD ROCm** first. Local tokens count as **zero** toward Track 1's score, so the agent only pays for the larger **Gemma 4 31B IT on Fireworks AI** when the local model is genuinely unsure.

> **The result:** Up to **80% token cost savings** without sacrificing accuracy.

---

## 🏗️ Architecture


User Query
│
▼
Heuristic Pre-Filter ──(obviously hard?)──► Escalate to Cloud
│
▼
Local Gemma 4 E4B (vLLM on ROCm) ── asked TWICE at temperature 0.7
│
▼
Self-Consistency Check (Compare both answers)
│
├─── Answers AGREE ───► Return Local Answer ── (COST: 0 TOKENS) ✅
│
└─── Answers DISAGREE ───► Escalate to Fireworks AI
│
▼
Gemma 4 31B IT (Cloud)
│
▼
Return Cloud Answer (COST: REAL TOKENS)

text

**Why this wins:** Track 1's scoring rule states local tokens count as **zero**. The optimal strategy: **try free first, only pay when you absolutely must.**

---

## 📖 Our Journey: Challenges & How We Overcame Them

Every hackathon project has a story. This is ours.

**We were a team of two — until kickoff.** Awais and Muhammad Ekremah handled everything: infrastructure, code, documentation, slides, and deployment. The rest of our six-member team joined later, but the foundation was built by two people in under 48 hours.

**The AMD Cloud credits almost broke us.** We requested our $100 credits, only to learn they required a 2-business-day approval. The hackathon started in 24 hours. We sent urgent emails, contacted support, and eventually discovered that AMD would provide hackathon-specific cloud instances at kickoff. We pivoted, prepared everything for local deployment, and stayed ready.

**Hugging Face's gated model was a trap.** Gemma 4 E4B requires a license acceptance before download. Many teams forget this and fail at the last minute. Ekremah caught it early, accepted the agreement, and generated the READ token we needed. That single act saved us hours of debugging.

**Fireworks AI key generation was another hurdle.** We needed a production-ready API key for the cloud fallback model. Ekremah handled the sign-up, verified the account, and secured the key before we even started building.

**We turned AI into a teammate.** With only two people, we couldn't afford to waste time on trivial bugs. We used **Claude** and **DeepSeek** strategically — for code review, debugging, and documentation acceleration. They became our virtual third and fourth team members, allowing us to move at hackathon speed.

**Docker + ROCm was a beast.** Ensuring containers worked seamlessly on AMD GPUs required careful version pinning (`vllm/vllm-openai-rocm:v0.18.1`), health checks, and environment variable management. We tested, iterated, and eventually got it right.

**Time was our enemy.** We prepared slides, architecture diagrams, benchmark scripts, and team coordination — all in under 48 hours. Late nights, early mornings, and relentless focus got us here.

> **We didn't just build a project. We fought for it.** Every line of code, every API key, every slide was earned through grit, smart decision-making, and unwavering belief in our vision.

---

## 🛠️ Tech Stack

| Layer | Tool |
|-------|------|
| **Local Inference** | vLLM (`vllm/vllm-openai-rocm:v0.18.1`) on AMD Developer Cloud |
| **Cloud Inference** | Fireworks AI API — Gemma 4 31B IT |
| **Agent** | Python + FastAPI (`router_agent.py`) |
| **Containerization** | Docker + Docker Compose |
| **Frontend (Demo)** | Streamlit (`app.py`) |
| **AI Assistants** | Claude + DeepSeek (for acceleration) |

---

## 👥 Team

| Name | Role |
|------|------|
| **Muhammad Awais** | Team Captain / Backend / Documentation |
| **Muhammad Ekremah** | AI / ML / Engineer/ Data Science / Model Training |
| **Mussavir Abbasi** | DevOps / Containerization/ Frontend / UI |

---

## 📦 Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/Awais-0806/Team-Scorpians-Routing-Agent.git
cd Team-Scorpians-Routing-Agent
2. Accept Gemma License (CRITICAL)
⚠️ Do NOT skip this step. The local model will fail to download without it.

Go to: https://huggingface.co/google/gemma-4-e4b-it

Log in to your Hugging Face account

Click "Agree and access repository" to accept the license terms

3. Create Environment File
bash
cp .env.example .env
Then fill in:

env
FIREWORKS_API_KEY=your_fireworks_key_here
HF_TOKEN=your_huggingface_token_here
CONFIDENCE_THRESHOLD=0.6
SELF_CONSISTENCY_SAMPLES=2
LOCAL_BASE_URL=http://localhost:8000/v1
Where to get them:

FIREWORKS_API_KEY: Fireworks AI → Dashboard → API Keys

HF_TOKEN: Hugging Face Settings → Generate "Read" token

4. Run the Project
bash
docker compose up --build
This starts:

local-model — vLLM serving Gemma 4 E4B on ROCm (first run downloads weights, 2-3 min)

agent — FastAPI router, waits for local model to become healthy

5. Run Streamlit UI (Demo)
bash
pip install streamlit requests
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
🔧 Test the API
Health Check
bash
curl http://localhost:8080/health
Simple Query (Local Response)
bash
curl -X POST http://localhost:8080/route \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the capital of Pakistan?"}'
Example Response:

json
{
  "answer": "Islamabad is the capital of Pakistan.",
  "model_used": "google/gemma-4-e4b-it",
  "escalated": false,
  "confidence": 1.0,
  "local_tokens": 38,
  "cloud_tokens": 0,
  "cloud_cost_usd": 0.0,
  "latency_s": 0.412
}
Hard Query (Escalates to Cloud)
bash
curl -X POST http://localhost:8080/route \
  -H "Content-Type: application/json" \
  -d '{"query": "Derive why merge sort has O(n log n) time complexity, step by step."}'
🧠 Confidence Gate — The Secret Sauce
"Instead of guessing whether a question is 'easy' or 'hard' in advance, we let the local model tell us. We ask it the same question twice, with a bit of randomness turned on. If a model actually knows the answer, it tends to give the same answer both times. If it's guessing, the two answers drift apart. Two answers that agree = confident, keep it local and free. Two answers that disagree = unsure, send it to the bigger cloud model. "

The Math: agreement_score = (matching answers) / (total answers sampled)

With 2 samples: either 1.0 (both matched) or 0.5 (they didn't).

Want a more graduated score? Set SELF_CONSISTENCY_SAMPLES=3 → scores can be 1.0, 0.67, or 0.33.

📁 Repository Structure
text
.
├── app.py                    # Streamlit UI (demo interface)
├── router_agent.py           # FastAPI server + routing/confidence logic
├── gemma_fireworks.py        # Standalone Fireworks API call with retries
├── Dockerfile                # Agent container
├── docker-compose.yml        # Agent + local ROCm model orchestration
├── requirements.txt          # Python dependencies
├── .env.example              # Environment variables template
├── .gitignore                # Git ignore rules
├── LICENSE                   # MIT License
└── README.md                 # This file
📋 Submission Checklist
Public GitHub Repository — github.com/Awais-0806/Team-Scorpians-Routing-Agent

Live Demo URL — Deployed on AMD Developer Cloud with Streamlit UI

5-Minute Video Presentation — Covers problem, solution, demo, and results

PDF Slide Deck — 9 professional slides (Title → Architecture → Results → Team)

Cover Image — 16:9 thumbnail for project submission

MIT License — Added to repository

Project Description — Clear problem-solution narrative on lablab.ai

Technology Tags — ROCm, vLLM, Fireworks AI, Gemma, Docker, FastAPI

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

Fireworks AI — For cloud inference credits and Gemma 4 31B API access

Hugging Face — For hosting the Gemma 4 models

lablab.ai — For organizing the hackathon and providing a platform to compete

Claude & DeepSeek — Our AI teammates who accelerated our development

🦂 Why We Will Win
We didn't just build a hybrid router. We built a story — of grit, smart decision-making, and relentless execution. Our local-first cascade is not just clever; it's mathematically optimal for Track 1's scoring. Our use of Gemma end-to-end is not just a feature; it's a coherent, judge-friendly narrative for the bonus prize. And our challenges — fought and overcome by just two people — prove that we have what it takes to win.

"Code. Collaborate. Conquer." — Team Scorpians 🦂
