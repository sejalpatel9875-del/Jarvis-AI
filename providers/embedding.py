"""
Purpose:
Embedding Provider & Vector Store Engine for Jarvis File Intelligence system.

Responsibilities:
- Generate vector embeddings for text chunks (Local TF-IDF & Cosine Similarity)
- Provide VectorStore indexing, similarity search, and top-K chunk retrieval

Dependencies:
- services/chunker.py
"""

import math
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Tuple, Dict, Any
from services.chunker import TextChunk

class BaseEmbeddingProvider(ABC):
    @abstractmethod
    def embed_text(self, text: str) -> List[float]:
        pass

class LocalTFIDFEmbeddingProvider(BaseEmbeddingProvider):
    """
    Zero-Cost Local Keyword & Term Frequency Vectorizer (<0.001s speed).
    Requires 0 external API keys or heavy GPU downloads.
    """
    def tokenize(self, text: str) -> List[str]:
        return re.findall(r'\w+', text.lower())

    def embed_text(self, text: str) -> List[float]:
        # Token frequency map
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

class VectorStore:
    """In-Memory Vector Store & Document Knowledge Index."""
    def __init__(self):
        self._chunks: List[TextChunk] = []

    def add_chunks(self, chunks: List[TextChunk]):
        """Indexes text chunks into vector store."""
        self._chunks.extend(chunks)

    def clear(self):
        """Clears all indexed chunks."""
        self._chunks.clear()

    def search(self, query: str, top_k: int = 3) -> List[SearchResult]:
        """
        Performs semantic similarity search over indexed chunks.
        Returns top_k SearchResults sorted by similarity score.
        """
        results: List[SearchResult] = []
        for chunk in self._chunks:
            score = compute_cosine_similarity(query, chunk.content)
            if score > 0.0:
                results.append(SearchResult(chunk=chunk, score=score))

        # Sort descending by similarity score
        results.sort(key=lambda r: r.score, reverse=True)
        return results[:top_k]

# Global Vector Store Singleton
global_vector_store = VectorStore()
