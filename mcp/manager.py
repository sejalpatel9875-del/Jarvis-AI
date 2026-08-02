"""
mcp/manager.py
~~~~~~~~~~~~~~
Multi-Server MCP Manager & Fallback Orchestration Engine for JARVIS AI OS.

Responsibilities:
- Support multiple external MCP servers simultaneously
- Dynamic tool aggregation across all registered servers
- Internal ToolRegistry proxying & integration
- Automated fallback to native tools on external MCP failure or timeout
"""

import time
from typing import Dict, List, Any, Optional
from mcp.models import MCPClientConfig, MCPTool, MCPResponse
from mcp.client import MCPClient
from tools.registry import global_tool_registry


class MCPManager:
    """Orchestrates multiple MCP servers and fallbacks to internal tools."""

    def __init__(self):
        self.clients: Dict[str, MCPClient] = {}
        self.aggregated_tools: Dict[str, MCPTool] = {}

    def add_server(self, config: MCPClientConfig) -> bool:
        """Connects and registers an external MCP server."""
        client = MCPClient(config)
        connected = client.connect()
        self.clients[config.name] = client

        if connected:
            self._register_tools_to_internal_registry(client)

        return connected

    def _register_tools_to_internal_registry(self, client: MCPClient):
        """Registers discovered MCP tools into internal global_tool_registry as proxies."""
        for tool_name, tool in client.discovered_tools.items():
            qualified_name = tool.qualified_name
            self.aggregated_tools[qualified_name] = tool

            # Register proxy function into ToolRegistry
            def make_proxy_handler(srv_name=client.config.name, t_name=tool_name):
                def proxy_handler(**kwargs):
                    res = self.execute_tool(srv_name, t_name, kwargs)
                    if res.success:
                        return str(res.result)
                    else:
                        return f"MCP Tool Execution Error: {res.error}"

                return proxy_handler

            global_tool_registry.register_tool(
                name=qualified_name,
                func=make_proxy_handler(),
                description=f"[MCP External: {client.config.name}] {tool.description}",
            )

    def discover_all_tools(self) -> List[Dict[str, Any]]:
        """Aggregates tools from all active connected MCP servers."""
        all_tools = []
        for srv_name, client in self.clients.items():
            if client.is_connected:
                tools = client.discover_tools()
                for t in tools:
                    all_tools.append(t.to_dict())
        return all_tools

    def execute_tool(
        self, server_name: str, tool_name: str, arguments: Dict[str, Any]
    ) -> MCPResponse:
        """Executes a tool on a specific external MCP server."""
        if server_name not in self.clients:
            return MCPResponse(success=False, error=f"MCP Server '{server_name}' not registered.")

        client = self.clients[server_name]
        return client.execute_tool(tool_name, arguments)

    def execute_tool_with_fallback(
        self,
        server_name: str,
        tool_name: str,
        arguments: Dict[str, Any],
        fallback_internal_tool: Optional[str] = None,
    ) -> MCPResponse:
        """Executes MCP tool with automatic fallback to internal native tool if external call fails."""
        res = self.execute_tool(server_name, tool_name, arguments)

        if not res.success and fallback_internal_tool:
            print(
                f"[MCP Fallback Alert] External MCP Tool '{tool_name}' failed ({res.error}). Falling back to internal tool '{fallback_internal_tool}'..."
            )
            start_time = time.time()
            try:
                internal_output = global_tool_registry.execute_tool(
                    fallback_internal_tool, **arguments
                )
                duration_ms = round((time.time() - start_time) * 1000, 2)
                return MCPResponse(
                    success=True,
                    result={
                        "fallback_used": fallback_internal_tool,
                        "output": str(
                            internal_output.result
                            if hasattr(internal_output, "result")
                            else internal_output
                        ),
                    },
                    duration_ms=duration_ms,
                )
            except Exception as ex:
                duration_ms = round((time.time() - start_time) * 1000, 2)
                return MCPResponse(
                    success=False,
                    error=f"Both MCP external call and internal fallback '{fallback_internal_tool}' failed: {ex}",
                    duration_ms=duration_ms,
                )

        return res

    def get_server_statuses(self) -> List[Dict[str, Any]]:
        """Returns connection and tool metrics for all registered MCP servers."""
        statuses = []
        for srv_name, client in self.clients.items():
            statuses.append(
                {
                    "name": srv_name,
                    "connected": client.is_connected,
                    "transport": client.config.transport,
                    "url": client.config.url,
                    "tools_count": len(client.discovered_tools),
                }
            )
        return statuses


# Global Singleton Instance
mcp_manager = MCPManager()
