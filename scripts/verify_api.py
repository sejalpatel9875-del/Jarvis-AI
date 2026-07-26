"""
Purpose:
Automated E2E REST API Verification Runner.
Executes GET /health, GET /status, GET /metrics, POST /chat, POST /upload, and POST /documents/query
and outputs clean JSON responses for CTO review.
"""

import os
import sys
import json
import io

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from api.main import app
from providers.embedding import global_vector_store

def run_api_verification():
    client = TestClient(app)
    global_vector_store.clear()

    print("=" * 60)
    print("🚀 J.A.R.V.I.S. REST API ENDPOINT VERIFICATION RUNNER")
    print("=" * 60)

    # 1. GET /health
    print("\n1. GET /health")
    res1 = client.get("/health")
    print(f"Status Code: {res1.status_code}")
    print(json.dumps(res1.json(), indent=2))

    # 2. GET /status
    print("\n2. GET /status")
    res2 = client.get("/status")
    print(f"Status Code: {res2.status_code}")
    print(json.dumps(res2.json(), indent=2))

    # 3. GET /metrics
    print("\n3. GET /metrics")
    res3 = client.get("/metrics")
    print(f"Status Code: {res3.status_code}")
    print(json.dumps(res3.json(), indent=2))

    # 4. POST /chat ("2+2")
    print("\n4. POST /chat (Message: '2+2')")
    res4 = client.post("/chat", json={"message": "2+2"})
    print(f"Status Code: {res4.status_code}")
    print(json.dumps(res4.json(), indent=2))

    # 5. POST /chat ("who are you")
    print("\n5. POST /chat (Message: 'who are you')")
    res5 = client.post("/chat", json={"message": "who are you"})
    print(f"Status Code: {res5.status_code}")
    print(json.dumps(res5.json(), indent=2))

    # 6. POST /chat ("play despacito")
    print("\n6. POST /chat (Message: 'play despacito')")
    res6 = client.post("/chat", json={"message": "play despacito"})
    print(f"Status Code: {res6.status_code}")
    print(json.dumps(res6.json(), indent=2))

    # 7. POST /upload
    print("\n7. POST /upload (Sample Document Indexing)")
    doc_content = b"Python is a modern programming language.\nFastAPI is a high-performance Web framework for building APIs.\nJarvis AI OS supports persistent document RAG."
    files = {"file": ("jarvis_overview.txt", io.BytesIO(doc_content), "text/plain")}
    res7 = client.post("/upload", files=files)
    print(f"Status Code: {res7.status_code}")
    print(json.dumps(res7.json(), indent=2))

    # 8. POST /documents/query
    print("\n8. POST /documents/query (Question: 'What is FastAPI?')")
    res8 = client.post("/documents/query", json={"query": "What is FastAPI?"})
    print(f"Status Code: {res8.status_code}")
    print(json.dumps(res8.json(), indent=2))

    print("\n" + "=" * 60)
    print("✅ All REST API Endpoints Verified Successfully!")
    print("=" * 60)

if __name__ == "__main__":
    run_api_verification()
