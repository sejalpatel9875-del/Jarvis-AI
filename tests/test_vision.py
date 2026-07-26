"""
Unit tests for Vision Intelligence Service and VisionTool.
"""

import unittest
import os
from services.vision import VisionService, vision_service
from tools.vision import VisionTool
from tools.registry import tool_registry

class TestVisionIntelligence(unittest.TestCase):
    def test_vision_service_screenshot(self):
        """Verify screenshot capture returning valid file path."""
        snap_path = VisionService.capture_screenshot()
        self.assertTrue(os.path.exists(snap_path))
        if os.path.exists(snap_path):
            os.remove(snap_path)

    def test_vision_tool_registration(self):
        """Verify VisionTool is registered in ToolRegistry."""
        tool = tool_registry.get_tool("vision")
        self.assertIsNotNone(tool)
        self.assertEqual(tool.name, "vision")

    def test_vision_tool_execution(self):
        """Verify VisionTool screenshot execution."""
        res = tool_registry.execute("vision", action="screenshot")
        self.assertTrue(res.success)
        self.assertIn("Desktop screenshot captured", res.result)

if __name__ == "__main__":
    unittest.main()
