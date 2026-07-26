# 📝 CHANGELOG — J.A.R.V.I.S. AI OS

All notable changes to the Jarvis AI Operating System project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [v4.0.0] - 2026-07-26 (AUTONOMOUS BUSINESS AI OPERATING SYSTEM MAJOR RELEASE)

### ✨ Added
- **Conversation Vector Memory Engine ([memory/vector_memory.py](file:///c:/Users/Aryan/Documents/jarvis/memory/vector_memory.py))**: TF-IDF keyword vector embeddings stored in SQLite `conversation_vectors` table. Cosine similarity-based semantic recall across past conversations.
- **Usage Analytics Subsystem ([services/analytics.py](file:///c:/Users/Aryan/Documents/jarvis/services/analytics.py))**: Thread-safe per-user usage tracking (queries, tokens, tools used, agents used) with `GET /analytics` REST API.
- **Subscription Billing System ([services/billing.py](file:///c:/Users/Aryan/Documents/jarvis/services/billing.py))**: SaaS plan tiers (FREE/PRO/BUSINESS/ENTERPRISE) with quota enforcement and `GET /billing/plans` REST API.
- **Agent Marketplace ([services/marketplace.py](file:///c:/Users/Aryan/Documents/jarvis/services/marketplace.py))**: Registry of 6 specialized AI agents (Marketing, Sales, Coding, Research, Finance, Writing) with search/activate/deactivate and `GET /marketplace/agents` REST API.
- REST API endpoints: `GET /analytics`, `GET /billing/plans`, `GET /marketplace/agents`.
- Unit tests in [tests/test_v4_platform.py](file:///c:/Users/Aryan/Documents/jarvis/tests/test_v4_platform.py) (Total 70 unit tests passing 100%).

---

## [v3.0.0] - 2026-07-26 (THE ENTERPRISE AI EMPLOYEE PLATFORM MAJOR RELEASE)

### ✨ Added
- **Multi-Tenant User Authentication Engine ([core/auth.py](file:///c:/Users/Aryan/Documents/jarvis/core/auth.py))**.
- **Real-World Execution Tools Suite ([tools/github_tool.py](file:///c:/Users/Aryan/Documents/jarvis/tools/github_tool.py), [tools/email_tool.py](file:///c:/Users/Aryan/Documents/jarvis/tools/email_tool.py), [tools/file_tool.py](file:///c:/Users/Aryan/Documents/jarvis/tools/file_tool.py))**.
- **Voice STT / TTS Audio Pipeline Engine ([services/voice_pipeline.py](file:///c:/Users/Aryan/Documents/jarvis/services/voice_pipeline.py))**.

---

## [v2.5.0] - 2026-07-26 (AUTONOMOUS AI OPERATOR CENTER, SECURITY & DEPLOYMENT RELEASE)

### ✨ Added
- **Futuristic AI Operator Center UI**, **Security Subsystem**, **Production Docker Deployment Stack**.

---

## [v2.0.0] - 2026-07-26 (THE AUTONOMOUS MULTI-AGENT ENGINE & TASK QUEUE RELEASE)

### ✨ Added
- **Multi-Agent Orchestrator Manager** & **Asynchronous Task Queue Engine**.
