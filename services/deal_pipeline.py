"""
Purpose:
Enterprise Deal Pipeline Service for Jarvis AI OS (Sprint v4.5).

Responsibilities:
- Manage sales deal pipelines, stage transitions, and revenue analytics summary
"""

import datetime
from typing import Dict, Any, List, Optional
import memory.database as db

def init_deal_db():
    with db.get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS deals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                lead_id INTEGER NOT NULL,
                workspace_id TEXT NOT NULL,
                title TEXT NOT NULL,
                value_usd REAL DEFAULT 0.0,
                stage TEXT DEFAULT 'PROSPECTING',
                expected_close_date TEXT DEFAULT '',
                created_at TEXT NOT NULL
            )
        """)

init_deal_db()

class DealPipelineService:
    """Enterprise Sales Deal Pipeline & Revenue Analytics Engine."""

    def create_deal(
        self,
        lead_id: int,
        workspace_id: str,
        title: str,
        value_usd: float,
        stage: str = "PROSPECTING",
        expected_close_date: str = ""
    ) -> Dict[str, Any]:
        """Creates a deal associated with a lead and workspace."""
        ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if not expected_close_date:
            expected_close_date = (datetime.datetime.now() + datetime.timedelta(days=30)).strftime("%Y-%m-%d")

        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO deals (lead_id, workspace_id, title, value_usd, stage, expected_close_date, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (lead_id, workspace_id, title, float(value_usd), stage, expected_close_date, ts)
            )
            deal_id = cursor.lastrowid

        deal_dict = {
            "id": deal_id,
            "lead_id": lead_id,
            "workspace_id": workspace_id,
            "title": title,
            "value_usd": float(value_usd),
            "stage": stage,
            "expected_close_date": expected_close_date,
            "created_at": ts
        }

        return {"success": True, "deal": deal_dict}

    def update_deal_stage(self, deal_id: int, new_stage: str) -> Dict[str, Any]:
        """Updates the stage of an active deal."""
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE deals SET stage = ? WHERE id = ?", (new_stage, deal_id))

        return {"success": True, "deal_id": deal_id, "stage": new_stage}

    def get_pipeline_summary(self, workspace_id: str = "default") -> Dict[str, Any]:
        """Calculates total pipeline revenue metrics for a workspace."""
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, lead_id, workspace_id, title, value_usd, stage FROM deals WHERE workspace_id = ?",
                (workspace_id,)
            )
            rows = cursor.fetchall()

        total_deals = len(rows)
        total_value = sum(dict(r)["value_usd"] for r in rows) if rows else 0.0
        avg_deal_size = total_value / total_deals if total_deals > 0 else 0.0

        stage_counts = {}
        for r in rows:
            stg = dict(r)["stage"]
            stage_counts[stg] = stage_counts.get(stg, 0) + 1

        return {
            "success": True,
            "workspace_id": workspace_id,
            "total_deals": total_deals,
            "total_pipeline_value_usd": round(total_value, 2),
            "avg_deal_size_usd": round(avg_deal_size, 2),
            "deals_by_stage": stage_counts
        }

    def list_deals(self, workspace_id: str = "default") -> List[Dict[str, Any]]:
        """Lists sales deals for a workspace."""
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, lead_id, workspace_id, title, value_usd, stage, expected_close_date, created_at FROM deals WHERE workspace_id = ? ORDER BY id DESC",
                (workspace_id,)
            )
            rows = cursor.fetchall()
        return [dict(r) for r in rows]

# Global Singleton
deal_pipeline = DealPipelineService()

