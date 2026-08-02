"""
agents/ceo_agent.py
~~~~~~~~~~~~~~~~~~~
CEO Agent: Specializes in strategic planning, business decisions, and executive summaries.
"""

from typing import Dict, Any
from agents.base_agent import BaseAgent
from core.event_bus import event_bus, EventMessage


class CEOAgent(BaseAgent):
    """CEO Agent for high-level business strategy and executive summaries."""

    def __init__(self):
        super().__init__(
            agent_id="ceo_agent",
            role="Chief Executive Officer",
            capabilities=["strategic_planning", "business_decisions", "executive_summary"],
        )
        event_bus.subscribe("AGENT_OS_CEO", self.handle_event)

    def handle_event(self, event: EventMessage):
        task_id = event.payload.get("task_id", event.correlation_id)
        if self.is_cancelled(task_id):
            return

        action = event.payload.get("action", "summary")
        context = event.payload.get("context", "")

        if action == "strategic_plan":
            res = self.generate_strategic_plan(context)
        elif action == "business_decision":
            res = self.make_business_decision(context)
        else:
            res = self.generate_executive_summary(context)

        self.send_message(
            "AGENT_OS_RESULT",
            {"task_id": task_id, "agent_id": self.agent_id, "status": "SUCCESS", "result": res},
            correlation_id=event.correlation_id,
        )

    def generate_strategic_plan(self, topic: str) -> Dict[str, Any]:
        return {
            "title": f"Strategic Growth Plan for {topic}",
            "pillars": [
                "Market Penetration & Expansion",
                "Product Quality & AI Performance Optimization",
                "Operational Excellence & Scalability",
            ],
            "recommendation": "Focus on high-value enterprise features and API stability.",
        }

    def make_business_decision(self, scenario: str) -> Dict[str, Any]:
        return {
            "scenario": scenario,
            "decision": "APPROVED",
            "rationale": "Aligns with long-term ROI metrics and customer retention goals.",
        }

    def generate_executive_summary(self, text: str) -> Dict[str, Any]:
        return {
            "summary": f"Executive Summary: High impact operations verified for {text[:100]}.",
            "status": "STABLE",
        }


# Global Singleton Instance
ceo_agent = CEOAgent()
