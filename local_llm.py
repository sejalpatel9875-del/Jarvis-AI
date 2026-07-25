import sys
import os
import requests
import json
import config

# Reconfigure stdout/stderr to support printing UTF-8 characters (like Hindi) on Windows command prompt
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
if sys.stderr.encoding != 'utf-8':
    try:
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

class LocalChatbot:
    """
    Manages conversational session with local Gemma 3 via Ollama's local REST API.
    Builds its system instruction dynamically from memory.json to support learned facts and personality guidelines.
    """
    def __init__(self, model_name: str = None):
        self.model_name = model_name or getattr(config, "LOCAL_MODEL", "gemma3:1b")
        self.ollama_url = "http://localhost:11434/api/chat"
        self.history = []
        
        # Build initial system instruction from memory.json
        self.system_instruction = self.build_system_instruction()
        
        # Seed history with system instruction
        self.history.append({"role": "system", "content": self.system_instruction})
        print(f"[Local LLM] Initialized {self.model_name} with Dynamic Memory via Ollama.")

    def build_system_instruction(self) -> str:
        """Loads facts and personality guidelines from memory.json and builds a system prompt."""
        try:
            import memory_manager
            mem = memory_manager.load_memory()
        except Exception as e:
            print(f"[Local LLM Memory Load Error] {e}")
            mem = {
                "user_facts": {"name": "Kajal maam", "location": "Prayagraj"},
                "personality": {"tone": "friendly, casual, and funny", "guidelines": []},
                "custom_contacts": {}
            }
            
        tone = mem.get("personality", {}).get("tone", "friendly, casual, and funny")
        guidelines = mem.get("personality", {}).get("guidelines", [])
        facts = mem.get("user_facts", {})
        
        guidelines_str = "\n".join([f"- {g}" for g in guidelines])
        facts_str = "\n".join([f"- {k}: {v}" for k, v in facts.items()])
        
        prompt = (
            "You are Jarvis, a concise AI voice assistant. Always address user as 'Kajal maam'. "
            f"Your current personality style is: {tone}. Respond in Hinglish. Default location: Prayagraj. "
            "No markdown, no bold, no code blocks. Never say 'fetching data' or 'let me search'. Just answer.\n\n"
            "PERSONALITY INSTRUCTIONS:\n"
            "- Be friendly, casual, funny, and witty. Avoid repeating same words or lines.\n"
            "- Never be lazy, boring, or robotic.\n"
            f"{guidelines_str}\n\n"
            "LEARNED FACTS ABOUT THE USER (Use these to personalize chat):\n"
            f"{facts_str}\n\n"
            "MEMORIZATION & LEARNING SYSTEM:\n"
            "If the user tells you to remember something (e.g., 'remember my phone is red', 'remember I love tea'), "
            "or wants to save/add a contact (e.g., 'save dad number as +919988776655', 'save contact mom'), "
            "or wants to change your personality/behavior (e.g., 'be more friendly', 'be casual', 'stop saying maam'), "
            "you MUST prepend matching memory action tags to the response:\n"
            "- [ACTION: learn | key:value] (e.g., [ACTION: learn | favorite_color:red])\n"
            "- [ACTION: add_contact | name:number] (e.g., [ACTION: add_contact | dad:+919988776655])\n"
            "- [ACTION: update_personality | style] (e.g., [ACTION: update_personality | be extremely funny and sarcastic])\n\n"
            "HALLUCINATION CONTROL: You are a small local model. NEVER guess or make up facts, songs, names, or real-time info. "
            "If the user asks about general knowledge, facts, news, weather, or current events (e.g., 'who is Arijit Singh', 'search Arijit Singh songs'), "
            "you MUST route it to [ACTION: search_google | <exact query>] so the system can fetch real information. "
            "Ensure the argument for search_google contains the full, exact context (e.g., '[ACTION: search_google | arijit singh songs]' instead of just 'arjit singh').\n\n"
            "ACTION ROUTING RULES:\n"
            "If user wants to open apps, websites, close apps, play songs, lock PC, take screenshot, or run commands, you MUST prepend [ACTION: <intent> | <arg>] tags to the very beginning of your response.\n"
            "For multiple requests in one go, prepend multiple separate tags sequentially. E.g., 'open youtube and instagram' -> '[ACTION: open_app | youtube] [ACTION: open_app | instagram]'.\n"
            "Available Intents:\n"
            "- play_music (arg: song or artist name)\n"
            "- open_app (arg: app name like calculator, notepad, chrome, vscode, whatsapp, instagram, youtube)\n"
            "- close_app (arg: app name to close like chrome, notepad, whatsapp, vscode)\n"
            "- open_website (arg: website name or domain)\n"
            "- search_google (arg: exact search query)\n"
            "- adjust_volume (arg: up/down/value)\n"
            "- adjust_brightness (arg: up/down/value)\n"
            "- open_youtube (no arg)\n"
            "- open_browser (no arg)\n"
            "- lock_pc (no arg)\n"
            "- take_screenshot (no arg)\n"
            "- send_whatsapp (arg: recipient:message - e.g., '[ACTION: send_whatsapp | kuldeep:hi]')\n"
            "- send_instagram (arg: username:message)\n"
            "- learn (arg: key:value)\n"
            "- add_contact (arg: name:number)\n"
            "- update_personality (arg: style)\n\n"
            "Example for multi-command 'open youtube and search google for weather':\n"
            "[ACTION: open_app | youtube] [ACTION: search_google | weather] Okay Kajal maam, opening YouTube and searching for weather."
        )
        return prompt

    def refresh_prompt(self):
        """Reloads the memory and refreshes the system instruction in conversation history."""
        self.system_instruction = self.build_system_instruction()
        if len(self.history) > 0 and self.history[0]["role"] == "system":
            self.history[0]["content"] = self.system_instruction
            print("[Local LLM] System prompt refreshed with latest memories.")

    def ask(self, user_text: str) -> str:
        """
        Queries Ollama's local API and returns the text response.
        """
        if not user_text:
            return ""
            
        print(f"[Local Chatbot] User: '{user_text}'")
        
        # Refresh prompt to make sure any recently learned memories are active
        self.refresh_prompt()
        
        # Append user message
        self.history.append({"role": "user", "content": user_text})
        
        # Keep sliding history window to save RAM on 8GB machines (max 10 recent messages + system instruction)
        if len(self.history) > 11:
            self.history = [self.history[0]] + self.history[-10:]
            
        payload = {
            "model": self.model_name,
            "messages": self.history,
            "stream": False,
            "options": {
                "temperature": 0.7
            }
        }
        
        try:
            print("[Local Chatbot] Thinking... (CPU inference, please wait)")
            response = requests.post(self.ollama_url, json=payload, timeout=120)
            if response.status_code == 200:
                result = response.json()
                reply = result["message"]["content"].strip()
                
                # Append assistant reply to history
                self.history.append({"role": "assistant", "content": reply})
                print(f"[Local Chatbot] Jarvis: '{reply}'")
                return reply
            else:
                print(f"[Local LLM Error] Ollama returned status code: {response.status_code}")
                return "Sorry Kajal maam, I couldn't get a response from my local brain."
        except requests.exceptions.ConnectionError:
            print("[Local LLM Error] Ollama is not running!")
            return "Sorry Kajal maam, Ollama band hai. Please Ollama app open karo system tray se."
        except requests.exceptions.ReadTimeout:
            print("[Local LLM Error] Response took too long (>120s).")
            return "Sorry Kajal maam, response mein bahut time lag raha hai. Chhota sawaal puchiye."
        except Exception as e:
            print(f"[Local LLM Error] Connection failed: {e}")
            return "Sorry Kajal maam, Ollama is not running. Please make sure Ollama is open."

if __name__ == "__main__":
    print("--- Jarvis Local Chatbot Test ---")
    bot = LocalChatbot()
    while True:
        try:
            inp = input("\nYou: ")
            if inp.lower() in ["exit", "quit"]:
                break
            bot.ask(inp)
        except KeyboardInterrupt:
            break
