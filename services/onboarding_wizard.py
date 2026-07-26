"""
Purpose:
Interactive User Onboarding Wizard Service for Jarvis AI OS (Sprint v4.7).

Responsibilities:
- Guide new users step-by-step (Workspace -> Team -> AI Config -> Sample Data -> Completed)
"""

import json
import datetime
from typing import Dict, Any, List
import memory.database as db

def init_onboarding_db():
    with db.get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS onboarding_progress (
                workspace_id TEXT PRIMARY KEY,
                current_step TEXT DEFAULT 'workspace_setup',
                completed_steps_json TEXT DEFAULT '[]',
                is_finished INTEGER DEFAULT 0,
                updated_at TEXT NOT NULL
            )
        """)

init_onboarding_db()

class OnboardingWizardService:
    """Enterprise Interactive User Onboarding Wizard Engine."""

    ALL_STEPS = ["workspace_setup", "team_invite", "ai_configuration", "sample_data"]

    def get_onboarding_status(self, workspace_id: str = "default") -> Dict[str, Any]:
        """Retrieves onboarding progress status for a workspace."""
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT workspace_id, current_step, completed_steps_json, is_finished, updated_at FROM onboarding_progress WHERE workspace_id = ?",
                (workspace_id,)
            )
            row = cursor.fetchone()

        if not row:
            # Auto-initialize workspace onboarding record
            ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with db.get_connection() as conn:
                conn.execute(
                    "INSERT INTO onboarding_progress (workspace_id, current_step, completed_steps_json, is_finished, updated_at) VALUES (?, 'workspace_setup', '[]', 0, ?)",
                    (workspace_id, ts)
                )
            return {
                "success": True,
                "workspace_id": workspace_id,
                "current_step": "workspace_setup",
                "completed_steps": [],
                "all_steps": self.ALL_STEPS,
                "is_finished": False,
                "progress_percentage": 0.0
            }

        row_dict = dict(row)
        completed = json.loads(row_dict["completed_steps_json"]) if row_dict["completed_steps_json"] else []
        pct = round((len(completed) / len(self.ALL_STEPS)) * 100, 1)

        return {
            "success": True,
            "workspace_id": workspace_id,
            "current_step": row_dict["current_step"],
            "completed_steps": completed,
            "all_steps": self.ALL_STEPS,
            "is_finished": bool(row_dict["is_finished"]),
            "progress_percentage": pct
        }

    def complete_onboarding_step(self, workspace_id: str = "default", step_name: str = "workspace_setup") -> Dict[str, Any]:
        """Marks an onboarding step as completed and advances progress."""
        status = self.get_onboarding_status(workspace_id)
        completed = status["completed_steps"]

        if step_name not in completed:
            completed.append(step_name)

        is_finished = len(completed) >= len(self.ALL_STEPS)
        if is_finished:
            next_step = "completed"
        else:
            next_step = self.ALL_STEPS[len(completed)]

        ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE onboarding_progress
                SET current_step = ?, completed_steps_json = ?, is_finished = ?, updated_at = ?
                WHERE workspace_id = ?
                """,
                (next_step, json.dumps(completed), 1 if is_finished else 0, ts, workspace_id)
            )

        return {
            "success": True,
            "workspace_id": workspace_id,
            "completed_step": step_name,
            "completed_steps": completed,
            "current_step": next_step,
            "is_finished": is_finished,
            "progress_percentage": round((len(completed) / len(self.ALL_STEPS)) * 100, 1)
        }

# Global Singleton
onboarding_wizard = OnboardingWizardService()
