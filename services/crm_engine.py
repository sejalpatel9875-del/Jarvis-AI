"""
Purpose:
Enterprise Lead CRM Intelligence Engine for Jarvis AI OS (Sprint v4.5).

Responsibilities:
- Manage lead capture, workspace isolation, and status updates
- Compute automated AI lead scoring (0-100) based on intent and domain parameters
"""

import datetime
from enum import Enum
from typing import Dict, Any, List, Optional, Union
import memory.database as db

class LeadStatus(str, Enum):
    NEW = "NEW"
    QUALIFIED = "QUALIFIED"
    PROPOSAL = "PROPOSAL"
    WON = "WON"
    LOST = "LOST"

def init_crm_db():
    with db.get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS leads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                workspace_id TEXT NOT NULL,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                company TEXT DEFAULT '',
                phone TEXT DEFAULT '',
                status TEXT DEFAULT 'NEW',
                score INTEGER DEFAULT 50,
                source TEXT DEFAULT 'web',
                created_at TEXT NOT NULL
            )
        """)

init_crm_db()

class CRMEngineService:
    """Enterprise Lead CRM Management & AI Scoring Engine."""

    def create_lead(
        self,
        workspace_id: str,
        name: str,
        email: str,
        company: str = "",
        phone: str = "",
        source: str = "web"
    ) -> Dict[str, Any]:
        """Captures and stores a new workspace lead."""
        ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        initial_score = 75 if ("enterprise" in email.lower() or "acme" in company.lower()) else 60

        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO leads (workspace_id, name, email, company, phone, status, score, source, created_at)
                VALUES (?, ?, ?, ?, ?, 'NEW', ?, ?, ?)
                """,
                (workspace_id, name, email, company, phone, initial_score, source, ts)
            )
            lead_id = cursor.lastrowid

        lead_dict = {
            "id": lead_id,
            "workspace_id": workspace_id,
            "name": name,
            "email": email,
            "company": company,
            "phone": phone,
            "status": "NEW",
            "score": initial_score,
            "source": source,
            "created_at": ts
        }

        return {"success": True, "lead": lead_dict}

    def list_leads(self, workspace_id: str = "default", status: Optional[Union[str, Enum]] = None) -> List[Dict[str, Any]]:
        """Lists workspace leads with optional status filter."""
        with db.get_connection() as conn:
            cursor = conn.cursor()
            if status:
                status_str = status.value if hasattr(status, "value") else str(status)
                cursor.execute(
                    "SELECT id, workspace_id, name, email, company, phone, status, score, source, created_at FROM leads WHERE workspace_id = ? AND status = ? ORDER BY id DESC",
                    (workspace_id, status_str)
                )
            else:
                cursor.execute(
                    "SELECT id, workspace_id, name, email, company, phone, status, score, source, created_at FROM leads WHERE workspace_id = ? ORDER BY id DESC",
                    (workspace_id,)
                )
            rows = cursor.fetchall()
        return [dict(r) for r in rows]

    def get_lead(self, lead_id: int) -> Optional[Dict[str, Any]]:
        """Retrieves a lead by ID."""
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, workspace_id, name, email, company, phone, status, score, source, created_at FROM leads WHERE id = ?",
                (lead_id,)
            )
            row = cursor.fetchone()
        return dict(row) if row else None

    def update_lead_status(self, lead_id: int, status: Union[str, Enum]) -> Dict[str, Any]:
        """Updates the status of a lead."""
        status_str = status.value if hasattr(status, "value") else str(status)
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE leads SET status = ? WHERE id = ?", (status_str, lead_id))

        return {"success": True, "lead_id": lead_id, "status": status_str}

    def score_lead(self, lead_id: int) -> Dict[str, Any]:
        """Calculates and updates AI lead quality score (0-100)."""
        lead = self.get_lead(lead_id)
        if not lead:
            return {"success": False, "error": f"Lead {lead_id} not found"}

        score = 50
        email = lead.get("email", "").lower()
        company = lead.get("company", "").lower()

        if "@" in email and not any(email.endswith(free) for free in ["gmail.com", "yahoo.com", "hotmail.com"]):
            score += 25
        if company:
            score += 15
        if "enterprise" in company or "corp" in company or "ai" in company:
            score += 10

        score = min(score, 100)

        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE leads SET score = ? WHERE id = ?", (score, lead_id))

        return {"success": True, "lead_id": lead_id, "score": score}

# Global Singleton
crm_engine = CRMEngineService()
