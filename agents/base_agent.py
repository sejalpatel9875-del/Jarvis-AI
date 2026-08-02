"""
agents/base_agent.py
~~~~~~~~~~~~~~~~~~~~
Abstract Base Class for specialized AI Agents in JARVIS Multi-Agent AI OS.
"""

from typing import Dict, List, Any, Optional
from core.event_bus import event_bus, EventMessage


class BaseAgent:
    """Base abstract agent contract for JARVIS AI OS."""

    def __init__(self, agent_id: str, role: str, capabilities: List[str]):
        self.agent_id = agent_id
        self.role = role
        self.capabilities = capabilities
        self.is_active = True

    def handle_event(self, event: EventMessage):
        """Must be implemented by subclasses to process subscribed events."""
        raise NotImplementedError("Subclasses must implement handle_event()")

    def send_message(
        self, topic: str, payload: Dict[str, Any], correlation_id: Optional[str] = None
    ) -> EventMessage:
        """Sends an event message to the Event Bus."""
        return event_bus.publish(
            topic, sender=self.agent_id, payload=payload, correlation_id=correlation_id
        )

    def cancel_task(self, task_id: str):
        """Marks a task ID for cancellation."""
        event_bus.cancel_task(task_id)

    def is_cancelled(self, task_id: str) -> bool:
        """Checks if a task ID is marked cancelled."""
        return event_bus.is_cancelled(task_id)

    def get_info(self) -> Dict[str, Any]:
        """Returns agent metadata."""
        return {
            "agent_id": self.agent_id,
            "role": self.role,
            "capabilities": self.capabilities,
            "is_active": self.is_active,
        }
