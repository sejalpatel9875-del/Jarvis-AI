# 📝 CHANGELOG — J.A.R.V.I.S. AI OS

All notable changes to the Jarvis AI Operating System project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [v1.9.0] - 2026-07-26 (PERSISTENT MEMORY, DAILY LOGGING, CI/CD & PLUGIN ECOSYSTEM RELEASE)

### ✨ Added
- **Persistent Preference Memory ([agents/memory.py](file:///c:/Users/Aryan/Documents/jarvis/agents/memory.py))**: Auto-learning rules for `User Name`, `Company Name`, `Active Project`, and `Favorites` stored persistently in SQLite and injected into reasoning system prompt.
- **Structured Daily Observability Logging ([services/logger.py](file:///c:/Users/Aryan/Documents/jarvis/services/logger.py))**: `JarvisLogger` writing formatted daily rotated logs (`logs/YYYY-MM-DD.log`) with latency monitoring.
- **Dynamic Plugin Ecosystem ([services/plugin_loader.py](file:///c:/Users/Aryan/Documents/jarvis/services/plugin_loader.py) & [plugins/](file:///c:/Users/Aryan/Documents/jarvis/plugins))**: `BasePlugin` interface and dynamic directory scanner registering plugins into `ToolRegistry`.
- **GitHub Actions CI/CD Pipeline ([.github/workflows/ci.yml](file:///c:/Users/Aryan/Documents/jarvis/.github/workflows/ci.yml))**: Automated workflow running `54+ unit tests` on every commit and pull request.
- Unit test suites in [tests/test_logger.py](file:///c:/Users/Aryan/Documents/jarvis/tests/test_logger.py) and [tests/test_plugin_loader.py](file:///c:/Users/Aryan/Documents/jarvis/tests/test_plugin_loader.py) (Total 54 unit tests passing 100%).

---

## [v1.8.0] - 2026-07-26 (DESKTOP OPERATOR & SAFETY GUARDRAIL RELEASE)

### ✨ Added
- **Desktop Operator Engine ([services/desktop_operator.py](file:///c:/Users/Aryan/Documents/jarvis/services/desktop_operator.py))**: Modular desktop operator subsystem featuring `WindowManager`, `AppLauncher`, `MouseController`, `KeyboardController`, and `SafetyGuardrail`.
- **Safety Interceptor Layer**: `SafetyGuardrail` intercepting high-risk or destructive actions (`delete all`, `format`, `rmdir /s`) before tool execution.
- **System Tool Upgrade ([tools/system.py](file:///c:/Users/Aryan/Documents/jarvis/tools/system.py))**: Integrated `DesktopOperatorService` into `SystemTool` registered into `ToolRegistry`.
