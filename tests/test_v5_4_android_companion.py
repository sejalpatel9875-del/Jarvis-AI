"""
tests/test_v5_4_android_companion.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Unittest Suite validating Android Mobile Companion App API Contracts & Payloads.
"""

import unittest
from services.desktop_assistant import desktop_assistant
from services.activity_feed import activity_feed
from services.calendar_reminders import calendar_reminders
from core.agent_os import agent_os


class TestV54AndroidCompanion(unittest.TestCase):
    def test_mobile_remote_command_payload_contract(self):
        res = desktop_assistant.execute_desktop_action(
            "control_volume", {"sub_action": "set", "level": 80}
        )
        self.assertTrue(res["success"])
        self.assertEqual(res["status"], "COMPLETED")
        self.assertIn("duration_ms", res)

    def test_mobile_activity_feed_sync(self):
        activity_feed.log_activity(
            "default", "MobileApp", "MOBILE_SYNC", "Synchronized offline Room DB"
        )
        feed = activity_feed.get_activity_feed("default", limit=5)
        self.assertIsInstance(feed, list)
        self.assertGreaterEqual(len(feed), 1)

    def test_mobile_reminders_sync(self):
        rem = calendar_reminders.create_reminder(
            "default", "Mobile Sync Call Client", "2026-08-05 14:00"
        )
        self.assertTrue(rem["success"])
        pending = calendar_reminders.list_reminders("default", pending_only=True)
        self.assertGreaterEqual(len(pending), 1)

    def test_mobile_multi_agent_telemetry(self):
        telemetry = agent_os.get_system_status()
        self.assertEqual(telemetry["status"], "HEALTHY")
        self.assertEqual(telemetry["active_agents"], 8)


if __name__ == "__main__":
    unittest.main()
