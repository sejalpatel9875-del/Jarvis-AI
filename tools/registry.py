"""
Purpose:
Central Tool Registry & Dispatcher for Jarvis.

Responsibilities:
- Register, discover, and list available system tools
- Execute tools in a safe, decoupled manner
- Enforce standard ToolResult response

Dependencies:
- tools/base.py
"""

import threading
from typing import Dict, List, Type
from tools.base import BaseTool, ToolResult

class ToolRegistry:
    """Thread-safe Central Tool Registry for Jarvis."""
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(ToolRegistry, cls).__new__(cls)
                cls._instance._registry: Dict[str, BaseTool] = {}
            return cls._instance

    def register(self, tool: BaseTool):
        """Registers a tool instance in the registry."""
        with self._lock:
            tool_name = tool.name.strip().lower()
            self._registry[tool_name] = tool
            print(f"[Tool Registry] Registered tool: '{tool_name}' ({tool.description})")

    def get_tool(self, name: str) -> BaseTool:
        """Retrieves a registered tool by name."""
        with self._lock:
            return self._registry.get(name.strip().lower())

    def list_tools(self) -> List[dict]:
        """Lists all registered tools."""
        with self._lock:
            return [
                {"name": tool.name, "description": tool.description}
                for tool in self._registry.values()
            ]

    def execute(self, name: str, **kwargs) -> ToolResult:
        """Executes a registered tool by name."""
        tool = self.get_tool(name)
        if not tool:
            return ToolResult(
                success=False,
                result=f"Tool '{name}' is not registered in Jarvis Tool Registry."
            )
        try:
            return tool.execute(**kwargs)
        except Exception as e:
            return ToolResult(
                success=False,
                result=f"Execution error in tool '{name}': {e}"
            )

# Global Tool Registry Singleton
tool_registry = ToolRegistry()

def register_tool(tool_cls: Type[BaseTool]):
    """Decorator to register a tool class into global ToolRegistry."""
    tool_instance = tool_cls()
    tool_registry.register(tool_instance)
    return tool_cls
