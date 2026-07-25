"""
Purpose:
Semantic Chunking Engine for Jarvis File Intelligence system.

Responsibilities:
- Break DocumentContent into sliding window text chunks with page tracking
- Assign unique chunk IDs, page citations, and overlap metadata

Dependencies:
- services/document_loader.py
"""

import uuid
from dataclasses import dataclass, field
from typing import List, Dict, Any
from services.document_loader import DocumentContent, DocumentPage

@dataclass
class TextChunk:
    chunk_id: str
    source_file: str
    page_number: int
    chunk_index: int
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)

class SemanticChunker:
    """Sliding Window Semantic Text Chunker."""
    def __init__(self, chunk_size: int = 400, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_document(self, document: DocumentContent) -> List[TextChunk]:
        """
        Splits a DocumentContent into structured TextChunk items.
        Preserves page citations and source file metadata.
        """
        chunks: List[TextChunk] = []
        chunk_counter = 0

        for page in document.pages:
            text = page.text.strip()
            if not text:
                continue

            # Sliding window over page text
            start = 0
            text_len = len(text)

            while start < text_len:
                end = min(start + self.chunk_size, text_len)
                chunk_text = text[start:end].strip()

                if chunk_text:
                    chunk_counter += 1
                    chunks.append(
                        TextChunk(
                            chunk_id=f"chk_{uuid.uuid4().hex[:8]}",
                            source_file=page.source_file,
                            page_number=page.page_number,
                            chunk_index=chunk_counter,
                            content=chunk_text,
                            metadata={
                                "file_type": document.file_type,
                                "total_pages": document.total_pages,
                                "char_length": len(chunk_text)
                            }
                        )
                    )

                if end == text_len:
                    break
                    
                start += (self.chunk_size - self.chunk_overlap)

        return chunks
