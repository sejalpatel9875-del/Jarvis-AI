"""
Purpose:
Calendar & Follow-Up Reminders Service for Jarvis AI OS (Sprint v4.6).

Responsibilities:
- Manage follow-up tasks, reminders, due dates, and completion status
"""

import datetime
from typing import Dict, Any, List
import memory.database as db

def init_calendar_db():
    with db.get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS calendar_reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                workspace_id TEXT NOT NULL,
                title TEXT NOT NULL,
                due_at TEXT DEFAULT '',
                assignee TEXT DEFAULT 'me',
                is_completed INTEGER DEFAULT 0,
                created_at TEXT NOT NULL
            )
        """)

init_calendar_db()

class CalendarReminderService:
    """Enterprise Follow-Up Reminders & Calendar Engine."""

    def create_reminder(
        self,
        workspace_id: str,
        title: str,
        due_at: str = "",
        assignee: str = "me"
    ) -> Dict[str, Any]:
        """Creates a follow-up reminder."""
        ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if not due_at:
            due_at = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")

        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO calendar_reminders (workspace_id, title, due_at, assignee, is_completed, created_at)
                VALUES (?, ?, ?, ?, 0, ?)
                """,
                (workspace_id, title, due_at, assignee, ts)
            )
            rem_id = cursor.lastrowid

        reminder_dict = {
            "id": rem_id,
            "workspace_id": workspace_id,
            "title": title,
            "due_at": due_at,
            "assignee": assignee,
            "is_completed": False,
            "created_at": ts
        }

        return {
            "success": True,
            "id": rem_id,
            "reminder": reminder_dict,
            **reminder_dict
        }

    def list_reminders(self, workspace_id: str = "default", pending_only: bool = True) -> List[Dict[str, Any]]:
        """Lists workspace reminders."""
        with db.get_connection() as conn:
            cursor = conn.cursor()
            if pending_only:
                cursor.execute(
                    "SELECT id, workspace_id, title, due_at, assignee, is_completed, created_at FROM calendar_reminders WHERE workspace_id = ? AND is_completed = 0 ORDER BY id DESC",
                    (workspace_id,)
                )
            else:
                cursor.execute(
                    "SELECT id, workspace_id, title, due_at, assignee, is_completed, created_at FROM calendar_reminders WHERE workspace_id = ? ORDER BY id DESC",
                    (workspace_id,)
                )
            rows = cursor.fetchall()

        result = []
        for r in rows:
            rd = dict(r)
            rd["is_completed"] = bool(rd["is_completed"])
            result.append(rd)
        return result

    def complete_reminder(self, reminder_id: int) -> Dict[str, Any]:
        """Marks a reminder as completed."""
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE calendar_reminders SET is_completed = 1 WHERE id = ?", (reminder_id,))

        return {"success": True, "reminder_id": reminder_id, "is_completed": True}

# Global Singleton
calendar_reminders = CalendarReminderService()
