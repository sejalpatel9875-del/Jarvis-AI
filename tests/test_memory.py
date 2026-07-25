"""
Unit tests for Memory Engine, Singleton Pattern, and In-Memory Preference Cache.
"""

import unittest
from memory.manager import MemoryManager
from memory.models import ConversationModel

class TestMemoryEngine(unittest.TestCase):
    def setUp(self):
        self.memory = MemoryManager()

    def test_singleton_pattern(self):
        """Verify that MemoryManager follows the Singleton pattern."""
        instance2 = MemoryManager()
        self.assertIs(self.memory, instance2)

    def test_save_and_load_recent(self):
        """Verify saving a turn and loading recent history from SQLite."""
        conv = self.memory.save_turn("Test Prompt", "Test Answer", provider="Groq")
        self.assertIsInstance(conv, ConversationModel)
        self.assertEqual(conv.user_message, "Test Prompt")
        
        recent = self.memory.get_recent(limit=1)
        self.assertTrue(len(recent) > 0)
        self.assertEqual(recent[-1].user_message, "Test Prompt")

    def test_preference_caching(self):
        """Verify preference saving and in-memory cache hit."""
        self.memory.save_preference("theme_mode", "Dark")
        val1 = self.memory.get_preference("theme_mode")
        self.assertEqual(val1, "Dark")
        
        # Verify in-memory cache hit
        self.assertIn("theme_mode", self.memory._pref_cache)
        self.assertEqual(self.memory._pref_cache["theme_mode"], "Dark")

if __name__ == "__main__":
    unittest.main()
