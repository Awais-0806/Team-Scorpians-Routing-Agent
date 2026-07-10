"""FastAPI application entry point."""
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import JSONResponse, Response
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

# ============================================================
# PROMETHEUS METRICS
# ============================================================
try:
    from prometheus_client import Counter, Histogram, generate_latest, REGISTRY
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    print("⚠️ prometheus-client not installed. Metrics disabled.")

settings = get_settings()

# Global components
local_client = LocalLLMClient()
cloud_client = FireworksClient()
cache = CacheManager()
scorer = ConfidenceScorer()
classifier: QueryClassifier = None
router: HybridRouter = None

# Prometheus metrics (if available)
if PROMETHEUS_AVAILABLE:
    REQUESTS = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
    LATENCY = Histogram('http_request_duration_seconds', 'HTTP request latency', ['method', 'endpoint'])


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    log.info("Starting Hybrid Router V2")
    await cache.connect()
    scorer.load()
    global classifier, router
    classifier = QueryClassifier(scorer)
    router = HybridRouter(
        local_client=local_client,
        cloud_client=cloud_client,
        scorer=scorer,
        classifier=classifier,
        cache=cache,
    )
    yield
    # Shutdown
    await local_client.close()
    await cloud_client.close()
    await cache.close()
    log.info("Shutdown complete")


app = FastAPI(
    title="Hybrid Routing Agent V2",
    version="2.0.0",
    lifespan=lifespan,
)

# Rate limiter state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# ============================================================
# MIDDLEWARE: Request Logging + Prometheus Metrics
# ============================================================
@app.middleware("http")
async def add_request_id_and_logging(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    latency = (time.time() - start) * 1000
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
    
    # Prometheus metrics
    if PROMETHEUS_AVAILABLE:
        REQUESTS.labels(
            method=request.method,
            endpoint=request.url.path,
            status=response.status_code
        ).inc()
        LATENCY.labels(
            method=request.method,
            endpoint=request.url.path
        ).observe(latency / 1000)  # Convert to seconds
    
    return response


# ============================================================
# ENDPOINTS
# ============================================================
@app.post("/chat", response_model=ChatResponse)
@limiter.limit(settings.rate_limit)
async def chat(request: Request, payload: ChatRequest):
    # Verify API key
    if not verify_api_key(payload.api_key):
        raise HTTPException(status_code=401, detail="Invalid API key")

    # Prompt injection detection
    if detect_injection(payload.query):
        raise HTTPException(status_code=400, detail="Potential prompt injection detected")

    # Handle forced cloud
    if payload.use_cloud_override:
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
    answer, meta = await router.route(payload.query)
    return ChatResponse(
        answer=answer,
        source=meta["source"],
        confidence=meta["confidence"],
        category=meta["category"],
        cached=meta["cached"],
        request_id=meta["request_id"],
        latency_ms=meta["latency_ms"],
    )


@app.get("/health", response_model=HealthResponse)
async def health():
    redis_ok = cache.connected
    # Quick local model ping
    local_ok = True
    try:
        # Just test connectivity
        _ = await local_client.generate("test", max_tokens=2)
    except Exception:
        local_ok = False
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


# ============================================================
# PROMETHEUS METRICS ENDPOINT
# ============================================================
@app.get("/prometheus")
async def prometheus_metrics():
    """Prometheus metrics endpoint for monitoring."""
    if not PROMETHEUS_AVAILABLE:
        return Response("prometheus-client not installed", media_type="text/plain", status_code=503)
    return Response(generate_latest(REGISTRY), media_type="text/plain")


# ============================================================
# HTTPS SUPPORT (Direct Run)
# ============================================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=443,
        ssl_keyfile="./key.pem",
        ssl_certfile="./cert.pem"
    )