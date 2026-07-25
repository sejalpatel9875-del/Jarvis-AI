# 📝 CHANGELOG — J.A.R.V.I.S. AI OS

All notable changes to the Jarvis AI Operating System project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [v1.5.0-alpha4] - 2026-07-25

### ✨ Added
- **Result Validator & Goal Verifier ([agents/validator.py](file:///c:/Users/Aryan/Documents/jarvis/agents/validator.py))**: Decoupled goal verification engine.
- Structured `ValidationResult` with `is_valid`, `completion_rate`, `missing_requirements`, and recommendations (`APPROVE`, `RE_PLAN`, `PARTIAL_SUCCESS`).
- Automated unit test suite in `tests/test_validator.py`.

---

## [v1.5.0-alpha3] - 2026-07-25

### ✨ Added
- **Reasoner Engine ([agents/reasoner.py](file:///c:/Users/Aryan/Documents/jarvis/agents/reasoner.py))**: LLM-powered goal analyzer and step generator.
- Capability-abstracted planning (thinks in terms of `web_search`, `math`, `web_scrape` capabilities without hardcoded tool names).
- Dynamic step dependency generation (`depends_on`) and confidence estimation.
- **CHANGELOG.md**: Open-source standard release tracking.

---

## [v1.5.0-alpha2] - 2026-07-25

### ✨ Added
- **Step Executor Engine ([agents/executor.py](file:///c:/Users/Aryan/Documents/jarvis/agents/executor.py))**: Decoupled step execution manager.
- Dynamic Capability ➔ Tool Resolution via `ToolRegistry`.
- Retry Engine with exponential backoff (`0.2s * 2^attempt`, max 2 retries).
- `ExecutionEvent` timestamped history logging per step.

---

## [v1.5.0-alpha1] - 2026-07-25

### ✨ Added
- **Planner State Machine ([agents/state.py](file:///c:/Users/Aryan/Documents/jarvis/agents/state.py))**: `PlanModel`, `PlanStep`, `PlanStatus`, `StepStatus`, and `Capability` enums.
- Dependency readiness check (`step.is_ready(completed_step_ids)`).

---

## [v1.4.1] - 2026-07-25

### ✨ Added
- **Automated Test Suite ([tests/](file:///c:/Users/Aryan/Documents/jarvis/tests))**: Unit tests for registry, memory, router, and state machine.
- **[ARCHITECTURE.md](file:///c:/Users/Aryan/Documents/jarvis/ARCHITECTURE.md)**: Master platform specification and sequence diagrams.
- Exception resilience in `ToolRegistry` (tool crashes return `ToolResult(success=False)` without crashing Jarvis).

---

## [v1.4.0] - 2026-07-25

### ✨ Added
- **Central Tool Registry Framework ([tools/](file:///c:/Users/Aryan/Documents/jarvis/tools))**: `BaseTool`, `ToolResult`, `ToolRegistry`, and `@register_tool` decorator.
- Plug-and-play tools: `CalculatorTool`, `MusicTool`, `SearchTool`, `SystemTool`, `BrowserTool`.
- Provider Telemetry Metrics Tracker ([services/metrics.py](file:///c:/Users/Aryan/Documents/jarvis/services/metrics.py)).

---

## [v1.3.0] - 2026-07-25

### ✨ Added
- **Intelligent Decision Engine ([services/llm_router.py](file:///c:/Users/Aryan/Documents/jarvis/services/llm_router.py))**: Dynamic query classifier (Casual ➔ Groq, Complex ➔ Gemini).
- Socket-based internet connectivity detection and offline fallback to local Ollama.
- Thread-safe Singleton & $O(1)$ in-memory preference caching in `MemoryManager`.

---

## [v1.2.0] - 2026-07-25

### ✨ Added
- **Persistent SQLite Memory Engine ([memory/](file:///c:/Users/Aryan/Documents/jarvis/memory))**: `conversations` and `preferences` tables in `jarvis.db`.
- High-level Memory API: `save_conversation()`, `load_recent()`, `search_history()`, `save_preference()`, `get_preference()`.
