"""
FastAPI Server for Stellar.ai UI
Handles /health and /route endpoints
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.router import HybridRouter
import uvicorn

app = FastAPI()

# CORS — allow UI to call
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize router
router = HybridRouter()

class QueryRequest(BaseModel):
    query: str

class RouteResponse(BaseModel):
    answer: str
    escalated: bool        # True if cloud, False if local
    confidence: float
    local_tokens: int
    cloud_cost_usd: float
    latency_ms: float

@app.post("/route", response_model=RouteResponse)
async def route_query(request: QueryRequest):
    try:
        answer, meta = await router.route(request.query)
        
        # Map our response to UI expected fields
        is_cloud = meta["source"] == "cloud"
        
        return RouteResponse(
            answer=answer,
            escalated=is_cloud,
            confidence=meta["confidence"],
            local_tokens=150 if not is_cloud else 0,  # Mock token savings
            cloud_cost_usd=0.0001 if is_cloud else 0.0,
            latency_ms=meta["latency_ms"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)