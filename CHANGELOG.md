# 📝 CHANGELOG — J.A.R.V.I.S. AI OS

All notable changes to the Jarvis AI Operating System project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [v1.6.0-alpha1] - 2026-07-25

### ✨ Added
- **Document Loader Service ([services/document_loader.py](file:///c:/Users/Aryan/Documents/jarvis/services/document_loader.py))**: Extraction pipeline for PDF, DOCX, TXT, MD, CSV documents.
- **Semantic Text Chunker ([services/chunker.py](file:///c:/Users/Aryan/Documents/jarvis/services/chunker.py))**: Sliding window text chunking preserving source file & page citations.
- **VectorStore & Embedding Provider ([providers/embedding.py](file:///c:/Users/Aryan/Documents/jarvis/providers/embedding.py))**: Zero-cost local term frequency vector embeddings and cosine similarity search.
- **Document RAG Tool ([tools/document.py](file:///c:/Users/Aryan/Documents/jarvis/tools/document.py))**: `DocumentTool` registered into `ToolRegistry` for document indexing and querying.
- Automated unit test suite in `tests/test_document.py`.

---

## [v1.5.2] - 2026-07-25

### ✨ Added
- **Core Package ([core/](file:///c:/Users/Aryan/Documents/jarvis/core))**: Centralized `constants.py`, custom `exceptions.py` hierarchy, and `interfaces.py`.
- **Modern Project Tooling**: `pyproject.toml` configuration for Black, Ruff, and Mypy.
- Pre-commit hooks configuration ([.pre-commit-config.yaml](file:///c:/Users/Aryan/Documents/jarvis/.pre-commit-config.yaml)).
- Performance Benchmark Suite ([scripts/benchmark.py](file:///c:/Users/Aryan/Documents/jarvis/scripts/benchmark.py)).

---

## [v1.5.1] - 2026-07-25

### ✨ Added
- GitHub Actions CI workflow ([.github/workflows/test.yml](file:///c:/Users/Aryan/Documents/jarvis/.github/workflows/test.yml)).
- Open-source MIT License ([LICENSE](file:///c:/Users/Aryan/Documents/jarvis/LICENSE)).
- Open-source Contribution Guide ([CONTRIBUTING.md](file:///c:/Users/Aryan/Documents/jarvis/CONTRIBUTING.md)).
- GitHub issue templates and pull request templates.
- Environment validator ([utils/env_validator.py](file:///c:/Users/Aryan/Documents/jarvis/utils/env_validator.py)) and structured production logger ([utils/logger.py](file:///c:/Users/Aryan/Documents/jarvis/utils/logger.py)).

---

## [v1.5.0] - 2026-07-25 (STABLE RELEASE)

### ✨ Added
- **Autonomous Planner Agent ([agents/planner.py](file:///c:/Users/Aryan/Documents/jarvis/agents/planner.py))**: Master orchestrator connecting Reasoner -> Executor -> Validator -> Final LLM Synthesis.
- Full `JarvisBrain` integration delegating user goals to PlannerAgent.
