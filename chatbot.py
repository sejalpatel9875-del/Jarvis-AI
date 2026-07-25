import os
import sys
import time
import random
import re
import requests
from google import genai
from google.genai import types
import config
import memory_manager

# Reconfigure stdout/stderr to support printing UTF-8 characters on Windows command prompt
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Persistent HTTP Session for fast TCP connection pooling (reduces API overhead to < 1.0s)
_http_session = requests.Session()
_http_session.headers.update({
    "Connection": "keep-alive",
    "Accept-Encoding": "gzip, deflate"
})

LOGS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
os.makedirs(LOGS_DIR, exist_ok=True)

def append_to_daily_log(provider: str, model: str, latency: float, prompt: str, response: str):
    """Appends interaction telemetry entry to logs/YYYY-MM-DD.log."""
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

class Chatbot:
    """
    Universal Ultra-Fast Multi-Provider AI Engine (Groq -> Gemini -> Ollama).
    Includes Provider Telemetry Monitor, Memory Persistence, & Natural Hinglish Personality.
    """
    def __init__(self):
        self.groq_key = getattr(config, "GROQ_API_KEY", "")
        self.cerebras_key = getattr(config, "CEREBRAS_API_KEY", "")
        self.gemini_key = getattr(config, "GEMINI_API_KEY", "")
        
        self.conversation_history = []
        self._update_system_instruction()
        
        # Initialize Gemini Client if key available
        self.gemini_client = None
        self.gemini_chat = None
        if self.gemini_key and self.gemini_key != "your_gemini_api_key_here":
            self._init_gemini_fallback()

        print("[Chatbot] Multi-Provider AI Engine Initialized.")

    def _update_system_instruction(self):
        """Builds natural system instruction with dynamic user title ('Boss') and memory facts."""
        user_title = memory_manager.get_user_title()  # Defaults to 'Boss'
        profile = memory_manager.load_profile()
        long_mem = memory_manager.load_long_memory()
        
        user_lang = profile.get("preferred_language", "Hinglish (Hindi + English)")
        city = profile.get("city", "")
        location_info = f"City: {city}" if city else ""
        
        # Dynamic facts memory string
        user_facts = long_mem.get("user_facts", {})
        facts_list = [f"{k}: {v}" for k, v in user_facts.items()]
        memory_context = f"\nSaved User Facts & Preferences: [{', '.join(facts_list)}]" if facts_list else ""

        self.system_instruction = (
            f"Tum Jarvis ho — ek professional, intelligent aur friendly AI assistant. "
            f"User ko '{user_title}' bolo. "
            f"Short, natural {user_lang} me jawab do. "
            "Kabhi facts invent mat karo. Agar information nahi pata ho to clearly bolo. "
            f"Har response 1-2 short lines me rakho jab tak user detail na maange. {location_info}{memory_context}\n\n"
            "COMMAND RULES: Prepend action tag(s) at start if user asks to open/search/send:\n"
            "[ACTION: <intent> | <arg>]\n"
            "Examples:\n"
            "- 'chatgpt par search karo website kaise banta hai' -> [ACTION: search_chatgpt | website kaise banta hai]\n"
            "- 'whatsapp open karke kuldeep ko message kare hello' -> [ACTION: send_whatsapp | kuldeep:hello]\n"
            "- 'chrome open karo aur usmein charging search karo' -> [ACTION: search_google | charging]\n"
            "Intents: search_chatgpt (query), send_whatsapp (recipient:message), send_instagram (user:msg), search_google (query), "
            "open_app (app), open_website (domain), play_music (song), close_app (app), adjust_volume (level), adjust_brightness (level), "
            "lock_pc (none), take_screenshot (none), generate_image (prompt), describe_screen (none), search_wikipedia (query), "
            "shutdown_pc (none), restart_pc (none), sleep_pc (none), cancel_shutdown (none)."
        )

    def _init_gemini_fallback(self, preferred_model: str = "gemini-3.1-flash-lite"):
        """Initializes Gemini chat session with dynamic model fallback."""
        if not self.gemini_key or self.gemini_key == "your_gemini_api_key_here":
            return
        candidate_models = [preferred_model, "gemini-3.1-flash-lite", "gemini-1.5-flash", "gemini-2.0-flash"]
        for m in candidate_models:
            try:
                self.gemini_client = genai.Client(api_key=self.gemini_key)
                self.gemini_chat = self.gemini_client.chats.create(
                    model=m,
                    config=types.GenerateContentConfig(
                        system_instruction=self.system_instruction,
                        temperature=0.5
                    )
                )
                self.active_gemini_model = m
                break
            except Exception as e:
                print(f"[Gemini Init Warning] Model '{m}' failed: {e}")

    def classify_query(self, user_text: str) -> str:
        text = user_text.lower().strip()
        words = text.split()
        advanced_keywords = [
            "why", "how to", "explain", "code", "python", "script", "compare",
            "calculate", "detail", "describe", "difference", "solution", "debug"
        ]
        is_advanced = (
            len(words) > 10 or
            any(kw in text for kw in advanced_keywords)
        )
        return "Advanced" if is_advanced else "Casual"

    def _log_provider_monitor(self, provider: str, model: str, latency: float, approx_tokens: int, fallback: bool = False, prompt: str = "", response: str = ""):
        """Prints clean Provider Monitor Telemetry block and logs to file."""
        print("-" * 60)
        print("[Provider Monitor]")
        print(f"Provider : {provider}")
        print(f"Model    : {model}")
        print(f"Latency  : {latency:.2f} s")
        print(f"Tokens   : ~{approx_tokens}")
        print(f"Fallback : {'Yes' if fallback else 'No'}")
        print("-" * 60)
        append_to_daily_log(provider, model, latency, prompt, response)

    def _ask_groq(self, user_text: str, is_advanced: bool) -> tuple[bool, str]:
        """Queries Groq AI API using connection pooling (< 1.5s target speed)."""
        model = "llama-3.1-8b-instant"
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.groq_key}",
            "Content-Type": "application/json"
        }
        
        self._update_system_instruction()
        messages = [{"role": "system", "content": self.system_instruction}]
        
        # Trim history to max 2 turns for ultra-fast token processing
        for h in self.conversation_history[-2:]:
            messages.append(h)
        messages.append({"role": "user", "content": user_text})
        
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
                data = res.json()
                reply = data["choices"][0]["message"]["content"].strip()
                approx_tokens = len(user_text.split()) + len(reply.split()) + 50
                self._log_provider_monitor("Groq", model, elapsed, approx_tokens, fallback=False, prompt=user_text, response=reply)
                print(f"Jarvis: '{reply}'")
                return True, reply
            else:
                print(f"[Groq Error {res.status_code}] {res.text[:100]}")
                return False, ""
        except Exception as ex:
            print(f"[Groq Exception] {ex}")
            return False, ""

    def _ask_gemini(self, user_text: str) -> tuple[bool, str]:
        """Queries Gemini Cloud API (Secondary)."""
        if not self.gemini_client:
            self._init_gemini_fallback()
        if not self.gemini_chat:
            return False, ""
        
        self._update_system_instruction()
        user_title = memory_manager.get_user_title()
        prompt = f"[User: {user_title}]\n{user_text}"
        
        for attempt in range(2):
            try:
                start_t = time.time()
                res = self.gemini_chat.send_message(prompt)
                elapsed = time.time() - start_t
                reply = res.text.strip()
                model = getattr(self, 'active_gemini_model', 'gemini-3.1-flash-lite')
                approx_tokens = len(user_text.split()) + len(reply.split()) + 50
                self._log_provider_monitor("Gemini", model, elapsed, approx_tokens, fallback=True, prompt=user_text, response=reply)
                print(f"Jarvis: '{reply}'")
                return True, reply
            except Exception as ex:
                print(f"[Gemini Fallback Error] {ex}")
                self._init_gemini_fallback(preferred_model="gemini-1.5-flash")
        return False, ""

    def _ask_ollama(self, user_text: str) -> tuple[bool, str]:
        """Queries local Ollama instance (Tertiary)."""
        ollama_url = getattr(config, "OLLAMA_URL", "http://localhost:11434/api/chat")
        ollama_model = getattr(config, "OLLAMA_MODEL", "llama3.2")
        
        self._update_system_instruction()
        messages = [{"role": "system", "content": self.system_instruction}]
        for h in self.conversation_history[-2:]:
            messages.append(h)
        messages.append({"role": "user", "content": user_text})
        
        payload = {
            "model": ollama_model,
            "messages": messages,
            "stream": False
        }
        try:
            start_t = time.time()
            res = _http_session.post(ollama_url, json=payload, timeout=8)
            elapsed = time.time() - start_t
            if res.status_code == 200:
                reply = res.json()["message"]["content"].strip()
                approx_tokens = len(user_text.split()) + len(reply.split()) + 50
                self._log_provider_monitor("Ollama (Local)", ollama_model, elapsed, approx_tokens, fallback=True, prompt=user_text, response=reply)
                print(f"Jarvis: '{reply}'")
                return True, reply
        except Exception:
            pass
        return False, ""

    def ask(self, user_text: str) -> str:
        if not user_text:
            return ""
            
        # 0. Auto-learn memory facts (e.g. favorite language, name, contacts)
        memory_manager.auto_learn_from_input(user_text)
        
        mode_label = self.classify_query(user_text)
        print(f"[Chatbot] [{mode_label} Mode] User: '{user_text}'")
        
        # Priority Fallback Sequence: 1. Groq  ->  2. Gemini  ->  3. Ollama
        
        # 1. Groq AI (Primary)
        if self.groq_key and self.groq_key != "your_groq_api_key_here":
            ok, reply = self._ask_groq(user_text, mode_label == "Advanced")
            if ok:
                self.conversation_history.append({"role": "user", "content": user_text})
                self.conversation_history.append({"role": "assistant", "content": reply})
                memory_manager.add_short_turn(user_text, reply)
                return reply

        # 2. Gemini Cloud API (Secondary)
        if self.gemini_client:
            ok, reply = self._ask_gemini(user_text)
            if ok:
                self.conversation_history.append({"role": "user", "content": user_text})
                self.conversation_history.append({"role": "assistant", "content": reply})
                memory_manager.add_short_turn(user_text, reply)
                return reply

        # 3. Ollama Local AI (Tertiary)
        ok_ollama, reply_ollama = self._ask_ollama(user_text)
        if ok_ollama:
            self.conversation_history.append({"role": "user", "content": user_text})
            self.conversation_history.append({"role": "assistant", "content": reply_ollama})
            memory_manager.add_short_turn(user_text, reply_ollama)
            return reply_ollama

        return "Sorry Boss, please add a free Groq or Gemini API key in your .env file or run Ollama locally."

if __name__ == "__main__":
    bot = Chatbot()
    print(bot.ask("hello how are you"))
