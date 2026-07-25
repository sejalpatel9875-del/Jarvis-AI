"""
Purpose:
Abstract Interfaces and Protocols for Jarvis Core Services.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict

class IService(ABC):
    """Abstract interface for all Jarvis Services."""
    
    @abstractmethod
    def ask(self, prompt: str, **kwargs) -> Any:
        pass
