"""
Pydantic Data Transfer Objects for Chat endpoints.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Any

class ChatRequest(BaseModel):
    message: str = Field(..., description="User prompt message to Jarvis AI OS", example="Calculate 15% of 800")
    user_id: Optional[str] = Field("Boss", description="Identifier for user session")

class ChatResponse(BaseModel):
    user_message: str
    assistant_reply: str
    provider: str
    latency: float
    status: str = "success"
