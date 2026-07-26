"""
Unit tests for J.A.R.V.I.S. v4.3 Universal Knowledge Intelligence Platform.
"""

import os
import unittest
import tempfile
from services.universal_document_loader import universal_loader
from services.knowledge_engine import knowledge_engine
from services.report_generator import report_generator
from services.knowledge_timeline import knowledge_timeline

class TestV43KnowledgePlatform(unittest.TestCase):
    def test_universal_document_loader_txt(self):
        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".txt") as tmp:
            tmp.write("Jarvis Knowledge Intelligence Platform Test.")
            tmp_path = tmp.name
        res = universal_loader.load_file(tmp_path, "sample.txt")
        self.assertEqual(res["status"], "success")
        os.remove(tmp_path)

    def test_knowledge_engine_query(self):
        res = knowledge_engine.query_workspace_knowledge("ws_test", "knowledge query")
        self.assertIn("formatted_answer", res)

    def test_report_generator(self):
        rep = report_generator.generate_executive_report("Q3 Strategy", "AI Expansion")
        self.assertEqual(rep["title"], "Q3 Strategy")
        self.assertIn("Executive Summary", rep["markdown_content"])

    def test_knowledge_timeline(self):
        event = knowledge_timeline.add_event("ws_test", "DOC_INDEXED", "Indexed Q3 Plan")
        self.assertTrue(event["success"])
        timeline = knowledge_timeline.get_timeline("ws_test")
        self.assertGreaterEqual(len(timeline), 1)

if __name__ == "__main__":
    unittest.main()
