"""
Purpose:
Document Loader Service for Jarvis File Intelligence system.

Responsibilities:
- Extract text content from PDF, DOCX, TXT, MD, CSV, and LOG files
- Represent extracted content cleanly as DocumentPage or raw text
- Resilient fallback parser handling

Dependencies:
- core/exceptions.py
"""

import os
import re
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass
class DocumentPage:
    source_file: str
    page_number: int
    text: str
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class DocumentContent:
    file_path: str
    file_name: str
    file_type: str
    total_pages: int
    pages: List[DocumentPage] = field(default_factory=list)

    @property
    def full_text(self) -> str:
        return "\n\n".join([page.text for page in self.pages])

class DocumentLoader:
    """Unified Document Loader for Jarvis File Intelligence."""

    @staticmethod
    def load_text_file(filepath: str) -> DocumentContent:
        """Loads plain text files (.txt, .md, .csv, .log, .json)."""
        filename = os.path.basename(filepath)
        ext = os.path.splitext(filename)[1].lower().replace(".", "")
        
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        page = DocumentPage(
            source_file=filename,
            page_number=1,
            text=content,
            metadata={"file_type": ext}
        )

        return DocumentContent(
            file_path=filepath,
            file_name=filename,
            file_type=ext,
            total_pages=1,
            pages=[page]
        )

    @staticmethod
    def load_pdf_file(filepath: str) -> DocumentContent:
        """Loads PDF documents using pypdf / PyPDF2 if available, or fallback reader."""
        filename = os.path.basename(filepath)
        pages = []

        try:
            import pypdf
            reader = pypdf.PdfReader(filepath)
            total = len(reader.pages)
            for idx, page_obj in enumerate(reader.pages):
                text = page_obj.extract_text() or ""
                pages.append(
                    DocumentPage(
                        source_file=filename,
                        page_number=idx + 1,
                        text=text.strip(),
                        metadata={"total_pages": total}
                    )
                )
        except ImportError:
            try:
                import PyPDF2
                reader = PyPDF2.PdfReader(filepath)
                total = len(reader.pages)
                for idx, page_obj in enumerate(reader.pages):
                    text = page_obj.extract_text() or ""
                    pages.append(
                        DocumentPage(
                            source_file=filename,
                            page_number=idx + 1,
                            text=text.strip(),
                            metadata={"total_pages": total}
                        )
                    )
            except Exception as e:
                # Fallback text extraction for PDF text streams
                with open(filepath, "rb") as f:
                    raw_data = f.read().decode("latin1", errors="ignore")
                text_matches = re.findall(r'\((.*?)\)\s*Tj', raw_data)
                extracted_text = " ".join(text_matches) if text_matches else raw_data[:2000]
                pages.append(
                    DocumentPage(
                        source_file=filename,
                        page_number=1,
                        text=extracted_text,
                        metadata={"fallback": True}
                    )
                )

        return DocumentContent(
            file_path=filepath,
            file_name=filename,
            file_type="pdf",
            total_pages=len(pages),
            pages=pages
        )

    @staticmethod
    def load_docx_file(filepath: str) -> DocumentContent:
        """Loads Word (.docx) documents using python-docx if available."""
        filename = os.path.basename(filepath)
        pages = []

        try:
            import docx
            doc = docx.Document(filepath)
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
            full_text = "\n".join(paragraphs)
            pages.append(
                DocumentPage(
                    source_file=filename,
                    page_number=1,
                    text=full_text,
                    metadata={"paragraph_count": len(paragraphs)}
                )
            )
        except Exception:
            # Fallback text reader for docx XML text
            with open(filepath, "rb") as f:
                raw_data = f.read().decode("utf-8", errors="ignore")
            text_matches = re.findall(r'<w:t[^>]*>(.*?)</w:t>', raw_data)
            extracted_text = " ".join(text_matches) if text_matches else raw_data[:2000]
            pages.append(
                DocumentPage(
                    source_file=filename,
                    page_number=1,
                    text=extracted_text,
                    metadata={"fallback": True}
                )
            )

        return DocumentContent(
            file_path=filepath,
            file_name=filename,
            file_type="docx",
            total_pages=len(pages),
            pages=pages
        )

    @classmethod
    def load_document(cls, filepath: str) -> DocumentContent:
        """Unified document loader entry point."""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Document file '{filepath}' does not exist.")

        ext = os.path.splitext(filepath)[1].lower()
        if ext == ".pdf":
            return cls.load_pdf_file(filepath)
        elif ext in [".docx", ".doc"]:
            return cls.load_docx_file(filepath)
        else:
            return cls.load_text_file(filepath)
