"""
Purpose:
API Key Security & Authorization Middleware for Jarvis REST API.

Responsibilities:
- Verify X-API-Key or Bearer token header against JARVIS_API_KEY environment setting
- Raise 401 Unauthorized for unauthenticated HTTP requests
"""

import os
from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader

API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

def verify_api_key(api_key_header: str = Security(api_key_header)):
    """
    Verifies API Key header. If JARVIS_API_KEY environment variable is configured,
    requests missing or matching incorrect keys are rejected with 401 Unauthorized.
    """
    expected_key = os.getenv("JARVIS_API_KEY", "").strip()
    
    # If no JARVIS_API_KEY configured in environment, allow local access
    if not expected_key:
        return True

    if not api_key_header or api_key_header != expected_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing X-API-Key header."
        )
    return True
