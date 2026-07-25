"""
Purpose:
Zero-Cost Local Math Calculator Tool for Jarvis.

Responsibilities:
- Evaluate arithmetic expressions (<0.005s speed)
- Eliminate LLM API calls for math calculations

Dependencies:
- tools/base.py
- tools/registry.py
- tool_router.py
"""

from tools.base import BaseTool, ToolResult
from tools.registry import register_tool
import tool_router

@register_tool
class CalculatorTool(BaseTool):
    @property
    def name(self) -> str:
        return "calculator"

    @property
    def description(self) -> str:
        return "Evaluates arithmetic math expressions instantly in <0.005s with 0 API cost."

    def execute(self, expression: str = "", **kwargs) -> ToolResult:
        query = expression or kwargs.get("query", "")
        if not query:
            return ToolResult(success=False, result="No math expression provided.")
            
        handled, answer = tool_router.route_local_tool(query)
        if handled:
            return ToolResult(success=True, result=answer)
            
        # Direct fallback evaluation
        ans = tool_router.evaluate_math(query)
        if ans is not None:
            return ToolResult(success=True, result=f"Boss, the answer is {ans}.")
            
        return ToolResult(success=False, result=f"Could not evaluate expression '{query}'.")
