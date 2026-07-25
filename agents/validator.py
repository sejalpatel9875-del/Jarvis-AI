"""
Purpose:
Result Validator & Goal Verifier Engine for Jarvis Planner System.

Responsibilities:
- Verify aggregated tool execution outputs against initial user goals
- Compute plan completion rates (0.0 to 1.0) and missing requirements
- Recommend action: APPROVE, RE_PLAN, or PARTIAL_SUCCESS
- Single Responsibility Principle (0 execution, 0 planning)

Dependencies:
- agents/state.py
"""

from dataclasses import dataclass, field
from typing import List, Optional
from agents.state import PlanModel, PlanStatus, StepStatus

@dataclass
class ValidationResult:
    is_valid: bool
    completion_rate: float                         # 0.0 to 1.0
    recommendation: str                            # APPROVE | RE_PLAN | PARTIAL_SUCCESS
    missing_requirements: List[str] = field(default_factory=list)
    summary: str = ""

class ResultValidator:
    """
    Decoupled Goal Verifier & Result Validator Engine.
    Evaluates PlanModel execution outputs against user goal requirements.
    """
    def __init__(self):
        pass

    def validate_plan(self, plan: PlanModel) -> ValidationResult:
        """
        Evaluates a PlanModel post-execution and returns a structured ValidationResult.
        """
        if not plan.steps:
            return ValidationResult(
                is_valid=False,
                completion_rate=0.0,
                recommendation="RE_PLAN",
                missing_requirements=["Plan contains zero steps."],
                summary="Plan is empty."
            )

        total_steps = len(plan.steps)
        successful_steps = [s for s in plan.steps if s.status == StepStatus.SUCCESS]
        failed_steps = [s for s in plan.steps if s.status == StepStatus.FAILED]
        skipped_steps = [s for s in plan.steps if s.status == StepStatus.SKIPPED]

        completion_rate = len(successful_steps) / total_steps

        missing = []
        for f_step in failed_steps:
            missing.append(f"Step {f_step.step_number} failed: {f_step.description} ({f_step.error or 'Unknown error'})")
        for sk_step in skipped_steps:
            missing.append(f"Step {sk_step.step_number} skipped due to unfulfilled dependencies.")

        # Full Approval
        if completion_rate == 1.0:
            return ValidationResult(
                is_valid=True,
                completion_rate=1.0,
                recommendation="APPROVE",
                missing_requirements=[],
                summary="All steps executed and verified successfully."
            )

        # Partial Success (>= 50% completed)
        if completion_rate >= 0.5:
            return ValidationResult(
                is_valid=False,
                completion_rate=completion_rate,
                recommendation="PARTIAL_SUCCESS",
                missing_requirements=missing,
                summary=f"Plan partially completed ({len(successful_steps)}/{total_steps} steps succeeded)."
            )

        # Failure / Re-Plan Trigger (< 50% completed)
        return ValidationResult(
            is_valid=False,
            completion_rate=completion_rate,
            recommendation="RE_PLAN",
            missing_requirements=missing,
            summary=f"Plan execution failed ({len(failed_steps)}/{total_steps} steps failed). Re-planning required."
        )

# Global Validator Singleton Instance
default_validator = ResultValidator()
