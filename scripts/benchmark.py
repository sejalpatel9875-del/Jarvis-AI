"""
Purpose:
Performance Benchmark Script for Jarvis AI OS.
Measures execution latencies for memory caching, tool registry, reasoner engine, and vector indexing/retrieval.
"""

import time
import os
import sys

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from memory.manager import MemoryManager
from tools.registry import tool_registry
from agents.reasoner import ReasonerEngine
from services.document_loader import DocumentLoader
from services.chunker import SemanticChunker
from providers.embedding import global_vector_store

def run_benchmarks():
    print("=" * 60)
    print("🚀 J.A.R.V.I.S. AI OS — PERFORMANCE BENCHMARK SUITE")
    print("=" * 60)

    mm = MemoryManager()
    reasoner = ReasonerEngine()

    # 1. In-Memory Cache Benchmark
    mm.save_preference("benchmark_key", "benchmark_value")
    start = time.perf_counter()
    iterations = 10000
    for _ in range(iterations):
        mm.get_preference("benchmark_key")
    elapsed = time.perf_counter() - start
    ops_per_sec = iterations / elapsed
    print(f"1. Memory Cache Read ({iterations} ops): {elapsed*1000:.2f} ms ({ops_per_sec:,.0f} ops/sec)")

    # 2. Tool Registry Benchmark
    start = time.perf_counter()
    for _ in range(iterations):
        tool_registry.get_tool("calculator")
    elapsed = time.perf_counter() - start
    ops_per_sec = iterations / elapsed
    print(f"2. Tool Registry Lookup ({iterations} ops): {elapsed*1000:.2f} ms ({ops_per_sec:,.0f} ops/sec)")

    # 3. Local Math Evaluation Benchmark
    start = time.perf_counter()
    for _ in range(1000):
        tool_registry.execute("calculator", expression="15% of 800")
    elapsed = time.perf_counter() - start
    print(f"3. Fast Math Tool Execution (1000 ops): {elapsed*1000:.2f} ms (Avg {(elapsed/1000)*1000:.3f} ms/op)")

    # 4. Reasoner Plan Generation Benchmark
    start = time.perf_counter()
    for _ in range(100):
        reasoner.generate_plan("calculate 15% of 800")
    elapsed = time.perf_counter() - start
    print(f"4. Reasoner Plan Generation (100 ops): {elapsed*1000:.2f} ms (Avg {(elapsed/100)*1000:.3f} ms/plan)")

    # 5. Document RAG Chunking & Vector Search Benchmark
    chunker = SemanticChunker(chunk_size=200, chunk_overlap=20)
    sample_text = "Python 3.14 features memory optimizations. Page 17 describes memory layout changes. JIT compiler improves speed." * 100
    
    from services.document_loader import DocumentContent, DocumentPage
    sample_doc = DocumentContent(
        file_path="benchmark.txt",
        file_name="benchmark.txt",
        file_type="txt",
        total_pages=1,
        pages=[DocumentPage(source_file="benchmark.txt", page_number=1, text=sample_text)]
    )

    start = time.perf_counter()
    chunks = chunker.chunk_document(sample_doc)
    chunk_elapsed = time.perf_counter() - start
    chunks_per_sec = len(chunks) / chunk_elapsed if chunk_elapsed > 0 else 0
    print(f"5. Document Chunking Speed ({len(chunks)} chunks): {chunk_elapsed*1000:.2f} ms ({chunks_per_sec:,.0f} chunks/sec)")

    global_vector_store.clear()
    start = time.perf_counter()
    global_vector_store.add_chunks(chunks)
    index_elapsed = time.perf_counter() - start
    print(f"6. Persistent Vector Indexing Speed ({len(chunks)} chunks): {index_elapsed*1000:.2f} ms")

    start = time.perf_counter()
    search_results = global_vector_store.search("memory optimizations", top_k=3)
    search_elapsed = time.perf_counter() - start
    print(f"7. Vector Similarity Search Latency: {search_elapsed*1000:.3f} ms")

    print("=" * 60)
    print("✅ Benchmark Completed Successfully!")
    print("=" * 60)

if __name__ == "__main__":
    run_benchmarks()
