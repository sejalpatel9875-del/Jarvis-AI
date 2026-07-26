# 📝 CHANGELOG — J.A.R.V.I.S. AI OS

All notable changes to the Jarvis AI Operating System project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [v4.7.0] - 2026-07-26 (PRODUCT POLISH & COMMERCIAL LAUNCH READINESS PLATFORM RELEASE)

### ✨ Added
- **Global Enterprise Search Engine ([services/global_search.py](file:///c:/Users/Aryan/Documents/jarvis/services/global_search.py))**: Cross-entity search indexing across Leads, Deals, Workflows, Knowledge, and Activity Logs (`search_all`).
- **Command Palette Shortcuts Registry ([services/command_palette.py](file:///c:/Users/Aryan/Documents/jarvis/services/command_palette.py))**: Quick action shortcuts engine for `Ctrl+K`, `Ctrl+Shift+L`, `Ctrl+Shift+U`, `Ctrl+Shift+W`.
- **Interactive User Onboarding Wizard ([services/onboarding_wizard.py](file:///c:/Users/Aryan/Documents/jarvis/services/onboarding_wizard.py))**: Guided 4-step setup progress tracker with SQLite persistence.
- **Polished CEO Executive Command Center ([services/dashboard.py](file:///c:/Users/Aryan/Documents/jarvis/services/dashboard.py))**: Multi-module metrics aggregator (Leads, Pipeline Value, Active Workflows, Storage, System Health).
- **Commercial Launch Guide ([docs/COMMERCIAL_LAUNCH_GUIDE.md](file:///c:/Users/Aryan/Documents/jarvis/docs/COMMERCIAL_LAUNCH_GUIDE.md))**: Full SaaS Commercial Pricing Tiers, Architecture diagrams, and API docs.
- REST API v1 Endpoints: `GET /api/v1/search`, `GET /api/v1/command-palette`, `GET /api/v1/onboarding/status`, `POST /api/v1/onboarding/complete-step`.
- Comprehensive Unit Test suite in [tests/test_v4_7_polish.py](file:///c:/Users/Aryan/Documents/jarvis/tests/test_v4_7_polish.py).

---

## [v4.6.0] - 2026-07-26 (BUSINESS COMMUNICATION HUB & ACTIVITY FEED RELEASE)

### ✨ Added
- **GitHub-Style Workspace Activity Feed ([services/activity_feed.py](file:///c:/Users/Aryan/Documents/jarvis/services/activity_feed.py))**.
- **Departmental Team Inbox ([services/team_inbox.py](file:///c:/Users/Aryan/Documents/jarvis/services/team_inbox.py))**.
- **Calendar & Follow-Up Reminders Engine ([services/calendar_reminders.py](file:///c:/Users/Aryan/Documents/jarvis/services/calendar_reminders.py))**.
