"""Pydantic models for request/response and internal data."""
from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


class QueryCategory(str, Enum):
    coding = "coding"
    math = "math"
    reasoning = "reasoning"
    creative = "creative"
    general = "general"


class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=4000)
    api_key: str = Field(..., description="API key for authentication")
    use_cloud_override: bool = False  # allow forcing cloud


class ChatResponse(BaseModel):
    answer: str
    source: str  # "local" or "cloud"
    confidence: float
    category: QueryCategory
    cached: bool = False
    request_id: str
    latency_ms: float


class HealthResponse(BaseModel):
    status: str = "ok"
    redis: bool
    local_model: bool


class MetricsResponse(BaseModel):
    total_requests: int
    local_count: int
    cloud_count: int
    cache_hits: int
    avg_latency_ms: float
    estimated_cost_saved_usd: float