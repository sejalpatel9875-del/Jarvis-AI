"""
Purpose:
Tracks performance metrics and health analytics for AI providers.

Responsibilities:
- Record latency, success count, and error count per provider
- Compute success rates and average latencies for dynamic routing decisions

Dependencies:
- None
"""

import time
import threading
from dataclasses import dataclass, field
from typing import Dict

@dataclass
class ProviderMetrics:
    total_calls: int = 0
    success_calls: int = 0
    error_calls: int = 0
    total_latency: float = 0.0

    @property
    def avg_latency(self) -> float:
        return (self.total_latency / self.success_calls) if self.success_calls > 0 else 0.0

    @property
    def success_rate(self) -> float:
        return (self.success_calls / self.total_calls * 100.0) if self.total_calls > 0 else 100.0

class MetricsTracker:
    """Thread-safe telemetry & performance tracker for AI Providers."""
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(MetricsTracker, cls).__new__(cls)
                cls._instance._metrics: Dict[str, ProviderMetrics] = {}
            return cls._instance

    def record_call(self, provider: str, latency: float, success: bool):
        with self._lock:
            if provider not in self._metrics:
                self._metrics[provider] = ProviderMetrics()
            m = self._metrics[provider]
            m.total_calls += 1
            if success:
                m.success_calls += 1
                m.total_latency += latency
            else:
                m.error_calls += 1

    def get_summary(self) -> dict:
        with self._lock:
            return {
                provider: {
                    "total_calls": m.total_calls,
                    "success_calls": m.success_calls,
                    "error_calls": m.error_calls,
                    "success_rate": f"{m.success_rate:.1f}%",
                    "avg_latency": f"{m.avg_latency:.2f}s"
                }
                for provider, m in self._metrics.items()
            }

# Global Metrics Tracker Singleton
metrics_tracker = MetricsTracker()
