"""
Purpose:
Automated Benchmarking Suite for Jarvis AI OS.

Usage:
python scripts/benchmark.py
"""

import time
import os
import sys

# Ensure root workspace is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.registry import tool_registry
from services.vision import vision_service
from providers.embedding import global_vector_store
from services.llm_router import ask_ai

def run_benchmarks():
    print("\n" + "=" * 60)
    print("🚀 J.A.R.V.I.S. AI OS — AUTOMATED PERFORMANCE BENCHMARKS")
    print("=" * 60)

    benchmarks = []

    # 1. Fast Math Benchmark
    t0 = time.perf_counter()
    res_math = tool_registry.execute("calculator", expression="25*16")
    t_math = (time.perf_counter() - t0) * 1000
    benchmarks.append(("Fast Math Calculation", f"{t_math:.2f} ms", "0 API Cost"))

    # 2. Desktop Screenshot Benchmark
    t0 = time.perf_counter()
    snap_path = vision_service.capture_screenshot()
    t_snap = (time.perf_counter() - t0) * 1000
    if os.path.exists(snap_path):
        os.remove(snap_path)
    benchmarks.append(("Desktop Screenshot Capture", f"{t_snap:.2f} ms", "PIL ImageGrab"))

    # 3. Active Window Detection Benchmark
    t0 = time.perf_counter()
    win_title = vision_service.get_active_window_title()
    t_win = (time.perf_counter() - t0) * 1000
    benchmarks.append(("Active Window Title Detection", f"{t_win:.2f} ms", win_title[:25]))

    # 4. Vector Knowledge Search Benchmark
    t0 = time.perf_counter()
    vec_results = global_vector_store.search("python", top_k=3)
    t_vec = (time.perf_counter() - t0) * 1000
    benchmarks.append(("Vector Knowledge DB Search", f"{t_vec:.2f} ms", "SQLite Persistent"))

    # 5. Groq LLM Router Inference Benchmark
    t0 = time.perf_counter()
    res_ai = ask_ai("Hello")
    t_groq = (time.perf_counter() - t0) * 1000
    reply = res_ai[0] if isinstance(res_ai, tuple) else res_ai
    benchmarks.append(("Groq LLM Router Inference", f"{t_groq:.2f} ms", "Ultra-Fast Router"))

    print(f"{'Benchmark Metric':<32} | {'Latency':<12} | {'Notes'}")
    print("-" * 60)
    for name, lat, note in benchmarks:
        print(f"{name:<32} | {lat:<12} | {note}")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    run_benchmarks()
