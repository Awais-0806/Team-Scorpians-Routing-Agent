# Team Scorpians — Hybrid Token-Efficient Routing Agent

Built for the **AMD Developer Hackathon: ACT II** (July 6–11, 2026) — Track 1 (Hybrid Token-Efficient Routing Agent) + Best Use of Gemma bonus.

## What this does

Answers every query with a small **Gemma 4 model running locally on AMD ROCm** first. Local tokens count as **zero** toward Track 1's score, so the agent only pays for the larger **Gemma 4 31B IT on Fireworks AI** when the local model is genuinely unsure.

## Architecture

```
Query → Heuristic pre-filter → Local Gemma 4 E4B (vLLM on ROCm, asked twice)
                                          │
                                   Self-consistency check
                                          │
                        ┌─────────────────┴─────────────────┐
                    answers agree                      answers disagree
                        │                                     │
                  return local answer              escalate to Fireworks
                  (cost: 0 tokens)                  Gemma 4 31B IT (cost: real tokens)
```

## Tech stack

| Layer | Tool |
|---|---|
| Local inference | vLLM (`vllm/vllm-openai-rocm:v0.18.1`) on AMD Developer Cloud |
| Cloud inference | Fireworks AI API — Gemma 4 31B IT |
| Agent | Python + FastAPI (`router_agent.py`) |
| Containerization | Docker + Docker Compose |

## Team

| Name | Role |
|---|---|
| Awais | Documentation, Testing & Security |
| Muhammad Ekremah | Full-Stack Development |
| Muhammad Eraj | Data Science / ML / Model Training |
| Alveena Haneef | Frontend / UI |
| Hina Munawar | Frontend / UI |
| Mussavir Abbasi | DevOps & Containerization |

## Setup

1. Clone the repo:
   ```bash
   git clone https://github.com/<your-org>/team-scorpians-routing-agent.git
   cd team-scorpians-routing-agent
   ```

2. Accept the Gemma license on Hugging Face (one-time, required for the local model to download):
   visit `huggingface.co/google/gemma-4-e4b-it` while logged in and accept the terms.

3. Create your environment file:
   ```bash
   cp .env.example .env
   ```
   Then fill in:
   - `FIREWORKS_API_KEY` — from your Fireworks AI account
   - `HF_TOKEN` — a Hugging Face access token with read access (needed for the gated Gemma weights)

## Run

```bash
docker compose up --build
```

This starts two containers:
- `local-model` — vLLM serving Gemma 4 E4B on ROCm (takes a minute or two to download weights on first run)
- `agent` — the FastAPI router, waits for `local-model` to report healthy before starting

## Test the API

Health check:
```bash
curl http://localhost:8080/health
```

Send a query:
```bash
curl -X POST http://localhost:8080/route \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the capital of Pakistan?"}'
```

Example response:
```json
{
  "answer": "The capital of Pakistan is Islamabad.",
  "model_used": "google/gemma-4-e4b-it",
  "escalated": false,
  "confidence": 1.0,
  "local_tokens": 38,
  "cloud_tokens": 0,
  "cloud_cost_usd": 0.0,
  "latency_s": 0.412
}
```

Try a harder query to see it escalate:
```bash
curl -X POST http://localhost:8080/route \
  -H "Content-Type: application/json" \
  -d '{"query": "Derive why merge sort has O(n log n) time complexity, step by step."}'
```

## Confidence Gate — how to explain it in your video (simple version)

> "Instead of guessing whether a question is 'easy' or 'hard' in advance, we let the local model tell us. We ask it the same question **twice**, with a bit of randomness turned on. If a model actually knows the answer, it tends to give the same answer both times, even with randomness. If it's guessing, the two answers tend to drift apart. So: **two answers that agree = confident, keep it local and free. Two answers that disagree = unsure, send it to the bigger cloud model.** This technique is called self-consistency, and it costs us nothing extra because both attempts stay on our free local model."

The math, in one line: `agreement_score = (number of matching answers) / (total answers sampled)`. With 2 samples that's either 1.0 (both matched) or 0.5 (they didn't) — simple to demo live. If you want a more graduated score for the video, bump `SELF_CONSISTENCY_SAMPLES` to 3 in your `.env` (then scores can land at 1.0, 0.67, or 0.33), which makes for a nicer chart in your slide deck.

## Repository structure

```
.
├── router_agent.py      # FastAPI server + full routing/confidence-gate logic
├── gemma_fireworks.py   # standalone Gemma-on-Fireworks call with retries/error handling
├── Dockerfile           # agent container
├── docker-compose.yml   # agent + local ROCm model, wired together
├── requirements.txt
└── .env.example
```

## License

MIT — add a `LICENSE` file before submitting (required for hackathon compliance).

## Hackathon details

- Event: AMD Developer Hackathon: ACT II (lablab.ai), July 6–11, 2026
- Track: Track 1 — Hybrid Token-Efficient Routing Agent
- Bonus target: Best Use of Gemma Models
- Judging also weighs creativity, originality, and product/market potential — make sure your video and slides tell the "why" of the local-first design, not just the "what"
