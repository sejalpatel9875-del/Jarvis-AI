"""
agents/memory_agent.py
~~~~~~~~~~~~~~~~~~~~~~
Memory Agent: Specializes in long-term memory management, semantic retrieval, and memory updates.
"""

from typing import Dict, Any
from agents.base_agent import BaseAgent
from core.event_bus import event_bus, EventMessage
from memory.manager import _default_manager


class MemoryAgent(BaseAgent):
    """Memory Agent for semantic retrieval, preference management, and long-term memory facts."""

    def __init__(self):
        super().__init__(
            agent_id="memory_agent",
            role="Long-Term Memory Administrator",
            capabilities=["long_term_memory", "semantic_retrieval", "memory_updates"],
        )
        event_bus.subscribe("AGENT_OS_MEMORY", self.handle_event)

    def handle_event(self, event: EventMessage):
        task_id = event.payload.get("task_id", event.correlation_id)
        if self.is_cancelled(task_id):
            return

        action = event.payload.get("action", "search")
        query = event.payload.get("query", event.payload.get("key", ""))
        value = event.payload.get("value", "")

        if action == "save_fact":
            _default_manager.save_long_term_fact(query, value)
            res = {"status": "saved", "key": query, "value": value}
        elif action == "save_preference":
            _default_manager.save_preference(query, value)
            res = {"status": "preference_saved", "key": query, "value": value}
        else:
            search_res = _default_manager.semantic_search_long_term(query, limit=5)
            res = {"query": query, "matches": search_res}

        self.send_message(
            "AGENT_OS_RESULT",
            {"task_id": task_id, "agent_id": self.agent_id, "status": "SUCCESS", "result": res},
            correlation_id=event.correlation_id,
        )


# Global Singleton Instance
memory_agent_os = MemoryAgent()
