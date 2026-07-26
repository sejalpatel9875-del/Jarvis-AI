"""
Unit tests for StepExecutor tool timeout enforcement.
"""

import unittest
import time
from tools.base import BaseTool, ToolResult
from tools.registry import register_tool, tool_registry
from agents.executor import StepExecutor
from agents.state import PlanStep

@register_tool
class SlowTool(BaseTool):
    @property
    def name(self) -> str:
        return "slow_tool"

    @property
    def description(self) -> str:
        return "Simulates a slow hanging tool for timeout testing."

    @property
    def timeout(self) -> float:
        return 0.2  # 200ms timeout for test

    def execute(self, **kwargs) -> ToolResult:
        time.sleep(1.0)  # Sleep longer than 0.2s timeout
        return ToolResult(success=True, result="Completed slow task")

class TestExecutorTimeout(unittest.TestCase):
    def test_tool_timeout_enforcement(self):
        """Verify StepExecutor times out hanging tools after timeout property."""
        executor = StepExecutor(max_retries=0)
        step = PlanStep(
            step_number=1,
            description="Test slow tool timeout",
            capability="slow_capability",
            tool_name="slow_tool"
        )
        res = executor.execute_step(step, completed_step_ids=[])
        self.assertFalse(res.success)
        self.assertIn("timed out", res.result)

if __name__ == "__main__":
    unittest.main()
