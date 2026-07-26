"""
Purpose:
Departmental Team Inbox & Messaging Engine for Jarvis AI OS (Sprint v4.6).

Responsibilities:
- Channel messaging for Sales, HR, Engineering, Marketing
- Workspace-isolated internal team inbox
"""

import datetime
from typing import Dict, Any, List
import memory.database as db

def init_inbox_db():
    with db.get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS team_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                workspace_id TEXT NOT NULL,
                channel TEXT NOT NULL,
                sender TEXT NOT NULL,
                message TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
        """)

init_inbox_db()

class TeamInboxService:
    """Departmental Team Inbox Messaging Engine."""

    def send_message(
        self,
        workspace_id: str,
        channel: str,
        sender: str,
        message: str
    ) -> Dict[str, Any]:
        """Dispatches a message to a workspace team channel."""
        ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        channel_upper = channel.upper()
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO team_messages (workspace_id, channel, sender, message, timestamp)
                VALUES (?, ?, ?, ?, ?)
                """,
                (workspace_id, channel_upper, sender, message, ts)
            )
            msg_id = cursor.lastrowid

        msg_dict = {
            "id": msg_id,
            "workspace_id": workspace_id,
            "channel": channel_upper,
            "sender": sender,
            "content": message,
            "message": message,
            "timestamp": ts
        }

        return {
            "success": True,
            "id": msg_id,
            "message": msg_dict,
            **msg_dict
        }

    def get_channel_messages(self, workspace_id: str = "default", channel: str = "SALES", limit: int = 50) -> List[Dict[str, Any]]:
        """Retrieves recent messages from a channel."""
        channel_upper = channel.upper()
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, workspace_id, channel, sender, message, timestamp FROM team_messages WHERE workspace_id = ? AND channel = ? ORDER BY id DESC LIMIT ?",
                (workspace_id, channel_upper, limit)
            )
            rows = cursor.fetchall()
        return [dict(r) for r in rows]

# Global Singleton
team_inbox = TeamInboxService()
