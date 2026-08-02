"""
agents/planner_agent.py
~~~~~~~~~~~~~~~~~~~~~~~
Planner Agent: Specializes in task decomposition and routing work to specialized agents over the Event Bus.
"""

from typing import Dict, List, Any
from agents.base_agent import BaseAgent
from core.event_bus import event_bus, EventMessage


class PlannerAgent(BaseAgent):
    """Planner Agent for task decomposition and agent work assignment."""

    def __init__(self):
        super().__init__(
            agent_id="planner_agent",
            role="Multi-Agent Task Planner",
            capabilities=["task_planning", "agent_assignment", "step_decomposition"],
        )
        event_bus.subscribe("AGENT_OS_PLANNER", self.handle_event)

    def handle_event(self, event: EventMessage):
        task_id = event.payload.get("task_id", event.correlation_id)
        if self.is_cancelled(task_id):
            return

        goal = event.payload.get("goal", event.payload.get("context", ""))
        steps = self.decompose_goal(goal)

        self.send_message(
            "AGENT_OS_RESULT",
            {
                "task_id": task_id,
                "agent_id": self.agent_id,
                "status": "SUCCESS",
                "result": {"goal": goal, "planned_steps": steps},
            },
            correlation_id=event.correlation_id,
        )

    def decompose_goal(self, goal: str) -> List[Dict[str, Any]]:
        goal_lower = goal.lower()
        steps = []

        if "code" in goal_lower or "debug" in goal_lower or "refactor" in goal_lower:
            steps.append(
                {
                    "step": 1,
                    "target_agent": "developer_agent",
                    "action": "code_generation",
                    "description": "Generate or review implementation code.",
                }
            )
        if "research" in goal_lower or "analyze" in goal_lower:
            steps.append(
                {
                    "step": 2,
                    "target_agent": "research_agent",
                    "action": "deep_research",
                    "description": "Synthesize background domain knowledge.",
                }
            )
        if "strategy" in goal_lower or "summary" in goal_lower or "business" in goal_lower:
            steps.append(
                {
                    "step": 3,
                    "target_agent": "ceo_agent",
                    "action": "strategic_plan",
                    "description": "Formulate executive strategy and business plan.",
                }
            )

        if not steps:
            steps.append(
                {
                    "step": 1,
                    "target_agent": "automation_agent",
                    "action": "execute_workflow",
                    "description": "Orchestrate general workflow task.",
                }
            )

        return steps


# Global Singleton Instance
planner_agent_os = PlannerAgent()
