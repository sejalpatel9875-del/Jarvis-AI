"""
Purpose:
Bridge connecting Agent Brain to the Central Tool Registry.

Responsibilities:
- Route intent action tags to registered tools via tool_registry.execute()
- Intercept fast local tool commands (<0.005s speed)

Dependencies:
- tools/
- agents/memory.py
"""

import re
from tools.registry import tool_registry
import agents.memory as memory_agent

def execute_tool(intent: str, arg: str, command_text: str = "") -> str:
    """Executes an action intent by dispatching to Central Tool Registry."""
    intent_clean = intent.strip().lower()
    arg_clean = arg.strip()

    if intent_clean == "play_music":
        res = tool_registry.execute("music", song_name=arg_clean)
        return res.result
    elif intent_clean in ["search_google", "search_chatgpt"]:
        engine = "chatgpt" if intent_clean == "search_chatgpt" else "google"
        res = tool_registry.execute("search", query=arg_clean, engine=engine)
        return res.result
    elif intent_clean in ["open_app", "close_app", "lock_pc", "take_screenshot", "adjust_volume", "adjust_brightness"]:
        res = tool_registry.execute("system", action=intent_clean, target=arg_clean)
        return res.result
    elif intent_clean == "open_website":
        res = tool_registry.execute("browser", url=arg_clean)
        return res.result

    return f"Executed '{intent_clean}' for '{arg_clean}', Boss."

def check_fast_local_tools(command_text: str) -> tuple[bool, str]:
    """Intercepts math expressions and memory commands via Tool Registry in <0.005s."""
    cmd_lower = command_text.lower().strip()

    # 1. Explicit Remember / Forget commands
    m_rem = re.search(r'^remember\s+(?:that\s+)?(.+?)\s+is\s+(.+?)$', cmd_lower)
    if m_rem:
        res = memory_agent.remember_fact(m_rem.group(1), m_rem.group(2))
        return True, res

    m_for = re.search(r'^forget\s+(.+?)$', cmd_lower)
    if m_for:
        res = memory_agent.forget_fact(m_for.group(1))
        return True, res

    # 2. Fast Calculator Tool Registry Check
    calc_res = tool_registry.execute("calculator", expression=command_text)
    if calc_res.success:
        return True, calc_res.result

    return False, ""
