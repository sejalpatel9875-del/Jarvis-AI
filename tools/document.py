"""
Purpose:
Document Intelligence & RAG Tool for Jarvis.

Responsibilities:
- Index document files (.pdf, .docx, .txt, .csv) into VectorStore
- Search indexed document chunks with page citations
- Provide full document summaries

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
        return "Indexes, searches, and summarizes document files (.pdf, .docx, .txt) with page citations."

    def execute(self, action: str = "query", filepath: str = "", query: str = "", **kwargs) -> ToolResult:
        act = action.lower().strip()
        target_path = filepath or kwargs.get("filepath", "") or kwargs.get("path", "")
        search_query = query or kwargs.get("query", "")

        # Action 1: Index Document
        if act == "index" or (target_path and not search_query):
            if not target_path or not os.path.exists(target_path):
                return ToolResult(success=False, result=f"Document path '{target_path}' not found.")

            doc = DocumentLoader.load_document(target_path)
            chunks = self.chunker.chunk_document(doc)
            global_vector_store.clear()
            global_vector_store.add_chunks(chunks)

            return ToolResult(
                success=True,
                result=f"Successfully indexed document '{doc.file_name}' ({doc.total_pages} pages, {len(chunks)} chunks)."
            )

        # Action 2: Query Document Knowledge Base
        elif act == "query" or search_query:
            if not search_query:
                return ToolResult(success=False, result="No query string provided for document search.")

            results = global_vector_store.search(search_query, top_k=3)
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
