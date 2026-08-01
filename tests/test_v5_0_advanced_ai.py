import unittest
import uuid
import os
from services.advanced_ai import advanced_ai
from tools.registry import tool_registry

class TestV50AdvancedAI(unittest.TestCase):
    """Comprehensively tests all advanced AI capabilities in the AdvancedAIEngine."""

    def test_plan_and_reason(self):
        goal = "Send a notification that task planning test is successful"
        res = advanced_ai.plan_and_reason(goal)
        self.assertTrue(res["success"])
        self.assertEqual(res["goal"], goal)
        self.assertIn("status", res)

    def test_analyze_document(self):
        # Create a mock document
        doc_path = os.path.abspath(f"doc_{uuid.uuid4().hex[:6]}.txt")
        content = "Quarterly Sales Report.\nHighlights: revenue up 20%.\nIssues: shipping delays."
        
        tool_registry.execute("file_manager", action="create", path=doc_path, content=content)
        
        try:
            res = advanced_ai.analyze_document(doc_path)
            self.assertTrue(res["success"])
            self.assertIn("summary", res)
            self.assertIn("highlights", res)
            self.assertIn("action_items", res)
        finally:
            if os.path.exists(doc_path):
                os.remove(doc_path)

    def test_understand_image(self):
        res = advanced_ai.understand_image("screenshot.png", "What is the system status?")
        self.assertTrue(res["success"])
        self.assertEqual(res["image_path"], "screenshot.png")
        self.assertIn("ocr_text", res)
        self.assertIn("analysis", res)

    def test_summarize_meeting(self):
        transcript = "Aman: We should deploy to Railway today. Rahul: Agree. Let's do it after testing."
        res = advanced_ai.summarize_meeting(transcript)
        self.assertTrue(res["success"])
        self.assertIn("summary", res)
        self.assertIn("action_items", res)
        self.assertIn("key_decisions", res)

    def test_create_ai_note(self):
        res = advanced_ai.create_ai_note("Sprint Review Feedback", "The UI orb animations look incredibly premium, but the particle canvas speed could be slightly slower.")
        self.assertTrue(res["success"])
        self.assertIn("note_title", res)
        self.assertIn("summary", res)
        self.assertIn("tags", res)

    def test_parse_and_create_reminder(self):
        res = advanced_ai.parse_and_create_reminder("Schedule call with Client Rahul tomorrow morning")
        self.assertTrue(res["success"])
        self.assertIsNotNone(res["reminder"])
        self.assertIn("Rahul", res["parsed_title"])

    def test_retrieve_knowledge(self):
        res = advanced_ai.retrieve_knowledge("orbital radius of Earth")
        self.assertTrue(res["success"])
        self.assertIn("knowledge_facts", res)
        self.assertIn("long_term_memories", res)

    def test_execute_voice_command(self):
        res = advanced_ai.execute_voice_command("Volume up, please.")
        self.assertTrue(res["success"])
        self.assertEqual(res["command"], "Volume up, please.")
        self.assertIn("voice_response", res)

if __name__ == "__main__":
    unittest.main()
