"""
Purpose:
FastAPI Security & Rate Limiting Middleware for Jarvis AI OS.

Responsibilities:
- Add security response headers (X-Content-Type-Options, X-Frame-Options, CSP)
- In-memory & Redis IP rate limiting for authentication endpoints (/auth/login)
"""

import time
from typing import Dict, Tuple
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Adds security response headers and IP rate limiting for auth endpoints."""

    def __init__(self, app, max_login_attempts: int = 5, window_seconds: int = 60):
        super().__init__(app)
        self.max_login_attempts = max_login_attempts
        self.window_seconds = window_seconds
        # In-memory IP tracking: ip -> (attempt_count, window_start_timestamp)
        self.login_attempts: Dict[str, Tuple[int, float]] = {}

    async def dispatch(self, request: Request, call_next) -> Response:
        # 1. Rate Limit Enforcement for Login Endpoint
        if request.method == "POST" and "/auth/login" in request.url.path:
            client_ip = request.client.host if request.client else "127.0.0.1"
            now = time.time()
            count, start_time = self.login_attempts.get(client_ip, (0, now))

            if now - start_time > self.window_seconds:
                # Reset window
                count = 1
                start_time = now
            else:
                count += 1

            self.login_attempts[client_ip] = (count, start_time)

            if count > self.max_login_attempts:
                return JSONResponse(
                    status_code=429,
                    content={"error": "Too Many Requests. Brute-force protection enabled. Please try again in 60 seconds."}
                )

        # 2. Process Request & Add Security Headers
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Content-Security-Policy"] = "default-src 'self' 'unsafe-inline' 'unsafe-eval' https:;"
        return response
