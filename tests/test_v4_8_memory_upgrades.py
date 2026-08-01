import unittest
import uuid
from memory.manager import _default_manager, save_turn, get_recent, save_preference, get_preference

class TestV48MemoryUpgrades(unittest.TestCase):
    """Comprehensively validates the separated, semantic unified memory manager."""

    def test_conversation_memory(self):
        # Save a unique conversation turn
        user_msg = f"Can you index my project reports? {uuid.uuid4().hex[:6]}"
        assistant_rep = "I have successfully indexed all user files and documents."
        
        turn = save_turn(user_msg, assistant_rep, provider="Gemini")
        self.assertEqual(turn.user_message, user_msg)
        self.assertEqual(turn.assistant_reply, assistant_rep)
        
        # Test get recent
        recent = get_recent(limit=5)
        self.assertGreaterEqual(len(recent), 1)
        self.assertEqual(recent[-1].user_message, user_msg)
        
        # Test semantic search conversations
        search_res = _default_manager.search("project reports")
        self.assertGreaterEqual(len(search_res), 1)
        self.assertEqual(search_res[0].user_message, user_msg)

    def test_user_preferences_memory(self):
        pref_key = f"theme_pref_{uuid.uuid4().hex[:6]}"
        save_preference(pref_key, "Neon Glow")
        
        # Retrieval from cache / database
        val = get_preference(pref_key)
        self.assertEqual(val, "Neon Glow")
        
        # Category preference save
        _default_manager.save_user_preference(pref_key, "Dark Cyberpunk", category="visuals")
        val2 = _default_manager.get_user_preference(pref_key)
        self.assertEqual(val2, "Dark Cyberpunk")

    def test_task_memory(self):
        task_id = f"task_{uuid.uuid4().hex[:8]}"
        goal = "Optimize database index settings"
        steps = [{"step": 1, "description": "Run check"}]
        
        # Save task memory
        _default_manager.save_task_run(task_id, goal, steps, "COMPLETED", current_step=1)
        
        # Retrieve by ID
        task = _default_manager.get_task_run(task_id)
        self.assertIsNotNone(task)
        self.assertEqual(task["goal"], goal)
        self.assertEqual(task["status"], "COMPLETED")
        self.assertEqual(task["steps"][0]["description"], "Run check")
        
        # Semantic search tasks
        search_res = _default_manager.semantic_search_tasks("database settings")
        self.assertGreaterEqual(len(search_res), 1)
        self.assertEqual(search_res[0]["task_id"], task_id)

    def test_knowledge_memory(self):
        chunk_id = f"chunk_{uuid.uuid4().hex[:8]}"
        content = "The orbital radius of the Earth is approximately 149.6 million kilometers."
        
        _default_manager.save_knowledge_fact(chunk_id, "astronomy_facts.txt", content)
        
        # Semantic recall
        search_res = _default_manager.semantic_search_knowledge("Earth orbital radius")
        self.assertGreaterEqual(len(search_res), 1)
        self.assertEqual(search_res[0]["chunk_id"], chunk_id)
        self.assertIn("149.6 million", search_res[0]["content"])

    def test_session_memory(self):
        sess_id = f"session_{uuid.uuid4().hex[:8]}"
        
        # Store variables
        _default_manager.save_session_variable(sess_id, "active_user", "Rahul")
        _default_manager.save_session_variable(sess_id, "auth_token", "jwt_abc123")
        
        # Retrieve variables
        user = _default_manager.get_session_variable(sess_id, "active_user")
        token = _default_manager.get_session_variable(sess_id, "auth_token")
        self.assertEqual(user, "Rahul")
        self.assertEqual(token, "jwt_abc123")

    def test_long_term_memory(self):
        mem_key = f"ltm_{uuid.uuid4().hex[:8]}"
        summary = "User likes Prayagraj conversational tone and Hinglish neural voice outputs."
        
        # Save
        _default_manager.save_long_term_fact(mem_key, summary)
        
        # Semantic recall
        search_res = _default_manager.semantic_search_long_term("voice language conversational preference")
        self.assertGreaterEqual(len(search_res), 1)
        self.assertEqual(search_res[0]["key"], mem_key)
        self.assertEqual(search_res[0]["abstract_summary"], summary)

if __name__ == "__main__":
    unittest.main()
