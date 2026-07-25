"""
Purpose:
Search Tool for Google & ChatGPT for Jarvis.

Responsibilities:
- Search Google & ChatGPT in-page prompt

Dependencies:
- tools/base.py
- tools/registry.py
- automation.py
"""

from tools.base import BaseTool, ToolResult
from tools.registry import register_tool
import automation

@register_tool
class SearchTool(BaseTool):
    @property
    def name(self) -> str:
        return "search"

    @property
    def description(self) -> str:
        return "Performs web searches on Google or ChatGPT."

    def execute(self, query: str = "", engine: str = "google", **kwargs) -> ToolResult:
        search_query = query or kwargs.get("query", "")
        if not search_query:
            return ToolResult(success=False, result="No search query provided.")
            
        eng = engine.lower().strip()
        if eng == "chatgpt":
            res = automation.search_chatgpt(search_query)
        else:
            res = automation.search_google(search_query)
            
        return ToolResult(success=True, result=res or f"Searching '{search_query}' on {eng}, Boss.")
