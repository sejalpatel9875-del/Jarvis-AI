# 📝 CHANGELOG — J.A.R.V.I.S. AI OS

All notable changes to the Jarvis AI Operating System project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [v1.6.1] - 2026-07-26 (FASTAPI STABILIZATION RELEASE)

### ✨ Added
- **FastAPI Application Layer ([api/main.py](file:///c:/Users/Aryan/Documents/jarvis/api/main.py))**: Complete REST API web server supporting `uvicorn api.main:app --reload` with interactive Swagger docs at `http://127.0.0.1:8000/docs`.
- **Pydantic Schemas ([schemas/](file:///c:/Users/Aryan/Documents/jarvis/schemas))**: DTOs for `ChatRequest`, `ChatResponse`, `DocumentQueryRequest`, `DocumentQueryResponse`, `HealthResponse`, `MetricsResponse`, `StatusResponse`.
- **REST Endpoints ([api/routes.py](file:///c:/Users/Aryan/Documents/jarvis/api/routes.py))**:
  - `GET /health` & `GET /status`: Health check & provider connection status.
  - `GET /metrics`: Telemetry statistics.
  - `POST /chat`: Main Chat & Autonomous Planner execution endpoint.
  - `POST /upload`: Multi-format document upload & persistent SQLite indexing.
  - `POST /documents/query`: Document RAG query endpoint with citations.
- **Planner Fixes**: Corrected capability mapping in `agents/executor.py` (`document_read` -> `document` tool) and updated music pattern matching in `agents/reasoner.py`.
- Automated API test suite in [tests/test_api.py](file:///c:/Users/Aryan/Documents/jarvis/tests/test_api.py).

---

## [v1.6.0] - 2026-07-26 (STABLE RELEASE)

### ✨ Added
- **File Intelligence & Document RAG Knowledge Base**: Complete PDF, DOCX, TXT, MD, CSV, LOG extraction pipeline.
- **Persistent SQLite Vector Storage ([providers/embedding.py](file:///c:/Users/Aryan/Documents/jarvis/providers/embedding.py))**: SQLite vector store surviving application restarts with metadata filtering (`filter_source`, `filter_type`).
- **Multi-Document Comparison**: Side-by-side contract & document comparison with page citations.
- **Planner Agent Integration**: `Capability.DOCUMENT_READ` registered in Reasoner & ToolRegistry.
- **Documentation Redesign**: Complete architecture diagrams, capabilities showcase, and benchmarks in `README.md`.
