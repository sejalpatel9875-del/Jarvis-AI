"""
mcp/models.py
~~~~~~~~~~~~~
Model Context Protocol Data Structures & Spec Models for JARVIS AI OS.
"""

import time
import uuid
from typing import Dict, List, Any, Optional


class MCPCapability:
    """Represents negotiated MCP capabilities."""

    def __init__(
        self,
        tools: bool = True,
        prompts: bool = False,
        resources: bool = False,
        logging: bool = True,
    ):
        self.tools = tools
        self.prompts = prompts
        self.resources = resources
        self.logging = logging

    def to_dict(self) -> Dict[str, bool]:
        return {
            "tools": self.tools,
            "prompts": self.prompts,
            "resources": self.resources,
            "logging": self.logging,
        }


class MCPClientConfig:
    """Configuration for an external MCP server connection."""

    def __init__(
        self,
        name: str,
        transport: str = "http",  # http, sse, stdio
        url: str = "",
        auth_token: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout_seconds: float = 10.0,
    ):
        self.name = name
        self.transport = transport
        self.url = url
        self.auth_token = auth_token
        self.headers = headers or {}
        self.timeout_seconds = timeout_seconds

        if auth_token:
            self.headers["Authorization"] = f"Bearer {auth_token}"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "transport": self.transport,
            "url": self.url,
            "has_auth": bool(self.auth_token),
            "timeout_seconds": self.timeout_seconds,
        }


class MCPTool:
    """Represents a dynamically discovered tool from an MCP server."""

    def __init__(self, name: str, description: str, input_schema: Dict[str, Any], server_name: str):
        self.name = name
        self.description = description
        self.input_schema = input_schema
        self.server_name = server_name
        self.qualified_name = f"mcp_{server_name}_{name}"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "qualified_name": self.qualified_name,
            "description": self.description,
            "input_schema": self.input_schema,
            "server_name": self.server_name,
        }


class MCPResponse:
    """Standardized JSON-RPC response wrapper for MCP execution."""

    def __init__(
        self,
        success: bool = True,
        result: Optional[Any] = None,
        error: Optional[str] = None,
        duration_ms: float = 0.0,
        request_id: Optional[str] = None,
    ):
        self.success = success
        self.result = result
        self.error = error
        self.duration_ms = duration_ms
        self.request_id = request_id or f"mcp_req_{uuid.uuid4().hex[:8]}"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "result": self.result,
            "error": self.error,
            "duration_ms": self.duration_ms,
            "request_id": self.request_id,
        }
