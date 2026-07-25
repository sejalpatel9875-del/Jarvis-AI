"""
Unit tests for ResultValidator, Goal Verification, and Re-Plan Recommendation Logic.
"""

import unittest
from agents.state import PlanModel, PlanStep, StepStatus, Capability
from agents.validator import ResultValidator, ValidationResult

class TestResultValidator(unittest.TestCase):
    def setUp(self):
        self.validator = ResultValidator()

    def test_full_approval_validation(self):
        """Verify that a fully successful plan receives APPROVE recommendation."""
        step1 = PlanStep(step_number=1, description="Math calculation", capability=Capability.MATH, status=StepStatus.SUCCESS)
        plan = PlanModel(goal="Calculate math", steps=[step1])
        
        res = self.validator.validate_plan(plan)
        self.assertTrue(res.is_valid)
        self.assertEqual(res.completion_rate, 1.0)
        self.assertEqual(res.recommendation, "APPROVE")

    def test_partial_success_validation(self):
        """Verify that a 50% completed plan receives PARTIAL_SUCCESS recommendation."""
        step1 = PlanStep(step_number=1, description="Search Google", capability=Capability.WEB_SEARCH, status=StepStatus.SUCCESS)
        step2 = PlanStep(step_number=2, description="Scrape Webpage", capability=Capability.WEB_SCRAPE, status=StepStatus.FAILED, error="Timeout")
        plan = PlanModel(goal="Search & Scrape", steps=[step1, step2])
        
        res = self.validator.validate_plan(plan)
        self.assertFalse(res.is_valid)
        self.assertEqual(res.completion_rate, 0.5)
        self.assertEqual(res.recommendation, "PARTIAL_SUCCESS")
        self.assertTrue(len(res.missing_requirements) > 0)

    def test_replan_recommendation_on_failure(self):
        """Verify that a failed plan receives RE_PLAN recommendation."""
        step1 = PlanStep(step_number=1, description="Step 1", capability=Capability.MATH, status=StepStatus.FAILED, error="Failed")
        step2 = PlanStep(step_number=2, description="Step 2", capability=Capability.WEB_SEARCH, status=StepStatus.FAILED, error="Failed")
        plan = PlanModel(goal="Failed goal", steps=[step1, step2])
        
        res = self.validator.validate_plan(plan)
        self.assertFalse(res.is_valid)
        self.assertEqual(res.completion_rate, 0.0)
        self.assertEqual(res.recommendation, "RE_PLAN")

if __name__ == "__main__":
    unittest.main()
