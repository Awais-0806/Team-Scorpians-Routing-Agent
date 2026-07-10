"""Configuration for Hackathon Submission — Reads Env Vars ONLY."""
import os

class Settings:
    def __init__(self):
        # Fireworks (Injected by Harness)
        self.fireworks_api_key = os.getenv("FIREWORKS_API_KEY", "")
        self.fireworks_base_url = os.getenv("FIREWORKS_BASE_URL", "")
        self.allowed_models = os.getenv("ALLOWED_MODELS", "")
        
        # Local mock settings (No external calls)
        self.confidence_threshold = 0.6
        
        # Safety checks
        if not self.fireworks_api_key:
            print("⚠️ Warning: FIREWORKS_API_KEY not set. Running in pure mock mode.")
        if not self.fireworks_base_url:
            print("⚠️ Warning: FIREWORKS_BASE_URL not set. Fireworks calls will fail.")

    @property
    def fireworks_model(self):
        # Use the first model from ALLOWED_MODELS, or fallback to a safe mock
        if self.allowed_models:
            return self.allowed_models.split(",")[0].strip()
        return "accounts/fireworks/models/phi-3-mini-4k-instruct"

settings = Settings()