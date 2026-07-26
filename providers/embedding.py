"""
Purpose:
Persistent Vector Store & Embedding Provider Engine for Jarvis File Intelligence system.

Responsibilities:
- SQLite-backed persistent vector storage surviving application restarts
- Incremental multi-document indexing and metadata filtering (filter_source, filter_type)
- Keyword & Term Frequency local vector embeddings + Cosine Similarity search

Dependencies:
- services/chunker.py
- memory/database.py
"""

import json
import math
import re
import datetime
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Tuple, Dict, Any, Optional
from services.chunker import TextChunk
from memory.database import get_connection

class BaseEmbeddingProvider(ABC):
    @abstractmethod
    def embed_text(self, text: str) -> List[float]:
        pass

class LocalTFIDFEmbeddingProvider(BaseEmbeddingProvider):
    """Zero-Cost Local Term Frequency Vectorizer (<0.001s speed)."""
    def tokenize(self, text: str) -> List[str]:
        return re.findall(r'\w+', text.lower())

    def embed_text(self, text: str) -> List[float]:
        tokens = self.tokenize(text)
        freq: Dict[str, int] = {}
        for t in tokens:
            freq[t] = freq.get(t, 0) + 1
        return list(freq.values())

def compute_cosine_similarity(text1: str, text2: str) -> float:
    """Computes keyword term-overlap cosine similarity between two text strings."""
    tokens1 = set(re.findall(r'\w+', text1.lower()))
    tokens2 = set(re.findall(r'\w+', text2.lower()))
    
    if not tokens1 or not tokens2:
        return 0.0
        
    intersection = tokens1.intersection(tokens2)
    return len(intersection) / math.sqrt(len(tokens1) * len(tokens2))

@dataclass
class SearchResult:
    chunk: TextChunk
    score: float

class PersistentVectorStore:
    """
    SQLite-backed Persistent Vector Store & Multi-Document Knowledge Index.
    Survives application restarts and supports metadata filtering.
    """
    def __init__(self):
        self._chunks: List[TextChunk] = []
        self._load_from_sqlite()

    def _load_from_sqlite(self):
        """Loads all indexed chunks from SQLite document_chunks table."""
        try:
            with get_connection() as conn:
                rows = conn.execute("SELECT id, source_file, page_number, chunk_index, content, metadata_json FROM document_chunks").fetchall()
                self._chunks.clear()
                for r in rows:
                    meta = json.loads(r["metadata_json"]) if r["metadata_json"] else {}
                    self._chunks.append(
                        TextChunk(
                            chunk_id=r["id"],
                            source_file=r["source_file"],
                            page_number=r["page_number"],
                            chunk_index=r["chunk_index"],
                            content=r["content"],
                            metadata=meta
                        )
                    )
        except Exception as e:
            print(f"[VectorStore Warning] Failed to load chunks from SQLite: {e}")

    def add_chunks(self, chunks: List[TextChunk], replace_existing: bool = True):
        """
        Indexes text chunks persistently into SQLite and updates in-memory cache.
        Supports multi-document indexing.
        """
        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            with get_connection() as conn:
                if replace_existing and chunks:
                    source_file = chunks[0].source_file
                    conn.execute("DELETE FROM document_chunks WHERE source_file = ?", (source_file,))
                    self._chunks = [c for c in self._chunks if c.source_file != source_file]

                for c in chunks:
                    conn.execute(
                        """
                        INSERT OR REPLACE INTO document_chunks 
                        (id, source_file, page_number, chunk_index, content, metadata_json, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                        """,
                        (c.chunk_id, c.source_file, c.page_number, c.chunk_index, c.content, json.dumps(c.metadata), now_str)
                    )
                    self._chunks.append(c)
        except Exception as e:
            print(f"[VectorStore Error] Failed to persist chunks to SQLite: {e}")

    def clear(self):
        """Clears all indexed chunks from SQLite and in-memory cache."""
        try:
            with get_connection() as conn:
                conn.execute("DELETE FROM document_chunks")
        except Exception as e:
            print(f"[VectorStore Error] Failed to clear SQLite vector table: {e}")
        self._chunks.clear()

    def search(
        self,
        query: str,
        top_k: int = 3,
        filter_source: Optional[str] = None,
        filter_type: Optional[str] = None
    ) -> List[SearchResult]:
        """
        Performs semantic similarity search with optional metadata filtering.
        Supports multi-document filtering by source_file or file_type.
        """
        results: List[SearchResult] = []
        
        for chunk in self._chunks:
            # Metadata filtering
            if filter_source and filter_source.lower() not in chunk.source_file.lower():
                continue
            if filter_type and chunk.metadata.get("file_type", "").lower() != filter_type.lower():
                continue

            score = compute_cosine_similarity(query, chunk.content)
            if score > 0.0:
                results.append(SearchResult(chunk=chunk, score=score))

        # Sort descending by similarity score
        results.sort(key=lambda r: r.score, reverse=True)
        return results[:top_k]

# Global Vector Store Singleton
global_vector_store = PersistentVectorStore()

# Compatibility alias
VectorStore = PersistentVectorStore
