"""
Purpose:
Multi-Agent Orchestrator Manager for Jarvis AI OS (Sprint v2.0).

Architecture:
- ResearchAgent: Specialized in web search, browsing, and document retrieval
- CoderAgent: Specialized in Python code execution, calculation, and script diagnosis
- AgentManager: Central orchestrator routing prompts to specialized subagents
"""

from typing import Dict, Any, Tuple
from agents.planner import PlannerAgent
from tools.registry import tool_registry
from services.logger import logger

class ResearchAgent:
    """Specialized Subagent for Web & Document Research Tasks."""

    def execute_research(self, topic: str) -> str:
        logger.info("RESEARCH_AGENT", f"Executing deep research on '{topic}'")
        res = tool_registry.execute("search", query=topic)
        return res.result if res.success else f"Research failed for '{topic}'."

class CoderAgent:
    """Specialized Subagent for Code & Logic Tasks."""

    def solve_problem(self, expression_or_code: str) -> str:
        logger.info("CODER_AGENT", f"Evaluating problem '{expression_or_code}'")
        res = tool_registry.execute("calculator", expression=expression_or_code)
        return res.result if res.success else f"Coder evaluation error for '{expression_or_code}'."

class AgentManager:
    """Central Multi-Agent Orchestrator Routing Tasks to Subagents."""

    def __init__(self):
        self.planner = PlannerAgent()
        self.researcher = ResearchAgent()
        self.coder = CoderAgent()

    def route_task(self, user_prompt: str, memory_context: str = "") -> Tuple[str, list]:
        prompt_lower = user_prompt.lower().strip()

        # 1. Route to Research Agent
        if any(k in prompt_lower for k in ["search", "find online", "lookup", "google", "latest news"]):
            logger.info("AGENT_MANAGER", "Routing prompt to ResearchAgent")
            res = self.researcher.execute_research(user_prompt)
            return res, ["search"]

        # 2. Route to Coder Agent
        elif any(k in prompt_lower for k in ["calculate", "math", "evaluate"]):
            logger.info("AGENT_MANAGER", "Routing prompt to CoderAgent")
            res = self.coder.solve_problem(user_prompt)
            return res, ["calculator"]

        # 3. Default to Autonomous Planner Agent
        else:
            logger.info("AGENT_MANAGER", "Routing prompt to PlannerAgent")
            return self.planner.solve_goal(user_prompt, memory_context=memory_context)

# Global AgentManager Singleton
agent_manager = AgentManager()
