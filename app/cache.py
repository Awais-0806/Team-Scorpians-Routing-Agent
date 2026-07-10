import time
import asyncio

class CacheManager:
    def __init__(self, ttl: int = 300):
        self.ttl = ttl
        self._store = {}

    async def connect(self):
        """Async initializer – no-op for in‑memory cache."""
        pass

    async def close(self):
        """Async cleanup."""
        self._store.clear()

    async def get(self, key):
        """Return cached value if not expired, else None."""
        entry = self._store.get(key)
        if entry and time.time() - entry["time"] < self.ttl:
            return entry["value"]
        elif entry:
            del self._store[key]
        return None

    async def set(self, key, value):
        """Store a value with current timestamp."""
        self._store[key] = {"value": value, "time": time.time()}

    async def clear(self):
        """Clear all cached entries."""
        self._store.clear()