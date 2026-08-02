"""
Purpose:
Intelligent Decision Engine & Fallback Router for Jarvis AI Services.

Responsibilities:
- Classify queries into Casual vs Complex/Coding
- Smart Routing: Casual -> Groq, Complex/Coding -> Gemini
- Internet connectivity check (Online -> Cloud APIs, Offline -> Ollama)
- Multi-provider fallback chain (Groq <-> Gemini <-> Ollama)

Dependencies:
- services/groq.py
- services/gemini.py
- services/ollama.py
- memory/database.py
"""

import os
import time
import socket
from services.groq import GroqService
from services.gemini import GeminiService
from services.ollama import OllamaService
from memory.database import log_conversation_turn
from core.human_voice import HUMAN_VOICE_CORE

LOGS_DIR = (
    "/tmp/jarvis-logs"
    if os.getenv("VERCEL")
    else os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
)
os.makedirs(LOGS_DIR, exist_ok=True)


def is_internet_available(timeout: float = 0.8) -> bool:
    """Fast socket check to determine if internet connection is live."""
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(("8.8.8.8", 53))
        return True
    except Exception:
        return False


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
    """
    Intelligent Decision Engine & Multi-Provider Router.
    Routes queries dynamically based on complexity and connectivity.
    """

    def __init__(self):
        self.groq_service = GroqService()
        self.gemini_service = GeminiService()
        self.ollama_service = OllamaService()

    def classify_query(self, prompt: str) -> str:
        """Classifies prompt as 'Casual' (Fast response) or 'Complex' (Deep reasoning/Coding)."""
        text = prompt.lower().strip()
        words = text.split()
        complex_keywords = [
            "code",
            "python",
            "script",
            "api",
            "function",
            "write a",
            "explain in detail",
            "architecture",
            "refactor",
            "debug",
            "compare",
            "solution",
            "database",
            "algorithm",
        ]
        if len(words) > 12 or any(kw in text for kw in complex_keywords):
            return "Complex"
        return "Casual"

    def print_provider_monitor(
        self,
        provider: str,
        model: str,
        latency: float,
        approx_tokens: int,
        fallback: bool = False,
        prompt: str = "",
        response: str = "",
    ):
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

    def route_and_ask(self, prompt: str, system_instruction: str = "", history: list = None) -> str:
        """
        Intelligent Routing Flow:
        1. Check Internet Connectivity (Online vs Offline)
        2. Classify Query (Casual -> Groq, Complex -> Gemini)
        3. Execute with Automatic Provider Fallback Chain
        """
        hist = history if history is not None else []
        system_instruction = f"{HUMAN_VOICE_CORE}\n\n{system_instruction}".strip()
        online = is_internet_available()
        query_type = self.classify_query(prompt)

        if online:
            if query_type == "Complex":
                # Route Complex/Coding queries to Gemini first
                start_t = time.time()
                ok_gem, reply_gem = self.gemini_service.ask(
                    prompt, system_instruction=system_instruction
                )
                elapsed = time.time() - start_t
                if ok_gem:
                    model = getattr(self.gemini_service, "active_model", "gemini-3.1-flash-lite")
                    approx_tokens = len(prompt.split()) + len(reply_gem.split()) + 50
                    self.print_provider_monitor(
                        "Gemini (Cloud)",
                        model,
                        elapsed,
                        approx_tokens,
                        fallback=False,
                        prompt=prompt,
                        response=reply_gem,
                    )
                    print(f"Jarvis: '{reply_gem}'")
                    return reply_gem

            # Primary for Casual or Fallback for Complex: Groq AI
            ok_groq, reply_groq, elapsed = self.groq_service.ask(
                prompt, system_instruction=system_instruction, history=hist
            )
            if ok_groq:
                approx_tokens = len(prompt.split()) + len(reply_groq.split()) + 50
                fallback_flag = query_type == "Complex"
                self.print_provider_monitor(
                    "Groq (Ultra-Fast)",
                    self.groq_service.model,
                    elapsed,
                    approx_tokens,
                    fallback=fallback_flag,
                    prompt=prompt,
                    response=reply_groq,
                )
                print(f"Jarvis: '{reply_groq}'")
                return reply_groq

            # Fallback to Gemini if Groq was unavailable
            if query_type == "Casual":
                start_t = time.time()
                ok_gem, reply_gem = self.gemini_service.ask(
                    prompt, system_instruction=system_instruction
                )
                elapsed = time.time() - start_t
                if ok_gem:
                    model = getattr(self.gemini_service, "active_model", "gemini-3.1-flash-lite")
                    approx_tokens = len(prompt.split()) + len(reply_gem.split()) + 50
                    self.print_provider_monitor(
                        "Gemini (Cloud)",
                        model,
                        elapsed,
                        approx_tokens,
                        fallback=True,
                        prompt=prompt,
                        response=reply_gem,
                    )
                    print(f"Jarvis: '{reply_gem}'")
                    return reply_gem

        # Offline / Tertiary Fallback: Ollama Local AI
        print("[LLM Router] Offline mode or Cloud API unavailable. Routing to Local Ollama AI...")
        messages_ol = [{"role": "system", "content": system_instruction or "You are Jarvis AI."}]
        for h in hist[-2:]:
            messages_ol.append(h)
        messages_ol.append({"role": "user", "content": prompt})

        ok_ol, reply_ol, elapsed = self.ollama_service.ask(messages_ol)
        if ok_ol:
            approx_tokens = len(prompt.split()) + len(reply_ol.split()) + 50
            self.print_provider_monitor(
                "Ollama (Local)",
                self.ollama_service.model,
                elapsed,
                approx_tokens,
                fallback=True,
                prompt=prompt,
                response=reply_ol,
            )
            print(f"Jarvis: '{reply_ol}'")
            return reply_ol

        return "Sorry Boss, please add a free Groq or Gemini API key in your .env file or run Ollama locally."


# Global Router Instance
_global_router = LLMRouter()


def ask_ai(user_message: str, system_instruction: str = "", history: list = None) -> str:
    """Standalone function to query Intelligent Decision Engine."""
    return _global_router.route_and_ask(
        user_message, system_instruction=system_instruction, history=history
    )
