"""
Purpose:
Playwright-Powered Web Browser & Scraper Tool for Jarvis.

Responsibilities:
- Extract webpage text and capture webpage screenshots via Playwright

Dependencies:
- tools/base.py
- tools/registry.py
- services/browser_automation.py
"""

from tools.base import BaseTool, ToolResult
from tools.registry import register_tool
from services.browser_automation import browser_service

@register_tool
class BrowserTool(BaseTool):
    @property
    def name(self) -> str:
        return "browser"

    @property
    def description(self) -> str:
        return "Automates web browsing, extracts clean text content, and captures webpage screenshots."

    def execute(self, action: str = "fetch", url: str = "", **kwargs) -> ToolResult:
        target_url = url or kwargs.get("url", "") or kwargs.get("query", "")
        act = action.lower().strip()

        if not target_url:
            return ToolResult(success=False, result="No URL provided for browser tool execution.")

        if act in ["screenshot", "snap"]:
            snap_path = browser_service.capture_webpage_screenshot(target_url)
            return ToolResult(success=True, result=f"Webpage screenshot saved to: '{snap_path}'")
        else:
            text = browser_service.fetch_webpage_text(target_url)
            if text:
                return ToolResult(success=True, result=text[:2500])
            return ToolResult(success=False, result=f"Could not fetch webpage content from '{target_url}'.")
