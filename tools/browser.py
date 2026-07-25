"""
Purpose:
Web Scraper & Webpage Reader Tool for Jarvis.

Responsibilities:
- Extract text content from URLs via BeautifulSoup & requests

Dependencies:
- tools/base.py
- tools/registry.py
- browser_agent.py
"""

from tools.base import BaseTool, ToolResult
from tools.registry import register_tool
import browser_agent

@register_tool
class BrowserTool(BaseTool):
    @property
    def name(self) -> str:
        return "browser"

    @property
    def description(self) -> str:
        return "Fetches and extracts clean text content from webpages."

    def execute(self, url: str = "", **kwargs) -> ToolResult:
        target_url = url or kwargs.get("url", "")
        if not target_url:
            return ToolResult(success=False, result="No URL provided.")
            
        content = browser_agent.read_web_page(target_url)
        if content:
            return ToolResult(success=True, result=content[:1500])
            
        return ToolResult(success=False, result=f"Could not fetch webpage '{target_url}'.")
