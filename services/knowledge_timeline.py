"""
Purpose:
Chronological Knowledge Timeline Service for Jarvis AI OS (Sprint v4.3).

Responsibilities:
- Record document indexing events, meeting notes, and project milestones chronologically
"""

import time
import datetime
from typing import Dict, Any, List
import memory.database as db

def init_timeline_db():
    with db.get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS knowledge_timeline (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                workspace_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT DEFAULT ''
            )
        """)

init_timeline_db()

class KnowledgeTimelineService:
    """Chronological Knowledge Event Timeline Engine."""

    def add_event(self, workspace_id: str, event_type: str, title: str, description: str = "") -> Dict[str, Any]:
        ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO knowledge_timeline (timestamp, workspace_id, event_type, title, description) VALUES (?, ?, ?, ?, ?)",
                (ts, workspace_id, event_type, title, description)
            )
            event_id = cursor.lastrowid

        return {
            "id": event_id,
            "success": True,
            "timestamp": ts,
            "workspace_id": workspace_id,
            "event_type": event_type,
            "title": title,
            "description": description
        }

    def get_timeline(self, workspace_id: str = "default", limit: int = 30) -> List[Dict[str, Any]]:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, timestamp, workspace_id, event_type, title, description FROM knowledge_timeline WHERE workspace_id = ? ORDER BY id DESC LIMIT ?",
                (workspace_id, limit)
            )
            rows = cursor.fetchall()

        return [dict(r) for r in rows]

# Global Singleton
knowledge_timeline = KnowledgeTimelineService()
