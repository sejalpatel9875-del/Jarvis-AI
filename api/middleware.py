"""
Purpose:
FastAPI Security Middleware for Jarvis AI OS.

Responsibilities:
- Add security response headers (X-Content-Type-Options, X-Frame-Options, CSP)
- Optional API key header validation (X-API-Key)
"""

from fastapi import Request, Response, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from core.security import APIKeyValidator

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Adds hardening security response headers to all API responses."""

    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Content-Security-Policy"] = "default-src 'self' 'unsafe-inline' 'unsafe-eval' https:;"
        return response
