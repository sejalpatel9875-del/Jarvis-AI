"""
tests/test_v5_2_multi_agent_os.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Comprehensive Unittest Suite for JARVIS Multi-Agent AI OS (v5.2.0).
"""

import unittest
from core.event_bus import event_bus, EventMessage
from core.agent_os import agent_os
from agents.ceo_agent import ceo_agent
from agents.developer_agent import developer_agent
from agents.research_agent import research_agent
from agents.automation_agent import automation_agent_os
from agents.memory_agent import memory_agent_os
from agents.voice_agent import voice_agent_os
from agents.planner_agent import planner_agent_os
from agents.validator_agent import validator_agent_os


class TestV52MultiAgentOS(unittest.TestCase):
    def test_event_bus_pub_sub(self):
        received = []

        def test_handler(msg: EventMessage):
            received.append(msg.payload.get("data"))

        event_bus.subscribe("TEST_TOPIC", test_handler)
        event_bus.publish("TEST_TOPIC", sender="test", payload={"data": "hello_event_bus"})
        event_bus.unsubscribe("TEST_TOPIC", test_handler)

        self.assertEqual(len(received), 1)
        self.assertEqual(received[0], "hello_event_bus")

    def test_registered_agents_count(self):
        status = agent_os.get_system_status()
        self.assertEqual(status["status"], "HEALTHY")
        self.assertEqual(status["total_agents"], 8)
        self.assertEqual(status["active_agents"], 8)

    def test_ceo_agent(self):
        plan = ceo_agent.generate_strategic_plan("Market Expansion")
        self.assertIn("pillars", plan)
        summary = ceo_agent.generate_executive_summary("Q3 Financials")
        self.assertIn("Executive Summary", summary["summary"])

    def test_developer_agent(self):
        code_res = developer_agent.generate_code("Create user auth endpoint")
        self.assertIn("def execute_task", code_res["code"])
        debug_res = developer_agent.debug_code("NullPointerException")
        self.assertIn("root_cause", debug_res)

    def test_research_agent(self):
        res = research_agent.conduct_deep_research("Multi-Agent Systems")
        self.assertGreaterEqual(res["confidence_score"], 0.9)

    def test_voice_agent_lang_detection(self):
        lang = voice_agent_os.detect_language("Namaste boss, kya haal hai?")
        self.assertEqual(lang, "hinglish")

    def test_planner_agent_decomposition(self):
        steps = planner_agent_os.decompose_goal("Research strategy and write code for AI pipeline")
        self.assertGreaterEqual(len(steps), 2)

    def test_validator_agent(self):
        valid_res = validator_agent_os.validate_result({"success": True, "output": "ok"})
        self.assertTrue(valid_res["is_valid"])
        invalid_res = validator_agent_os.validate_result(None)
        self.assertFalse(invalid_res["is_valid"])

    def test_agent_os_goal_dispatch(self):
        res = agent_os.dispatch_goal("Develop high performance business analytics code")
        self.assertEqual(res["status"], "SUCCESS")
        self.assertIn("execution_results", res)
        self.assertGreaterEqual(len(res["execution_results"]), 1)

    def test_task_cancellation(self):
        cancel_res = agent_os.cancel_goal("task_test_123")
        self.assertEqual(cancel_res["status"], "CANCELLED")
        self.assertTrue(event_bus.is_cancelled("task_test_123"))


if __name__ == "__main__":
    unittest.main()
