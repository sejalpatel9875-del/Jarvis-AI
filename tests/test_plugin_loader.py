"""
Unit tests for Dynamic Plugin Loader Subsystem.
"""

import unittest
from services.plugin_loader import plugin_loader
from tools.registry import tool_registry

class TestPluginLoader(unittest.TestCase):
    def test_discover_and_load_plugins(self):
        """Verify plugin loader discovers and registers weather plugin."""
        loaded = plugin_loader.discover_and_load()
        self.assertIn("weather", loaded)
        
        # Verify tool registry has weather plugin tool
        tool_res = tool_registry.execute("weather", city="Mumbai")
        self.assertTrue(tool_res.success)
        self.assertIn("Mumbai", tool_res.result)

if __name__ == "__main__":
    unittest.main()
