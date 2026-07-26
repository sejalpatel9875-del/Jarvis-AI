# 📝 CHANGELOG — J.A.R.V.I.S. AI OS

All notable changes to the Jarvis AI Operating System project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [v1.7.1] - 2026-07-26 (QUALITY & STABILIZATION HARDENING RELEASE)

### ✨ Added
- **Tool Timeout Enforcement ([tools/base.py](file:///c:/Users/Aryan/Documents/jarvis/tools/base.py) & [agents/executor.py](file:///c:/Users/Aryan/Documents/jarvis/agents/executor.py))**: Added `timeout` property contract and threadpool execution timeout guard to prevent long-running calls from blocking execution loops.
- **Automated Benchmarking Suite ([scripts/benchmark.py](file:///c:/Users/Aryan/Documents/jarvis/scripts/benchmark.py))**: Benchmarks for Fast Math (<0.5ms), Desktop Screenshots (<90ms), Windows Active Window Title Detection (<0.3ms), Vector DB Search (<0.2ms), and LLM Router.
- **Timeout Unit Test Suite ([tests/test_executor_timeout.py](file:///c:/Users/Aryan/Documents/jarvis/tests/test_executor_timeout.py))**: Test suite verifying timeout enforcement and retry backoff guards.

---

## [v1.7.0] - 2026-07-26 (VISION INTELLIGENCE & PLAYWRIGHT BROWSER AUTOMATION RELEASE)

### ✨ Added
- **Vision Intelligence Service ([services/vision.py](file:///c:/Users/Aryan/Documents/jarvis/services/vision.py))**: Desktop screen capture (`PIL.ImageGrab`) and OCR text extraction.
- **Vision Tool ([tools/vision.py](file:///c:/Users/Aryan/Documents/jarvis/tools/vision.py))**: `VisionTool` registered into `ToolRegistry` under `Capability.VISION_ANALYSIS`.
- **Browser Automation Service ([services/browser_automation.py](file:///c:/Users/Aryan/Documents/jarvis/services/browser_automation.py))**: Playwright web browsing and webpage screenshots.
- **Streaming Chat Endpoint (`POST /chat/stream`)**: Server-Sent Events (SSE) token streaming endpoint in [api/routes.py](file:///c:/Users/Aryan/Documents/jarvis/api/routes.py).
- **Web Dashboard Voice Input & Token Typing Animation ([static/app.js](file:///c:/Users/Aryan/Documents/jarvis/static/app.js))**: Web Speech API microphone voice recognition.
