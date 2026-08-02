"""
Purpose:
Dedicated service for Groq Ultra-Fast AI API.

Responsibilities:
- Fast TCP keep-alive connection pooling
- Groq API completion requests (<0.3s speed)
- Error handling & latency tracking

Dependencies:
- config.py
"""

import time
import requests
import config

_http_session = requests.Session()
_http_session.headers.update({"Connection": "keep-alive", "Accept-Encoding": "gzip, deflate"})


class GroqService:
    """Service for querying Groq Ultra-Fast AI API."""

    def __init__(self, api_key: str = None):
        self.api_key = api_key or getattr(config, "GROQ_API_KEY", "")
        # Prefer the stronger model for fluent multilingual sentences; Groq/Gemini fallback remains available.
        self.model = getattr(config, "GROQ_MODEL", "llama-3.3-70b-versatile")
        self.url = "https://api.groq.com/openai/v1/chat/completions"

    def ask(
        self, prompt: str, system_instruction: str = "", history: list = None
    ) -> tuple[bool, str, float]:
        """Queries Groq API and returns (success, reply, elapsed_seconds)."""
        if not self.api_key or self.api_key == "your_groq_api_key_here":
            return False, "", 0.0

        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}

        messages = [{"role": "system", "content": system_instruction or "You are Jarvis AI."}]
        if history:
            for h in history[-2:]:
                messages.append(h)
        messages.append({"role": "user", "content": prompt})

        payload = {"model": self.model, "messages": messages, "temperature": 0.5, "max_tokens": 180}

        try:
            start_t = time.time()
            res = _http_session.post(self.url, headers=headers, json=payload, timeout=6)
            elapsed = time.time() - start_t
            if res.status_code == 200:
                reply = res.json()["choices"][0]["message"]["content"].strip()
                return True, reply, elapsed
            else:
                print(f"[Groq Service Warning {res.status_code}] {res.text[:100]}")
        except Exception as e:
            print(f"[Groq Service Exception] {e}")

        return False, "", 0.0
