"""
Unit tests for Persistent Vector Storage, SQLite Reconnects, Multi-Document Indexing, and Metadata Filtering.
"""

import unittest
import os
import tempfile
from services.document_loader import DocumentLoader
from services.chunker import SemanticChunker
from providers.embedding import PersistentVectorStore, global_vector_store

class TestPersistentRetrieval(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.doc_a = os.path.join(self.temp_dir.name, "contract_a.txt")
        self.doc_b = os.path.join(self.temp_dir.name, "specs_b.txt")

        with open(self.doc_a, "w", encoding="utf-8") as f:
            f.write("Contract A states that the payment deadline is 30 days. Penalty fee is 5% for delayed payments.")

        with open(self.doc_b, "w", encoding="utf-8") as f:
            f.write("System Specifications B state that maximum memory allocation is 16GB RAM and GPU requirement is RTX 4090.")

        self.chunker = SemanticChunker(chunk_size=100, chunk_overlap=10)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_persistent_storage_survival_on_restart(self):
        """Verify vector index survives restart by instantiating a new PersistentVectorStore instance."""
        doc = DocumentLoader.load_document(self.doc_a)
        chunks = self.chunker.chunk_document(doc)

        global_vector_store.clear()
        global_vector_store.add_chunks(chunks)

        # Simulate Application Restart
        new_vector_store = PersistentVectorStore()
        results = new_vector_store.search("payment deadline", top_k=1)

        self.assertTrue(len(results) > 0)
        self.assertEqual(results[0].chunk.source_file, "contract_a.txt")
        self.assertIn("30 days", results[0].chunk.content)

    def test_multi_document_indexing(self):
        """Verify indexing multiple documents simultaneously."""
        doc_a_content = DocumentLoader.load_document(self.doc_a)
        doc_b_content = DocumentLoader.load_document(self.doc_b)

        chunks_a = self.chunker.chunk_document(doc_a_content)
        chunks_b = self.chunker.chunk_document(doc_b_content)

        global_vector_store.clear()
        global_vector_store.add_chunks(chunks_a)
        global_vector_store.add_chunks(chunks_b, replace_existing=False)

        res_a = global_vector_store.search("penalty fee", top_k=1)
        res_b = global_vector_store.search("memory allocation", top_k=1)

        self.assertEqual(res_a[0].chunk.source_file, "contract_a.txt")
        self.assertEqual(res_b[0].chunk.source_file, "specs_b.txt")

    def test_metadata_filtering_by_source(self):
        """Verify metadata filtering by source_file."""
        doc_a_content = DocumentLoader.load_document(self.doc_a)
        doc_b_content = DocumentLoader.load_document(self.doc_b)

        global_vector_store.clear()
        global_vector_store.add_chunks(self.chunker.chunk_document(doc_a_content))
        global_vector_store.add_chunks(self.chunker.chunk_document(doc_b_content), replace_existing=False)

        # Query searching only contract_a.txt
        results = global_vector_store.search("payment", filter_source="contract_a.txt")
        self.assertTrue(len(results) > 0)
        self.assertTrue(all(r.chunk.source_file == "contract_a.txt" for r in results))

if __name__ == "__main__":
    unittest.main()
