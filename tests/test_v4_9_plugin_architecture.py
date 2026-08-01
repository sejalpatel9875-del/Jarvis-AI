import unittest
from tools.registry import tool_registry
from tools.base import ToolResult

class TestV49PluginArchitecture(unittest.TestCase):
    """Verifies that all required plugins are loaded and implement the new lifecycle methods."""

    def setUp(self):
        self.plugin_names = [
            "email",
            "calendar",
            "ocr",
            "pdf",
            "file_manager", # Filesystem
            "weather",
            "maps",
            "whatsapp",
            "terminal",
            "search"
        ]

    def test_plugins_existence_and_registration(self):
        for name in self.plugin_names:
            plugin = tool_registry.get_tool(name)
            self.assertIsNotNone(plugin, f"Plugin '{name}' should be registered in ToolRegistry.")
            
            # Verify lifecycle interface methods are exposed
            self.assertTrue(has_attr(plugin, "execute"), f"Plugin '{name}' should expose execute().")
            self.assertTrue(has_attr(plugin, "validate"), f"Plugin '{name}' should expose validate().")
            self.assertTrue(has_attr(plugin, "rollback"), f"Plugin '{name}' should expose rollback().")
            self.assertTrue(has_attr(plugin, "status"), f"Plugin '{name}' should expose status().")
            
            # Verify status is active
            self.assertEqual(plugin.status(), "ACTIVE")

    def test_lifecycle_validation_and_rollback(self):
        # Email Plugin Lifecycle Test
        email_plugin = tool_registry.get_tool("email")
        res = email_plugin.execute(recipient="test@example.com", subject="Test", body="Hello")
        self.assertTrue(email_plugin.validate(res))
        
        rollback_res = email_plugin.rollback(recipient="test@example.com")
        self.assertTrue(rollback_res.success)
        self.assertIn("recalled", rollback_res.result)

        # Weather Plugin Lifecycle Test
        weather_plugin = tool_registry.get_tool("weather")
        res_weather = weather_plugin.execute(city="Delhi")
        self.assertTrue(weather_plugin.validate(res_weather))

        # Maps Plugin Lifecycle Test
        maps_plugin = tool_registry.get_tool("maps")
        res_maps = maps_plugin.execute(destination="Lucknow", origin="Prayagraj")
        self.assertTrue(maps_plugin.validate(res_maps))
        
        # WhatsApp Plugin Lifecycle Test
        whatsapp_plugin = tool_registry.get_tool("whatsapp")
        res_wa = whatsapp_plugin.execute(recipient="Papa", message="Hello")
        self.assertTrue(whatsapp_plugin.validate(res_wa))
        
        # Terminal Plugin Lifecycle Test
        term_plugin = tool_registry.get_tool("terminal")
        res_term = term_plugin.execute(command="echo Hello World")
        self.assertTrue(term_plugin.validate(res_term))
        self.assertEqual(res_term.result.strip(), "Hello World")

def has_attr(obj, name):
    return hasattr(obj, name) and callable(getattr(obj, name))

if __name__ == "__main__":
    unittest.main()
