import unittest
import uuid
from memory.vector_memory import vector_memory
from services.analytics import analytics
from services.billing import billing
from services.marketplace import marketplace

class TestV4Platform(unittest.TestCase):
    def test_vector_memory_save_and_recall(self):
        vector_memory.save_embedding("What is AI?", "AI is artificial intelligence.", "Groq")
        results = vector_memory.semantic_recall("artificial intelligence")
        self.assertIsInstance(results, list)

    def test_analytics_record_query(self):
        uid = f"user_{uuid.uuid4().hex[:6]}"
        analytics.record_query(uid, 50, "calculator", "PlannerAgent")
        stats = analytics.get_user_stats(uid)
        self.assertEqual(stats["total_queries"], 1)

    def test_billing_quota_check(self):
        allowed, remaining = billing.check_quota("free_user", plan="free")
        self.assertIsInstance(allowed, bool)
        self.assertIsInstance(remaining, int)

    def test_marketplace_list_agents(self):
        agents = marketplace.list_agents()
        self.assertGreaterEqual(len(agents), 5)

    def test_marketplace_search(self):
        results = marketplace.search_agents("coding")
        self.assertGreaterEqual(len(results), 1)

if __name__ == "__main__":
    unittest.main()
