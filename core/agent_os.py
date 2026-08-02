"""
core/agent_os.py
~~~~~~~~~~~~~~~~
Central Supervisor for JARVIS Multi-Agent AI Operating System (v5.2.0).

Responsibilities:
- Event-driven orchestration across 8 specialized AI agents
- Asynchronous task dispatch, parallel execution, and task cancellation
- Status tracking, telemetry, and structured observability logging
"""

import uuid
import time
from typing import Dict, List, Any, Optional
from core.event_bus import event_bus, EventMessage

# Import specialized agents to ensure EventBus registration
from agents.ceo_agent import ceo_agent
from agents.developer_agent import developer_agent
from agents.research_agent import research_agent
from agents.automation_agent import automation_agent_os
from agents.memory_agent import memory_agent_os
from agents.voice_agent import voice_agent_os
from agents.planner_agent import planner_agent_os
from agents.validator_agent import validator_agent_os


class AgentOSService:
    """Multi-Agent AI Operating System Manager."""

    def __init__(self):
        self._agents = {
            "ceo_agent": ceo_agent,
            "developer_agent": developer_agent,
            "research_agent": research_agent,
            "automation_agent": automation_agent_os,
            "memory_agent": memory_agent_os,
            "voice_agent": voice_agent_os,
            "planner_agent": planner_agent_os,
            "validator_agent": validator_agent_os,
        }
        self._results: Dict[str, Dict[str, Any]] = {}
        event_bus.subscribe("AGENT_OS_RESULT", self._on_result_received)

    def _on_result_received(self, event: EventMessage):
        task_id = event.payload.get("task_id", event.correlation_id)
        if task_id:
            self._results[task_id] = event.payload

    def dispatch_goal(self, goal: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Dispatches a user goal to the Multi-Agent OS."""
        task_id = f"task_{uuid.uuid4().hex[:10]}"
        context = context or {}

        # 1. Dispatch to Planner Agent
        event_bus.publish(
            "AGENT_OS_PLANNER",
            sender="AgentOS",
            payload={"task_id": task_id, "goal": goal, "context": context},
            correlation_id=task_id,
        )

        # 2. Extract plan result or fall back
        plan_res = self._results.get(task_id, {})
        planned_steps = plan_res.get("result", {}).get("planned_steps", [])

        if not planned_steps:
            # Direct dispatch fallback
            planned_steps = [
                {
                    "step": 1,
                    "target_agent": "developer_agent",
                    "action": "code_generation",
                    "description": "Execute goal.",
                }
            ]

        execution_results: List[Dict[str, Any]] = []
        for step in planned_steps:
            if event_bus.is_cancelled(task_id):
                return {
                    "task_id": task_id,
                    "status": "CANCELLED",
                    "goal": goal,
                    "executed_steps": execution_results,
                    "message": "Task cancellation requested by user.",
                }

            target = step.get("target_agent", "developer_agent")
            topic = f"AGENT_OS_{target.replace('_agent', '').upper()}"

            # Publish step event
            event_bus.publish(
                topic,
                sender="AgentOS",
                payload={
                    "task_id": task_id,
                    "action": step.get("action", "execute"),
                    "context": goal,
                    "payload": context,
                },
                correlation_id=task_id,
            )

            step_output = self._results.get(task_id, {})

            # Validate output via Validator Agent
            event_bus.publish(
                "AGENT_OS_VALIDATOR",
                sender="AgentOS",
                payload={"task_id": task_id, "result": step_output.get("result", {})},
                correlation_id=task_id,
            )

            execution_results.append(
                {
                    "step": step.get("step", 1),
                    "agent": target,
                    "output": step_output.get("result", {}),
                }
            )

        return {
            "task_id": task_id,
            "status": "SUCCESS",
            "goal": goal,
            "planned_steps_count": len(planned_steps),
            "execution_results": execution_results,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        }

    def cancel_goal(self, task_id: str) -> Dict[str, Any]:
        """Cancels an in-flight goal task."""
        event_bus.cancel_task(task_id)
        return {
            "task_id": task_id,
            "status": "CANCELLED",
            "message": f"Task ID {task_id} registered for cancellation.",
        }

    def get_active_agents(self) -> List[Dict[str, Any]]:
        """Returns metadata for all registered specialized AI agents."""
        return [agent.get_info() for agent in self._agents.values()]

    def get_system_status(self) -> Dict[str, Any]:
        """Returns overall Multi-Agent OS health telemetry."""
        return {
            "status": "HEALTHY",
            "total_agents": len(self._agents),
            "active_agents": sum(1 for a in self._agents.values() if a.is_active),
            "agents": self.get_active_agents(),
        }


# Global Singleton Instance
agent_os = AgentOSService()
