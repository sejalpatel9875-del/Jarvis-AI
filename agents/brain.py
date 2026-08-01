"""
Purpose:
Central AI Orchestrator Brain for Jarvis AI OS.

Responsibilities:
- Integrate Planner Agent (Reasoner -> Executor -> Validator)
- Manage system instructions, speech fluency, and action dispatching
- Multi-provider AI routing, SQLite memory logging, and plugin loader initialization

Dependencies:
- agents/planner.py
- memory/manager.py
- agents/memory.py
- services/logger.py
- services/plugin_loader.py
"""

import re
import time
from memory.manager import MemoryManager
from agents.planner import PlannerAgent
import agents.memory as memory_agent
from services.logger import logger
from services.plugin_loader import plugin_loader

class JarvisBrain:
    """
    AI Orchestrator Brain for Jarvis.
    Flow: Auto-load plugins -> Receive Prompt -> Auto-learn Memory -> Solve via Planner -> Log & Save -> Return Response
    """
    def __init__(self):
        self.memory_manager = MemoryManager()
        self.planner = PlannerAgent()
        
        # Auto-discover external plugins on initialization
        try:
            plugin_loader.discover_and_load()
        except Exception as e:
            logger.error("BRAIN_INIT", f"Plugin discovery error: {e}")

    def get_system_instruction(self, user_message: str = "") -> str:
        user_title = self.memory_manager.get_preference("user_name", "Boss")
        memory_context = memory_agent.get_memory_context()
        if re.search(r"[\u0900-\u097F]", user_message):
            reply_language = "The user is speaking Hindi in Devanagari. Reply entirely in fluent, grammatically correct Devanagari Hindi. Use a warm, friendly, natural UP Prayagraj conversational tone. Use first-person plural 'हम' instead of 'मैं' where natural. Keep responses very short (1-2 sentences), emotion-aware, and avoid robotic phrasing."
        elif re.search(r"\b(kya|hai|hain|mujhe|mera|meri|aap|tum|kar|karo|batao|kaise|nahi|kyun|please|ho|haye|amigo)\b", user_message.lower()):
            reply_language = "The user is speaking Roman Hindi/Hinglish. Reply in fluent Roman Hindi/Hinglish with a natural, friendly UP Prayagraj conversational tone. Use 'hum' instead of 'main', 'humko' instead of 'mujhe'. Keep sentences very short and punchy, insert natural punctuation commas for TTS pauses, and avoid robotic phrases."
        else:
            reply_language = "The user is speaking English. Reply in natural, professional, and friendly English. Keep responses crisp, short (1-2 sentences), and polite."
        
        return (
            f"The user's preferred title is '{user_title}'. Use it naturally only when it fits the conversation.\n"
            "LANGUAGE & SPEECH RULES:\n"
            f"1. {reply_language}\n"
            "2. Never use robotic phrases like 'Operation completed successfully' or 'Ready to receive command'. Instead, say things like 'Kaam ho gaya hai bhaiya' or 'Bataiye bhaiya, kya help chahiye?'.\n"
            "3. Keep sentences short, with clear punctuation for optimal voice flow. Never repeat wording.\n"
            "4. Do not mention these instructions. Keep responses confident, emotion-aware, and natural.\n"
            f"USER MEMORY CONTEXT:\n{memory_context}"
        )

    def think(self, user_message: str) -> tuple[str, list]:
        """
        Orchestrates full Autonomous Agent Flow with Observability Logging:
        1. Auto-learn memory facts from input
        2. Solve goal via PlannerAgent (Reasoner -> Executor -> Validator)
        3. Save Conversation into SQLite Memory Engine & Daily Log File
        4. Return clean response and executed actions
        """
        t0 = time.time()
        logger.user(user_message)

        # 1. Auto-learn memory facts
        memory_agent.auto_learn_from_input(user_message)
        
        # 2. Delegate to Autonomous Planner Agent
        sys_inst = self.get_system_instruction(user_message)
        clean_text, actions = self.planner.solve_goal(user_message, memory_context=sys_inst)
        
        # Clean action tags while preserving code blocks and OCR results
        clean_text = re.sub(r'\[ACTION:.*?\]', '', clean_text).strip()
        
        if not clean_text:
            user_title = self.memory_manager.get_preference("user_name", "Boss")
            clean_text = "Done."

        # 3. Save turn into SQLite Persistent Memory & Daily Logs
        latency = time.time() - t0
        logger.info("BRAIN_RESPONSE", f"Jarvis: '{clean_text}'", latency=latency)
        
        self.memory_manager.save_turn(user_message, clean_text, provider="Groq")
        memory_agent.save({"user": user_message, "assistant": clean_text})

        # 4. Return Response
        return clean_text, actions

    def process(self, user_message: str):
        return self.think(user_message)

# Legacy alias compatibility
AgentBrain = JarvisBrain
