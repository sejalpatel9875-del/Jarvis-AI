"""
Unit tests for Playwright & BrowserAutomationService and BrowserTool.
"""

import unittest
from services.browser_automation import browser_service
from tools.browser import BrowserTool
from tools.registry import tool_registry

class TestBrowserAutomation(unittest.TestCase):
    def test_browser_service_fetch_text(self):
        """Verify fetching text from python.org or fallback HTTP."""
        text = browser_service.fetch_webpage_text("https://www.python.org")
        self.assertTrue(len(text) > 0)
        self.assertIn("Python", text)

    def test_browser_tool_registration(self):
        """Verify BrowserTool is registered in ToolRegistry."""
        tool = tool_registry.get_tool("browser")
        self.assertIsNotNone(tool)
        self.assertEqual(tool.name, "browser")

    def test_browser_tool_execution(self):
        """Verify BrowserTool execution for URL fetching."""
        res = tool_registry.execute("browser", action="fetch", url="https://www.python.org")
        self.assertTrue(res.success)
        self.assertIn("Python", res.result)

if __name__ == "__main__":
    unittest.main()
