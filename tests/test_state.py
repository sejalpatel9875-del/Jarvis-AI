"""
Unit tests for Planner State Machine, PlanStep, and PlanModel.
"""

import unittest
from agents.state import PlanModel, PlanStep, StepStatus, PlanStatus, Capability

class TestPlannerState(unittest.TestCase):
    def test_step_dependency_ready_check(self):
        """Verify that step is_ready returns True only when depends_on steps are completed."""
        step1 = PlanStep(step_number=1, description="Search Google", capability=Capability.WEB_SEARCH)
        step2 = PlanStep(step_number=2, description="Scrape Webpage", capability=Capability.WEB_SCRAPE, depends_on=[1])

        self.assertTrue(step1.is_ready(completed_step_numbers=[]))
        self.assertFalse(step2.is_ready(completed_step_numbers=[]))
        self.assertTrue(step2.is_ready(completed_step_numbers=[1]))

    def test_plan_model_completion(self):
        """Verify PlanModel completion status and step ID tracking."""
        step1 = PlanStep(step_number=1, description="Calculate math", capability=Capability.MATH, status=StepStatus.SUCCESS)
        step2 = PlanStep(step_number=2, description="Search features", capability=Capability.WEB_SEARCH, status=StepStatus.SUCCESS)

        plan = PlanModel(goal="Test Goal", steps=[step1, step2])
        self.assertTrue(plan.is_complete())
        self.assertEqual(plan.get_completed_step_ids(), [1, 2])

    def test_incomplete_plan(self):
        """Verify incomplete plan detection when a step is pending."""
        step1 = PlanStep(step_number=1, description="Step 1", capability=Capability.MATH, status=StepStatus.SUCCESS)
        step2 = PlanStep(step_number=2, description="Step 2", capability=Capability.WEB_SEARCH, status=StepStatus.PENDING)

        plan = PlanModel(goal="Incomplete Goal", steps=[step1, step2])
        self.assertFalse(plan.is_complete())
        self.assertEqual(plan.get_completed_step_ids(), [1])

if __name__ == "__main__":
    unittest.main()
