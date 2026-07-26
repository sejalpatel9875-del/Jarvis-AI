"""
Unit tests for KnowledgeEngineService and knowledge_engine singleton.
"""

import os
import tempfile
import unittest

from memory.workspace_memory import workspace_memory
from providers.embedding import global_vector_store
from services.knowledge_engine import KnowledgeEngineService, knowledge_engine


class TestKnowledgeEngineService(unittest.TestCase):
    """Test suite for KnowledgeEngineService operations."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.doc_file = os.path.join(self.temp_dir.name, "sample_policy.txt")
        with open(self.doc_file, "w", encoding="utf-8") as f:
            f.write(
                "Company Policy Document.\n"
                "The standard vacation allowance is 25 days per calendar year.\n"
                "Remote work policy allows 2 days per week working from home."
            )
        global_vector_store.clear()

    def tearDown(self):
        self.temp_dir.cleanup()
        global_vector_store.clear()

    def test_singleton_instance(self):
        """Verify knowledge_engine is an instance of KnowledgeEngineService."""
        self.assertIsInstance(knowledge_engine, KnowledgeEngineService)

    def test_index_document_success(self):
        """Verify document indexing into global_vector_store and workspace_memory."""
        res = knowledge_engine.index_document(
            file_path=self.doc_file,
            filename="policy.txt",
            workspace_id="hr_workspace",
        )

        self.assertTrue(res["success"])
        self.assertEqual(res["filename"], "policy.txt")
        self.assertEqual(res["workspace_id"], "hr_workspace")
        self.assertGreater(res["total_chunks"], 0)

        # Verify fact was recorded in workspace memory
        facts = workspace_memory.get_facts("hr_workspace")
        self.assertTrue(any("policy.txt" in f["value"] for f in facts))

    def test_index_document_nonexistent_file(self):
        """Verify error handling when indexing non-existent file."""
        res = knowledge_engine.index_document(
            file_path="non_existent_file.txt",
            filename="missing.txt",
            workspace_id="default",
        )

        self.assertFalse(res["success"])
        self.assertIn("File not found", res["error"])

    def test_query_workspace_knowledge(self):
        """Verify querying workspace knowledge returns matching chunks, formatted_answer, and citations."""
        # Index document into target workspace
        knowledge_engine.index_document(
            file_path=self.doc_file,
            filename="policy.txt",
            workspace_id="test_ws",
        )

        res = knowledge_engine.query_workspace_knowledge(
            workspace_id="test_ws",
            query="vacation allowance",
            top_k=3,
        )

        self.assertTrue(res["success"])
        self.assertEqual(res["workspace_id"], "test_ws")
        self.assertIn("matching_chunks", res)
        self.assertIn("chunks", res)
        self.assertIn("formatted_answer", res)
        self.assertIn("citations", res)

        self.assertGreater(len(res["matching_chunks"]), 0)
        self.assertIn("vacation", res["matching_chunks"][0]["content"].lower())
        self.assertIn("[Source: policy.txt | Page 1]", res["citations"])
        self.assertIn("Knowledge Base Results for Workspace 'test_ws'", res["formatted_answer"])

    def test_workspace_isolation(self):
        """Verify queries for another workspace do not return chunks from target workspace."""
        knowledge_engine.index_document(
            file_path=self.doc_file,
            filename="secret_doc.txt",
            workspace_id="confidential_ws",
        )

        res = knowledge_engine.query_workspace_knowledge(
            workspace_id="other_ws",
            query="vacation allowance",
            top_k=3,
        )

        self.assertTrue(res["success"])
        self.assertEqual(len(res["matching_chunks"]), 0)
        self.assertIn("No relevant knowledge found", res["formatted_answer"])


if __name__ == "__main__":
    unittest.main()
