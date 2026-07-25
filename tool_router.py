import os
import re
import math
import subprocess
import automation
import memory_manager

# ============================================================
# Local Fast Tool Router (Zero-Cost, Ultra-Low Latency Dispatcher)
# Evaluates math, system controls, and app commands in <0.005s!
# ============================================================

def evaluate_math(expression: str) -> str:
    """Evaluates arithmetic expressions safely without LLM tokens."""
    expr = expression.lower().strip()
    
    # Handle percentage expressions: "15% of 800" -> "(15/100)*800"
    m_pct = re.search(r'(\d+(?:\.\d+)?)\s*%\s*(?:of)?\s*(\d+(?:\.\d+)?)', expr)
    if m_pct:
        pct = float(m_pct.group(1))
        val = float(m_pct.group(2))
        res = (pct / 100.0) * val
        return f"Boss, {pct}% of {val} is {res:g}."
        
    # Clean expression for basic arithmetic
    clean_expr = re.sub(r'[^0-9\+\-\*\/\.\(\)\^]', '', expr)
    clean_expr = clean_expr.replace('^', '**')
    
    if not clean_expr or len(clean_expr) > 50:
        return None
        
    try:
        # Safe math evaluation using restricted globals/locals
        allowed_names = {
            "abs": abs, "round": round, "pow": pow,
            "sqrt": math.sqrt, "sin": math.sin, "cos": math.cos, "tan": math.tan, "pi": math.pi
        }
        val = eval(clean_expr, {"__builtins__": None}, allowed_names)
        if isinstance(val, (int, float)):
            return f"Boss, the answer is {val:g}."
    except Exception:
        pass
        
    return None

def create_folder_on_desktop(folder_name: str) -> str:
    """Creates a new folder on the user's Desktop."""
    try:
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        folder_path = os.path.join(desktop_path, folder_name.strip())
        os.makedirs(folder_path, exist_ok=True)
        print(f"[Tool Router] 📁 Created folder on Desktop: '{folder_name}'")
        return f"Created folder '{folder_name}' on your Desktop, Boss."
    except Exception as e:
        print(f"[Tool Router Error] Failed to create folder: {e}")
        return f"Sorry Boss, I couldn't create folder '{folder_name}'."

def route_local_tool(command_text: str) -> tuple[bool, str]:
    """
    Checks if command can be executed locally without calling Cloud LLM.
    Returns (True, response_text) if handled, or (False, "") if LLM routing is needed.
    """
    cmd = command_text.strip()
    cmd_lower = cmd.lower().strip()
    
    # 1. Pure Arithmetic / Math Expression Check
    # Match patterns like: "2+2", "what is 50 * 12", "calculate 100/4", "15% of 800"
    if re.match(r'^(?:what\s+is|calculate|eval|compute)?\s*[\d\s\+\-\*\/\(\)\%\.\^]+$', cmd_lower) or " % of " in cmd_lower:
        math_result = evaluate_math(cmd_lower)
        if math_result:
            print(f"[Tool Router Fast Math (<0.005s)] Answer: '{math_result}'")
            return True, math_result

    # 2. Desktop Folder Creation
    m_folder = re.search(r'(?:create|make|new)\s+folder\s+(?:named\s+|called\s+)?(["\']?[\w\s\-]+["\']?)', cmd_lower)
    if m_folder:
        fname = m_folder.group(1).replace('"', '').replace("'", '').strip()
        res = create_folder_on_desktop(fname)
        return True, res

    # 3. Simple System Commands (Volume, Brightness, Screenshot, Lock PC)
    if cmd_lower in ["volume up", "louder"]:
        automation.change_volume(0.1)
        return True, "Volume increased, Boss."
    elif cmd_lower in ["volume down", "quieter"]:
        automation.change_volume(-0.1)
        return True, "Volume decreased, Boss."
    elif cmd_lower in ["mute", "silence"]:
        automation.set_volume(0.0)
        return True, "Muted audio, Boss."
    elif cmd_lower in ["take screenshot", "screenshot", "capture screen"]:
        res = automation.take_screenshot()
        return True, res
    elif cmd_lower in ["lock pc", "lock screen", "lock computer"]:
        res = automation.lock_pc()
        return True, res
        
    return False, ""
