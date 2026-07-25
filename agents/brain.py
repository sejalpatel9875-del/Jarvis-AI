import re
import agents.memory as memory_agent
from services.llm_router import ask_ai

ALLOWED_ACTION_INTENTS = {
    "search_chatgpt", "send_whatsapp", "send_instagram", "search_google",
    "open_app", "open_website", "play_music", "close_app", "adjust_volume",
    "adjust_brightness", "lock_pc", "take_screenshot", "generate_image",
    "describe_screen", "search_wikipedia", "shutdown_pc", "restart_pc",
    "sleep_pc", "cancel_shutdown"
}

def parse_action_tags(response_text: str) -> tuple[list, str]:
    """Parses prefix tags like [ACTION: play_music | song] ONLY if intent is in ALLOWED_ACTION_INTENTS."""
    pattern = r'\[ACTION:\s*(\w+)\s*\|\s*(.*?)\]'
    matches = list(re.finditer(pattern, response_text))
    
    actions = []
    clean_text = response_text
    
    for m in matches:
        intent = m.group(1).strip().lower()
        argument = m.group(2).strip()
        if intent in ALLOWED_ACTION_INTENTS:
            actions.append((intent, argument))
            clean_text = clean_text.replace(m.group(0), "")
        else:
            clean_text = clean_text.replace(m.group(0), "")
            
    clean_text = re.sub(r'\[ACTION:.*?\]', '', clean_text)
    clean_text = re.sub(r'```.*?```', '', clean_text, flags=re.DOTALL).strip()
    return actions, clean_text

class JarvisBrain:
    """AI Orchestrator Agent."""
    def __init__(self):
        self.conversation_history = []

    def get_system_instruction(self) -> str:
        user_title = memory_agent.get_user_title()
        memory_context = memory_agent.get_memory_context()
        
        return (
            f"You are Jarvis — an ultra-smart, loyal, highly professional AI assistant. "
            f"Always address the user as '{user_title}'.\n"
            "FLUENCY & SPEECH RULES:\n"
            "1. Speak in clean, natural Hinglish (conversational blend of Hindi and English).\n"
            "2. If any technical phrase or explanation sounds awkward in Hindi, USE ENGLISH naturally instead.\n"
            "3. Ensure 100% perfect grammar and natural sentence flow. NEVER produce literal broken Hindi translations (e.g. NEVER say 'Main tumhare service mein hai').\n"
            f"4. Keep responses crisp, polite, and confident (max 1-2 short sentences). {memory_context}\n\n"
            "COMMAND RULES: Prepend action tag(s) at start if user asks to open/search/send:\n"
            "[ACTION: <intent> | <arg>]\n"
            "Examples:\n"
            "- 'chatgpt par search karo website kaise banta hai' -> [ACTION: search_chatgpt | website kaise banta hai]\n"
            "- 'whatsapp open karke kuldeep ko message kare hello' -> [ACTION: send_whatsapp | kuldeep:hello]\n"
            "Intents: search_chatgpt (query), send_whatsapp (recipient:message), send_instagram (user:msg), search_google (query), "
            "open_app (app), open_website (domain), play_music (song), close_app (app), adjust_volume (level), adjust_brightness (level), "
            "lock_pc (none), take_screenshot (none), generate_image (prompt), describe_screen (none), search_wikipedia (query), "
            "shutdown_pc (none), restart_pc (none), sleep_pc (none), cancel_shutdown (none)."
        )

    def think(self, user_message: str) -> tuple[str, list]:
        """Processes user message through multi-provider AI engine via ask_ai."""
        # 1. Auto-learn memory facts from input
        memory_agent.auto_learn_from_input(user_message)
        
        # 2. Get response from multi-provider LLM Router via ask_ai
        sys_inst = self.get_system_instruction()
        raw_reply = ask_ai(user_message, system_instruction=sys_inst, history=self.conversation_history)
        
        # 3. Parse action tags
        actions, clean_text = parse_action_tags(raw_reply)
        
        if not clean_text or clean_text.startswith("[ACTION:"):
            clean_text = f"Sure {memory_agent.get_user_title()}, executing your command now."
            
        self.conversation_history.append({"role": "user", "content": user_message})
        self.conversation_history.append({"role": "assistant", "content": clean_text})
        
        return clean_text, actions

    def process(self, user_message: str):
        return self.think(user_message)

# Legacy alias compatibility
AgentBrain = JarvisBrain
