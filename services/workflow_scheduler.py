"""
Purpose:
Workflow Scheduler Service for Jarvis AI OS (Sprint v4.4).

Responsibilities:
- Manage recurring cron workflow execution schedules
"""

import datetime
from typing import Dict, Any, List, Union
import memory.database as db

def init_scheduler_db():
    with db.get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS workflow_schedules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                workflow_id TEXT NOT NULL,
                cron_expression TEXT NOT NULL,
                next_run_at TEXT NOT NULL,
                is_active INTEGER DEFAULT 1
            )
        """)

init_scheduler_db()

class WorkflowSchedulerService:
    """Recurring Cron Workflow Scheduler."""

    def schedule_workflow(self, workflow_id: Union[int, str], cron_expression: str, is_active: bool = True) -> Dict[str, Any]:
        """Schedules a recurring cron job for a workflow."""
        if not workflow_id or not cron_expression:
            return {"success": False, "error": "workflow_id and cron_expression are required."}

        next_run = (datetime.datetime.now() + datetime.timedelta(hours=24)).strftime("%Y-%m-%d %H:%M:%S")

        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO workflow_schedules (workflow_id, cron_expression, next_run_at, is_active)
                VALUES (?, ?, ?, ?)
                """,
                (str(workflow_id), str(cron_expression), next_run, 1 if is_active else 0)
            )
            sch_id = cursor.lastrowid

        return {
            "success": True,
            "id": sch_id,
            "workflow_id": workflow_id,
            "cron_expression": cron_expression,
            "next_run_at": next_run,
            "is_active": is_active,
            "schedule": {
                "id": sch_id,
                "workflow_id": workflow_id,
                "cron_expression": cron_expression,
                "next_run_at": next_run,
                "is_active": is_active
            }
        }

    def list_scheduled_jobs(self) -> List[Dict[str, Any]]:
        """Lists active scheduled cron jobs."""
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, workflow_id, cron_expression, next_run_at, is_active FROM workflow_schedules WHERE is_active = 1")
            rows = cursor.fetchall()
        
        result = []
        for r in rows:
            rd = dict(r)
            rd["is_active"] = bool(rd["is_active"])
            result.append(rd)
        return result

# Global Singleton
workflow_scheduler = WorkflowSchedulerService()
