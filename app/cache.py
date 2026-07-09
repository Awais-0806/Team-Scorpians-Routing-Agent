"""Async caching layer with Redis primary and in‑memory fallback."""
import asyncio
from typing import Optional
import redis.asyncio as aioredis
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from app.config import get_settings
from app.logger import log

settings = get_settings()


class CacheManager:
    def __init__(self):
        self.redis: Optional[aioredis.Redis] = None
        self.memory_cache: dict = {}
        self.connected = False

    async def connect(self):
        try:
            self.redis = aioredis.from_url(settings.redis_url, decode_responses=True)
            await self.redis.ping()
            self.connected = True
            log.info("Redis connected")
        except Exception:
            log.warning("Redis unavailable, falling back to in‑memory cache")
            self.redis = None
            self.connected = False

    async def get(self, key: str) -> Optional[str]:
        if self.connected and self.redis:
            try:
                return await self._redis_get_with_retry(key)
            except Exception:
                log.warning("Redis get failed, using memory cache")
        return self.memory_cache.get(key)

    @retry(
        stop=stop_after_attempt(settings.redis_retry_max),
        wait=wait_exponential(multiplier=0.2, min=0.1, max=1),
        retry=retry_if_exception_type(),
        reraise=False,
    )
    async def _redis_get_with_retry(self, key: str) -> Optional[str]:
        return await self.redis.get(key)

    async def set(self, key: str, value: str, ttl: int = None):
        ttl = ttl or settings.cache_ttl
        if self.connected and self.redis:
            try:
                await self.redis.set(key, value, ex=ttl)
            except Exception:
                log.warning("Redis set failed, saving to memory")
        self.memory_cache[key] = value

    async def close(self):
        if self.redis:
            await self.redis.aclose()