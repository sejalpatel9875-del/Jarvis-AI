"""
Purpose:
Desktop Operator System & Application Control Tool for Jarvis ToolRegistry.

Responsibilities:
- Control desktop applications (Chrome, VS Code, Notepad, Calc, Terminal)
- Execute mouse/keyboard/window operations with Safety Guardrail protection

Dependencies:
- tools/base.py
- tools/registry.py
- services/desktop_operator.py
- automation.py
"""

from tools.base import BaseTool, ToolResult
from tools.registry import register_tool
from services.desktop_operator import desktop_operator
import automation

@register_tool
class SystemTool(BaseTool):
    @property
    def name(self) -> str:
        return "system"

    @property
    def description(self) -> str:
        return "Controls Desktop applications, mouse/keyboard/window operations, volume/brightness, and PC power."

    def execute(self, action: str = "", target: str = "", **kwargs) -> ToolResult:
        act = action.lower().strip() or kwargs.get("intent", "").lower()
        tgt = target.strip() or kwargs.get("arg", "")

        # 1. Delegate to Desktop Operator Subsystem with Safety Guardrails
        op_res = desktop_operator.execute_action(act, tgt, **kwargs)
        if not op_res["safe"]:
            return ToolResult(success=False, result=op_res["result"])
        
        if op_res["success"] and op_res["result"] != f"Unknown desktop operator action '{act}'.":
            return ToolResult(success=True, result=op_res["result"])

        # 2. Fallback to Automation Module
        if act == "open_app":
            res = automation.open_app(tgt)
        elif act == "close_app":
            res = automation.close_app(tgt)
        elif act == "lock_pc":
            res = automation.lock_pc()
        elif act == "take_screenshot":
            res = automation.take_screenshot()
        elif act == "adjust_volume":
            res = automation.route_automation(f"volume {tgt}")
        elif act == "adjust_brightness":
            res = automation.route_automation(f"brightness {tgt}")
        else:
            res = automation.route_automation(f"{act} {tgt}".strip())
            
        return ToolResult(success=True, result=res or f"Executed system command '{act} {tgt}', Boss.")
