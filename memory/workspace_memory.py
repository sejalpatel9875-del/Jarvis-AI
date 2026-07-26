"""
Workspace Memory Subsystem for J.A.R.V.I.S. AI OS.

Provides isolated fact storage and memory management per workspace.
Stores facts in SQLite database using memory.database connection manager.
"""

import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List
import memory.database as db
from services.logger import logger


class WorkspaceMemoryManager:
    """Manager for handling workspace-scoped facts and persistent memory."""

    def __init__(self) -> None:
        """Initialise WorkspaceMemoryManager and ensure database schema exists."""
        self._init_db()

    def _init_db(self) -> None:
        """Initialise the workspace_memory_facts SQLite table and indexes."""
        try:
            with db.get_connection() as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS workspace_memory_facts (
                        id TEXT PRIMARY KEY,
                        workspace_id TEXT NOT NULL,
                        key TEXT NOT NULL,
                        value TEXT NOT NULL,
                        created_at TEXT NOT NULL
                    )
                """)
                conn.execute(
                    "CREATE INDEX IF NOT EXISTS idx_ws_facts_ws ON workspace_memory_facts(workspace_id);"
                )
                conn.execute(
                    "CREATE INDEX IF NOT EXISTS idx_ws_facts_key ON workspace_memory_facts(key);"
                )
        except Exception as e:
            logger.error("WORKSPACE_MEMORY", f"Failed to initialize database table: {e}")

    def save_fact(self, workspace_id: str, key: str, value: str) -> Dict[str, Any]:
        """Save or store a key-value fact for a specific workspace.

        Args:
            workspace_id: Unique identifier for the target workspace.
            key: Key / topic descriptor for the fact.
            value: Detailed content or value of the fact.

        Returns:
            Dict containing operation success status, fact ID, and fact details.
        """
        fact_id = f"fact_{uuid.uuid4().hex[:12]}"
        created_at = datetime.now(timezone.utc).isoformat()

        try:
            with db.get_connection() as conn:
                conn.execute(
                    """
                    INSERT INTO workspace_memory_facts (id, workspace_id, key, value, created_at)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (fact_id, workspace_id, key, value, created_at),
                )

            fact_data = {
                "id": fact_id,
                "workspace_id": workspace_id,
                "key": key,
                "value": value,
                "created_at": created_at,
            }
            logger.info(
                "WORKSPACE_MEMORY",
                f"Saved fact '{key}' for workspace '{workspace_id}' (ID: {fact_id})",
            )
            return {"success": True, "fact": fact_data, **fact_data}
        except Exception as e:
            logger.error("WORKSPACE_MEMORY", f"Failed to save fact: {e}")
            return {"success": False, "error": str(e)}

    def get_facts(self, workspace_id: str) -> List[Dict[str, Any]]:
        """Retrieve all facts associated with a given workspace.

        Args:
            workspace_id: Unique identifier for the workspace.

        Returns:
            List of dictionaries representing fact records.
        """
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT id, workspace_id, key, value, created_at
                    FROM workspace_memory_facts
                    WHERE workspace_id = ?
                    ORDER BY created_at DESC
                    """,
                    (workspace_id,),
                )
                rows = cursor.fetchall()
                return [
                    {
                        "id": row["id"],
                        "workspace_id": row["workspace_id"],
                        "key": row["key"],
                        "value": row["value"],
                        "created_at": row["created_at"],
                    }
                    for row in rows
                ]
        except Exception as e:
            logger.error("WORKSPACE_MEMORY", f"Failed to retrieve facts for workspace '{workspace_id}': {e}")
            return []

    def search_workspace_facts(self, workspace_id: str, query: str) -> List[Dict[str, Any]]:
        """Search workspace facts by key or value matching a query string.

        Args:
            workspace_id: Unique identifier for the workspace.
            query: Search query string to match against key or value fields.

        Returns:
            List of matching fact dictionaries.
        """
        search_pattern = f"%{query}%"
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT id, workspace_id, key, value, created_at
                    FROM workspace_memory_facts
                    WHERE workspace_id = ? AND (key LIKE ? OR value LIKE ?)
                    ORDER BY created_at DESC
                    """,
                    (workspace_id, search_pattern, search_pattern),
                )
                rows = cursor.fetchall()
                return [
                    {
                        "id": row["id"],
                        "workspace_id": row["workspace_id"],
                        "key": row["key"],
                        "value": row["value"],
                        "created_at": row["created_at"],
                    }
                    for row in rows
                ]
        except Exception as e:
            logger.error(
                "WORKSPACE_MEMORY",
                f"Failed to search facts for workspace '{workspace_id}' with query '{query}': {e}",
            )
            return []


# Singleton instance
workspace_memory = WorkspaceMemoryManager()
