"""
Team Scorpians - Hybrid Token-Efficient Routing Agent
AMD Developer Hackathon: ACT II - Track 1 + Best Use of Gemma bonus

WHAT THIS FILE DOES
--------------------
Runs a FastAPI server with one main endpoint: POST /route
Every incoming query goes through this cascade:

  1. Ask the LOCAL Gemma model (running on ROCm) the same question TWICE,
     with some randomness (temperature 0.7). This is called "self-consistency".
  2. Compare the two answers.
       - If they agree  -> the local model is confident. Return its answer.
         Cost: 0 tokens scored (local tokens count as zero on the leaderboard).
       - If they disagree -> the local model is unsure. Escalate the SAME
         query to Fireworks AI's larger Gemma 4 31B IT model in the cloud.
         Cost: real tokens, so this should happen only when genuinely needed.
  3. Always return which model actually answered + how many tokens were
     spent, so you can show this live in your demo/video.

WHY THIS MATCHES THE SCORING RULE
----------------------------------
Track 1's rule: "All models and tokens used locally count as zero toward the
final score." That means the optimal agent is NOT a 50/50 balance -- it's
"try free first, only pay when you must." This file is built around exactly
that idea, end-to-end in the Gemma family (small Gemma locally, big Gemma
in the cloud), which also makes the case for the Best Use of Gemma bonus.
"""

import os
import re
import time
import logging
from dataclasses import dataclass, asdict
from typing import Optional

import requests
from collections import defaultdict
from fastapi import FastAPI, Header, HTTPException, Request, Depends
from pydantic import BaseModel, Field

try:
    import tiktoken
    _ENC = tiktoken.get_encoding("cl100k_base")
except ImportError:
    _ENC = None

# ---------------------------------------------------------------------------
# CONFIG -- all pulled from environment variables so you can change models,
# thresholds, or endpoints at kickoff without touching any code.
# ---------------------------------------------------------------------------
LOCAL_BASE_URL = os.getenv("LOCAL_BASE_URL", "http://local-model:8000/v1")
LOCAL_MODEL = os.getenv("LOCAL_MODEL", "google/gemma-4-e4b-it")

FIREWORKS_API_KEY = os.getenv("FIREWORKS_API_KEY", "")
FIREWORKS_BASE_URL = "https://api.fireworks.ai/inference/v1"
FIREWORKS_MODEL = os.getenv("FIREWORKS_MODEL", "accounts/fireworks/models/gemma-4-31b-it")
# Verify current price at docs.fireworks.ai/serverless/pricing before your demo.
FIREWORKS_PRICE_PER_1M_TOKENS = float(os.getenv("FIREWORKS_PRICE_PER_1M", "0.20"))

CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", "0.6"))
SELF_CONSISTENCY_SAMPLES = int(os.getenv("SELF_CONSISTENCY_SAMPLES", "2"))
REQUEST_TIMEOUT = 30
MAX_RETRIES = 2

# --- Security config ---
# AGENT_API_KEY: leave blank during judging so judges can hit the endpoint
# freely; set it in production to require `X-API-Key: <value>` on requests.
AGENT_API_KEY = os.getenv("AGENT_API_KEY", "")
RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "20"))
MAX_QUERY_LENGTH = int(os.getenv("MAX_QUERY_LENGTH", "2000"))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("router_agent")


@dataclass
class RouteResult:
    answer: str
    model_used: str
    escalated: bool
    confidence: Optional[float] = None
    local_tokens: int = 0          # zero-cost on the leaderboard, tracked for transparency
    cloud_tokens: int = 0          # this is the number that actually costs points/$
    cloud_cost_usd: float = 0.0
    latency_s: float = 0.0
    error: Optional[str] = None


# ---------------------------------------------------------------------------
# Free heuristic pre-filter -- catches obviously hard queries before wasting
# a local round trip on something that will fail the confidence gate anyway.
# ---------------------------------------------------------------------------
_HARD_PATTERNS = [
    r"\bprove\b", r"\bderive\b", r"multi[- ]step", r"\bexplain why\b",
    r"\bcompare\b.+\band\b", r"\bwrite (a|the) function\b", r"\bdebug\b",
    r"(\d+\s*[\+\-\*/]\s*\d+){2,}",
]

def looks_hard(query: str) -> bool:
    q = query.lower()
    if len(query) > 400:
        return True
    return any(re.search(p, q) for p in _HARD_PATTERNS)


def estimate_tokens_approx(text: str) -> int:
    """Fast cross-model approximation for pre-call budgeting only.
    Real accounting always comes from the API's own `usage` field."""
    if _ENC is None:
        return max(1, len(text) // 4)
    return len(_ENC.encode(text))


# ---------------------------------------------------------------------------
# Local model call (OpenAI-compatible endpoint served by vLLM on ROCm)
# ---------------------------------------------------------------------------
def call_local_model(query: str, temperature: float = 0.7) -> dict:
    payload = {
        "model": LOCAL_MODEL,
        "messages": [{"role": "user", "content": query}],
        "temperature": temperature,
        "max_tokens": 512,
    }
    last_err = None
    for attempt in range(MAX_RETRIES + 1):
        try:
            resp = requests.post(f"{LOCAL_BASE_URL}/chat/completions", json=payload, timeout=REQUEST_TIMEOUT)
            resp.raise_for_status()
            data = resp.json()
            usage = data.get("usage", {})
            return {
                "text": data["choices"][0]["message"]["content"],
                "tokens": usage.get("total_tokens", estimate_tokens_approx(query)),
            }
        except requests.exceptions.RequestException as e:
            last_err = e
            log.warning("Local model call failed (attempt %d/%d): %s", attempt + 1, MAX_RETRIES + 1, e)
            time.sleep(1)
    raise last_err


# ---------------------------------------------------------------------------
# Confidence gate: self-consistency (still 100% local -> still free)
# ---------------------------------------------------------------------------
def estimate_confidence(query: str) -> tuple[str, float, int]:
    answers, total_tokens = [], 0
    for _ in range(SELF_CONSISTENCY_SAMPLES):
        result = call_local_model(query, temperature=0.7)
        answers.append(result["text"].strip())
        total_tokens += result["tokens"]

    def sig(t: str) -> str:
        return " ".join(t.lower().split()[:12])  # compare the first ~12 words

    sigs = [sig(a) for a in answers]
    agreement = sigs.count(sigs[0]) / len(sigs)
    return answers[0], agreement, total_tokens


# ---------------------------------------------------------------------------
# Cloud model call via Fireworks -- the ONLY step that spends real tokens
# ---------------------------------------------------------------------------
def call_fireworks_model(query: str) -> dict:
    if not FIREWORKS_API_KEY:
        raise RuntimeError("FIREWORKS_API_KEY is not set")
    headers = {"Authorization": f"Bearer {FIREWORKS_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": FIREWORKS_MODEL,
        "messages": [{"role": "user", "content": query}],
        "temperature": 0.2,
        "max_tokens": 512,
    }
    last_err = None
    for attempt in range(MAX_RETRIES + 1):
        try:
            resp = requests.post(f"{FIREWORKS_BASE_URL}/chat/completions", headers=headers, json=payload, timeout=REQUEST_TIMEOUT)
            resp.raise_for_status()
            data = resp.json()
            usage = data.get("usage", {})
            total = usage.get("total_tokens", 0)
            return {
                "text": data["choices"][0]["message"]["content"],
                "total_tokens": total,
                "cost_usd": round((total / 1_000_000) * FIREWORKS_PRICE_PER_1M_TOKENS, 6),
            }
        except requests.exceptions.RequestException as e:
            last_err = e
            log.warning("Fireworks call failed (attempt %d/%d): %s", attempt + 1, MAX_RETRIES + 1, e)
            time.sleep(1)
    raise last_err


# ---------------------------------------------------------------------------
# The router: ties every step above together
# ---------------------------------------------------------------------------
def route_query(query: str) -> RouteResult:
    start = time.time()
    local_tokens_spent = 0
    confidence_val: Optional[float] = None

    try:
        force_cloud = looks_hard(query)

        if not force_cloud:
            answer, confidence_val, tokens = estimate_confidence(query)
            local_tokens_spent += tokens
            if confidence_val >= CONFIDENCE_THRESHOLD:
                return RouteResult(
                    answer=answer, model_used=LOCAL_MODEL, escalated=False,
                    confidence=confidence_val, local_tokens=local_tokens_spent,
                    latency_s=round(time.time() - start, 3),
                )

        cloud = call_fireworks_model(query)
        return RouteResult(
            answer=cloud["text"], model_used=FIREWORKS_MODEL, escalated=True,
            confidence=confidence_val, local_tokens=local_tokens_spent,
            cloud_tokens=cloud["total_tokens"], cloud_cost_usd=cloud["cost_usd"],
            latency_s=round(time.time() - start, 3),
        )

    except requests.exceptions.RequestException as e:
        log.warning("Local model unreachable (%s); falling back to Fireworks directly.", e)
        try:
            cloud = call_fireworks_model(query)
            return RouteResult(
                answer=cloud["text"], model_used=FIREWORKS_MODEL, escalated=True,
                cloud_tokens=cloud["total_tokens"], cloud_cost_usd=cloud["cost_usd"],
                latency_s=round(time.time() - start, 3), error=f"local_unavailable: {e}",
            )
        except Exception as e2:
            return RouteResult(
                answer="Sorry, both the local and cloud models are unavailable right now.",
                model_used="none", escalated=False,
                latency_s=round(time.time() - start, 3),
                error=f"both backends failed -- local: {e}; cloud: {e2}",
            )
    except Exception as e:
        return RouteResult(
            answer="Something went wrong processing your query.",
            model_used="none", escalated=False,
            latency_s=round(time.time() - start, 3), error=str(e),
        )


# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------
app = FastAPI(title="Team Scorpians - Hybrid Token-Efficient Routing Agent")

# In-memory rate limiter: {client_ip: [timestamps of recent requests]}
# Good enough for a hackathon demo on a single instance. For real production
# scale, swap this for Redis-backed rate limiting.
_request_log: dict[str, list[float]] = defaultdict(list)


def check_rate_limit(request: Request) -> None:
    client_ip = request.client.host if request.client else "unknown"
    now = time.time()
    window_start = now - 60
    _request_log[client_ip] = [t for t in _request_log[client_ip] if t > window_start]
    if len(_request_log[client_ip]) >= RATE_LIMIT_PER_MINUTE:
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Try again in a minute.")
    _request_log[client_ip].append(now)


def check_api_key(x_api_key: Optional[str] = Header(default=None)) -> None:
    # If AGENT_API_KEY is unset, auth is disabled (useful during judging demos).
    if AGENT_API_KEY and x_api_key != AGENT_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing X-API-Key header.")


def security_checks(request: Request, x_api_key: Optional[str] = Header(default=None)) -> None:
    check_rate_limit(request)
    check_api_key(x_api_key)


class QueryIn(BaseModel):
    query: str = Field(..., min_length=1, max_length=MAX_QUERY_LENGTH)


@app.get("/health")
def health():
    return {"status": "ok", "local_model": LOCAL_MODEL, "cloud_model": FIREWORKS_MODEL}


@app.post("/route", dependencies=[Depends(security_checks)])
def route(q: QueryIn):
    """Send a query through the local-first cascade and get back the answer
    plus routing metadata (which model answered, confidence, tokens spent).

    Protected by: rate limiting (per IP) and optional API key (X-API-Key header,
    only enforced if AGENT_API_KEY env var is set)."""
    result = route_query(q.query)
    return asdict(result)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
