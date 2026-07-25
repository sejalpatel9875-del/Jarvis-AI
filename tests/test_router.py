"""
Unit tests for Intelligent LLM Router, Query Classification, and Provider Metrics.
"""

import unittest
from services.llm_router import LLMRouter
from services.metrics import metrics_tracker

class TestLLMRouter(unittest.TestCase):
    def setUp(self):
        self.router = LLMRouter()

    def test_query_classification(self):
        """Verify Casual vs Complex prompt classification."""
        self.assertEqual(self.router.classify_query("hello how are you"), "Casual")
        self.assertEqual(self.router.classify_query("Write a Python script for file management"), "Complex")

    def test_metrics_tracker(self):
        """Verify thread-safe provider metrics recording."""
        metrics_tracker.record_call("Groq", latency=0.25, success=True)
        summary = metrics_tracker.get_summary()
        self.assertIn("Groq", summary)
        self.assertEqual(summary["Groq"]["success_calls"], 1)

if __name__ == "__main__":
    unittest.main()
