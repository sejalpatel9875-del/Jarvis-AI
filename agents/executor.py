"""
Purpose:
Step Execution Manager & Retry Engine for Jarvis Planner System.

Responsibilities:
- Verify step dependencies before execution
- Resolve tools dynamically from ToolRegistry via capability or tool_name
- Execute steps with automatic retry engine & exponential backoff (max 2 retries)
- Update PlanStep state transitions (RUNNING -> SUCCESS/FAILED)
- Log ExecutionEvent timestamps into step history

Dependencies:
- agents/state.py
- tools/registry.py
- tools/base.py
"""

import time
from typing import List, Optional
from agents.state import PlanModel, PlanStep, StepStatus, PlanStatus, ExecutionEvent
from tools.registry import tool_registry
from tools.base import ToolResult

# Map capabilities to default registered tool names
CAPABILITY_TOOL_MAP = {
    "math": "calculator",
    "web_search": "search",
    "web_scrape": "browser",
    "system_control": "system",
    "music_playback": "music",
    "document_read": "browser"
}

class StepExecutor:
    """
    Decoupled Step Executor & Retry Engine.
    Executes single PlanSteps and PlanModels with strict Single Responsibility Principle.
    """
    def __init__(self, max_retries: int = 2, base_backoff: float = 0.2):
        self.max_retries = max_retries
        self.base_backoff = base_backoff

    def resolve_tool_name(self, step: PlanStep) -> Optional[str]:
        """Resolves registered tool name from tool_name or capability mapping."""
        if step.tool_name and tool_registry.get_tool(step.tool_name):
            return step.tool_name.strip().lower()
            
        mapped = CAPABILITY_TOOL_MAP.get(step.capability.strip().lower())
        if mapped and tool_registry.get_tool(mapped):
            return mapped
            
        return None

    def execute_step(self, step: PlanStep, completed_step_ids: List[int]) -> ToolResult:
        """
        Executes a single PlanStep following strict lifecycle:
        1. Dependency Check
        2. Tool Resolution
        3. Execution & Retry Loop (Exponential Backoff)
        4. State Update & History Event Logging
        """
        # 1. Dependency Check
        if not step.is_ready(completed_step_ids):
            msg = f"Step {step.step_number} skipped: Dependencies {step.depends_on} not satisfied."
            step.status = StepStatus.SKIPPED
            step.error = msg
            step.log_event("SKIPPED", msg)
            return ToolResult(success=False, result=msg)

        # 2. Tool Resolution
        resolved_tool = self.resolve_tool_name(step)
        if not resolved_tool:
            msg = f"No registered tool found for capability '{step.capability}' or name '{step.tool_name}'."
            step.status = StepStatus.FAILED
            step.error = msg
            step.log_event("FAILED", msg)
            return ToolResult(success=False, result=msg)

        step.tool_name = resolved_tool
        step.status = StepStatus.RUNNING
        step.log_event("STARTED", f"Executing tool '{resolved_tool}' with args {step.args}")

        # 3. Execution & Retry Loop
        last_result = None
        for attempt in range(self.max_retries + 1):
            if attempt > 0:
                step.retries = attempt
                step.status = StepStatus.RETRYING
                backoff_time = self.base_backoff * (2 ** (attempt - 1))
                step.log_event("RETRYING", f"Attempt {attempt}/{self.max_retries} after {backoff_time:.2f}s backoff...")
                time.sleep(backoff_time)

            res = tool_registry.execute(resolved_tool, **step.args)
            last_result = res

            if res.success:
                step.status = StepStatus.SUCCESS
                step.result = res.result
                step.error = None
                step.log_event("SUCCESS", f"Step {step.step_number} completed successfully.")
                return res

        # Retries Exhausted
        step.status = StepStatus.FAILED
        step.error = last_result.result if last_result else "Execution retries exhausted."
        step.log_event("FAILED", f"Step {step.step_number} failed after {self.max_retries} retries: {step.error}")
        return last_result or ToolResult(success=False, result=step.error)

    def execute_plan(self, plan: PlanModel) -> PlanModel:
        """
        Sequentially executes all steps in a PlanModel.
        Updates plan status dynamically.
        """
        plan.status = PlanStatus.IN_PROGRESS
        
        for idx, step in enumerate(plan.steps):
            plan.current_step_index = idx
            completed_ids = plan.get_completed_step_ids()
            
            res = self.execute_step(step, completed_ids)
            if not res.success and step.status == StepStatus.FAILED:
                print(f"[Executor Warning] Step {step.step_number} failed: {step.error}")

        if plan.is_complete():
            plan.status = PlanStatus.COMPLETED
        else:
            plan.status = PlanStatus.FAILED

        return plan

# Global Executor Singleton Instance
default_executor = StepExecutor()
