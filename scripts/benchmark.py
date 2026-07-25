"""
Purpose:
Performance Benchmark Script for Jarvis AI OS.
Measures execution latencies for memory caching, tool registry, and reasoner engine.
"""

import time
import os
import sys

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from memory.manager import MemoryManager
from tools.registry import tool_registry
from agents.reasoner import ReasonerEngine

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

    print("=" * 60)
    print("✅ Benchmark Completed Successfully!")
    print("=" * 60)

if __name__ == "__main__":
    run_benchmarks()
