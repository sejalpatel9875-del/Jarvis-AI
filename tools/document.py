"""
Purpose:
Document Intelligence & Persistent RAG Tool for Jarvis.

Responsibilities:
- Persistently index document files (.pdf, .docx, .txt, .csv) into SQLite VectorStore
- Search multi-document knowledge base with metadata filtering & page citations
- Compare multi-document contents side-by-side with source citations

Dependencies:
- tools/base.py
- tools/registry.py
- services/document_loader.py
- services/chunker.py
- providers/embedding.py
"""

import os
from tools.base import BaseTool, ToolResult
from tools.registry import register_tool
from services.document_loader import DocumentLoader
from services.chunker import SemanticChunker
from providers.embedding import global_vector_store

@register_tool
class DocumentTool(BaseTool):
    def __init__(self):
        self.chunker = SemanticChunker(chunk_size=400, chunk_overlap=50)

    @property
    def name(self) -> str:
        return "document"

    @property
    def description(self) -> str:
        return "Persistently indexes, searches, compares, and summarizes documents (.pdf, .docx, .txt) with page citations."

    def execute(self, action: str = "query", filepath: str = "", query: str = "", **kwargs) -> ToolResult:
        act = action.lower().strip()
        target_path = filepath or kwargs.get("filepath", "") or kwargs.get("path", "")
        search_query = query or kwargs.get("query", "")
        filter_source = kwargs.get("filter_source") or kwargs.get("source_file")
        filter_type = kwargs.get("filter_type") or kwargs.get("file_type")
        file1 = kwargs.get("file1") or kwargs.get("doc1", "")
        file2 = kwargs.get("file2") or kwargs.get("doc2", "")

        # Action 1: Multi-Document Comparison
        if act == "compare" or (file1 and file2):
            if not os.path.exists(file1) or not os.path.exists(file2):
                return ToolResult(success=False, result=f"One or both files to compare were not found: '{file1}', '{file2}'.")

            doc1 = DocumentLoader.load_document(file1)
            doc2 = DocumentLoader.load_document(file2)

            comp_result = (
                f"=== MULTI-DOCUMENT COMPARISON ===\n"
                f"📄 Document A: {doc1.file_name} ({doc1.total_pages} pages, Type: {doc1.file_type})\n"
                f"Content Summary (Page 1):\n\"{doc1.pages[0].text[:300]}...\"\n\n"
                f"📄 Document B: {doc2.file_name} ({doc2.total_pages} pages, Type: {doc2.file_type})\n"
                f"Content Summary (Page 1):\n\"{doc2.pages[0].text[:300]}...\"\n"
                f"================================="
            )
            return ToolResult(success=True, result=comp_result)

        # Action 2: Persistent Multi-Document Indexing
        elif act == "index" or (target_path and not search_query):
            if not target_path or not os.path.exists(target_path):
                return ToolResult(success=False, result=f"Document path '{target_path}' not found.")

            doc = DocumentLoader.load_document(target_path)
            chunks = self.chunker.chunk_document(doc)
            global_vector_store.add_chunks(chunks, replace_existing=True)

            return ToolResult(
                success=True,
                result=f"Successfully indexed document '{doc.file_name}' persistently into SQLite ({doc.total_pages} pages, {len(chunks)} chunks)."
            )

        # Action 3: Multi-Document Knowledge Base Search
        elif act == "query" or search_query:
            if not search_query:
                return ToolResult(success=False, result="No query string provided for document search.")

            results = global_vector_store.search(
                search_query,
                top_k=3,
                filter_source=filter_source,
                filter_type=filter_type
            )
            if not results:
                return ToolResult(success=False, result=f"No matching content found for '{search_query}'.")

            citations = []
            for r in results:
                citations.append(
                    f"[Source: {r.chunk.source_file} | Page {r.chunk.page_number}]\n\"{r.chunk.content}\""
                )

            formatted_result = "\n\n".join(citations)
            return ToolResult(success=True, result=formatted_result)

        return ToolResult(success=False, result=f"Unknown document tool action '{act}'.")
