"""
Unit tests for StepExecutor Engine, Dependency Check, Retry Engine, and Capability Resolution.
"""

import unittest
from agents.state import PlanModel, PlanStep, StepStatus, PlanStatus, Capability
from agents.executor import StepExecutor
from tools.base import BaseTool, ToolResult
from tools.registry import tool_registry, BaseTool

# Custom Flaky Tool for Retry Testing
class FlakyTool(BaseTool):
    def __init__(self):
        self.attempts = 0

    @property
    def name(self) -> str:
        return "flaky_tool"

    @property
    def description(self) -> str:
        return "Tool that fails on first call and succeeds on second call."

    def execute(self, **kwargs) -> ToolResult:
        self.attempts += 1
        if self.attempts < 2:
            raise RuntimeError("Flaky tool temporary failure!")
        return ToolResult(success=True, result="Flaky tool recovered!")

class TestStepExecutor(unittest.TestCase):
    def setUp(self):
        self.executor = StepExecutor(max_retries=2, base_backoff=0.01)
        self.flaky_tool = FlakyTool()
        tool_registry.register(self.flaky_tool)

    def test_dependency_check_skips_unready_step(self):
        """Verify that step with unfulfilled dependencies is skipped."""
        step2 = PlanStep(step_number=2, description="Step 2", capability=Capability.MATH, depends_on=[1])
        res = self.executor.execute_step(step2, completed_step_ids=[])
        self.assertFalse(res.success)
        self.assertEqual(step2.status, StepStatus.SKIPPED)

    def test_capability_resolution(self):
        """Verify that capability='math' resolves to registered tool 'calculator'."""
        step = PlanStep(step_number=1, description="Calculate 2+2", capability=Capability.MATH, args={"expression": "2+2"})
        res = self.executor.execute_step(step, completed_step_ids=[])
        self.assertTrue(res.success)
        self.assertEqual(step.status, StepStatus.SUCCESS)
        self.assertEqual(step.tool_name, "calculator")

    def test_retry_engine_recovery(self):
        """Verify that executor retries on failure and recovers successfully."""
        step = PlanStep(step_number=1, description="Flaky step", capability="custom", tool_name="flaky_tool")
        res = self.executor.execute_step(step, completed_step_ids=[])
        self.assertTrue(res.success)
        self.assertEqual(step.status, StepStatus.SUCCESS)
        self.assertEqual(step.retries, 1)
        self.assertTrue(len(step.history) > 1)

    def test_plan_execution_loop(self):
        """Verify full sequential plan execution."""
        step1 = PlanStep(step_number=1, description="Step 1 Math", capability=Capability.MATH, args={"expression": "10+5"})
        plan = PlanModel(goal="Test Plan", steps=[step1])
        
        executed_plan = self.executor.execute_plan(plan)
        self.assertEqual(executed_plan.status, PlanStatus.COMPLETED)
        self.assertEqual(step1.status, StepStatus.SUCCESS)

if __name__ == "__main__":
    unittest.main()
