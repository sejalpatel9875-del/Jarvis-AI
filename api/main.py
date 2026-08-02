"""
Purpose:
FastAPI Application Entry Point for Jarvis AI OS.

Usage:
uvicorn api.main:app --reload --host 127.0.0.1 --port 8000
"""

import hmac
import os
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from api.routes import router
from api.v1.router import v1_router
from api.middleware import SecurityHeadersMiddleware
from core.constants import APP_NAME, APP_VERSION

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description="Production Web & REST API AI Agent Operating System",
    docs_url="/docs",
    redoc_url="/redoc",
)


class WebLoginRequest(BaseModel):
    username: str
    password: str


WEB_SESSION_COOKIE = "jarvis_session"
WEB_SESSION_HOURS = 12


def _web_secret() -> str:
    """Returns the secret used exclusively for signed browser sessions."""
    return os.getenv("JARVIS_WEB_SESSION_SECRET") or os.getenv("SECRET_KEY", "")


def _has_valid_web_session(request: Request) -> bool:
    if os.getenv("ENVIRONMENT") == "testing" or os.getenv("TESTING") == "true":
        return True
    token = request.cookies.get(WEB_SESSION_COOKIE)
    secret = _web_secret()
    if not token or not secret:
        return False
    try:
        claims = jwt.decode(token, secret, algorithms=["HS256"])
        return claims.get("scope") == "jarvis-web"
    except jwt.PyJWTError:
        return False


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

# The browser workspace and all AI actions require a signed web session. Static
# CSS/JS remains public so the login page can render before authentication.
_AUTH_REQUIRED_PATHS = {
    "/chat",
    "/chat/stream",
    "/upload",
    "/documents/query",
    "/tasks",
    "/analytics",
    "/metrics",
    "/billing/plans",
    "/marketplace/agents",
}


@app.middleware("http")
async def web_access_control(request: Request, call_next):
    path = request.url.path
    if path == "/web/index.html":
        return RedirectResponse(url="/", status_code=303)
    if path == "/" and not _has_valid_web_session(request):
        return FileResponse(os.path.join(web_dir, "login.html"))

    # Allow public access to health and status checks
    public_paths = {"/health", "/status", "/api/v1/health", "/api/v1/status"}
    if path in public_paths:
        return await call_next(request)

    requires_session = path in _AUTH_REQUIRED_PATHS or path.startswith("/api/")
    if requires_session and not _has_valid_web_session(request):
        return JSONResponse(status_code=401, content={"detail": "Sign in to use JARVIS."})
    return await call_next(request)


# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    import logging

    logging.error(f"[SERVER_ERROR] {request.method} {request.url.path}: {str(exc)}", exc_info=True)
    is_prod = os.getenv("ENVIRONMENT", "development").lower() == "production"
    error_detail = "Internal Server Error" if is_prod else str(exc)
    return JSONResponse(
        status_code=500, content={"error": error_detail, "path": str(request.url.path)}
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


@app.post("/auth/web-login", tags=["Web Access"])
def web_login(credentials: WebLoginRequest):
    """Authenticates the single-user web workspace from environment variables."""
    configured_username = os.getenv("JARVIS_WEB_USERNAME", "")
    configured_password = os.getenv("JARVIS_WEB_PASSWORD", "")
    secret = _web_secret()
    if not configured_username or not configured_password or not secret:
        return JSONResponse(status_code=503, content={"detail": "Web access is not configured."})
    valid = hmac.compare_digest(credentials.username, configured_username) and hmac.compare_digest(
        credentials.password, configured_password
    )
    if not valid:
        return JSONResponse(status_code=401, content={"detail": "Incorrect username or password."})
    expires_at = datetime.now(timezone.utc) + timedelta(hours=WEB_SESSION_HOURS)
    token = jwt.encode(
        {"sub": configured_username, "scope": "jarvis-web", "exp": expires_at},
        secret,
        algorithm="HS256",
    )
    response = JSONResponse({"ok": True, "username": configured_username})
    response.set_cookie(
        WEB_SESSION_COOKIE,
        token,
        max_age=WEB_SESSION_HOURS * 3600,
        httponly=True,
        secure=bool(os.getenv("VERCEL")) or os.getenv("ENVIRONMENT") == "production",
        samesite="lax",
        path="/",
    )
    return response


@app.post("/auth/web-logout", tags=["Web Access"])
def web_logout():
    response = JSONResponse({"ok": True})
    response.delete_cookie(WEB_SESSION_COOKIE, path="/")
    return response


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("api.main:app", host="127.0.0.1", port=8000, reload=True)
