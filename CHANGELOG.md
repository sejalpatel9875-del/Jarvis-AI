# 📝 CHANGELOG — J.A.R.V.I.S. AI OS

All notable changes to the Jarvis AI Operating System project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [v1.7.0-alpha2] - 2026-07-26 (PLAYWRIGHT BROWSER AUTOMATION RELEASE)

### ✨ Added
- **Browser Automation Service ([services/browser_automation.py](file:///c:/Users/Aryan/Documents/jarvis/services/browser_automation.py))**: Playwright & resilient HTTP browser automation for clean text extraction and webpage screenshots.
- **Playwright Browser Tool ([tools/browser.py](file:///c:/Users/Aryan/Documents/jarvis/tools/browser.py))**: Upgraded `BrowserTool` registered into `ToolRegistry` supporting `fetch` and `screenshot` actions.
- Automated browser automation unit test suite in [tests/test_browser_automation.py](file:///c:/Users/Aryan/Documents/jarvis/tests/test_browser_automation.py).

---

## [v1.7.0-alpha1] - 2026-07-26 (VISION & STREAMING CHAT RELEASE)

### ✨ Added
- **Vision Intelligence Service ([services/vision.py](file:///c:/Users/Aryan/Documents/jarvis/services/vision.py))**: Desktop screen capture (`PIL.ImageGrab`) and OCR text extraction.
- **Vision Tool ([tools/vision.py](file:///c:/Users/Aryan/Documents/jarvis/tools/vision.py))**: `VisionTool` registered into `ToolRegistry` under `Capability.VISION_ANALYSIS`.
- **Streaming Chat Endpoint (`POST /chat/stream`)**: Server-Sent Events (SSE) token streaming endpoint in [api/routes.py](file:///c:/Users/Aryan/Documents/jarvis/api/routes.py).
- **Web Dashboard Voice Input & Token Typing Animation ([static/app.js](file:///c:/Users/Aryan/Documents/jarvis/static/app.js))**: Web Speech API microphone voice recognition and real-time word-by-word streaming token rendering.
- Automated unit test suite in [tests/test_vision.py](file:///c:/Users/Aryan/Documents/jarvis/tests/test_vision.py).

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
