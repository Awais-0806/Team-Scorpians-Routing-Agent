\# 🦂 Team Scorpians — Hybrid Token-Efficient Routing Agent



\*\*AMD Developer Hackathon: ACT II (July 6–11, 2026)\*\*  

\*\*Track 1: Hybrid Token-Efficient Routing Agent\*\*  

🎯 \*Also targeting: Best Use of Gemma Models\*



\[!\[AMD](https://img.shields.io/badge/AMD-ROCm-red)](https://www.amd.com/en/developer/rocm.html)

\[!\[Fireworks AI](https://img.shields.io/badge/Cloud-Fireworks\_AI-orange)](https://fireworks.ai)

\[!\[Docker](https://img.shields.io/badge/Docker-Ready-blue)](https://www.docker.com/)

\[!\[License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)



\---



\## 🚀 What This Does



Answers every query with a \*\*small Gemma model running locally on AMD ROCm first\*\*.  

Local tokens count as \*\*zero\*\* toward Track 1's score, so the agent only pays for the larger \*\*Gemma 4 31B IT on Fireworks AI\*\* when the local model is genuinely unsure.



\---



\## 🧠 Architecture

Query → Heuristic pre-filter → Local Gemma 4 E4B (vLLM on ROCm, asked twice)

│

Self-consistency check

│

┌─────────────────┴─────────────────┐

answers agree answers disagree

│ │

return local answer escalate to Fireworks

(cost: 0 tokens) Gemma 4 31B IT (cost: real tokens)



text



\---



\## ⚙️ Tech Stack



| Layer | Tool |

|-------|------|

| \*\*Local inference\*\* | vLLM (`vllm/vllm-openai-rocm:v0.18.1`) on AMD Instinct MI300X |

| \*\*Cloud inference\*\* | Fireworks AI API — Gemma 4 31B IT |

| \*\*Agent\*\* | Python + FastAPI (`app/router.py`) |

| \*\*Containerization\*\* | Docker + Docker Compose |

| \*\*Frontend\*\* | Streamlit (3D crystal UI) |



\---



\## 💻 Local Development (CPU Fallback)



```bash

\# Create virtual environment

python -m venv venv

.\\venv\\Scripts\\activate   # Windows



\# Install dependencies

pip install -r requirements.txt



\# Start backend

python run.py



\# Start UI (separate terminal)

streamlit run app\_ui.py

🚀 Deployment on AMD Instinct MI300X

Clone the repository



bash

git clone https://github.com/Awais-0806/Team-Scorpians-Routing-Agent.git

cd Team-Scorpians-Routing-Agent

Set up environment variables



bash

cp .env.example .env

\# Edit .env with your tokens:

\#   HF\_TOKEN=hf\_...

\#   FIREWORKS\_API\_KEY=fw\_...

\#   FIREWORKS\_MODEL=accounts/fireworks/models/gemma-4-31b-it

Launch the stack



bash

docker compose up --build

This starts:



local-model — vLLM serving Gemma 4 E4B on AMD ROCm



agent — FastAPI router on port 8080



Test the API



bash

curl http://localhost:8080/health

curl -X POST http://localhost:8080/route \\

&#x20; -H "Content-Type: application/json" \\

&#x20; -d '{"query": "What is the capital of Pakistan?"}'

💰 Token Efficiency

90%+ queries handled locally — zero scored tokens on the leaderboard



Cloud escalation only for genuinely hard queries — self-consistency gate triggers Fireworks fallback



Accuracy maintained above 80% — confidence threshold of 0.6 ensures quality



Local tokens = completely FREE under Track 1 scoring rules



📊 Benchmark

Query Type	Escalated	Latency	Tokens (cloud)

"Capital of Pakistan?"	No	0.4s	0

"What is 15 + 27?"	No	0.3s	0

"Derive merge sort complexity"	Yes	1.2s	42

"Compare TCP vs UDP"	Yes	1.0s	38

(Numbers from local AMD ROCm deployment)



📂 Repository Structure

text

.

├── app/

│   ├── main.py          # FastAPI application

│   ├── router.py        # HybridRouter with self-consistency

│   ├── clients.py       # LocalLLMClient + FireworksClient

│   ├── config.py        # Settings from .env

│   ├── classifier.py    # Query difficulty classifier

│   ├── cache.py         # Redis/in-memory cache

│   ├── confidence.py    # Confidence scoring

│   ├── security.py      # Rate limiting, API key auth

│   └── ...

├── Dockerfile           # Agent container

├── docker-compose.yml   # Full stack: vLLM + agent

├── requirements.txt

├── streamlit\_app.py     # 3D crystal UI

├── app\_ui.py            # Alternative Streamlit UI

├── .env.example         # Environment template

├── README.md

└── LICENSE              # MIT

🔑 Environment Variables

Variable	Description

HF\_TOKEN	Hugging Face read token (for gated Gemma weights)

FIREWORKS\_API\_KEY	Fireworks AI API key

FIREWORKS\_MODEL	Cloud model ID

LOCAL\_MODEL	Local model name (default: google/gemma-4-e4b-it)

CONFIDENCE\_THRESHOLD	Minimum agreement score (default: 0.6)

SELF\_CONSISTENCY\_SAMPLES	Number of local samples (default: 2, GPU: 3)

🦂 Team Scorpians

Core Team (2 members):



Muhammad Awais — Captain, Backend, DevOps, UI/UX, Documentation



Muhammad Ekremah — AI/ML Engineer, API Integration, Model Testing





📜 License

MIT — see LICENSE



🏆 Hackathon Details

Event: AMD Developer Hackathon: ACT II on lablab.ai



Track: Track 1 — Hybrid Token-Efficient Routing Agent



Bonus: Best Use of Gemma Models



Dates: July 6–11, 2026



Judging: Innovation, technical complexity, token efficiency, presentation quality



<p align="center"> <strong>Built with ❤️ by Team Scorpians 🦂 for AMD Hackathon 2026</strong><br> <em>Local-first. Token-efficient. AMD-powered.</em> </p> ```

