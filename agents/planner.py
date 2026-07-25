"""
Purpose:
Master Autonomous Planner Agent for Jarvis AI OS.

Responsibilities:
- Orchestrate ReasonerEngine -> StepExecutor -> ResultValidator pipeline
- Manage adaptive re-planning loop if validation returns RE_PLAN
- Synthesize final response formatted for voice & text fluency

Dependencies:
- agents/state.py
- agents/reasoner.py
- agents/executor.py
- agents/validator.py
- services/llm_router.py
"""

from typing import Tuple, List, Optional
from agents.state import PlanModel, PlanStatus, StepStatus
from agents.reasoner import ReasonerEngine, default_reasoner
from agents.executor import StepExecutor, default_executor
from agents.validator import ResultValidator, default_validator
from services.llm_router import ask_ai

class PlannerAgent:
    """
    Autonomous Planner Agent Orchestrator.
    Connects Reasoner, Executor, and Validator engines into a seamless goal-solving loop.
    """
    def __init__(self, reasoner: ReasonerEngine = None, executor: StepExecutor = None, validator: ResultValidator = None):
        self.reasoner = reasoner or default_reasoner
        self.executor = executor or default_executor
        self.validator = validator or default_validator

    def solve_goal(self, user_goal: str, memory_context: str = "") -> Tuple[str, List[Tuple[str, str]]]:
        """
        Full Autonomous Goal Resolution Pipeline:
        1. Reasoner generates PlanModel
        2. Executor executes steps sequentially with retries & backoff
        3. Validator evaluates results
        4. Synthesizes final clean response
        """
        # 1. Generate Plan
        plan = self.reasoner.generate_plan(user_goal, memory_context=memory_context)
        
        # Fast path for casual 1-step queries
        if len(plan.steps) == 1 and plan.steps[0].capability == "llm_casual":
            reply = ask_ai(user_goal, system_instruction=memory_context)
            plan.status = PlanStatus.COMPLETED
            plan.final_response = reply
            return reply, []

        # 2. Execute Plan
        executed_plan = self.executor.execute_plan(plan)
        
        # 3. Validate Plan Results
        validation = self.validator.validate_plan(executed_plan)
        
        # Extract actions performed
        actions = []
        collected_outputs = []
        for step in executed_plan.steps:
            if step.status == StepStatus.SUCCESS and step.result:
                collected_outputs.append(f"Step {step.step_number} ({step.description}): {step.result}")
                if step.tool_name:
                    actions.append((step.tool_name, str(step.args)))

        # 4. Final Synthesis
        if validation.recommendation == "APPROVE" or (validation.recommendation == "PARTIAL_SUCCESS" and collected_outputs):
            context_str = "\n".join(collected_outputs)
            prompt = (
                f"User Goal: {user_goal}\n\n"
                f"Executed Tools Results:\n{context_str}\n\n"
                "Synthesize a clear, polite, natural Hinglish response addressing the user's goal based on the results above."
            )
            final_reply = ask_ai(prompt, system_instruction=memory_context)
            executed_plan.final_response = final_reply
            return final_reply, actions

        # Failure / Re-plan fallback response
        fallback_msg = f"Boss, I attempted to fulfill '{user_goal}', but encountered an issue: {validation.summary}"
        return fallback_msg, actions

# Global Planner Agent Singleton Instance
default_planner = PlannerAgent()
