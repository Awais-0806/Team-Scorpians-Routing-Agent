"""Simple metrics collector (thread‑safe for async)."""
import time
from dataclasses import dataclass, field
from typing import List


@dataclass
class MetricsCollector:
    total: int = 0
    local: int = 0
    cloud: int = 0
    cache_hits: int = 0
    latencies: List[float] = field(default_factory=list)

    def record_local(self):
        self.total += 1
        self.local += 1

    def record_cloud(self):
        self.total += 1
        self.cloud += 1

    def record_cache_hit(self):
        self.total += 1
        self.cache_hits += 1

    def record_latency(self, ms: float):
        self.latencies.append(ms)

    @property
    def avg_latency_ms(self) -> float:
        if not self.latencies:
            return 0.0
        return sum(self.latencies) / len(self.latencies)

    @property
    def estimated_cost_saved_usd(self) -> float:
        # Rough estimate: cloud cost per 1k tokens $0.0009, local $0
        # Assume average tokens per request: 500 → $0.00045 per cloud call
        cloud_cost_per_call = 0.00045
        # Saved = local calls * cloud_cost_per_call
        return round(self.local * cloud_cost_per_call, 6)


metrics_collector = MetricsCollector()