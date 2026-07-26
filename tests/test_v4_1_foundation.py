"""
Unit tests for Sprint v4.1 Production Foundation.
"""

import unittest
from core.config import settings
from services.redis_cache import redis_cache
from fastapi.testclient import TestClient
from api.main import app

class TestV41Foundation(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_centralized_settings(self):
        """Verify SystemSettings loads configuration defaults."""
        self.assertEqual(settings.app_name, "J.A.R.V.I.S. AI OS")
        self.assertIsInstance(settings.is_production, bool)

    def test_redis_cache_fallback(self):
        """Verify RedisCacheService sets and gets keys using fallback cache."""
        redis_cache.set_cache("test_v41_key", {"status": "ok"}, ttl_seconds=60)
        cached = redis_cache.get_cache("test_v41_key")
        self.assertEqual(cached, {"status": "ok"})

    def test_api_v1_endpoints(self):
        """Verify namespaced /api/v1/* routes execute successfully."""
        resp = self.client.get("/api/v1/health")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["status"], "ok")

        status_resp = self.client.get("/api/v1/status")
        self.assertEqual(status_resp.status_code, 200)

        plans_resp = self.client.get("/api/v1/billing/plans")
        self.assertEqual(plans_resp.status_code, 200)
        self.assertIn("plans", plans_resp.json())

if __name__ == "__main__":
    unittest.main()
