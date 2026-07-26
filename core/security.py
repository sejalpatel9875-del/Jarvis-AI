"""
Purpose:
Security Subsystem & Prompt Injection Sanitizer for Jarvis AI OS.

Responsibilities:
- Detect and sanitize prompt injection attacks
- Validate API key authentication headers
- Neutralize dangerous script tags and system prompt override attempts

Dependencies:
- re, os, typing
"""

import re
import os
from typing import Tuple

class PromptSanitizer:
    """Prompt Injection & Malicious Script Detector."""

    INJECTION_PATTERNS = [
        r"ignore\s+(?:all\s+)?previous\s+instructions",
        r"system\s+prompt\s+dump",
        r"reveal\s+(?:your\s+)?instructions",
        r"you\s+are\s+now\s+DAN",
        r"jailbreak\s+mode",
        r"<script.*?>.*?</script>",
        r"sudo\s+su",
        r"rm\s+-rf\s+/"
    ]

    @classmethod
    def sanitize(cls, user_text: str) -> Tuple[bool, str]:
        """
        Sanitizes user prompt.
        Returns (is_safe, sanitized_text_or_warning).
        """
        text = user_text.strip()
        text_lower = text.lower()

        for pattern in cls.INJECTION_PATTERNS:
            if re.search(pattern, text_lower):
                return (
                    False,
                    "⚠ SECURITY ALERT: Malicious prompt injection or unauthorized instruction override pattern detected and blocked."
                )

        # Basic HTML tag stripping
        clean_text = re.sub(r'<[^>]*>', '', text)
        return True, clean_text

class APIKeyValidator:
    """API Key Authentication Guard."""

    @staticmethod
    def validate_key(provided_key: str) -> bool:
        """Validates client API key against system environment variable."""
        master_key = os.getenv("JARVIS_API_KEY", "")
        if not master_key:
            return True  # If no API key configured, pass in open dev mode
        return provided_key.strip() == master_key.strip()
