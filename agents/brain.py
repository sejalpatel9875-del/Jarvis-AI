"""
Purpose:
Central AI Orchestrator Brain for Jarvis AI OS.

Responsibilities:
- Integrate Planner Agent (Reasoner -> Executor -> Validator)
- Manage system instructions, speech fluency, and action dispatching
- Multi-provider AI routing and SQLite memory logging

Dependencies:
- agents/planner.py
- memory/manager.py
- agents/memory.py
"""

import re
from memory.manager import MemoryManager
from agents.planner import PlannerAgent
import agents.memory as memory_agent
from services.llm_router import ask_ai

class JarvisBrain:
    """
    AI Orchestrator Brain for Jarvis.
    Flow: Receive Prompt -> Load Memory -> Planner Agent (Reasoner -> Executor -> Validator) -> Return Response
    """
    def __init__(self):
        self.memory_manager = MemoryManager()
        self.planner = PlannerAgent()

    def get_system_instruction(self) -> str:
        user_title = self.memory_manager.get_preference("user_name", "Boss")
        memory_context = memory_agent.get_memory_context()
        
        return (
            f"You are Jarvis — an ultra-smart, loyal, highly professional AI assistant. "
            f"Always address the user as '{user_title}'.\n"
            "FLUENCY & SPEECH RULES:\n"
            "1. Speak in clean, natural Hinglish (conversational blend of Hindi and English).\n"
            "2. If any technical phrase or explanation sounds awkward in Hindi, USE ENGLISH naturally instead.\n"
            "3. Ensure 100% perfect grammar and natural sentence flow. NEVER produce literal broken Hindi translations.\n"
            f"4. Keep responses crisp, polite, and confident (max 1-2 short sentences). {memory_context}"
        )

    def think(self, user_message: str) -> tuple[str, list]:
        """
        Orchestrates full Autonomous Agent Flow:
        1. Auto-learn memory facts from input
        2. Solve goal via PlannerAgent (Reasoner -> Executor -> Validator)
        3. Save Conversation into SQLite Memory Engine
        4. Return clean response and executed actions
        """
        # 1. Auto-learn memory facts
        memory_agent.auto_learn_from_input(user_message)
        
        # 2. Delegate to Autonomous Planner Agent
        sys_inst = self.get_system_instruction()
        clean_text, actions = self.planner.solve_goal(user_message, memory_context=sys_inst)
        
        # Clean action tags while preserving code blocks and OCR results
        clean_text = re.sub(r'\[ACTION:.*?\]', '', clean_text).strip()
        
        if not clean_text:
            user_title = self.memory_manager.get_preference("user_name", "Boss")
            clean_text = f"Sure {user_title}, command executed successfully."

        # 3. Save turn into SQLite Persistent Memory
        self.memory_manager.save_turn(user_message, clean_text, provider="Groq")
        memory_agent.save({"user": user_message, "assistant": clean_text})

        # 4. Return Response
        return clean_text, actions

    def process(self, user_message: str):
        return self.think(user_message)

# Legacy alias compatibility
AgentBrain = JarvisBrain
