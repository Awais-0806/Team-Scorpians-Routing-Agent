"""Core intelligent routing engine."""
import asyncio
import time
import uuid
from typing import Tuple
from app.config import get_settings
from app.logger import log
from app.models import QueryCategory
from app.clients import LocalLLMClient, FireworksClient
from app.confidence import ConfidenceScorer
from app.classifier import QueryClassifier
from app.cache import CacheManager
from app.metrics import metrics_collector
from app.prompts import build_local_prompt

settings = get_settings()


class HybridRouter:
    def __init__(
        self,
        local_client: LocalLLMClient,
        cloud_client: FireworksClient,
        scorer: ConfidenceScorer,
        classifier: QueryClassifier,
        cache: CacheManager,
    ):
        self.local = local_client
        self.cloud = cloud_client
        self.scorer = scorer
        self.classifier = classifier
        self.cache = cache

    async def route(self, query: str) -> Tuple[str, dict]:
        request_id = str(uuid.uuid4())
        start = time.monotonic()
        log.info("Routing query", request_id=request_id, query=query[:80])
        
        # ========== DEBUG ==========
        print(f"\n[ROUTER DEBUG] ===== ROUTING QUERY =====")
        print(f"[ROUTER DEBUG] Query: {query[:100]}...")
        print(f"[ROUTER DEBUG] Local client URL: {self.local.base_url}")
        print(f"[ROUTER DEBUG] Local client model: {self.local.model_name}")
        # ========== END DEBUG ==========

        # 1. Cache lookup
        cache_key = f"response:{hash(query)}"
        try:
            cached = await self.cache.get(cache_key)
            if cached:
                metrics_collector.record_cache_hit()
                latency = (time.monotonic() - start) * 1000
                log.info("Cache hit", request_id=request_id, latency_ms=latency)
                return cached, {
                    "source": "cache",
                    "confidence": 1.0,
                    "category": QueryCategory.general,
                    "cached": True,
                    "latency_ms": latency,
                    "tokens_saved": 150,   # full savings on cached response
                    "request_id": request_id,
                }
        except Exception as e:
            log.warning(f"Cache lookup failed: {e}")

        # 2. Classify query
        try:
            category = self.classifier.classify(query)
        except Exception as e:
            category = QueryCategory.general
            print(f"[ROUTER DEBUG] Classification failed: {e}")
        log.info("Classified", request_id=request_id, category=category.value)
        print(f"[ROUTER DEBUG] Category: {category.value}")

        # 3. Local inference with self-consistency
        local_success = False
        conf = 0.0
        valid_responses = []
        
        # ============================================================
        # GPU OPTIMIZATION: Use more samples on GPU
        # ============================================================
        samples = settings.self_consistency_samples
        if settings.use_gpu:
            samples = max(samples, 3)  # 3 samples on GPU for better accuracy
            print(f"[ROUTER DEBUG] GPU mode: using {samples} samples")
        else:
            print(f"[ROUTER DEBUG] CPU mode: using {samples} samples")
        
        print(f"[ROUTER DEBUG] Starting local inference with {samples} samples")
        
        try:
            prompt = build_local_prompt(query)
            print(f"[ROUTER DEBUG] Prompt: {prompt[:100]}...")
            
            tasks = [
                self.local.generate(prompt)
                for _ in range(samples)
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # ========== DEBUG LOGS ==========
            print(f"[ROUTER DEBUG] Tasks created: {len(tasks)}")
            print(f"[ROUTER DEBUG] Results received: {len(results)}")
            for i, res in enumerate(results):
                if isinstance(res, Exception):
                    print(f"[ROUTER DEBUG] Local call {i} FAILED: {type(res).__name__}: {str(res)[:150]}")
                else:
                    print(f"[ROUTER DEBUG] Local call {i} SUCCESS: {str(res)[:150]}...")
            # ========== END DEBUG ==========
            
            valid_responses = [r for r in results if isinstance(r, str)]
            if len(valid_responses) >= 2:
                local_success = True
                print(f"[ROUTER DEBUG] local_success = True, valid_responses = {len(valid_responses)}")
            else:
                print(f"[ROUTER DEBUG] local_success = False, no valid responses")
                
        except Exception as e:
            log.warning("Local inference failed", error=str(e))
            print(f"[ROUTER DEBUG] Exception in local inference: {type(e).__name__}: {str(e)[:150]}")

<<<<<<< HEAD
        # 4. Confidence scoring (if we have at least two valid responses)
        if local_success and len(valid_responses) >= 2:
            try:
                # Use semantic similarity between first two responses
                conf = self.scorer.score(valid_responses[0], valid_responses[1])
                log.info("Local confidence", request_id=request_id, confidence=conf)
                # Optional reflection: skip for simplicity or keep if scorer has the method
                if settings.enable_reflection and hasattr(self.scorer, 'reflection_confidence'):
=======
        # 4. Confidence scoring (if we got local responses)
        if local_success:
            print(f"[ROUTER DEBUG] Calculating confidence...")
            try:
                conf = self.scorer.confidence(valid_responses)
                print(f"[ROUTER DEBUG] Confidence calculated: {conf}")
                log.info("Local confidence", request_id=request_id, confidence=conf)
                
                if settings.enable_reflection:
                    print(f"[ROUTER DEBUG] Calculating reflection confidence...")
>>>>>>> 254debbb1319dc71f4280d90a7d9c6a396c1eb5c
                    reflection_conf = self.scorer.reflection_confidence(valid_responses[0], query)
                    conf = (conf + reflection_conf) / 2
                    print(f"[ROUTER DEBUG] Reflection confidence: {reflection_conf}, Final: {conf}")
                    log.info("Reflection confidence", request_id=request_id, confidence=reflection_conf)
                    
            except Exception as e:
                print(f"[ROUTER DEBUG] Confidence calculation FAILED: {type(e).__name__}: {str(e)[:150]}")
                log.warning("Confidence calculation failed", error=str(e))
                conf = 0.0

        # 5. Decision
        threshold = settings.confidence_threshold
        if category in (QueryCategory.coding, QueryCategory.math):
            threshold = max(threshold, 0.8)
        
        print(f"[ROUTER DEBUG] local_success: {local_success}, conf: {conf}, threshold: {threshold}")

        if local_success and conf >= threshold:
            answer = valid_responses[0]
            source = "local"
            print(f"[ROUTER DEBUG] ✅ DECISION: LOCAL (conf {conf:.2f} >= threshold {threshold})")
            try:
                await self.cache.set(cache_key, answer)
            except Exception:
                pass
            latency = (time.monotonic() - start) * 1000
            metrics_collector.record_local()
            log.info("Local response served", request_id=request_id, latency_ms=latency)
            return answer, {
                "source": source,
                "confidence": conf,
                "category": category,
                "cached": False,
                "latency_ms": latency,
                "tokens_saved": 150,      # estimated cloud tokens saved by using local
                "request_id": request_id,
            }
        else:
            print(f"[ROUTER DEBUG] 🔄 DECISION: CLOUD FALLBACK (local_success={local_success}, conf={conf} < threshold={threshold})")

        # 6. Fallback to cloud
        try:
            print(f"[ROUTER DEBUG] Calling cloud fallback...")
            answer, cloud_meta = await self._cloud_fallback(query, request_id, start)
            print(f"[ROUTER DEBUG] Cloud fallback SUCCESS")
            try:
                await self.cache.set(cache_key, answer)
            except Exception:
                pass
            metrics_collector.record_cloud()
            return answer, {
                **cloud_meta,
                "confidence": conf,      # keep local confidence even if cloud was used
                "category": category,
                "cached": False,
                "tokens_saved": 0,       # no savings when cloud is used
            }
        except Exception as e:
            print(f"[ROUTER DEBUG] ❌ Cloud fallback FAILED: {type(e).__name__}: {str(e)[:150]}")
            log.error("Cloud fallback failed", error=str(e), request_id=request_id)
            # Everything failed – return a graceful error message
            return "Sorry, both local and cloud AI services are currently unavailable.", {
                "source": "error",
                "confidence": 0.0,
                "category": category,
                "cached": False,
                "latency_ms": (time.monotonic() - start) * 1000,
                "tokens_saved": 0,
                "request_id": request_id,
            }

    async def _cloud_fallback(self, query: str, request_id: str, start: float):
        messages = [{"role": "user", "content": query}]
        answer = await self.cloud.generate(messages)
        latency = (time.monotonic() - start) * 1000
        log.info("Cloud response", request_id=request_id, latency_ms=latency)
        return answer, {
            "source": "cloud",
            "confidence": 1.0,
            "category": QueryCategory.general,
            "cached": False,
            "latency_ms": latency,
            "tokens_saved": 0,
            "request_id": request_id,
        }