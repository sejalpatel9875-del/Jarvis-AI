import time
import requests
import config

class OllamaService:
    """Service for querying local Ollama instance."""
    def __init__(self):
        self.url = getattr(config, "OLLAMA_URL", "http://localhost:11434/api/chat")
        self.model = getattr(config, "OLLAMA_MODEL", "llama3.2")
        self.session = requests.Session()

    def ask(self, messages: list) -> tuple[bool, str, float]:
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False
        }
        try:
            start_t = time.time()
            res = self.session.post(self.url, json=payload, timeout=8)
            elapsed = time.time() - start_t
            if res.status_code == 200:
                reply = res.json()["message"]["content"].strip()
                return True, reply, elapsed
        except Exception as e:
            print(f"[Ollama Service Warning] {e}")
        return False, "", 0.0
