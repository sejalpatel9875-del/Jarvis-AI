"""
Unit tests for Multi-Agent Orchestrator Manager.
"""

import unittest
from agents.manager import agent_manager

class TestAgentManager(unittest.TestCase):
    def test_route_research_task(self):
        """Verify AgentManager routes search prompts to ResearchAgent."""
        reply, actions = agent_manager.route_task("search latest AI news online")
        self.assertIn("search", actions)

    def test_route_coder_task(self):
        """Verify AgentManager routes math prompts to CoderAgent."""
        reply, actions = agent_manager.route_task("calculate 25 * 16")
        self.assertIn("calculator", actions)

if __name__ == "__main__":
    unittest.main()
