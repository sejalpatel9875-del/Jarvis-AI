"""
Purpose:
FastAPI Application Entry Point for Jarvis AI OS.

Usage:
uvicorn api.main:app --reload --host 127.0.0.1 --port 8000
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from api.routes import router
from core.constants import APP_NAME, APP_VERSION

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description="Production Web & REST API AI Agent Operating System",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for Web Dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"error": str(exc), "path": str(request.url.path)}
    )

# Include API Routes
app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="127.0.0.1", port=8000, reload=True)
