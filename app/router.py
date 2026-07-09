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
                    "request_id": request_id,
                }
        except Exception:
            log.warning("Cache lookup failed, continuing")

        # 2. Classify query
        try:
            category = self.classifier.classify(query)
        except Exception:
            category = QueryCategory.general
        log.info("Classified", request_id=request_id, category=category.value)

        # 3. Local inference with self-consistency
        local_success = False
        conf = 0.0
        valid_responses = []
        try:
            tasks = [
                self.local.generate(build_local_prompt(query))
                for _ in range(settings.self_consistency_samples)
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            valid_responses = [r for r in results if isinstance(r, str)]
            if valid_responses:
                local_success = True
        except Exception as e:
            log.warning("Local inference failed", error=str(e))

        # 4. Confidence scoring (if we got local responses)
        if local_success:
            try:
                conf = self.scorer.confidence(valid_responses)
                log.info("Local confidence", request_id=request_id, confidence=conf)
                # Reflection
                if settings.enable_reflection:
                    reflection_conf = self.scorer.reflection_confidence(valid_responses[0], query)
                    conf = (conf + reflection_conf) / 2
                    log.info("Reflection confidence", request_id=request_id, confidence=reflection_conf)
            except Exception as e:
                log.warning("Confidence calculation failed", error=str(e))
                conf = 0.0

        # 5. Decision
        threshold = settings.confidence_threshold
        if category in (QueryCategory.coding, QueryCategory.math):
            threshold = max(threshold, 0.8)

        if local_success and conf >= threshold:
            answer = valid_responses[0]
            source = "local"
            # Cache local answer
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
                "request_id": request_id,
            }

        # 6. Fallback to cloud
        try:
            answer, cloud_meta = await self._cloud_fallback(query, request_id, start)
            try:
                await self.cache.set(cache_key, answer)
            except Exception:
                pass
            metrics_collector.record_cloud()
            return answer, {
                **cloud_meta,
                "confidence": conf,
                "category": category,
                "cached": False,
            }
        except Exception as e:
            log.error("Cloud fallback failed", error=str(e), request_id=request_id)
            # Everything failed – return a graceful error message
            return "Sorry, both local and cloud AI services are currently unavailable.", {
                "source": "error",
                "confidence": 0.0,
                "category": category,
                "cached": False,
                "latency_ms": (time.monotonic() - start) * 1000,
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
            "request_id": request_id,
        }
