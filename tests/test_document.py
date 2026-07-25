"""
Unit tests for DocumentLoader, SemanticChunker, VectorStore, and DocumentTool.
"""

import unittest
import os
import tempfile
from services.document_loader import DocumentLoader, DocumentContent
from services.chunker import SemanticChunker, TextChunk
from providers.embedding import VectorStore, compute_cosine_similarity
from tools.document import DocumentTool

class TestDocumentIntelligence(unittest.TestCase):
    def setUp(self):
        # Create temporary sample text document
        self.temp_dir = tempfile.TemporaryDirectory()
        self.sample_file = os.path.join(self.temp_dir.name, "sample.txt")
        with open(self.sample_file, "w", encoding="utf-8") as f:
            f.write("Python 3.14 includes new performance optimizations and JIT compilation improvements. Page 17 details memory layout changes.")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_document_loader(self):
        """Verify DocumentLoader text document parsing."""
        doc = DocumentLoader.load_document(self.sample_file)
        self.assertIsInstance(doc, DocumentContent)
        self.assertEqual(doc.total_pages, 1)
        self.assertIn("Python 3.14", doc.full_text)

    def test_semantic_chunker(self):
        """Verify SemanticChunker text chunking."""
        doc = DocumentLoader.load_document(self.sample_file)
        chunker = SemanticChunker(chunk_size=50, chunk_overlap=10)
        chunks = chunker.chunk_document(doc)
        self.assertTrue(len(chunks) > 0)
        self.assertEqual(chunks[0].source_file, "sample.txt")

    def test_vector_store_similarity_search(self):
        """Verify VectorStore cosine similarity search."""
        doc = DocumentLoader.load_document(self.sample_file)
        chunker = SemanticChunker(chunk_size=100, chunk_overlap=10)
        chunks = chunker.chunk_document(doc)

        vstore = VectorStore()
        vstore.add_chunks(chunks)

        results = vstore.search("performance optimizations", top_k=1)
        self.assertTrue(len(results) > 0)
        self.assertIn("performance optimizations", results[0].chunk.content.lower())

    def test_document_tool_indexing_and_query(self):
        """Verify end-to-end DocumentTool indexing and querying."""
        doc_tool = DocumentTool()
        index_res = doc_tool.execute(action="index", filepath=self.sample_file)
        self.assertTrue(index_res.success)

        query_res = doc_tool.execute(action="query", query="memory layout changes")
        self.assertTrue(query_res.success)
        self.assertIn("sample.txt", query_res.result)
        self.assertIn("Page 1", query_res.result)

if __name__ == "__main__":
    unittest.main()
