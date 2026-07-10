"""Async HTTP clients for local and cloud LLM endpoints."""
import httpx
import socket
import torch
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from app.config import get_settings
from app.logger import log

settings = get_settings()


class LocalLLMClient:
    def __init__(self):
        self.client = httpx.AsyncClient(
            timeout=settings.local_llm_timeout,
            headers={"Authorization": f"Bearer {settings.local_llm_api_key}"} if settings.local_llm_api_key else {}
        )
        self.base_url = "http://localhost:11434/api/generate"
        
        # GPU Detection
        self.use_gpu = torch.cuda.is_available()
        if self.use_gpu:
            self.model_name = "gemma3:4b"  # Better model on GPU
            self.max_tokens = 512
            log.info(f"✅ Using GPU: {torch.cuda.get_device_name(0)}")
        else:
            self.model_name = "phi3:mini"  # Lighter model on CPU
            self.max_tokens = 256
            log.info("⚠️ Using CPU (fallback mode)")
        
        log.info(f"LocalLLMClient initialized with URL: {self.base_url}, model: {self.model_name}")

    def _check_ollama_available(self) -> bool:
        """Check if Ollama server is running."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex(('127.0.0.1', 11434))
            sock.close()
            return result == 0
        except Exception:
            return False

    @retry(
        stop=stop_after_attempt(2),
        wait=wait_exponential(multiplier=0.5, min=0.1, max=2),
        retry=retry_if_exception_type((httpx.HTTPError, httpx.TimeoutException)),
    )
    async def generate(self, prompt: str, max_tokens: int = None) -> str:
        """Send prompt to local Ollama endpoint."""
        if not self._check_ollama_available():
            log.error("Ollama server is not running! Start it with 'ollama serve'")
            raise ConnectionError("Ollama server not running")

        if max_tokens is None:
            max_tokens = self.max_tokens

        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_predict": max_tokens,
                "temperature": 0.1,
                "top_p": 0.9,
                "repeat_penalty": 1.1,
            }
        }

        log.info(f"Calling Ollama with model: {self.model_name}, URL: {self.base_url}")

        try:
            resp = await self.client.post(self.base_url, json=payload)
            resp.raise_for_status()
            data = resp.json()
            response_text = data.get("response", "")
            log.info(f"Ollama response received, length: {len(response_text)} chars")
            return response_text
        except httpx.HTTPStatusError as e:
            log.error(f"Local LLM HTTP error: {e.response.status_code} - {e.response.text[:200]}")
            raise
        except httpx.ConnectError as e:
            log.error(f"Could not connect to Ollama at {self.base_url}. Is Ollama running?")
            raise ConnectionError(f"Ollama not reachable: {e}")
        except Exception as e:
            log.error(f"Local LLM error: {str(e)}")
            raise

    async def close(self):
        await self.client.aclose()


class FireworksClient:
    def __init__(self):
        self.client = httpx.AsyncClient(
            timeout=settings.fireworks_timeout,
            headers={
                "Authorization": f"Bearer {settings.fireworks_api_key}",
                "Content-Type": "application/json",
            },
        )
        self.api_url = settings.fireworks_api_url
        self.model = settings.fireworks_model
        self.use_gpu = torch.cuda.is_available()
        log.info(f"FireworksClient initialized with URL: {self.api_url}, model: {self.model}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=0.5, min=0.1, max=2),
        retry=retry_if_exception_type((httpx.HTTPError, httpx.TimeoutException)),
    )
    async def generate(self, messages: list[dict], max_tokens: int = 512) -> str:
        """Send messages to Fireworks AI cloud endpoint."""
        if not settings.fireworks_api_key:
            log.warning("Fireworks API key not set. Cloud fallback disabled.")
            raise Exception("Fireworks API key not set")

        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": 0.1,
            "top_p": 0.9,
        }

        log.info(f"Calling Fireworks with model: {self.model}")

        try:
            resp = await self.client.post(self.api_url, json=payload)
            resp.raise_for_status()
            data = resp.json()
            response_text = data["choices"][0]["message"]["content"]
            log.info(f"Fireworks response received, length: {len(response_text)} chars")
            return response_text
        except httpx.HTTPStatusError as e:
            error_body = e.response.text[:300] if e.response else "No response body"
            log.error(f"Fireworks HTTP error: {e.response.status_code} - {error_body}")
            if e.response.status_code == 404:
                raise Exception(f"Fireworks model '{self.model}' not found (404). Please deploy the model first.")
            elif e.response.status_code == 401:
                raise Exception(f"Fireworks API key invalid (401). Please check your API key.")
            raise
        except httpx.ConnectError as e:
            log.error(f"Could not connect to Fireworks API: {e}")
            raise ConnectionError(f"Fireworks API unreachable: {e}")
        except Exception as e:
            log.error(f"Fireworks error: {str(e)}")
            raise

    async def close(self):
        await self.client.aclose()