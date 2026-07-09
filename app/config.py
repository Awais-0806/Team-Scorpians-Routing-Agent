"""Centralised configuration loaded from environment variables."""
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    # Server
    host: str = "0.0.0.0"
    port: int = 8080

    # Local LLM (vLLM or similar)
    local_llm_url: str = "http://localhost:8000/generate"
    local_llm_api_key: str = ""  # if any
    local_llm_timeout: float = 30.0

    # Cloud LLM (Fireworks)
    fireworks_api_url: str = "https://api.fireworks.ai/inference/v1/chat/completions"
    fireworks_api_key: str = ""
    fireworks_model: str = "accounts/fireworks/models/llama-v3p1-70b-instruct"
    fireworks_timeout: float = 30.0

    # Router
    cache_ttl: int = 3600
    confidence_threshold: float = 0.75
    self_consistency_samples: int = 3
    enable_reflection: bool = True

    # Redis
    redis_url: str = "redis://localhost:6379/0"
    redis_retry_max: int = 3

    # Sentence Transformer
    embedding_model: str = "all-MiniLM-L6-v2"

    # Security
    api_key: str = "changeme"
    rate_limit: str = "100/minute"  # "100/minute"

    # Logging
    log_level: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env", extra="allow")


@lru_cache
def get_settings() -> Settings:
    return Settings()