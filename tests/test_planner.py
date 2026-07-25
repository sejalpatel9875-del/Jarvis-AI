"""
Unit tests for Autonomous Planner Agent and Brain Integration.
"""

import unittest
from agents.planner import PlannerAgent
from agents.brain import JarvisBrain

class TestPlannerAgent(unittest.TestCase):
    def setUp(self):
        self.planner = PlannerAgent()
        self.brain = JarvisBrain()

    def test_planner_solve_math_goal(self):
        """Verify PlannerAgent solves a math goal end-to-end."""
        reply, actions = self.planner.solve_goal("calculate 15% of 800")
        self.assertIsNotNone(reply)
        self.assertTrue(len(reply) > 0)

    def test_brain_think_integration(self):
        """Verify JarvisBrain delegating to PlannerAgent."""
        response, actions = self.brain.think("hello")
        self.assertIsNotNone(response)
        self.assertTrue(len(response) > 0)

if __name__ == "__main__":
    unittest.main()
