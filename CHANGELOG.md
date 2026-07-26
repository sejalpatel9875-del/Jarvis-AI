# 📝 CHANGELOG — J.A.R.V.I.S. AI OS

All notable changes to the Jarvis AI Operating System project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [v2.0.0] - 2026-07-26 (THE AUTONOMOUS MULTI-AGENT ENGINE & TASK QUEUE RELEASE)

### ✨ Added
- **Multi-Agent Orchestrator Manager ([agents/manager.py](file:///c:/Users/Aryan/Documents/jarvis/agents/manager.py))**: `AgentManager` routing prompts to specialized subagents (`PlannerAgent`, `ResearchAgent`, `CoderAgent`).
- **Asynchronous Task Queue & Long-Running Workflow Engine ([services/task_queue.py](file:///c:/Users/Aryan/Documents/jarvis/services/task_queue.py))**: `TaskQueueService` with progress tracking (0% -> 100%), task IDs, status updates (`PENDING`, `RUNNING`, `COMPLETED`), and step execution.
- **Task REST API Endpoints ([api/routes.py](file:///c:/Users/Aryan/Documents/jarvis/api/routes.py))**: `GET /tasks` and `POST /tasks` endpoints for tracking long-running tasks.
- Unit test suites in [tests/test_agent_manager.py](file:///c:/Users/Aryan/Documents/jarvis/tests/test_agent_manager.py) and [tests/test_task_queue.py](file:///c:/Users/Aryan/Documents/jarvis/tests/test_task_queue.py) (Total 58 unit tests passing 100%).

---

## [v1.9.0] - 2026-07-26 (PERSISTENT MEMORY, DAILY LOGGING, CI/CD & PLUGIN ECOSYSTEM RELEASE)

### ✨ Added
- **Persistent Preference Memory ([agents/memory.py](file:///c:/Users/Aryan/Documents/jarvis/agents/memory.py))**: Auto-learning rules for `User Name`, `Company Name`, `Active Project`, and `Favorites` stored persistently in SQLite.
- **Structured Daily Observability Logging ([services/logger.py](file:///c:/Users/Aryan/Documents/jarvis/services/logger.py))**: Daily rotated logs (`logs/YYYY-MM-DD.log`).
- **Dynamic Plugin Ecosystem ([services/plugin_loader.py](file:///c:/Users/Aryan/Documents/jarvis/services/plugin_loader.py))**: `BasePlugin` interface and dynamic directory scanner.
- **GitHub Actions CI/CD Pipeline ([.github/workflows/ci.yml](file:///c:/Users/Aryan/Documents/jarvis/.github/workflows/ci.yml))**.
