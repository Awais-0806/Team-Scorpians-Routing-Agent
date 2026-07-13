"""
Quick Backend for UI Demo (Uses same router as submit.py)
Run: python backend.py
"""

import sys
import os
import asyncio
sys.path.insert(0, os.getcwd())

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import time
import uuid

# Import router from app
from app.router import HybridRouter

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

router_instance = HybridRouter(model_path="model.gguf")

class ChatRequest(BaseModel):
    query: str
    api_key: str = "myHackathonKey2026"

class ChatResponse(BaseModel):
    content: str
    source: str
    confidence: float
    latency_ms: float
    tokens_saved: int
    request_id: str

@app.post("/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest):
    start = time.monotonic()
    request_id = str(uuid.uuid4())
    if not payload.query.strip():
        raise HTTPException(status_code=400, detail="Empty query")
    
    try:
        answer, meta = await asyncio.wait_for(
            router_instance.route(payload.query), 
            timeout=10.0
        )
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="Router timed out after 10 seconds")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Router error: {str(e)}")
    
    latency_ms = (time.monotonic() - start) * 1000
    return ChatResponse(
        content=answer,
        source=meta["source"],
        confidence=meta["confidence"],
        latency_ms=latency_ms,
        tokens_saved=meta.get("tokens_saved", 200),
        request_id=request_id
    )

@app.post("/route", response_model=ChatResponse)
async def route(payload: ChatRequest):
    """Alias for /chat — UI uses /route by default"""
    return await chat(payload)

@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)