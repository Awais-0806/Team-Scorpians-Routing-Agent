"""
Team Scorpians - standalone snippet: calling Gemma 4 31B IT on Fireworks AI

Run directly to test your Fireworks API key and Gemma access before wiring
it into the full router:

    export FIREWORKS_API_KEY=your_key_here
    python gemma_fireworks.py
"""

import os
import time
import requests

FIREWORKS_API_KEY = os.getenv("FIREWORKS_API_KEY", "")
FIREWORKS_URL = "https://api.fireworks.ai/inference/v1/chat/completions"
MODEL = "accounts/fireworks/models/gemma-4-31b-it"  # confirm exact model id at kickoff


def call_gemma(prompt: str, max_tokens: int = 300, temperature: float = 0.2,
               timeout: int = 30, max_retries: int = 3) -> dict:
    """Call Gemma 4 31B IT on Fireworks AI with retries and clear error handling.

    Returns a dict with the answer text and real token usage, or raises a
    RuntimeError with a human-readable message if every attempt fails.
    """
    if not FIREWORKS_API_KEY:
        raise RuntimeError(
            "FIREWORKS_API_KEY is not set. Export it or put it in your .env file."
        )

    headers = {
        "Authorization": f"Bearer {FIREWORKS_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": temperature,
    }

    last_error = None
    for attempt in range(1, max_retries + 1):
        try:
            response = requests.post(FIREWORKS_URL, headers=headers, json=payload, timeout=timeout)

            # Handle specific, common failure cases with clear messages
            if response.status_code == 401:
                raise RuntimeError("Invalid Fireworks API key (401 Unauthorized). Check FIREWORKS_API_KEY.")
            if response.status_code == 404:
                raise RuntimeError(
                    f"Model '{MODEL}' not found (404). It may have a different id at kickoff -- "
                    "check the Fireworks model library for the exact Gemma 4 model path."
                )
            if response.status_code == 429:
                # Rate-limited: back off and retry
                wait = 2 ** attempt
                print(f"Rate limited (429). Waiting {wait}s before retry {attempt}/{max_retries}...")
                time.sleep(wait)
                continue

            response.raise_for_status()
            data = response.json()

            return {
                "text": data["choices"][0]["message"]["content"],
                "prompt_tokens": data["usage"]["prompt_tokens"],
                "completion_tokens": data["usage"]["completion_tokens"],
                "total_tokens": data["usage"]["total_tokens"],
            }

        except requests.exceptions.Timeout:
            last_error = "Request timed out"
            print(f"Attempt {attempt}/{max_retries} timed out, retrying...")
        except requests.exceptions.ConnectionError as e:
            last_error = f"Connection error: {e}"
            print(f"Attempt {attempt}/{max_retries} connection error, retrying...")
        except RuntimeError:
            raise  # don't retry on auth/model-not-found errors, those won't fix themselves
        except Exception as e:
            last_error = str(e)
            print(f"Attempt {attempt}/{max_retries} failed: {e}")

        time.sleep(1.5 * attempt)  # simple backoff between retries

    raise RuntimeError(f"Failed to call Gemma on Fireworks after {max_retries} attempts. Last error: {last_error}")


if __name__ == "__main__":
    result = call_gemma("Explain the OWASP Top 10 for LLMs in 3 short bullet points.")
    print("\n--- Answer ---")
    print(result["text"])
    print("\n--- Token usage (this is what actually costs you) ---")
    print(f"Prompt: {result['prompt_tokens']} | Completion: {result['completion_tokens']} | Total: {result['total_tokens']}")
