"""
Notification Service for J.A.R.V.I.S. AI OS.

Manages user notifications, persisting unread and read alerts to SQLite via memory.database.
"""

import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List
import memory.database as db
from services.logger import logger


class NotificationService:
    """In-app and channel notification management service."""

    def __init__(self) -> None:
        """Initialise notification service and database schema."""
        self._init_db()

    def _init_db(self) -> None:
        """Initialise notifications table in database."""
        try:
            with db.get_connection() as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS notifications (
                        id TEXT PRIMARY KEY,
                        user_id TEXT NOT NULL,
                        title TEXT NOT NULL,
                        message TEXT NOT NULL,
                        channel TEXT DEFAULT 'dashboard',
                        read INTEGER DEFAULT 0,
                        created_at TEXT NOT NULL
                    )
                """)
                conn.execute("CREATE INDEX IF NOT EXISTS idx_notifications_user ON notifications(user_id, read);")
        except Exception as e:
            logger.error("NOTIFICATION_SERVICE", f"Failed to initialize notifications table: {e}")

    def send_notification(
        self,
        user_id: str,
        title: str,
        message: str,
        channel: str = "dashboard",
    ) -> Dict[str, Any]:
        """Dispatch a notification to a specific user.

        Args:
            user_id: Target user ID.
            title: Notification title.
            message: Notification message content.
            channel: Notification channel (e.g., 'dashboard', 'email'). Default: 'dashboard'.

        Returns:
            Dict indicating success and notification details.
        """
        notification_id = str(uuid.uuid4())
        created_at = datetime.now(timezone.utc).isoformat()

        try:
            with db.get_connection() as conn:
                conn.execute(
                    """
                    INSERT INTO notifications (id, user_id, title, message, channel, read, created_at)
                    VALUES (?, ?, ?, ?, ?, 0, ?)
                    """,
                    (notification_id, user_id, title, message, channel, created_at),
                )
            logger.info("NOTIFICATION_SERVICE", f"Sent notification '{title}' to user '{user_id}' via '{channel}'")
            return {
                "success": True,
                "id": notification_id,
                "user_id": user_id,
                "title": title,
                "message": message,
                "channel": channel,
                "read": False,
                "created_at": created_at,
            }
        except Exception as e:
            logger.error("NOTIFICATION_SERVICE", f"Failed to send notification: {e}")
            return {"success": False, "error": str(e)}

    def get_unread(self, user_id: str) -> List[Dict[str, Any]]:
        """Retrieve all unread notifications for a specified user.

        Args:
            user_id: Target user ID.

        Returns:
            List of unread notification dicts.
        """
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT id, user_id, title, message, channel, read, created_at
                    FROM notifications
                    WHERE user_id = ? AND read = 0
                    ORDER BY created_at DESC
                    """,
                    (user_id,),
                )
                rows = cursor.fetchall()
                return [
                    {
                        "id": row["id"],
                        "user_id": row["user_id"],
                        "title": row["title"],
                        "message": row["message"],
                        "channel": row["channel"],
                        "read": bool(row["read"]),
                        "created_at": row["created_at"],
                    }
                    for row in rows
                ]
        except Exception as e:
            logger.error("NOTIFICATION_SERVICE", f"Failed to retrieve unread notifications for user '{user_id}': {e}")
            return []

    def mark_as_read(self, notification_id: str) -> Dict[str, Any]:
        """Mark a notification as read.

        Args:
            notification_id: Notification ID to update.

        Returns:
            Dict with success flag.
        """
        try:
            with db.get_connection() as conn:
                conn.execute(
                    "UPDATE notifications SET read = 1 WHERE id = ?",
                    (notification_id,),
                )
            return {"success": True, "id": notification_id}
        except Exception as e:
            logger.error("NOTIFICATION_SERVICE", f"Failed to mark notification as read: {e}")
            return {"success": False, "error": str(e)}


# Singleton instance
notification_service = NotificationService()
