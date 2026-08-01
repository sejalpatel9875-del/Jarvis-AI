"""
Purpose:
Abstract Base Tool Class for all Jarvis Tools.

Responsibilities:
- Enforce standard execute(args) interface
- Define tool name, description, timeout, and metadata

Dependencies:
- None
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict

@dataclass
class ToolResult:
    success: bool
    result: str
    metadata: Dict[str, Any] = field(default_factory=dict)

class BaseTool(ABC):
    """Abstract Base Class for all Jarvis Tools."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Unique name identifier of the tool."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Human-readable description of what the tool does."""
        pass

    @property
    def timeout(self) -> float:
        """Execution timeout in seconds. Defaults to 10.0s."""
        return 10.0

    @abstractmethod
    def execute(self, **kwargs) -> ToolResult:
        """Executes the tool with keyword arguments."""
        pass

    def validate(self, result: ToolResult) -> bool:
        """Validates the execution results of this tool."""
        return result.success

    def rollback(self, **kwargs) -> ToolResult:
        """Compensates/rolls back side-effects of this tool execution."""
        return ToolResult(success=True, result=f"No rollback required for '{self.name}'.")

    def status(self) -> str:
        """Returns the current operational status of the tool."""
        return "ACTIVE"
