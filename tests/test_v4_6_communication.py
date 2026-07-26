"""
Unit tests for J.A.R.V.I.S. v4.6 Business Communication & Activity Feed Platform.
"""

import unittest
import uuid
from services.activity_feed import activity_feed
from services.team_inbox import team_inbox
from services.calendar_reminders import calendar_reminders
from services.smart_notifications import smart_notifications

class TestV46CommunicationPlatform(unittest.TestCase):
    def test_activity_feed_logging(self):
        ws_id = f"ws_{uuid.uuid4().hex[:6]}"
        res = activity_feed.log_activity(ws_id, "Rahul", "CREATED_LEAD", "Created lead Acme Corp")
        self.assertTrue(res["success"])
        feed = activity_feed.get_activity_feed(ws_id)
        self.assertEqual(len(feed), 1)

    def test_team_inbox_messaging(self):
        ws_id = f"ws_{uuid.uuid4().hex[:6]}"
        res = team_inbox.send_message(ws_id, "SALES", "Alice", "Q4 Strategy Update")
        self.assertTrue(res["success"])
        msgs = team_inbox.get_channel_messages(ws_id, "SALES")
        self.assertEqual(len(msgs), 1)

    def test_calendar_reminders(self):
        ws_id = f"ws_{uuid.uuid4().hex[:6]}"
        rem = calendar_reminders.create_reminder(ws_id, "Call Client John", "2026-07-27 10:00")
        self.assertTrue(rem["success"])
        rem_id = rem["reminder"]["id"]
        pending = calendar_reminders.list_reminders(ws_id, pending_only=True)
        self.assertEqual(len(pending), 1)
        comp = calendar_reminders.complete_reminder(rem_id)
        self.assertTrue(comp["success"])

    def test_smart_notifications(self):
        ws_id = f"ws_{uuid.uuid4().hex[:6]}"
        disp = smart_notifications.dispatch_event_notification(ws_id, "LEAD_QUALIFIED", {"lead_name": "TechCorp"})
        self.assertTrue(disp["success"])

if __name__ == "__main__":
    unittest.main()
