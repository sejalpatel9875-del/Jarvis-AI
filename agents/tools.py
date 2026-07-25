import re
import automation
import tool_router
import browser_agent
import pdf_agent
import agents.memory as memory_agent

def execute_tool(intent: str, arg: str, command_text: str = "") -> str:
    """Executes a parsed action intent tool."""
    intent_clean = intent.strip().lower()
    arg_clean = arg.strip()
    
    if intent_clean == "play_music":
        return automation.play_song(arg_clean)
    elif intent_clean == "open_app":
        return automation.open_app(arg_clean)
    elif intent_clean == "close_app":
        return automation.close_app(arg_clean)
    elif intent_clean == "lock_pc":
        return automation.lock_pc()
    elif intent_clean == "take_screenshot":
        return automation.take_screenshot()
    elif intent_clean == "generate_image":
        return automation.generate_image(arg_clean)
    elif intent_clean == "search_wikipedia":
        return automation.search_wikipedia(arg_clean)
    elif intent_clean == "open_website":
        return automation.open_website(arg_clean)
    elif intent_clean == "search_google":
        return automation.search_google(arg_clean)
    elif intent_clean == "search_chatgpt":
        return automation.search_chatgpt(arg_clean)
    elif intent_clean == "adjust_volume":
        return automation.route_automation(f"volume {arg_clean}")
    elif intent_clean == "adjust_brightness":
        return automation.route_automation(f"brightness {arg_clean}")
    elif intent_clean == "send_whatsapp":
        if ":" in arg_clean:
            recipient, msg = arg_clean.split(":", 1)
        else:
            recipient, msg = arg_clean, "Hello!"
        return automation.send_whatsapp_message(recipient, msg)
    elif intent_clean == "send_instagram":
        if ":" in arg_clean:
            recipient, msg = arg_clean.split(":", 1)
        else:
            recipient, msg = arg_clean, "Hello!"
        return automation.send_instagram_message(recipient, msg)
        
    return ""

def check_fast_local_tools(command_text: str) -> tuple[bool, str]:
    """Intercepts math, folder creation, system controls, and memory commands in <0.005s."""
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

    # 2. Fast Tool Router (Math, Desktop Folders, System Controls)
    is_handled, tool_reply = tool_router.route_local_tool(command_text)
    if is_handled:
        return True, tool_reply
        
    return False, ""
