# 📝 CHANGELOG — J.A.R.V.I.S. AI OS

All notable changes to the Jarvis AI Operating System project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [v4.5.0] - 2026-07-26 (BUSINESS CRM & LEAD WORKSPACE PLATFORM RELEASE)

### ✨ Added
- **Enterprise Lead Intelligence Engine ([services/crm_engine.py](file:///c:/Users/Aryan/Documents/jarvis/services/crm_engine.py))**: Lead capture, workspace isolation, status transitions (`NEW`, `QUALIFIED`, `PROPOSAL`, `WON`, `LOST`), and automated AI quality scoring (0-100).
- **Sales Deal Pipeline Engine ([services/deal_pipeline.py](file:///c:/Users/Aryan/Documents/jarvis/services/deal_pipeline.py))**: Deal tracking and pipeline summary aggregations (`total_pipeline_value_usd`, `avg_deal_size_usd`).
- **AI Sales Co-Pilot ([services/lead_ai_assistant.py](file:///c:/Users/Aryan/Documents/jarvis/services/lead_ai_assistant.py))**: Executive lead profiles, 1-click sales email outreach drafting, and meeting transcript decision summaries.
- REST API v1 Endpoints: `POST /api/v1/crm/leads`, `GET /api/v1/crm/leads`, `POST /api/v1/crm/deals`, `GET /api/v1/crm/deals/pipeline`, `POST /api/v1/crm/ai/draft-email`.
- Comprehensive Unit Test suite in [tests/test_v4_5_crm.py](file:///c:/Users/Aryan/Documents/jarvis/tests/test_v4_5_crm.py).

---

## [v4.4.0] - 2026-07-26 (ENTERPRISE NO-CODE AUTOMATION ENGINE RELEASE)

### ✨ Added
- **Trigger & Action Automation Pipeline Engine ([services/automation_engine.py](file:///c:/Users/Aryan/Documents/jarvis/services/automation_engine.py))**.
- **Recurring Workflow Cron Scheduler ([services/workflow_scheduler.py](file:///c:/Users/Aryan/Documents/jarvis/services/workflow_scheduler.py))**.
- **Workflow Execution History & Retry Engine ([services/workflow_execution.py](file:///c:/Users/Aryan/Documents/jarvis/services/workflow_execution.py))**.
