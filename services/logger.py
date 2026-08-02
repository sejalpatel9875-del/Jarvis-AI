"""
Purpose:
Structured Daily Observability Logger for Jarvis AI OS.

Responsibilities:
- Daily log file rotation in logs/YYYY-MM-DD.log
- Thread-safe formatted logging for User inputs, Planner decisions, Tool executions, and Latency
- Formatted console and file streaming

Dependencies:
- os, sys, datetime, threading
"""

import os
import sys
import threading
from datetime import datetime
from typing import Optional


class JarvisLogger:
    """Thread-safe Structured Daily Logger for Jarvis."""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(JarvisLogger, cls).__new__(cls)
                cls._instance._init_logger()
            return cls._instance

    def _init_logger(self):
        # Vercel Functions expose a read-only application bundle; /tmp is the
        # ephemeral writable location available during an invocation.
        self.logs_dir = (
            "/tmp/jarvis-logs" if os.getenv("VERCEL") else os.path.join(os.getcwd(), "logs")
        )
        os.makedirs(self.logs_dir, exist_ok=True)

    def _get_log_file_path(self) -> str:
        today_str = datetime.now().strftime("%Y-%m-%d")
        return os.path.join(self.logs_dir, f"{today_str}.log")

    def _write_entry(
        self, level: str, category: str, message: str, latency: Optional[float] = None
    ):
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        lat_str = f" | Latency: {latency:.2f}s" if latency is not None else ""
        formatted_line = f"[{timestamp}] [{level}] [{category}] {message}{lat_str}\n"

        log_file = self._get_log_file_path()
        try:
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(formatted_line)
        except Exception as e:
            print(f"[JarvisLogger Error] Failed to write log: {e}", file=sys.stderr)

    def info(self, category: str, message: str, latency: Optional[float] = None):
        self._write_entry("INFO", category, message, latency)

    def warning(self, category: str, message: str):
        self._write_entry("WARN", category, message)

    def error(self, category: str, message: str):
        self._write_entry("ERROR", category, message)

    def user(self, message: str):
        self._write_entry("INFO", "USER_INPUT", message)

    def planner(self, message: str):
        self._write_entry("INFO", "PLANNER", message)

    def executor(
        self, tool_name: str, status: str, result_snippet: str, latency: Optional[float] = None
    ):
        self._write_entry(
            "INFO", f"EXECUTOR:{tool_name}", f"Status={status} -> {result_snippet}", latency
        )


# Global Logger Singleton
logger = JarvisLogger()
