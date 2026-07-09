"""FastAPI application entry point."""
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.config import get_settings
from app.logger import log
from app.models import ChatRequest, ChatResponse, HealthResponse, MetricsResponse
from app.router import HybridRouter
from app.clients import LocalLLMClient, FireworksClient
from app.confidence import ConfidenceScorer
from app.classifier import QueryClassifier
from app.cache import CacheManager
from app.metrics import metrics_collector
from app.security import limiter, verify_api_key, detect_injection

settings = get_settings()

# ============================================================
# DEBUG: Print settings at startup
# ============================================================
print("\n" + "=" * 60)
print("🦂 TEAM SCORPIANS — SERVER STARTUP DEBUG")
print("=" * 60)
print(f"🔗 LOCAL_LLM_URL from settings: {settings.local_llm_url}")
print(f"📦 FIREWORKS_MODEL from settings: {settings.fireworks_model}")
print(f"🔑 API_KEY from settings: {settings.api_key[:10]}...")
print(f"📊 CONFIDENCE_THRESHOLD: {settings.confidence_threshold}")
print(f"🔄 SELF_CONSISTENCY_SAMPLES: {settings.self_consistency_samples}")
print("=" * 60 + "\n")

# Global components
local_client = None
cloud_client = None
cache = None
scorer = None
classifier = None
router = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("\n[LIFESPAN] 🚀 Starting up...")
    
    global local_client, cloud_client, cache, scorer, classifier, router
    
    # 1. Create clients
    print("[LIFESPAN] Creating LocalLLMClient...")
    local_client = LocalLLMClient()
    print(f"[LIFESPAN] ✅ Local client URL: {local_client.base_url}")
    print(f"[LIFESPAN] ✅ Local client model: {local_client.model_name}")
    
    print("[LIFESPAN] Creating FireworksClient...")
    cloud_client = FireworksClient()
    print(f"[LIFESPAN] ✅ Cloud client URL: {cloud_client.api_url}")
    print(f"[LIFESPAN] ✅ Cloud client model: {cloud_client.model}")
    
    print("[LIFESPAN] Creating CacheManager...")
    cache = CacheManager()
    await cache.connect()
    print(f"[LIFESPAN] ✅ Cache connected: {cache.connected}")
    
    print("[LIFESPAN] Creating ConfidenceScorer...")
    scorer = ConfidenceScorer()
    scorer.load()
    print(f"[LIFESPAN] ✅ ConfidenceScorer loaded")
    
    print("[LIFESPAN] Creating QueryClassifier...")
    classifier = QueryClassifier(scorer)
    print(f"[LIFESPAN] ✅ QueryClassifier created")
    
    print("[LIFESPAN] Creating HybridRouter...")
    router = HybridRouter(
        local_client=local_client,
        cloud_client=cloud_client,
        scorer=scorer,
        classifier=classifier,
        cache=cache,
    )
    print("[LIFESPAN] ✅ HybridRouter created")
    
    print("[LIFESPAN] ✅ All components initialized successfully!")
    print("=" * 60 + "\n")
    
    yield
    
    # Shutdown
    print("\n[LIFESPAN] 🔴 Shutting down...")
    await local_client.close()
    await cloud_client.close()
    await cache.close()
    log.info("Shutdown complete")
    print("[LIFESPAN] ✅ Shutdown complete")


app = FastAPI(
    title="Hybrid Routing Agent V2",
    version="2.0.0",
    lifespan=lifespan,
)

# Rate limiter state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.middleware("http")
async def add_request_id_and_logging(request: Request, call_next):
    start = time.time()
    
    # Debug: Log incoming request
    print(f"\n[MIDDLEWARE] 📥 {request.method} {request.url.path}")
    
    response = await call_next(request)
    latency = (time.time() - start) * 1000
    
    print(f"[MIDDLEWARE] 📤 {response.status_code} | Latency: {latency:.0f}ms")
    
    log.info(
        "Request completed",
        path=request.url.path,
        method=request.method,
        latency_ms=latency,
        status_code=response.status_code,
    )
    # Store latency in metrics if /chat
    if request.url.path == "/chat" and response.status_code == 200:
        metrics_collector.record_latency(latency)
    return response


@app.post("/chat", response_model=ChatResponse)
@limiter.limit(settings.rate_limit)
async def chat(request: Request, payload: ChatRequest):
    print(f"\n[CHAT] 📩 Received query: {payload.query[:100]}...")
    print(f"[CHAT] 🔑 API key: {payload.api_key[:10]}...")
    
    # Verify API key
    if not verify_api_key(payload.api_key):
        print(f"[CHAT] ❌ Invalid API key")
        raise HTTPException(status_code=401, detail="Invalid API key")

    # Prompt injection detection
    if detect_injection(payload.query):
        print(f"[CHAT] ❌ Prompt injection detected")
        raise HTTPException(status_code=400, detail="Potential prompt injection detected")

    # Handle forced cloud
    if payload.use_cloud_override:
        print(f"[CHAT] ☁️ Force cloud override")
        start = time.monotonic()
        answer, meta = await router._cloud_fallback(
            payload.query, request_id="force_cloud", start=start
        )
        return ChatResponse(
            answer=answer,
            source="cloud",
            confidence=1.0,
            category=meta["category"],
            cached=False,
            request_id=meta["request_id"],
            latency_ms=meta["latency_ms"],
        )

    # Route normally
    print(f"[CHAT] 🔄 Routing query through HybridRouter...")
    try:
        answer, meta = await router.route(payload.query)
        print(f"[CHAT] ✅ Route complete!")
        print(f"[CHAT] 📊 Source: {meta['source']}, Confidence: {meta['confidence']:.2f}")
        
        return ChatResponse(
            answer=answer,
            source=meta["source"],
            confidence=meta["confidence"],
            category=meta["category"],
            cached=meta["cached"],
            request_id=meta["request_id"],
            latency_ms=meta["latency_ms"],
        )
    except Exception as e:
        print(f"[CHAT] ❌ Route failed: {type(e).__name__}: {str(e)[:150]}")
        raise


@app.get("/health", response_model=HealthResponse)
async def health():
    redis_ok = cache.connected if cache else False
    
    # Quick local model ping
    local_ok = False
    try:
        if local_client:
            # Just test connectivity with a tiny prompt
            _ = await local_client.generate("test", max_tokens=2)
            local_ok = True
    except Exception as e:
        print(f"[HEALTH] ⚠️ Local model ping failed: {e}")
    
    print(f"[HEALTH] ✅ Health check: redis={redis_ok}, local_model={local_ok}")
    return HealthResponse(status="ok", redis=redis_ok, local_model=local_ok)


@app.get("/metrics", response_model=MetricsResponse)
async def metrics():
    return MetricsResponse(
        total_requests=metrics_collector.total,
        local_count=metrics_collector.local,
        cloud_count=metrics_collector.cloud,
        cache_hits=metrics_collector.cache_hits,
        avg_latency_ms=metrics_collector.avg_latency_ms,
        estimated_cost_saved_usd=metrics_collector.estimated_cost_saved_usd,
    )