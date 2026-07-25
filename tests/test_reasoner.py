"""
Unit tests for Reasoner Engine, Capability Abstracted Planning, and Multi-Step Dependency Generation.
"""

import unittest
from agents.state import PlanModel, Capability
from agents.reasoner import ReasonerEngine

class TestReasonerEngine(unittest.TestCase):
    def setUp(self):
        self.reasoner = ReasonerEngine()

    def test_casual_query_fast_path(self):
        """Verify that casual queries produce a fast 1-step plan."""
        plan = self.reasoner.generate_plan("hello")
        self.assertIsInstance(plan, PlanModel)
        self.assertEqual(len(plan.steps), 1)
        self.assertEqual(plan.steps[0].capability, "llm_casual")

    def test_math_capability_plan(self):
        """Verify that math queries produce a plan using Capability.MATH."""
        plan = self.reasoner.generate_plan("calculate 15% of 800")
        self.assertEqual(len(plan.steps), 1)
        self.assertEqual(plan.steps[0].capability, Capability.MATH.value)

    def test_multi_step_dependency_plan(self):
        """Verify that search + summarize query generates multi-step plan with depends_on=[1]."""
        plan = self.reasoner.generate_plan("search Python 3.14 features and summarize points")
        self.assertTrue(len(plan.steps) >= 2)
        self.assertEqual(plan.steps[0].capability, Capability.WEB_SEARCH.value)
        self.assertEqual(plan.steps[1].capability, Capability.WEB_SCRAPE.value)
        self.assertEqual(plan.steps[1].depends_on, [1])

    def test_capability_discovery(self):
        """Verify that Reasoner retrieves active capabilities from ToolRegistry."""
        caps = self.reasoner.get_available_capabilities()
        self.assertIn(Capability.MATH.value, caps)
        self.assertIn(Capability.WEB_SEARCH.value, caps)

if __name__ == "__main__":
    unittest.main()
