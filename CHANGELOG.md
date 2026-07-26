# 📝 CHANGELOG — J.A.R.V.I.S. AI OS

All notable changes to the Jarvis AI Operating System project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [v4.6.0] - 2026-07-26 (BUSINESS COMMUNICATION HUB & ACTIVITY FEED RELEASE)

### ✨ Added
- **GitHub-Style Workspace Activity Feed ([services/activity_feed.py](file:///c:/Users/Aryan/Documents/jarvis/services/activity_feed.py))**: Real-time chronological event timeline logger (`log_activity`, `get_activity_feed`).
- **Departmental Team Inbox ([services/team_inbox.py](file:///c:/Users/Aryan/Documents/jarvis/services/team_inbox.py))**: Workspace-isolated channel messaging (`#SALES`, `#ENGINEERING`, `#HR`, `#MARKETING`).
- **Calendar & Follow-Up Reminders Engine ([services/calendar_reminders.py](file:///c:/Users/Aryan/Documents/jarvis/services/calendar_reminders.py))**: Task due date scheduling and status tracking.
- **Smart Multi-Channel Notification Engine ([services/smart_notifications.py](file:///c:/Users/Aryan/Documents/jarvis/services/smart_notifications.py))**: Event-triggered alert dispatcher.
- REST API v1 Endpoints: `GET /api/v1/activity-feed`, `POST /api/v1/team-inbox/messages`, `GET /api/v1/team-inbox/messages`, `POST /api/v1/reminders`, `GET /api/v1/reminders`.
- Automated Unit Test suite in [tests/test_v4_6_communication.py](file:///c:/Users/Aryan/Documents/jarvis/tests/test_v4_6_communication.py).

---

## [v4.5.0] - 2026-07-26 (BUSINESS CRM & LEAD WORKSPACE PLATFORM RELEASE)

### ✨ Added
- **Enterprise Lead Intelligence Engine ([services/crm_engine.py](file:///c:/Users/Aryan/Documents/jarvis/services/crm_engine.py))**.
- **Sales Deal Pipeline Engine ([services/deal_pipeline.py](file:///c:/Users/Aryan/Documents/jarvis/services/deal_pipeline.py))**.
- **AI Sales Co-Pilot ([services/lead_ai_assistant.py](file:///c:/Users/Aryan/Documents/jarvis/services/lead_ai_assistant.py))**.
