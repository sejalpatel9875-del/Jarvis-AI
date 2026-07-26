"""
Purpose:
GitHub-Style Real-Time Activity Feed Engine for Jarvis AI OS (Sprint v4.6).

Responsibilities:
- Log user, AI agent, and workspace events chronologically
- Retrieve live activity timeline feeds for CEO Dashboard
"""

import datetime
from typing import Dict, Any, List
import memory.database as db

def init_activity_db():
    with db.get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS activity_feed (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                workspace_id TEXT NOT NULL,
                actor_name TEXT NOT NULL,
                actor_type TEXT DEFAULT 'USER',
                action TEXT NOT NULL,
                details TEXT DEFAULT '',
                timestamp TEXT NOT NULL
            )
        """)

init_activity_db()

class ActivityFeedService:
    """Enterprise Workspace Real-Time Activity Feed Engine."""

    def log_activity(
        self,
        workspace_id: str,
        actor_name: str,
        action: str,
        details: str = "",
        actor_type: str = "USER"
    ) -> Dict[str, Any]:
        """Logs a new activity item into the workspace timeline."""
        ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO activity_feed (workspace_id, actor_name, actor_type, action, details, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (workspace_id, actor_name, actor_type, action, details, ts)
            )
            act_id = cursor.lastrowid

        act_dict = {
            "id": act_id,
            "workspace_id": workspace_id,
            "actor_name": actor_name,
            "actor_type": actor_type,
            "action": action,
            "details": details,
            "timestamp": ts
        }

        return {
            "success": True,
            "id": act_id,
            "activity": act_dict,
            **act_dict
        }

    def get_activity_feed(self, workspace_id: str = "default", limit: int = 30) -> List[Dict[str, Any]]:
        """Retrieves chronological activity feed for a workspace."""
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, workspace_id, actor_name, actor_type, action, details, timestamp FROM activity_feed WHERE workspace_id = ? ORDER BY id DESC LIMIT ?",
                (workspace_id, limit)
            )
            rows = cursor.fetchall()
        return [dict(r) for r in rows]

# Global Singleton
activity_feed = ActivityFeedService()
