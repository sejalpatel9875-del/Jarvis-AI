"""
Unit tests for CalendarReminderService and SmartNotificationEngine.
"""

import unittest
from services.calendar_reminders import CalendarReminderService, calendar_reminders
from services.smart_notifications import SmartNotificationEngine, smart_notifications


class TestCalendarReminderService(unittest.TestCase):
    """Test cases for CalendarReminderService."""

    def test_create_and_list_reminders(self) -> None:
        """Test creating a reminder and listing pending reminders."""
        ws_id = "test_ws_reminders_1"
        res = calendar_reminders.create_reminder(
            workspace_id=ws_id,
            title="Team Sync Meeting",
            due_at="2026-08-01T10:00:00Z",
            assignee="alice",
        )
        self.assertTrue(res.get("success"))
        self.assertIn("id", res)
        self.assertEqual(res["workspace_id"], ws_id)
        self.assertEqual(res["title"], "Team Sync Meeting")
        self.assertEqual(res["due_at"], "2026-08-01T10:00:00Z")
        self.assertEqual(res["assignee"], "alice")
        self.assertFalse(res["is_completed"])

        # List pending reminders
        reminders = calendar_reminders.list_reminders(workspace_id=ws_id, pending_only=True)
        self.assertGreaterEqual(len(reminders), 1)
        item = reminders[0]
        self.assertEqual(item["id"], res["id"])
        self.assertFalse(item["is_completed"])

    def test_complete_reminder(self) -> None:
        """Test completing a reminder."""
        ws_id = "test_ws_reminders_2"
        create_res = calendar_reminders.create_reminder(
            workspace_id=ws_id,
            title="Submit Report",
        )
        reminder_id = create_res["id"]

        comp_res = calendar_reminders.complete_reminder(reminder_id)
        self.assertTrue(comp_res.get("success"))
        self.assertTrue(comp_res["is_completed"])

        # Pending list should not include completed item
        pending = calendar_reminders.list_reminders(workspace_id=ws_id, pending_only=True)
        pending_ids = [r["id"] for r in pending]
        self.assertNotIn(reminder_id, pending_ids)

        # All list should include completed item
        all_reminders = calendar_reminders.list_reminders(workspace_id=ws_id, pending_only=False)
        all_ids = [r["id"] for r in all_reminders]
        self.assertIn(reminder_id, all_ids)


class TestSmartNotificationEngine(unittest.TestCase):
    """Test cases for SmartNotificationEngine."""

    def test_dispatch_event_notification(self) -> None:
        """Test dispatching an event notification with default and custom channels."""
        ws_id = "test_ws_smart_notif_1"
        res = smart_notifications.dispatch_event_notification(
            workspace_id=ws_id,
            event_name="USER_SIGNUP",
            payload={
                "user_id": "usr_123",
                "title": "Welcome User",
                "message": "User usr_123 joined the workspace",
                "channels": ["dashboard", "email"],
            },
        )
        self.assertTrue(res.get("success"))
        self.assertEqual(res["workspace_id"], ws_id)
        self.assertEqual(res["event_name"], "USER_SIGNUP")
        self.assertEqual(res["dispatched_channels"], ["dashboard", "email"])
        self.assertIn("timestamp", res)

    def test_dispatch_event_notification_defaults(self) -> None:
        """Test dispatching event notification with empty payload."""
        ws_id = "test_ws_smart_notif_2"
        res = smart_notifications.dispatch_event_notification(
            workspace_id=ws_id,
            event_name="BACKUP_COMPLETE",
        )
        self.assertTrue(res.get("success"))
        self.assertEqual(res["dispatched_channels"], ["dashboard"])


if __name__ == "__main__":
    unittest.main()
