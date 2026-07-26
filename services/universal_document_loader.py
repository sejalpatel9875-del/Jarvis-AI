"""
Purpose:
Universal Multi-Format Document Ingestion Engine for Jarvis AI OS (Sprint v4.3).

Responsibilities:
- Ingest and parse .pdf, .docx, .pptx, .xlsx, .csv, .txt, .md documents
- Extract clean text, page/row metadata, and semantic chunks
"""

import os
from typing import Dict, Any, List
from services.document_loader import DocumentLoader
from services.chunker import SemanticChunker

class UniversalDocumentLoader:
    """Universal Multi-Format Document Ingestion Service."""

    def __init__(self):
        self.chunker = SemanticChunker(chunk_size=400, chunk_overlap=50)

    def load_file(self, file_path: str, filename: str = "") -> Dict[str, Any]:
        """Ingests and parses document file of any supported format."""
        target_path = os.path.abspath(file_path)
        file_name = filename.strip() or os.path.basename(target_path)
        ext_clean = os.path.splitext(file_name)[1].lower().replace(".", "")

        if not os.path.exists(target_path):
            return {
                "status": "error",
                "error": f"File '{file_name}' does not exist or non-existent file path.",
                "total_pages": 0,
                "total_rows": 0,
                "chunks": []
            }

        try:
            doc = DocumentLoader.load_document(target_path)
            doc.file_name = file_name
            text_content = doc.full_text
            total_pages = doc.total_pages
            total_rows = len(text_content.splitlines()) if text_content else 1
            chunks = self.chunker.chunk_document(doc)

            chunks_list = [
                {
                    "chunk_id": c.chunk_id,
                    "source_file": c.source_file,
                    "page_number": c.page_number,
                    "chunk_index": c.chunk_index,
                    "content": c.content,
                    "metadata": c.metadata
                }
                for c in chunks
            ]

            return {
                "status": "success",
                "file_name": file_name,
                "extension": ext_clean,
                "total_pages": total_pages,
                "total_rows": total_rows,
                "text_content": text_content,
                "total_chunks": len(chunks),
                "chunks": chunks_list
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "total_pages": 0,
                "total_rows": 0,
                "chunks": []
            }

# Global Singleton
universal_loader = UniversalDocumentLoader()
