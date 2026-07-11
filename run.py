"""
Mock Backend Server (No config dependency)
Runs on port 8080 and uses HybridRouter directly.
"""
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio
import time
import os

# Direct import (no config)
from app.router import HybridRouter

app = FastAPI(title="Scorpion Router (Mock)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global router instance
router = HybridRouter()

class ChatRequest(BaseModel):
    query: str
    api_key: str = "myHackathonKey2026"

class ChatResponse(BaseModel):
    answer: str
    source: str
    confidence: float
    latency_ms: float

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    if not request.query.strip():
        raise HTTPException(400, "Query cannot be empty")
    start = time.monotonic()
    answer, meta = await router.route(request.query)
    latency_ms = (time.monotonic() - start) * 1000
    return ChatResponse(
        answer=answer,
        source=meta["source"],
        confidence=meta["confidence"],
        latency_ms=latency_ms
    )

@app.get("/health")
async def health():
    return {"status": "online", "mode": "mock"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080, log_level="info")