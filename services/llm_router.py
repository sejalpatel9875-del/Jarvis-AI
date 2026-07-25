import os
import time
import requests
import config
from services.gemini import GeminiService
from services.ollama import OllamaService
from memory.database import log_conversation_turn

# HTTP Session Connection Pool for persistent TCP connections (< 0.5s response speed)
_http_session = requests.Session()
_http_session.headers.update({
    "Connection": "keep-alive",
    "Accept-Encoding": "gzip, deflate"
})

LOGS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
os.makedirs(LOGS_DIR, exist_ok=True)

def log_interaction(provider: str, model: str, latency: float, prompt: str, response: str):
    """Logs interaction telemetry entry to logs/YYYY-MM-DD.log."""
    try:
        import datetime
        today_str = datetime.date.today().strftime("%Y-%m-%d")
        now_time = datetime.datetime.now().strftime("%H:%M:%S")
        log_file = os.path.join(LOGS_DIR, f"{today_str}.log")
        
        entry = (
            f"Time: {now_time}\n"
            f"Provider: {provider}\n"
            f"Model: {model}\n"
            f"Latency: {latency:.2f}s\n"
            f"Prompt: {prompt}\n"
            f"Response: {response}\n"
            f"{'-' * 60}\n"
        )
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(entry)
    except Exception as e:
        print(f"[Logging Error] Failed to write daily log: {e}")

class LLMRouter:
    """Multi-Provider AI Router (Groq -> Gemini -> Ollama)."""
    def __init__(self):
        self.groq_key = getattr(config, "GROQ_API_KEY", "")
        self.gemini_service = GeminiService()
        self.ollama_service = OllamaService()

    def print_provider_monitor(self, provider: str, model: str, latency: float, approx_tokens: int, fallback: bool = False, prompt: str = "", response: str = ""):
        print("-" * 60)
        print("[Provider Monitor]")
        print(f"Provider : {provider}")
        print(f"Model    : {model}")
        print(f"Latency  : {latency:.2f} s")
        print(f"Tokens   : ~{approx_tokens}")
        print(f"Fallback : {'Yes' if fallback else 'No'}")
        print("-" * 60)
        log_interaction(provider, model, latency, prompt, response)
        log_conversation_turn(prompt, response, provider, latency)

    def route_and_ask(self, prompt: str, system_instruction: str, history: list) -> str:
        """Executes LLM call following priority sequence: Groq -> Gemini -> Ollama."""
        
        # 1. Primary: Groq AI (< 0.3s speed)
        if self.groq_key and self.groq_key != "your_groq_api_key_here":
            model = "llama-3.1-8b-instant"
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.groq_key}",
                "Content-Type": "application/json"
            }
            messages = [{"role": "system", "content": system_instruction}]
            for h in history[-2:]:
                messages.append(h)
            messages.append({"role": "user", "content": prompt})
            
            payload = {
                "model": model,
                "messages": messages,
                "temperature": 0.5,
                "max_tokens": 180
            }
            try:
                start_t = time.time()
                res = _http_session.post(url, headers=headers, json=payload, timeout=6)
                elapsed = time.time() - start_t
                if res.status_code == 200:
                    reply = res.json()["choices"][0]["message"]["content"].strip()
                    approx_tokens = len(prompt.split()) + len(reply.split()) + 50
                    self.print_provider_monitor("Groq", model, elapsed, approx_tokens, fallback=False, prompt=prompt, response=reply)
                    print(f"Jarvis: '{reply}'")
                    return reply
            except Exception as ex:
                print(f"[Groq Exception] {ex}")

        # 2. Secondary: Gemini Cloud API
        if self.gemini_service.api_key:
            start_t = time.time()
            ok_gem, reply_gem = self.gemini_service.ask(prompt, system_instruction=system_instruction)
            elapsed = time.time() - start_t
            if ok_gem:
                model = getattr(self.gemini_service, 'active_model', 'gemini-3.1-flash-lite')
                approx_tokens = len(prompt.split()) + len(reply_gem.split()) + 50
                self.print_provider_monitor("Gemini", model, elapsed, approx_tokens, fallback=True, prompt=prompt, response=reply_gem)
                print(f"Jarvis: '{reply_gem}'")
                return reply_gem

        # 3. Tertiary: Ollama Local AI
        messages_ol = [{"role": "system", "content": system_instruction}]
        for h in history[-2:]:
            messages_ol.append(h)
        messages_ol.append({"role": "user", "content": prompt})
        
        ok_ol, reply_ol, elapsed = self.ollama_service.ask(messages_ol)
        if ok_ol:
            approx_tokens = len(prompt.split()) + len(reply_ol.split()) + 50
            self.print_provider_monitor("Ollama (Local)", self.ollama_service.model, elapsed, approx_tokens, fallback=True, prompt=prompt, response=reply_ol)
            print(f"Jarvis: '{reply_ol}'")
            return reply_ol

        return "Sorry Boss, please add a free Groq or Gemini API key in your .env file or run Ollama locally."
