"""
tests/test_v5_6_mcp_integration.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Comprehensive Unittest Suite for JARVIS Model Context Protocol (MCP v5.6.0) Integration.
"""

import unittest
from mcp.models import MCPClientConfig, MCPCapability, MCPTool, MCPResponse
from mcp.client import MCPClient
from mcp.manager import mcp_manager
from tools.registry import tool_registry
from tools.base import BaseTool, ToolResult


class TestV56MCPIntegration(unittest.TestCase):
    def test_mcp_models_and_serialization(self):
        cfg = MCPClientConfig(
            name="github_mcp",
            transport="http",
            url="http://localhost:8080/mcp",
            auth_token="secret_token",
        )
        self.assertTrue(cfg.to_dict()["has_auth"])
        self.assertEqual(cfg.name, "github_mcp")

        tool = MCPTool(
            name="search_repos",
            description="Search GitHub Repositories",
            input_schema={"type": "object"},
            server_name="github_mcp",
        )
        self.assertEqual(tool.qualified_name, "mcp_github_mcp_search_repos")

        resp = MCPResponse(success=True, result={"repos": ["jarvis-ai"]})
        self.assertTrue(resp.to_dict()["success"])

    def test_mcp_client_connection_and_discovery(self):
        cfg = MCPClientConfig(name="test_server", transport="stdio")
        client = MCPClient(cfg)
        connected = client.connect()
        self.assertTrue(connected)
        self.assertGreaterEqual(len(client.discovered_tools), 1)

    def test_multi_server_mcp_manager(self):
        cfg1 = MCPClientConfig(name="server_alpha", transport="stdio")
        cfg2 = MCPClientConfig(name="server_beta", transport="stdio")

        self.assertTrue(mcp_manager.add_server(cfg1))
        self.assertTrue(mcp_manager.add_server(cfg2))

        statuses = mcp_manager.get_server_statuses()
        self.assertGreaterEqual(len(statuses), 2)

        all_tools = mcp_manager.discover_all_tools()
        self.assertGreaterEqual(len(all_tools), 2)

    def test_automated_fallback_engine(self):
        class NativeCalcTool(BaseTool):
            @property
            def name(self) -> str:
                return "native_calculator"

            @property
            def description(self) -> str:
                return "Internal Calculator"

            def execute(self, **kwargs) -> ToolResult:
                return ToolResult(success=True, result="Calculator Result: 52")

        tool_registry.register(NativeCalcTool())

        # Simulate execution on non-existent MCP server -> triggers fallback to native_calculator
        fallback_res = mcp_manager.execute_tool_with_fallback(
            server_name="offline_server",
            tool_name="remote_calc",
            arguments={"x": 10},
            fallback_internal_tool="native_calculator",
        )

        self.assertTrue(fallback_res.success)
        self.assertIn("native_calculator", fallback_res.result["fallback_used"])


if __name__ == "__main__":
    unittest.main()
