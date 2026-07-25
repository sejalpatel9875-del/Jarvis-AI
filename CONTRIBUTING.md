# 🤝 CONTRIBUTING TO J.A.R.V.I.S. AI OS

Thank you for considering contributing to the Jarvis AI Operating System!

---

## 🏗️ Architecture Design Rules

Before submitting any code, please adhere to our core architecture principles:

1. **Single Responsibility Principle**:
   - `Reasoner` only generates plans.
   - `Executor` only executes steps.
   - `Validator` only verifies results.
   - `Memory` only handles persistence.
   - `Brain` only orchestrates gateways.
2. **Capability-Abstracted Tools**:
   - Never hardcode tool names inside the `Reasoner` or `Planner`. Always think in terms of `Capability` enums (`Capability.WEB_SEARCH`, `Capability.MATH`, etc.).
3. **The 3 Maintainability Questions**:
   - *Will this change be maintainable in 6 months?*
   - *Does it keep the architecture clean?*
   - *Adding a new tool should modify EXACTLY 1 file in `tools/` with `@register_tool`.*

---

## 🛠️ Local Development Setup

```bash
# 1. Clone repository
git clone https://github.com/sejalpatel9875-del/Jarvis-AI.git
cd jarvis

# 2. Set up virtual environment
python -m venv .venv
.venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run automated test suite
python -m unittest discover tests
```

---

## 🧪 Pull Request Guidelines

1. Ensure all 24+ unit tests pass: `python -m unittest discover tests`
2. Update [CHANGELOG.md](file:///c:/Users/Aryan/Documents/jarvis/CHANGELOG.md) under `[Unreleased]` or the new version.
3. Submit your PR using our PR template.
