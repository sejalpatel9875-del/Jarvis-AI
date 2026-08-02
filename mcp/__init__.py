"""
mcp Package
~~~~~~~~~~~
Model Context Protocol (MCP v5.6.0) Engine for JARVIS AI OS.
"""

from mcp.models import MCPClientConfig, MCPCapability, MCPTool, MCPResponse
from mcp.client import MCPClient
from mcp.manager import mcp_manager

__all__ = [
    "MCPClientConfig",
    "MCPCapability",
    "MCPTool",
    "MCPResponse",
    "MCPClient",
    "mcp_manager"
]
