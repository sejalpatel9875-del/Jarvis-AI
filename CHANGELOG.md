# 📝 CHANGELOG — J.A.R.V.I.S. AI OS

All notable changes to the Jarvis AI Operating System project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [v4.4.0] - 2026-07-26 (ENTERPRISE NO-CODE AUTOMATION ENGINE RELEASE)

### ✨ Added
- **Trigger & Action Automation Pipeline Engine ([services/automation_engine.py](file:///c:/Users/Aryan/Documents/jarvis/services/automation_engine.py))**: Configurable trigger-condition-action workflow definitions (`DOCUMENT_UPLOADED`, `SCHEDULED_CRON`, `TASK_FINISHED`).
- **Recurring Workflow Cron Scheduler ([services/workflow_scheduler.py](file:///c:/Users/Aryan/Documents/jarvis/services/workflow_scheduler.py))**: Cron execution engine for automated recurring reports and emails.
- **Workflow Execution History & Retry Engine ([services/workflow_execution.py](file:///c:/Users/Aryan/Documents/jarvis/services/workflow_execution.py))**: Step execution logger (`SUCCESS`/`FAILED`, `duration_ms`) and retry backoff loop.
- REST API v1 Endpoints: `POST /api/v1/workflows/create`, `POST /api/v1/workflows/execute`, `GET /api/v1/workflows/history`.
- Unit test suite in [tests/test_v4_4_automation.py](file:///c:/Users/Aryan/Documents/jarvis/tests/test_v4_4_automation.py) (Total 105 unit tests passing 100%).

---

## [v4.3.0] - 2026-07-26 (UNIVERSAL KNOWLEDGE INTELLIGENCE PLATFORM RELEASE)

### ✨ Added
- **Universal Multi-Format Ingestion Engine ([services/universal_document_loader.py](file:///c:/Users/Aryan/Documents/jarvis/services/universal_document_loader.py))**.
- **Workspace-Aware RAG Engine ([services/knowledge_engine.py](file:///c:/Users/Aryan/Documents/jarvis/services/knowledge_engine.py))**.
- **AI Executive Report Generator ([services/report_generator.py](file:///c:/Users/Aryan/Documents/jarvis/services/report_generator.py))**.
