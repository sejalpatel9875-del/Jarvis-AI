"""
Pydantic Data Transfer Objects for System, Metrics, and Health endpoints.
"""

from pydantic import BaseModel
from typing import Dict, List, Any

class HealthResponse(BaseModel):
    status: str
    app_name: str
    version: str
    providers: Dict[str, bool]

class MetricsResponse(BaseModel):
    groq_calls: int
    gemini_calls: int
    ollama_calls: int
    avg_latency: float

class StatusResponse(BaseModel):
    app_name: str
    version: str
    active_tools: List[str]
    system_status: str
