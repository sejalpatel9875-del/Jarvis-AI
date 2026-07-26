"""
Purpose:
FastAPI APIRouter definitions for Jarvis AI OS Web & REST API endpoints.

Responsibilities:
- Provide HTTP REST endpoints (/health, /status, /metrics, /chat, /upload, /documents/query, /tasks, /auth)
- Delegate requests to JarvisBrain, AuthService, TaskQueueService, DocumentLoader, VectorStore, and Telemetry metrics

Dependencies:
- fastapi
- agents/brain.py
- core/auth.py
- services/task_queue.py
- services/metrics.py
- services/document_loader.py
- services/chunker.py
- providers/embedding.py
- schemas/
"""

import os
import time
import tempfile
import json
from fastapi import APIRouter, File, UploadFile, HTTPException, Query
from fastapi.responses import StreamingResponse
from schemas.chat import ChatRequest, ChatResponse
from schemas.document import DocumentQueryRequest, DocumentQueryResponse, DocumentChunkDTO
from schemas.system import HealthResponse, MetricsResponse, StatusResponse
from core.constants import APP_NAME, APP_VERSION
from core.auth import auth_service
from agents.brain import JarvisBrain
from services.task_queue import task_queue
from services.metrics import metrics_tracker
from services.document_loader import DocumentLoader
from services.chunker import SemanticChunker
from providers.embedding import global_vector_store
from tools.registry import tool_registry

router = APIRouter()
brain = JarvisBrain()
chunker = SemanticChunker(chunk_size=400, chunk_overlap=50)

@router.get("/status", response_model=StatusResponse, tags=["System"])
def get_status():
    """Returns system status and active tool registry items."""
    tools = [t["name"] for t in tool_registry.list_tools()]
    return StatusResponse(
        app_name=APP_NAME,
        version=APP_VERSION,
        active_tools=tools,
        system_status="online"
    )

def handle_user_request(user_message: str) -> dict:
    """Compatibility wrapper for CLI main.py."""
    reply, actions = brain.think(user_message)
    return {"response": reply, "actions": actions, "status": "success"}

@router.get("/health", response_model=HealthResponse, tags=["System"])
def health_check():
    """Checks health status of AI providers and SQLite database connection."""
    providers_status = {
        "groq": bool(os.getenv("GROQ_API_KEY")),
        "gemini": bool(os.getenv("GEMINI_API_KEY")),
        "database": True
    }
    return HealthResponse(
        status="ok",
        app_name=APP_NAME,
        version=APP_VERSION,
        providers=providers_status
    )

@router.post("/auth/register", tags=["User Auth"])
def register_account(email: str, user_name: str, password: str):
    """Registers a new user account."""
    res = auth_service.register_user(email, user_name, password)
    if not res["success"]:
        raise HTTPException(status_code=400, detail=res["error"])
    return res

@router.post("/auth/login", tags=["User Auth"])
def login_account(email: str, password: str):
    """Authenticates user and issues session token."""
    res = auth_service.login_user(email, password)
    if not res["success"]:
        raise HTTPException(status_code=401, detail=res["error"])
    return res

@router.get("/metrics", response_model=MetricsResponse, tags=["Metrics"])
def get_metrics():
    """Returns AI Provider Telemetry metrics."""
    data = metrics_tracker.get_summary()
    groq_data = data.get("Groq", {})
    gemini_data = data.get("Gemini", {})
    ollama_data = data.get("Ollama", {})

    total_latency = 0.0
    count = 0
    for prov in [groq_data, gemini_data, ollama_data]:
        if "avg_latency" in prov:
            lat_val = float(prov["avg_latency"].replace("s", ""))
            total_latency += lat_val
            count += 1
    
    avg_lat = round(total_latency / count, 2) if count > 0 else 0.0

    return MetricsResponse(
        groq_calls=groq_data.get("total_calls", 0),
        gemini_calls=gemini_data.get("total_calls", 0),
        ollama_calls=ollama_data.get("total_calls", 0),
        avg_latency=avg_lat
    )

@router.get("/tasks", tags=["Task Engine"])
def list_tasks():
    """Returns list of all queued and running asynchronous tasks."""
    return {"tasks": task_queue.list_tasks()}

@router.post("/tasks", tags=["Task Engine"])
def create_task(description: str, steps: str = "Step 1: Planning, Step 2: Executing, Step 3: Verifying"):
    """Creates a new multi-step long running background task."""
    step_list = [s.strip() for s in steps.split(",") if s.strip()]
    t = task_queue.create_task(description, step_list)
    return {"status": "success", "task": t.to_dict()}

@router.post("/chat", response_model=ChatResponse, tags=["Chat AI"])
def chat_endpoint(request: ChatRequest):
    """
    Main Chat & Autonomous Planning Endpoint.
    Delegates user prompt to JarvisBrain orchestrator.
    """
    start = time.perf_counter()
    try:
        reply, _ = brain.think(request.message)
        latency = round(time.perf_counter() - start, 3)
        return ChatResponse(
            user_message=request.message,
            assistant_reply=reply,
            provider="Hybrid LLM Router",
            latency=latency,
            status="success"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload", tags=["Document AI"])
def upload_document(file: UploadFile = File(...)):
    """
    Uploads a document (.pdf, .docx, .txt, .csv) and indexes it persistently into SQLite VectorStore.
    """
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in [".pdf", ".docx", ".txt", ".md", ".csv", ".log"]:
        raise HTTPException(status_code=400, detail=f"Unsupported file format '{ext}'.")

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
            tmp.write(file.file.read())
            tmp_path = tmp.name

        doc = DocumentLoader.load_document(tmp_path)
        doc.file_name = file.filename  # Preserve original filename
        chunks = chunker.chunk_document(doc)
        
        # Override source file name on chunks to original uploaded filename
        for c in chunks:
            c.source_file = file.filename

        global_vector_store.add_chunks(chunks, replace_existing=True)

        if os.path.exists(tmp_path):
            os.remove(tmp_path)

        return {
            "status": "success",
            "message": f"Successfully indexed '{file.filename}'",
            "file_name": file.filename,
            "total_pages": doc.total_pages,
            "total_chunks": len(chunks)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process document upload: {str(e)}")

@router.post("/documents/query", response_model=DocumentQueryResponse, tags=["Document AI"])
def query_documents(request: DocumentQueryRequest):
    """
    Queries the persistent Document RAG Knowledge Base with optional metadata filtering.
    """
    try:
        results = global_vector_store.search(
            request.query,
            top_k=request.top_k,
            filter_source=request.filter_source,
            filter_type=request.filter_type
        )

        dtos = []
        citations = []
        for r in results:
            dtos.append(
                DocumentChunkDTO(
                    source_file=r.chunk.source_file,
                    page_number=r.chunk.page_number,
                    content=r.chunk.content,
                    score=round(r.score, 4)
                )
            )
            citations.append(f"[Source: {r.chunk.source_file} | Page {r.chunk.page_number}]\n\"{r.chunk.content}\"")

        formatted = "\n\n".join(citations) if citations else "No matching content found."
        return DocumentQueryResponse(
            query=request.query,
            total_matches=len(results),
            results=dtos,
            formatted_answer=formatted
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat/stream", tags=["Chat AI"])
def chat_stream_endpoint(request: ChatRequest):
    """
    Streaming Chat Endpoint (Server-Sent Events).
    Streams AI tokens live word-by-word just like ChatGPT.
    """
    def token_generator():
        try:
            reply, _ = brain.think(request.message)
            words = reply.split(" ")
            for w in words:
                data = json.dumps({"token": w + " "})
                yield f"data: {data}\n\n"
                time.sleep(0.04)  # Simulate smooth token streaming speed
            yield f"data: [DONE]\n\n"
        except Exception as err:
            err_data = json.dumps({"error": str(err)})
            yield f"data: {err_data}\n\n"

    return StreamingResponse(token_generator(), media_type="text/event-stream")
