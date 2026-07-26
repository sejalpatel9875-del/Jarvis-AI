"""
Unit tests for UniversalDocumentLoader service.
"""

import unittest
import os
import tempfile
from services.universal_document_loader import UniversalDocumentLoader, universal_loader


class TestUniversalDocumentLoader(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_singleton_instance(self):
        """Verify universal_loader singleton instance exists."""
        self.assertIsInstance(universal_loader, UniversalDocumentLoader)

    def test_load_text_file(self):
        """Verify loading plain text (.txt) document."""
        txt_path = os.path.join(self.temp_dir.name, "sample.txt")
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write("Line 1: Hello World\nLine 2: Universal Loader Test\nLine 3: End of file")

        res = universal_loader.load_file(txt_path)
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["file_name"], "sample.txt")
        self.assertEqual(res["extension"], "txt")
        self.assertEqual(res["total_pages"], 1)
        self.assertEqual(res["total_rows"], 3)
        self.assertIn("Universal Loader Test", res["text_content"])
        self.assertTrue(len(res["chunks"]) > 0)

    def test_load_markdown_file(self):
        """Verify loading markdown (.md) document."""
        md_path = os.path.join(self.temp_dir.name, "notes.md")
        with open(md_path, "w", encoding="utf-8") as f:
            f.write("# Title\n\n## Section 1\n- Item A\n- Item B\n")

        res = universal_loader.load_file(md_path, filename="custom_notes.md")
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["file_name"], "custom_notes.md")
        self.assertEqual(res["extension"], "md")
        self.assertIn("Section 1", res["text_content"])

    def test_load_csv_file(self):
        """Verify loading CSV (.csv) document."""
        csv_path = os.path.join(self.temp_dir.name, "data.csv")
        with open(csv_path, "w", encoding="utf-8") as f:
            f.write("Name,Age,Role\nAlice,30,Engineer\nBob,25,Designer\n")

        res = universal_loader.load_file(csv_path)
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["extension"], "csv")
        self.assertEqual(res["total_rows"], 3)
        self.assertIn("Alice", res["text_content"])

    def test_load_non_existent_file(self):
        """Verify error handling for missing file."""
        res = universal_loader.load_file("/non/existent/file.pdf")
        self.assertEqual(res["status"], "error")
        self.assertIn("non-existent", res["error"])
        self.assertEqual(res["total_pages"], 0)
        self.assertEqual(res["total_rows"], 0)
        self.assertEqual(res["chunks"], [])

    def test_fallback_docx_and_pdf(self):
        """Verify graceful fallback for fallback binary reading."""
        pdf_path = os.path.join(self.temp_dir.name, "test.pdf")
        with open(pdf_path, "wb") as f:
            f.write(b"%PDF-1.4 (Sample Text) Tj /Count 2")

        res = universal_loader.load_file(pdf_path)
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["extension"], "pdf")


if __name__ == "__main__":
    unittest.main()
