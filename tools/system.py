"""
Purpose:
Desktop System & Application Control Tool for Jarvis.

Responsibilities:
- Open & close desktop applications
- Volume and brightness controls
- Lock PC, take screenshot, shutdown/restart

Dependencies:
- tools/base.py
- tools/registry.py
- automation.py
"""

from tools.base import BaseTool, ToolResult
from tools.registry import register_tool
import automation

@register_tool
class SystemTool(BaseTool):
    @property
    def name(self) -> str:
        return "system"

    @property
    def description(self) -> str:
        return "Controls Desktop applications, volume/brightness, screenshots, and PC power."

    def execute(self, action: str = "", target: str = "", **kwargs) -> ToolResult:
        act = action.lower().strip() or kwargs.get("intent", "").lower()
        tgt = target.strip() or kwargs.get("arg", "")
        
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
