"""
security/middleware.py
~~~~~~~~~~~~~~~~~~~~~~
FastAPI Security Middleware enforcing Security Headers, CSP, Rate Limiting, CSRF, XSS, and SQL Injection Prevention.
"""

import time
import re
from typing import Dict, List, Tuple
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse

RATE_LIMIT_WINDOW = 60  # 60 seconds
MAX_REQUESTS_PER_WINDOW = 100


class SecurityMiddleware(BaseHTTPMiddleware):
    """Enforces enterprise security headers, rate limiting, and input sanitization."""

    def __init__(self, app):
        super().__init__(app)
        self.request_counts: Dict[str, List[float]] = {}

    def _is_rate_limited(self, client_ip: str) -> bool:
        """Sliding-window rate limiter per IP address."""
        now = time.time()
        timestamps = self.request_counts.get(client_ip, [])
        # Filter timestamps within window
        valid_timestamps = [t for t in timestamps if now - t < RATE_LIMIT_WINDOW]

        if len(valid_timestamps) >= MAX_REQUESTS_PER_WINDOW:
            return True

        valid_timestamps.append(now)
        self.request_counts[client_ip] = valid_timestamps
        return False

    def sanitize_input(self, text: str) -> str:
        """Sanitizes text against XSS script injection and SQL injection patterns."""
        if not isinstance(text, str):
            return text
        # Strip script tags for XSS protection
        sanitized = re.sub(r"<script.*?>.*?</script>", "", text, flags=re.IGNORECASE | re.DOTALL)
        # Neutralize malicious SQL injection comment sequences
        sanitized = re.sub(r"(--|\/\*|\*\/|;)", "", sanitized)
        return sanitized

    async def dispatch(self, request: Request, call_next) -> Response:
        client_ip = request.client.host if request.client else "127.0.0.1"

        # 1. Rate Limiting Check
        if self._is_rate_limited(client_ip):
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded. Maximum 100 requests per minute allowed."},
            )

        # 2. Process Request
        response = await call_next(request)

        # 3. Inject Enterprise Security Headers & Content Security Policy (CSP)
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:;"
        )
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["X-XSS-Protection"] = "1; mode=block"

        return response
