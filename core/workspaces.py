"""
Purpose:
Multi-Tenant Organization & Workspace Management Module for Jarvis AI OS.

Responsibilities:
- SQLite schema initialization for 'organizations' and 'workspaces' tables
- Data models for OrganizationModel and WorkspaceModel
- WorkspaceManager singleton for CRUD operations on orgs and workspaces

Dependencies:
- memory/database.py
- services/logger.py
"""

import uuid
import datetime
from dataclasses import dataclass, asdict
from typing import Dict, Any, List, Optional
import memory.database as db
from services.logger import logger


@dataclass
class OrganizationModel:
    """Data model representing an Organization entity.

    Attributes:
        id (str): Unique organization ID.
        name (str): Organization display name.
        owner_id (str): User ID of the organization owner.
        plan (str): Subscription plan (default: 'business').
        created_at (str, optional): ISO timestamp of creation date.
    """
    id: str
    name: str
    owner_id: str
    plan: str = "business"
    created_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert organization model instance to a dictionary representation."""
        return asdict(self)


@dataclass
class WorkspaceModel:
    """Data model representing a Workspace entity.

    Attributes:
        id (str): Unique workspace ID.
        org_id (str): Parent organization ID.
        name (str): Workspace display name.
        department (str): Department associated with workspace (default: 'General').
        created_at (str, optional): ISO timestamp of creation date.
    """
    id: str
    org_id: str
    name: str
    department: str = "General"
    created_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert workspace model instance to a dictionary representation."""
        return asdict(self)


def init_workspaces_db() -> None:
    """Initializes SQLite organizations, workspaces, teams, and team members tables."""
    with db.get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS organizations (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                owner_id TEXT NOT NULL,
                plan TEXT DEFAULT 'business',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS workspaces (
                id TEXT PRIMARY KEY,
                org_id TEXT NOT NULL,
                name TEXT NOT NULL,
                department TEXT DEFAULT 'General',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (org_id) REFERENCES organizations(id) ON DELETE CASCADE
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS teams (
                id TEXT PRIMARY KEY,
                workspace_id TEXT NOT NULL,
                name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (workspace_id) REFERENCES workspaces(id) ON DELETE CASCADE
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS team_members (
                team_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                role TEXT DEFAULT 'employee',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (team_id, user_id),
                FOREIGN KEY (team_id) REFERENCES teams(id) ON DELETE CASCADE
            )
        """)


# Auto-initialize database tables on module import
init_workspaces_db()


class WorkspaceManager:
    """Workspace Manager Subsystem for organization and workspace operations."""

    def __init__(self):
        """Initializes WorkspaceManager and ensures DB tables exist."""
        init_workspaces_db()

    def create_organization(
        self, name: str, owner_id: str, plan: str = "business"
    ) -> Dict[str, Any]:
        """Creates a new organization.

        Args:
            name (str): Organization name.
            owner_id (str): User ID of the owner.
            plan (str): Subscription plan (default: 'business').

        Returns:
            Dict[str, Any]: Success status and organization dictionary or error message.
        """
        clean_name = name.strip() if name else ""
        if not clean_name:
            return {"success": False, "error": "Organization name cannot be empty."}

        org_id = f"org_{uuid.uuid4().hex[:8]}"
        created_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        try:
            with db.get_connection() as conn:
                conn.execute(
                    """
                    INSERT INTO organizations (id, name, owner_id, plan, created_at)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (org_id, clean_name, owner_id, plan, created_at),
                )

            org_model = OrganizationModel(
                id=org_id,
                name=clean_name,
                owner_id=owner_id,
                plan=plan,
                created_at=created_at,
            )
            logger.info(
                "WORKSPACE_MANAGER",
                f"Created organization '{clean_name}' (ID: {org_id})",
            )
            return {"success": True, "org": org_model.to_dict()}
        except Exception as e:
            logger.error(
                "WORKSPACE_MANAGER",
                f"Failed to create organization '{clean_name}': {str(e)}",
            )
            return {"success": False, "error": str(e)}

    def get_organization(self, org_id: str) -> Dict[str, Any]:
        """Retrieves organization details by org_id.

        Args:
            org_id (str): Organization ID to fetch.

        Returns:
            Dict[str, Any]: Success status and organization dict, or error message.
        """
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id, name, owner_id, plan, created_at FROM organizations WHERE id = ?",
                    (org_id,),
                )
                row = cursor.fetchone()

            if not row:
                return {
                    "success": False,
                    "error": f"Organization with ID '{org_id}' not found.",
                }

            org_model = OrganizationModel(
                id=row["id"],
                name=row["name"],
                owner_id=row["owner_id"],
                plan=row["plan"],
                created_at=str(row["created_at"]) if row["created_at"] else None,
            )
            return {"success": True, "org": org_model.to_dict()}
        except Exception as e:
            logger.error(
                "WORKSPACE_MANAGER",
                f"Failed to retrieve organization '{org_id}': {str(e)}",
            )
            return {"success": False, "error": str(e)}

    def create_workspace(
        self, org_id: str, name: str, department: str = "General"
    ) -> Dict[str, Any]:
        """Creates a new workspace within an organization.

        Args:
            org_id (str): Parent organization ID.
            name (str): Workspace name.
            department (str): Department associated with workspace (default: 'General').

        Returns:
            Dict[str, Any]: Success status and workspace dictionary or error message.
        """
        clean_name = name.strip() if name else ""
        if not clean_name:
            return {"success": False, "error": "Workspace name cannot be empty."}

        ws_id = f"ws_{uuid.uuid4().hex[:8]}"
        created_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        try:
            with db.get_connection() as conn:
                conn.execute(
                    """
                    INSERT INTO workspaces (id, org_id, name, department, created_at)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (ws_id, org_id, clean_name, department, created_at),
                )

            ws_model = WorkspaceModel(
                id=ws_id,
                org_id=org_id,
                name=clean_name,
                department=department,
                created_at=created_at,
            )
            logger.info(
                "WORKSPACE_MANAGER",
                f"Created workspace '{clean_name}' (ID: {ws_id}) in Org '{org_id}'",
            )
            return {"success": True, "workspace": ws_model.to_dict()}
        except Exception as e:
            logger.error(
                "WORKSPACE_MANAGER",
                f"Failed to create workspace '{clean_name}': {str(e)}",
            )
            return {"success": False, "error": str(e)}

    def list_workspaces(self, org_id: str) -> List[Dict[str, Any]]:
        """Lists all workspaces under a specified organization.

        Args:
            org_id (str): Organization ID to list workspaces for.

        Returns:
            List[Dict[str, Any]]: List of workspace dictionaries.
        """
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id, org_id, name, department, created_at FROM workspaces WHERE org_id = ?",
                    (org_id,),
                )
                rows = cursor.fetchall()

            workspaces = []
            for row in rows:
                ws_model = WorkspaceModel(
                    id=row["id"],
                    org_id=row["org_id"],
                    name=row["name"],
                    department=row["department"],
                    created_at=str(row["created_at"]) if row["created_at"] else None,
                )
                workspaces.append(ws_model.to_dict())

            return workspaces
        except Exception as e:
            logger.error(
                "WORKSPACE_MANAGER",
                f"Failed to list workspaces for org '{org_id}': {str(e)}",
            )
            return []

    def create_team(self, workspace_id: str, name: str) -> Dict[str, Any]:
        """Creates a new team inside a workspace."""
        clean_name = name.strip()
        if not clean_name:
            return {"success": False, "error": "Team name cannot be empty."}
        team_id = f"team_{uuid.uuid4().hex[:8]}"
        created_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            with db.get_connection() as conn:
                conn.execute(
                    "INSERT INTO teams (id, workspace_id, name, created_at) VALUES (?, ?, ?, ?)",
                    (team_id, workspace_id, clean_name, created_at)
                )
            logger.info("WORKSPACE_MANAGER", f"Created team '{clean_name}' (ID: {team_id}) in Workspace '{workspace_id}'")
            return {"success": True, "team": {"id": team_id, "workspace_id": workspace_id, "name": clean_name, "created_at": created_at}}
        except Exception as e:
            logger.error("WORKSPACE_MANAGER", f"Failed to create team '{clean_name}': {str(e)}")
            return {"success": False, "error": str(e)}

    def add_team_member(self, team_id: str, user_id: str, role: str = "employee") -> Dict[str, Any]:
        """Adds/invites a user to a team."""
        created_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            with db.get_connection() as conn:
                conn.execute(
                    "INSERT INTO team_members (team_id, user_id, role, created_at) VALUES (?, ?, ?, ?)",
                    (team_id, user_id, role, created_at)
                )
            logger.info("WORKSPACE_MANAGER", f"Added user '{user_id}' to team '{team_id}' with role '{role}'")
            return {"success": True, "member": {"team_id": team_id, "user_id": user_id, "role": role}}
        except Exception as e:
            logger.error("WORKSPACE_MANAGER", f"Failed to add member to team '{team_id}': {str(e)}")
            return {"success": False, "error": str(e)}

    def list_teams(self, workspace_id: str) -> List[Dict[str, Any]]:
        """Lists all teams under a workspace."""
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, workspace_id, name, created_at FROM teams WHERE workspace_id = ?", (workspace_id,))
                rows = cursor.fetchall()
            return [{"id": r["id"], "workspace_id": r["workspace_id"], "name": r["name"], "created_at": str(r["created_at"])} for r in rows]
        except Exception as e:
            logger.error("WORKSPACE_MANAGER", f"Failed to list teams for workspace '{workspace_id}': {str(e)}")
            return []


# Global WorkspaceManager Singleton
workspace_manager = WorkspaceManager()
