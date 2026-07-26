"""
Unit tests for Desktop Operator Subsystem & Safety Guardrail.
"""

import unittest
from services.desktop_operator import desktop_operator, SafetyGuardrail
from tools.system import SystemTool
from tools.registry import tool_registry

class TestDesktopOperator(unittest.TestCase):
    def test_safety_guardrail_dangerous_interception(self):
        """Verify SafetyGuardrail intercepts destructive commands."""
        is_safe, msg = SafetyGuardrail.inspect_command("delete all files")
        self.assertFalse(is_safe)
        self.assertIn("DANGEROUS ACTION INTERCEPTED", msg)

    def test_safety_guardrail_safe_action(self):
        """Verify SafetyGuardrail passes safe desktop actions."""
        is_safe, msg = SafetyGuardrail.inspect_command("open chrome")
        self.assertTrue(is_safe)

    def test_desktop_operator_app_launch(self):
        """Verify DesktopOperator executes open application."""
        res = desktop_operator.execute_action("open", "notepad")
        self.assertTrue(res["success"])
        self.assertIn("notepad", res["result"].lower())

    def test_desktop_operator_active_window(self):
        """Verify DesktopOperator returns active window title."""
        res = desktop_operator.execute_action("active_window")
        self.assertTrue(res["success"])
        self.assertIn("Active Window", res["result"])

    def test_system_tool_safety_interception(self):
        """Verify SystemTool blocks dangerous actions via SafetyGuardrail."""
        tool_res = tool_registry.execute("system", action="delete all", target="C:/")
        self.assertFalse(tool_res.success)
        self.assertIn("DANGEROUS ACTION INTERCEPTED", tool_res.result)

if __name__ == "__main__":
    unittest.main()
