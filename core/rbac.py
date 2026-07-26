"""
Purpose:
Role-Based Access Control (RBAC) Subsystem for Jarvis AI OS.

Responsibilities:
- Define Role enum/constants and permission matrices
- Check authorization for actions per user role
- Process organization member invitations with permission verification

Dependencies:
- services/logger.py
"""

from enum import Enum
from typing import Dict, List, Any, Union
from services.logger import logger


class Role(str, Enum):
    """Role constants for Role-Based Access Control."""
    OWNER = "owner"
    ADMIN = "admin"
    MANAGER = "manager"
    EMPLOYEE = "employee"
    GUEST = "guest"


PERMISSION_MATRIX: Dict[str, List[Union[Role, str]]] = {
    "delete_workspace": [Role.OWNER],
    "invite_users": [Role.OWNER, Role.ADMIN],
    "run_ai": [Role.OWNER, Role.ADMIN, Role.MANAGER, Role.EMPLOYEE, Role.GUEST],
    "view_reports": [Role.OWNER, Role.ADMIN, Role.MANAGER],
}


class RBACService:
    """Role-Based Access Control Service for authorization and member invitations."""

    def check_permission(self, role: Union[Role, str], action: str) -> bool:
        """Checks whether a given role is authorized to perform a specific action.

        Args:
            role (Union[Role, str]): Role enum or string representation.
            action (str): Action name to check permission for.

        Returns:
            bool: True if the role has permission, False otherwise.
        """
        if not role or not action:
            return False

        role_str = role.value if hasattr(role, "value") else str(role)
        role_str = role_str.lower().strip()

        allowed_roles = PERMISSION_MATRIX.get(action, [])
        allowed_roles_str = [
            r.value if hasattr(r, "value") else str(r).lower()
            for r in allowed_roles
        ]

        return role_str in allowed_roles_str

    def invite_member(
        self, org_id: str, inviter_role: Union[Role, str], email: str, role: Union[Role, str]
    ) -> Dict[str, Any]:
        """Invites a new member to an organization if the inviter has sufficient permissions.

        Args:
            org_id (str): Target organization ID.
            inviter_role (Union[Role, str]): Role of the user initiating the invite.
            email (str): Email address of the user being invited.
            role (Union[Role, str]): Target role to assign to the invited user.

        Returns:
            Dict[str, Any]: Success status dictionary with invite details or error message.
        """
        if not self.check_permission(inviter_role, "invite_users"):
            logger.warning(
                "RBAC_SERVICE",
                f"Unauthorized invitation attempt by role '{inviter_role}' for org '{org_id}'",
            )
            return {
                "success": False,
                "error": f"Role '{inviter_role}' is not authorized to invite members.",
            }

        clean_email = email.strip().lower() if email else ""
        if not clean_email:
            return {"success": False, "error": "Email address cannot be empty."}

        target_role_str = role.value if hasattr(role, "value") else str(role)

        logger.info(
            "RBAC_SERVICE",
            f"Invited '{clean_email}' as '{target_role_str}' to org '{org_id}'",
        )

        return {
            "success": True,
            "org_id": org_id,
            "email": clean_email,
            "role": target_role_str,
            "status": "invited",
            "message": f"Successfully invited '{clean_email}' as '{target_role_str}' to organization '{org_id}'.",
        }


# Global RBACService Singleton
rbac_service = RBACService()
