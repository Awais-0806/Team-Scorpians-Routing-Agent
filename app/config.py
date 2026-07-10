"""Configuration settings loaded from .env file."""
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Local LLM (Ollama)
    local_llm_url: str = "http://localhost:11434/api/generate"
    local_llm_api_key: str = ""
    local_llm_timeout: int = 60
    local_model: str = "google/gemma-4-e4b-it"
    
    # Fireworks AI (Cloud)
    fireworks_api_key: str = ""
    fireworks_api_url: str = "https://api.fireworks.ai/inference/v1/chat/completions"
    fireworks_model: str = "accounts/fireworks/models/gemma-4-31b-it"
    fireworks_timeout: int = 30
    
    # Hugging Face
    hf_token: str = ""
    
    # Embedding model for confidence scoring
    embedding_model: str = "all-MiniLM-L6-v2"
    
    # Router settings
    confidence_threshold: float = 0.6
    self_consistency_samples: int = 3
    enable_reflection: bool = False
    enable_verification: bool = False
    
    # Redis (optional)
    redis_url: str = "redis://localhost:6379"
    redis_retry_max: int = 3
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8080
    log_level: str = "info"
    
    # API & Security
    api_key: str = ""
    rate_limit: str = "100/minute"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

def get_settings():
    return Settings()