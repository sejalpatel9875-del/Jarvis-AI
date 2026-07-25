"""
Purpose:
Environment & Configuration Validator for Jarvis AI OS.

Responsibilities:
- Verify mandatory and optional .env configuration keys
- Warn cleanly if Cloud API keys are missing without crashing startup

Dependencies:
- config.py
"""

import config

def validate_environment() -> dict:
    """Validates presence of key configuration variables."""
    status = {
        "groq_configured": bool(getattr(config, "GROQ_API_KEY", "") and getattr(config, "GROQ_API_KEY", "") != "your_groq_api_key_here"),
        "gemini_configured": bool(getattr(config, "GEMINI_API_KEY", "") and getattr(config, "GEMINI_API_KEY", "") != "your_gemini_api_key_here"),
        "ollama_configured": True,  # Fallback local engine
    }

    if not status["groq_configured"] and not status["gemini_configured"]:
        print("[Env Warning] Neither GROQ_API_KEY nor GEMINI_API_KEY found in .env! Jarvis will fallback to Local Ollama AI.")

    return status
