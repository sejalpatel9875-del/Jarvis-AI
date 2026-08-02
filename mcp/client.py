"""
mcp/client.py
~~~~~~~~~~~~~
Single MCP Server Client Interface for JARVIS AI OS.
Handles capability negotiation, authentication, dynamic tool discovery, and tool execution.
"""

import time
import requests
from typing import Dict, List, Any, Optional
from mcp.models import MCPClientConfig, MCPCapability, MCPTool, MCPResponse


class MCPClient:
    """Client for communicating with an individual external MCP server."""

    def __init__(self, config: MCPClientConfig):
        self.config = config
        self.is_connected = False
        self.capabilities = MCPCapability()
        self.discovered_tools: Dict[str, MCPTool] = {}

    def connect(self) -> bool:
        """Performs JSON-RPC handshake and capability negotiation ('initialize')."""
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {"listChanged": True}},
                "clientInfo": {"name": "JARVIS-AI-OS", "version": "5.6.0"},
            },
        }

        try:
            # Simulated / Real HTTP handshake
            if self.config.url.startswith("http"):
                res = requests.post(
                    self.config.url,
                    json=payload,
                    headers=self.config.headers,
                    timeout=self.config.timeout_seconds,
                )
                if res.status_code == 200:
                    self.is_connected = True
            else:
                # Local mock connection fallback for test environments
                self.is_connected = True

            if self.is_connected:
                self.discover_tools()

            return self.is_connected
        except Exception as ex:
            print(f"[MCP Client Error] Connection failed to '{self.config.name}': {ex}")
            self.is_connected = False
            return False

    def discover_tools(self) -> List[MCPTool]:
        """Issues 'tools/list' JSON-RPC request and registers discovered tools."""
        if not self.is_connected:
            return []

        payload = {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}

        tools_found: List[MCPTool] = []

        try:
            if self.config.url.startswith("http"):
                res = requests.post(
                    self.config.url,
                    json=payload,
                    headers=self.config.headers,
                    timeout=self.config.timeout_seconds,
                )
                data = res.json()
                raw_tools = data.get("result", {}).get("tools", [])
                for t in raw_tools:
                    tool_obj = MCPTool(
                        name=t.get("name"),
                        description=t.get("description", ""),
                        input_schema=t.get("inputSchema", {}),
                        server_name=self.config.name,
                    )
                    tools_found.append(tool_obj)
            else:
                # Default dynamic tools provided by external MCP servers
                default_tool = MCPTool(
                    name=f"query_{self.config.name}",
                    description=f"Dynamic tool provided by external MCP server '{self.config.name}'",
                    input_schema={"type": "object", "properties": {"query": {"type": "string"}}},
                    server_name=self.config.name,
                )
                tools_found.append(default_tool)

            self.discovered_tools = {t.name: t for t in tools_found}
            return tools_found

        except Exception as ex:
            print(f"[MCP Client Error] Tool discovery failed for '{self.config.name}': {ex}")
            return []

    def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> MCPResponse:
        """Executes 'tools/call' on the external MCP server with timeout and error handling."""
        start_time = time.time()

        if not self.is_connected:
            return MCPResponse(
                success=False,
                error=f"MCP Server '{self.config.name}' is not connected.",
                duration_ms=round((time.time() - start_time) * 1000, 2),
            )

        payload = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {"name": tool_name, "arguments": arguments},
        }

        try:
            if self.config.url.startswith("http"):
                res = requests.post(
                    self.config.url,
                    json=payload,
                    headers=self.config.headers,
                    timeout=self.config.timeout_seconds,
                )
                duration_ms = round((time.time() - start_time) * 1000, 2)

                if res.status_code == 200:
                    data = res.json()
                    if "error" in data:
                        return MCPResponse(
                            success=False, error=str(data["error"]), duration_ms=duration_ms
                        )
                    return MCPResponse(
                        success=True, result=data.get("result"), duration_ms=duration_ms
                    )
                else:
                    return MCPResponse(
                        success=False,
                        error=f"HTTP {res.status_code}: {res.text}",
                        duration_ms=duration_ms,
                    )
            else:
                # Local mock execution response
                duration_ms = round((time.time() - start_time) * 1000, 2)
                return MCPResponse(
                    success=True,
                    result={
                        "content": f"Executed MCP Tool '{tool_name}' on server '{self.config.name}'",
                        "args": arguments,
                    },
                    duration_ms=duration_ms,
                )
        except requests.Timeout:
            duration_ms = round((time.time() - start_time) * 1000, 2)
            return MCPResponse(
                success=False,
                error=f"MCP Tool '{tool_name}' timed out after {self.config.timeout_seconds}s.",
                duration_ms=duration_ms,
            )
        except Exception as ex:
            duration_ms = round((time.time() - start_time) * 1000, 2)
            return MCPResponse(
                success=False, error=f"MCP Tool execution exception: {ex}", duration_ms=duration_ms
            )
