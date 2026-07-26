"""
Automated unit tests for FastAPI REST API endpoints (/health, /status, /metrics, /chat, /upload, /documents/query).
"""

import unittest
import io
from fastapi.testclient import TestClient
from api.main import app
from providers.embedding import global_vector_store

class TestFastAPIEndpoints(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        global_vector_store.clear()

    def tearDown(self):
        global_vector_store.clear()

    def test_health_endpoint(self):
        """Verify GET /health returns 200 OK and status == 'ok'."""
        res = self.client.get("/health")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "ok")
        self.assertIn("providers", data)

    def test_status_endpoint(self):
        """Verify GET /status returns system information."""
        res = self.client.get("/status")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["system_status"], "online")
        self.assertTrue(len(data["active_tools"]) > 0)

    def test_metrics_endpoint(self):
        """Verify GET /metrics returns telemetry stats."""
        res = self.client.get("/metrics")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("groq_calls", data)

    def test_chat_endpoint(self):
        """Verify POST /chat evaluates math expressions."""
        res = self.client.post("/chat", json={"message": "calculate 15% of 800"})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("120", data["assistant_reply"])

    def test_upload_and_document_query_endpoints(self):
        """Verify POST /upload document indexing and POST /documents/query RAG search."""
        file_content = b"Contract Alpha specifies a 30-day payment term and 5 percent penalty for late payments."
        files = {"file": ("contract_alpha.txt", io.BytesIO(file_content), "text/plain")}

        upload_res = self.client.post("/upload", files=files)
        self.assertEqual(upload_res.status_code, 200)
        upload_data = upload_res.json()
        self.assertEqual(upload_data["status"], "success")
        self.assertEqual(upload_data["file_name"], "contract_alpha.txt")

        # Query Document
        query_res = self.client.post("/documents/query", json={"query": "payment term"})
        self.assertEqual(query_res.status_code, 200)
        query_data = query_res.json()
        self.assertTrue(query_data["total_matches"] > 0)
        self.assertIn("contract_alpha.txt", query_data["formatted_answer"])

if __name__ == "__main__":
    unittest.main()
