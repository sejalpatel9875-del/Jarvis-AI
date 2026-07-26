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
