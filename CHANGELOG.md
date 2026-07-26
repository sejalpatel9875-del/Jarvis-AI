# 📝 CHANGELOG — J.A.R.V.I.S. AI OS

All notable changes to the Jarvis AI Operating System project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [v3.0.0] - 2026-07-26 (THE ENTERPRISE AI EMPLOYEE PLATFORM MAJOR RELEASE)

### ✨ Added
- **Multi-Tenant User Account & Authentication Engine ([core/auth.py](file:///c:/Users/Aryan/Documents/jarvis/core/auth.py))**: SQLite `users` table schema, salted SHA-256 password hashing, user registration, and session token issuing (`POST /api/auth/register`, `POST /api/auth/login`).
- **Real-World Execution Tools Suite ([tools/github_tool.py](file:///c:/Users/Aryan/Documents/jarvis/tools/github_tool.py), [tools/email_tool.py](file:///c:/Users/Aryan/Documents/jarvis/tools/email_tool.py), [tools/file_tool.py](file:///c:/Users/Aryan/Documents/jarvis/tools/file_tool.py))**: `GitHubTool`, `EmailTool`, and `FileTool` auto-registered into `ToolRegistry`.
- **Voice STT / TTS Audio Pipeline Engine ([services/voice_pipeline.py](file:///c:/Users/Aryan/Documents/jarvis/services/voice_pipeline.py))**: Speech-to-Text transcription & Text-to-Speech audio synthesis engine.
- Unit test suite in [tests/test_v3_platform.py](file:///c:/Users/Aryan/Documents/jarvis/tests/test_v3_platform.py) (Total 63 unit tests passing 100%).

---

## [v2.5.0] - 2026-07-26 (AUTONOMOUS AI OPERATOR CENTER, SECURITY & DEPLOYMENT RELEASE)

### ✨ Added
- **Futuristic AI Operator Center UI ([static/index.html](file:///c:/Users/Aryan/Documents/jarvis/static/index.html))**.
- **Security & Prompt Injection Subsystem ([core/security.py](file:///c:/Users/Aryan/Documents/jarvis/core/security.py))**.
- **Production Deployment Stack ([Dockerfile](file:///c:/Users/Aryan/Documents/jarvis/Dockerfile) & [docker-compose.yml](file:///c:/Users/Aryan/Documents/jarvis/docker-compose.yml))**.
