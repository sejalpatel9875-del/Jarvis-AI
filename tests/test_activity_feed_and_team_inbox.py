"""
Unit tests for ActivityFeedService and TeamInboxService.
"""

import unittest
from services.activity_feed import ActivityFeedService, activity_feed
from services.team_inbox import TeamInboxService, team_inbox


class TestActivityFeedService(unittest.TestCase):
    """Test cases for ActivityFeedService."""

    def test_log_and_get_activity(self) -> None:
        """Test logging an activity event and retrieving the feed."""
        ws_id = "test_ws_activity_1"
        res = activity_feed.log_activity(
            workspace_id=ws_id,
            actor_name="Test User",
            action="CREATE_PROJECT",
            details="Project A created",
            actor_type="USER",
        )
        self.assertTrue(res.get("success"))
        self.assertIn("id", res)
        self.assertEqual(res["workspace_id"], ws_id)
        self.assertEqual(res["actor_name"], "Test User")
        self.assertEqual(res["action"], "CREATE_PROJECT")

        feed = activity_feed.get_activity_feed(workspace_id=ws_id, limit=10)
        self.assertGreaterEqual(len(feed), 1)
        first_item = feed[0]
        self.assertEqual(first_item["workspace_id"], ws_id)
        self.assertEqual(first_item["actor_name"], "Test User")
        self.assertEqual(first_item["action"], "CREATE_PROJECT")
        self.assertEqual(first_item["details"], "Project A created")
        self.assertEqual(first_item["actor_type"], "USER")

    def test_default_workspace_and_actor_type(self) -> None:
        """Test default arguments for log_activity and get_activity_feed."""
        res = activity_feed.log_activity(
            workspace_id="default",
            actor_name="System Bot",
            action="AUTO_BACKUP",
        )
        self.assertTrue(res.get("success"))
        self.assertEqual(res["actor_type"], "USER")
        self.assertEqual(res["details"], "")

        feed = activity_feed.get_activity_feed()
        self.assertIsInstance(feed, list)
        self.assertGreater(len(feed), 0)


class TestTeamInboxService(unittest.TestCase):
    """Test cases for TeamInboxService."""

    def test_send_and_get_channel_messages(self) -> None:
        """Test sending a team message and fetching channel messages."""
        ws_id = "test_ws_inbox_1"
        channel = "SALES"
        res = team_inbox.send_message(
            workspace_id=ws_id,
            channel=channel,
            sender="Alice",
            message="Quarterly goals met!",
        )
        self.assertTrue(res.get("success"))
        self.assertIn("id", res)
        self.assertEqual(res["workspace_id"], ws_id)
        self.assertEqual(res["channel"], channel)
        self.assertEqual(res["sender"], "Alice")
        self.assertEqual(res["message"], "Quarterly goals met!")

        messages = team_inbox.get_channel_messages(workspace_id=ws_id, channel=channel, limit=20)
        self.assertGreaterEqual(len(messages), 1)
        msg = messages[0]
        self.assertEqual(msg["workspace_id"], ws_id)
        self.assertEqual(msg["channel"], channel)
        self.assertEqual(msg["sender"], "Alice")
        self.assertEqual(msg["message"], "Quarterly goals met!")

    def test_defaults(self) -> None:
        """Test default parameters for get_channel_messages."""
        res = team_inbox.send_message(
            workspace_id="default",
            channel="SALES",
            sender="Bob",
            message="Default channel test message",
        )
        self.assertTrue(res.get("success"))

        msgs = team_inbox.get_channel_messages()
        self.assertIsInstance(msgs, list)
        self.assertGreater(len(msgs), 0)


if __name__ == "__main__":
    unittest.main()
