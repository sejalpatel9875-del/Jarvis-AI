"""
Purpose:
Custom Exception Hierarchy for Jarvis AI OS.
"""

class JarvisException(Exception):
    """Base exception for all Jarvis AI OS errors."""
    pass

class ToolExecutionError(JarvisException):
    """Raised when a registered tool fails to execute cleanly."""
    pass

class PlannerError(JarvisException):
    """Raised when the Planner or Reasoner encounters a planning failure."""
    pass

class MemoryError(JarvisException):
    """Raised when SQLite or In-Memory Cache encounters a storage error."""
    pass

class RouterError(JarvisException):
    """Raised when multi-provider AI model routing fails."""
    pass
