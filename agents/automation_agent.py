"""
agents/automation_agent.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~
Automation Agent: Specializes in workflow step execution, tool orchestration, and scheduling.
"""

from typing import Dict, Any
from agents.base_agent import BaseAgent
from core.event_bus import event_bus, EventMessage
from services.workflow_execution import workflow_execution


class AutomationAgent(BaseAgent):
    """Automation Agent for tool orchestration, workflow execution, and scheduling."""

    def __init__(self):
        super().__init__(
            agent_id="automation_agent",
            role="Automation & Workflow Specialist",
            capabilities=["execute_workflows", "tool_orchestration", "scheduling"],
        )
        event_bus.subscribe("AGENT_OS_AUTOMATION", self.handle_event)

    def handle_event(self, event: EventMessage):
        task_id = event.payload.get("task_id", event.correlation_id)
        if self.is_cancelled(task_id):
            return

        workflow_id = event.payload.get("workflow_id", "adhoc_run")
        payload = event.payload.get("payload", {})

        exec_res = workflow_execution.execute_workflow(workflow_id, payload)

        self.send_message(
            "AGENT_OS_RESULT",
            {
                "task_id": task_id,
                "agent_id": self.agent_id,
                "status": exec_res.get("status", "SUCCESS"),
                "result": exec_res,
            },
            correlation_id=event.correlation_id,
        )


# Global Singleton Instance
automation_agent_os = AutomationAgent()
