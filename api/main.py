"""
Purpose:
FastAPI Application Entry Point for Jarvis AI OS.

Usage:
uvicorn api.main:app --reload --host 127.0.0.1 --port 8000
"""

import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from api.routes import router
from api.v1.router import v1_router
from api.middleware import SecurityHeadersMiddleware
from core.constants import APP_NAME, APP_VERSION

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description="Production Web & REST API AI Agent Operating System",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Security Response Headers Middleware
app.add_middleware(SecurityHeadersMiddleware)

# Configurable Production CORS Middleware
raw_cors = os.getenv("CORS_ORIGINS", "*")
allowed_origins = [origin.strip() for origin in raw_cors.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True if allowed_origins != ["*"] else False,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    import logging
    logging.error(f"[SERVER_ERROR] {request.method} {request.url.path}: {str(exc)}", exc_info=True)
    is_prod = os.getenv("ENVIRONMENT", "development").lower() == "production"
    error_detail = "Internal Server Error" if is_prod else str(exc)
    return JSONResponse(
        status_code=500,
        content={"error": error_detail, "path": str(request.url.path)}
    )

# Include Legacy Top-Level Routes & API v1 Namespaced Routes
app.include_router(router)
app.include_router(v1_router, prefix="/api")

# Mount Static Files & Serve Commercial Web App UI at http://127.0.0.1:8000/
web_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "web")
if os.path.exists(web_dir):
    app.mount("/web", StaticFiles(directory=web_dir), name="web")

    @app.get("/", include_in_schema=False)
    def serve_dashboard():
        return FileResponse(os.path.join(web_dir, "index.html"))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="127.0.0.1", port=8000, reload=True)
