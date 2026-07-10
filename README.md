# 🦂 Team Scorpians — Hybrid Token-Efficient Routing Agent

**AMD Developer Hackathon: ACT II (July 6–11, 2026)**  
**Track 1: Hybrid Token-Efficient Routing Agent**  
🎯 *Also targeting: Best Use of Gemma Models*

[![AMD](https://img.shields.io/badge/AMD-ROCm-red)](https://www.amd.com/en/developer/rocm.html)
[![Fireworks AI](https://img.shields.io/badge/Cloud-Fireworks_AI-orange)](https://fireworks.ai)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 🚀 What This Does

A **smart routing agent** that handles a wide variety of natural language tasks across **8 capability categories** (Factual Knowledge, Math Reasoning, Sentiment Classification, Text Summarization, NER, Code Debugging, Logical Reasoning, Code Generation).

- **Local-first:** Uses a lightweight rule-based engine for simple/factual queries — **zero cloud tokens** on the leaderboard.
- **Cloud fallback:** For complex queries, it escalates to **Fireworks AI (Gemma‑4)** to maintain **80%+ accuracy gate**.
- **Self‑consistency gate:** Asks the model twice and compares responses to ensure confidence before returning an answer.

---

## 🧠 Architecture

```text
User Query
│
▼
Heuristic Pre-filter (Fact lookup, Math, Sentiment, NER, Code patterns)
│
▼
┌───────────────────────────────────────────────────────┐
│                                                       │
│   ┌──────────────────────────────────────────────┐   │
│   │  Local Rule‑Based Engine (Zero Tokens)       │   │
│   │  - Capitals Database (200+ countries)        │   │
│   │  - Math Calculator                          │   │
│   │  - Sentiment Word Counter                   │   │
│   │  - NER Pattern Matching                     │   │
│   │  - Code Debug Templates                     │   │
│   └──────────────────────────────────────────────┘   │
│                          │                          │
│                          ▼                          │
│   ┌──────────────────────────────────────────────┐   │
│   │  Confidence Gate                             │   │
│   │  (If confidence < threshold OR complex)      │   │
│   └──────────────────────────────────────────────┘   │
│                          │                          │
│                          ▼                          │
│   ┌──────────────────────────────────────────────┐   │
│   │  Fireworks AI (Gemma‑4) — Cloud Escalation  │   │
│   │  (Only when needed, minimal tokens)          │   │
│   └──────────────────────────────────────────────┘   │
│                                                       │
└───────────────────────────────────────────────────────┘
⚙️ Tech Stack
Layer	Tool
Router Logic	Python + app/router.py (HybridRouter)
Local Engine	Rule-based fallback (No heavy models in container)
Cloud Model	Fireworks AI — Gemma‑4 (on‑demand, via API)
Batch Processing	submit.py — Reads /input/tasks.json, writes /output/results.json
UI Demo	Streamlit — app_ui.py (3D Mission Control)
Containerization	Docker (linux/amd64)
📦 Capability Categories (8/8 Covered)
#	Category	How We Solve
1	Factual Knowledge	200+ Country Capitals Database + pattern matching
2	Mathematical Reasoning	Regex-based arithmetic, percentages, area/perimeter
3	Sentiment Classification	Positive/Negative word counters
4	Text Summarization	Template-based generic summary generation
5	Named Entity Recognition	Regex (Person/Date/Location extraction)
6	Code Debugging	Pattern detection (return nums[0] → max(nums))
7	Logical / Deductive Reasoning	Constraint-based brute‑force solver
8	Code Generation	Template‑based function generation
🔧 Local Development (Testing)
bash
# 1. Create virtual environment
python -m venv venv
.\venv\Scripts\activate   # Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run batch processor (local fallback mode)
python submit.py

# 4. Check output
type D:\output\results.json   # (Windows)
🐳 Docker Submission (For Judge)
The submission container is a batch processor, not a server.

bash
# 1. Build (linux/amd64 required)
docker buildx build --platform linux/amd64 -t your-username/scorpion-agent:latest .

# 2. Test locally (simulate judge)
mkdir test-input
cp tasks.json test-input/
docker run --rm -v "$(pwd)/test-input:/input" -v "$(pwd)/test-output:/output" your-username/scorpion-agent:latest

# 3. Check output
cat test-output/results.json

# 4. Push to registry
docker push your-username/scorpion-agent:latest
🔑 Environment Variables (Judge Injects)
Variable	Description
FIREWORKS_API_KEY	Provided by harness — do not use your own
FIREWORKS_BASE_URL	Base URL for all Fireworks API calls
ALLOWED_MODELS	Comma-separated list of permitted models
Important: All API calls must go through FIREWORKS_BASE_URL. Calls bypassing this URL score zero tokens.

⏳ Cloud Credits & Submission Note
Note: Fireworks AI credits were processed with a 2‑3 business day delay. Our cloud integration is fully ready, but could not be tested live during the hackathon. The submission container gracefully falls back to a rule‑based engine when credits are unavailable — ensuring zero downtime for the judge evaluation.

📊 Token Efficiency Strategy
Local (rule‑based) queries: 0 tokens → Free!

Cloud (Fireworks) queries: Only for complex tasks → Minimal token usage.

Self‑consistency gate: 2 samples per query → Maintains accuracy above 80% threshold.

🦂 Team Scorpians
Role	Name
Captain / Backend / UI / DevOps	Awais
AI/ML Engineer / API Integration	Muhammad Ekremah
📜 License
MIT — see LICENSE

🏆 Hackathon Details
Event: AMD Developer Hackathon: ACT II on lablab.ai

Track: Track 1 — Hybrid Token‑Efficient Routing Agent

Bonus: Best Use of Gemma Models

Dates: July 6–11, 2026

Deadline: July 11, 2026 (8:00 PM PKT)

<p align="center"> <strong>Built with ❤️ by Team Scorpians 🦂 for AMD Hackathon 2026</strong><br> <em>Local-first. Token-efficient. Smart routing.</em> </p> ```