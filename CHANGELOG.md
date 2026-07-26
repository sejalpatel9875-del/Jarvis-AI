# 📝 CHANGELOG — J.A.R.V.I.S. AI OS

All notable changes to the Jarvis AI Operating System project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [v1.6.0] - 2026-07-26 (STABLE RELEASE)

### ✨ Added
- **File Intelligence & Document RAG Knowledge Base**: Complete PDF, DOCX, TXT, MD, CSV, LOG extraction pipeline.
- **Persistent SQLite Vector Storage ([providers/embedding.py](file:///c:/Users/Aryan/Documents/jarvis/providers/embedding.py))**: SQLite vector store surviving application restarts with metadata filtering (`filter_source`, `filter_type`).
- **Multi-Document Comparison**: Side-by-side contract & document comparison with page citations.
- **Planner Agent Integration**: `Capability.DOCUMENT_READ` registered in Reasoner & ToolRegistry.
- **Documentation Redesign**: Complete architecture diagrams, capabilities showcase, and benchmarks in `README.md`.

---

## [v1.6.0-alpha2] - 2026-07-26

### ✨ Added
- **Persistent SQLite Vector Store ([providers/embedding.py](file:///c:/Users/Aryan/Documents/jarvis/providers/embedding.py))**: `document_chunks` SQLite table in `memory/jarvis.db` ensuring document index survives application restarts.
- **Multi-Document Indexing & Metadata Filtering**: Filter knowledge base queries by `source_file` or `file_type`.
- **Retrieval Quality Unit Test Suite ([tests/test_retrieval.py](file:///c:/Users/Aryan/Documents/jarvis/tests/test_retrieval.py))**: Verified DB restart survival, multi-document search, and metadata filtering.
- **Vector Benchmark Expansion ([scripts/benchmark.py](file:///c:/Users/Aryan/Documents/jarvis/scripts/benchmark.py))**: Added chunking speed (`chunks/sec`), vector indexing latency, and similarity search benchmarks.

---

## [v1.6.0-alpha1] - 2026-07-25

### ✨ Added
- **Document Loader Service ([services/document_loader.py](file:///c:/Users/Aryan/Documents/jarvis/services/document_loader.py))**: Extraction pipeline for PDF, DOCX, TXT, MD, CSV documents.
- **Semantic Text Chunker ([services/chunker.py](file:///c:/Users/Aryan/Documents/jarvis/services/chunker.py))**: Sliding window text chunking preserving source file & page citations.
- **VectorStore & Embedding Provider ([providers/embedding.py](file:///c:/Users/Aryan/Documents/jarvis/providers/embedding.py))**: Zero-cost local term frequency vector embeddings and cosine similarity search.
- **Document RAG Tool ([tools/document.py](file:///c:/Users/Aryan/Documents/jarvis/tools/document.py))**: `DocumentTool` registered into `ToolRegistry` for document indexing and querying.
- Automated unit test suite in `tests/test_document.py`.
