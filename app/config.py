"""Configuration settings loaded from .env file."""
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Local LLM (Ollama)
    local_llm_url: str = "http://localhost:11434/api/generate"
    local_llm_api_key: str = ""
    local_llm_timeout: int = 60
    
    # Fireworks AI (Cloud)
    fireworks_api_key: str = ""
    fireworks_api_url: str = "https://api.fireworks.ai/inference/v1/chat/completions"
    fireworks_model: str = "accounts/fireworks/models/gemma-4-31b-it"
    fireworks_timeout: int = 30
    
    # Hugging Face
    hf_token: str = ""
    
    # Router settings
    confidence_threshold: float = 0.6
    self_consistency_samples: int = 3
    
    # Redis (optional)
    redis_url: str = "redis://localhost:6379"
    
    # Server
    log_level: str = "info"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

def get_settings():
    return Settings()