"""
Purpose:
Centralized System Configuration Management for Jarvis AI OS (Sprint v4.1).

Responsibilities:
- Load environment configuration (DATABASE_URL, REDIS_URL, API keys)
- Manage environment profiles (development, staging, production)
- Provide global settings access singleton

Dependencies:
- os, typing
"""

import os
from typing import Optional

class SystemSettings:
    """Centralized System Configuration Settings."""

    def __init__(self):
        self.app_name: str = "J.A.R.V.I.S. AI OS"
        self.environment: str = os.getenv("JARVIS_ENV", "development").lower()
        
        # Database & Cache URIs
        self.database_url: str = os.getenv("DATABASE_URL", "")
        self.redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        
        # API Keys
        self.groq_api_key: str = os.getenv("GROQ_API_KEY", "")
        self.gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
        self.master_api_key: str = os.getenv("JARVIS_API_KEY", "")
        
        # System Limits
        self.max_tool_timeout: float = float(os.getenv("TOOL_TIMEOUT", "10.0"))
        self.log_level: str = os.getenv("LOG_LEVEL", "INFO").upper()

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @property
    def is_postgres_enabled(self) -> bool:
        return bool(self.database_url and "postgres" in self.database_url.lower())

# Global Settings Singleton
settings = SystemSettings()
