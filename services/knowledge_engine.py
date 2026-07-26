"""
Purpose:
Workspace-Aware Knowledge RAG Engine for Jarvis AI OS (Sprint v4.3).

Responsibilities:
- Workspace-isolated RAG index & query engine
- Returns semantic matching chunks, formatted context answer, and page/file citations
"""

from typing import Dict, Any, List
from providers.embedding import global_vector_store
from memory.workspace_memory import workspace_memory
from services.universal_document_loader import universal_loader
from services.document_loader import DocumentLoader
from services.chunker import SemanticChunker

class KnowledgeEngineService:
    """Workspace Knowledge RAG Engine."""

    def __init__(self):
        self.chunker = SemanticChunker(chunk_size=400, chunk_overlap=50)

    def index_document(self, file_path: str, filename: str, workspace_id: str = "default") -> Dict[str, Any]:
        """Indexes document into VectorStore and registers workspace fact metadata."""
        res = universal_loader.load_file(file_path, filename)
        if res.get("status") != "success":
            return {
                "success": False,
                "status": "error",
                "error": f"File not found: {res.get('error', 'Failed to load document.')}"
            }

        # Index chunks directly into global_vector_store with workspace_id in metadata
        try:
            doc = DocumentLoader.load_document(file_path)
            doc.file_name = filename
            chunks = self.chunker.chunk_document(doc)
            for c in chunks:
                c.source_file = filename
                c.metadata["workspace_id"] = workspace_id
            if chunks:
                global_vector_store.add_chunks(chunks, replace_existing=True)
        except Exception:
            pass

        workspace_memory.save_fact(workspace_id, f"doc_{filename}", f"Indexed {res['total_chunks']} chunks from {filename}")
        return {
            "success": True,
            "status": "success",
            "workspace_id": workspace_id,
            "filename": filename,
            "total_chunks": res["total_chunks"]
        }

    def query_workspace_knowledge(self, workspace_id: str, query: str, top_k: int = 5) -> Dict[str, Any]:
        """Queries knowledge base enforcing workspace scope with citations."""
        results = global_vector_store.search(query, top_k=top_k * 2)
        
        citations = []
        chunks_data = []
        for r in results:
            ws_meta = r.chunk.metadata.get("workspace_id", "default")
            if ws_meta != workspace_id and workspace_id != "global":
                continue

            cit = f"[Source: {r.chunk.source_file} | Page {r.chunk.page_number}]"
            citations.append(cit)
            chunks_data.append({
                "chunk_id": r.chunk.chunk_id,
                "source_file": r.chunk.source_file,
                "page_number": r.chunk.page_number,
                "chunk_index": r.chunk.chunk_index,
                "content": r.chunk.content,
                "metadata": r.chunk.metadata
            })
            if len(citations) >= top_k:
                break

        if citations:
            formatted_answer = f"Knowledge Base Results for Workspace '{workspace_id}':\n\n" + "\n\n".join([f"{cit}\n\"{c['content']}\"" for cit, c in zip(citations, chunks_data)])
        else:
            formatted_answer = f"No relevant knowledge found for query '{query}' in workspace '{workspace_id}'."

        return {
            "success": True,
            "status": "success",
            "workspace_id": workspace_id,
            "query": query,
            "total_matches": len(chunks_data),
            "formatted_answer": formatted_answer,
            "citations": citations,
            "matching_chunks": chunks_data,
            "chunks": chunks_data
        }

# Global Singleton
knowledge_engine = KnowledgeEngineService()
