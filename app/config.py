"""Centralised configuration loaded from environment variables."""
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    # Server
    host: str = "0.0.0.0"
    port: int = 8080

    # Local LLM (vLLM or similar)
    local_llm_url: str = "http://localhost:11434/api/generate"
    local_llm_api_key: str = ""  # if any
    local_llm_timeout: float = 30.0

    # Cloud LLM (Fireworks)
    fireworks_api_url: str = "https://api.fireworks.ai/inference/v1/chat/completions"
    fireworks_api_key: str = ""  # Reads from .env file
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
    rate_limit: str = "100/minute"

    # Logging
    log_level: str = "INFO"

    # ============================================================
    # GPU SETTINGS
    # ============================================================
    use_gpu: bool = True  # Auto-detect GPU
    gpu_model: str = "gemma3:4b"  # Model to use on GPU
    max_tokens_gpu: int = 512  # Max tokens on GPU
    max_tokens_cpu: int = 128  # Max tokens on CPU (fallback)

    # ============================================================
    # PERFORMANCE SETTINGS
    # ============================================================
    max_tokens: int = 512  # Default max tokens
    temperature: float = 0.3  # Default temperature
    top_p: float = 0.9  # Default top_p
    repeat_penalty: float = 1.1  # Default repeat penalty

    # ============================================================
    # MODEL CONFIG
    # ============================================================
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="allow"
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()