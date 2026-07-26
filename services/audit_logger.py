"""
Audit Logging Service for J.A.R.V.I.S. AI OS.

Provides structured audit logging for multi-tenant organizations and workspaces,
storing security and operational events into SQLite via memory.database.
"""

import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
import memory.database as db
from services.logger import logger


class AuditLogger:
    """Audit logging service for tracking system events across organizations and workspaces."""

    def __init__(self) -> None:
        """Initialise the audit logger service and ensure database table schema."""
        self._init_db()

    def _init_db(self) -> None:
        """Initialise the sqlite audit_logs table schema."""
        try:
            with db.get_connection() as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS audit_logs (
                        id TEXT PRIMARY KEY,
                        timestamp TEXT NOT NULL,
                        org_id TEXT NOT NULL,
                        workspace_id TEXT NOT NULL,
                        actor_id TEXT NOT NULL,
                        action TEXT NOT NULL,
                        details TEXT DEFAULT ''
                    )
                """)
                conn.execute("CREATE INDEX IF NOT EXISTS idx_audit_org_ws ON audit_logs(org_id, workspace_id);")
        except Exception as e:
            logger.error("AUDIT_LOGGER", f"Failed to initialize audit_logs table: {e}")

    def log_event(
        self,
        org_id: str,
        workspace_id: str,
        actor_id: str,
        action: str,
        details: str = "",
    ) -> Dict[str, Any]:
        """Log an audit event to the database.

        Args:
            org_id: Organization identifier.
            workspace_id: Workspace identifier.
            actor_id: Actor / User identifier who performed the action.
            action: Description of the action (e.g. 'USER_INVITED', 'LOGIN').
            details: Optional additional details or JSON string.

        Returns:
            Dict containing success status and logged event details.
        """
        log_id = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc).isoformat()

        try:
            with db.get_connection() as conn:
                conn.execute(
                    """
                    INSERT INTO audit_logs (id, timestamp, org_id, workspace_id, actor_id, action, details)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (log_id, timestamp, org_id, workspace_id, actor_id, action, details),
                )
            logger.info("AUDIT_LOGGER", f"Logged event '{action}' by actor '{actor_id}' in org '{org_id}'")
            return {
                "success": True,
                "id": log_id,
                "timestamp": timestamp,
                "org_id": org_id,
                "workspace_id": workspace_id,
                "actor_id": actor_id,
                "action": action,
                "details": details,
            }
        except Exception as e:
            logger.error("AUDIT_LOGGER", f"Failed to log event: {e}")
            return {"success": False, "error": str(e)}

    def get_logs(
        self,
        org_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Retrieve audit logs with optional organization or workspace filtering.

        Args:
            org_id: Optional organization ID filter.
            workspace_id: Optional workspace ID filter.
            limit: Maximum number of audit log records to return (default: 50).

        Returns:
            List of dictionaries representing log entries.
        """
        query = "SELECT id, timestamp, org_id, workspace_id, actor_id, action, details FROM audit_logs"
        params: List[Any] = []
        conditions: List[str] = []

        if org_id:
            conditions.append("org_id = ?")
            params.append(org_id)
        if workspace_id:
            conditions.append("workspace_id = ?")
            params.append(workspace_id)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)

        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                rows = cursor.fetchall()
                return [
                    {
                        "id": row["id"],
                        "timestamp": row["timestamp"],
                        "org_id": row["org_id"],
                        "workspace_id": row["workspace_id"],
                        "actor_id": row["actor_id"],
                        "action": row["action"],
                        "details": row["details"],
                    }
                    for row in rows
                ]
        except Exception as e:
            logger.error("AUDIT_LOGGER", f"Failed to fetch audit logs: {e}")
            return []


# Singleton instance
audit_logger = AuditLogger()
