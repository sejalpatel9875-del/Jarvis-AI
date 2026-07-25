"""
Unit tests for Central Tool Registry and Exception Resilience.
"""

import unittest
from tools.base import BaseTool, ToolResult
from tools.registry import ToolRegistry, register_tool, tool_registry

# Dummy crashing tool for resilience testing
class CrashingTool(BaseTool):
    @property
    def name(self) -> str:
        return "crashing_tool"

    @property
    def description(self) -> str:
        return "Test tool designed to raise unhandled exceptions."

    def execute(self, **kwargs) -> ToolResult:
        raise RuntimeError("Simulated browser tool crash!")

class TestToolRegistry(unittest.TestCase):
    def setUp(self):
        self.registry = tool_registry
        self.crashing_tool = CrashingTool()
        self.registry.register(self.crashing_tool)

    def test_tool_registration(self):
        tool = self.registry.get_tool("crashing_tool")
        self.assertIsNotNone(tool)
        self.assertEqual(tool.name, "crashing_tool")

    def test_exception_resilience(self):
        """Verify that a tool crash returns ToolResult(success=False) without crashing Jarvis."""
        res = self.registry.execute("crashing_tool")
        self.assertIsInstance(res, ToolResult)
        self.assertFalse(res.success)
        self.assertIn("Simulated browser tool crash!", res.result)

    def test_unregistered_tool(self):
        """Verify that requesting an unregistered tool returns ToolResult(success=False)."""
        res = self.registry.execute("non_existent_tool")
        self.assertIsInstance(res, ToolResult)
        self.assertFalse(res.success)

if __name__ == "__main__":
    unittest.main()
