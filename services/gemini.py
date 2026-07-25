import sys
import config
from google import genai
from google.genai import types

class GeminiService:
    """Service for interacting with Google Gemini Cloud API with automatic model retry."""
    def __init__(self, api_key: str = None):
        self.api_key = api_key or getattr(config, "GEMINI_API_KEY", "")
        self.client = None
        self.chat = None
        self.active_model = "gemini-3.1-flash-lite"
        
        if self.api_key and self.api_key != "your_gemini_api_key_here":
            self.init_client()

    def init_client(self, preferred_model: str = "gemini-3.1-flash-lite", system_instruction: str = ""):
        candidate_models = [preferred_model, "gemini-3.1-flash-lite", "gemini-1.5-flash", "gemini-2.0-flash"]
        for m in candidate_models:
            try:
                self.client = genai.Client(api_key=self.api_key)
                self.chat = self.client.chats.create(
                    model=m,
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction or "You are Jarvis AI.",
                        temperature=0.5
                    )
                )
                self.active_model = m
                break
            except Exception as e:
                print(f"[Gemini Service Warning] Model '{m}' failed: {e}")

    def ask(self, prompt: str, system_instruction: str = "") -> tuple[bool, str]:
        if not self.client or not self.chat:
            self.init_client(system_instruction=system_instruction)
        if not self.chat:
            return False, ""
            
        for attempt in range(2):
            try:
                res = self.chat.send_message(prompt)
                reply = res.text.strip()
                return True, reply
            except Exception as ex:
                print(f"[Gemini Service Error] {ex}")
                self.init_client(preferred_model="gemini-1.5-flash", system_instruction=system_instruction)
        return False, ""
