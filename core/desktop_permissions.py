"""
core/desktop_permissions.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~
Permission & Safety Evaluation Layer for JARVIS Desktop Productivity Assistant.

Responsibilities:
- Classify action risk levels (SAFE vs DESTRUCTIVE)
- Require explicit user confirmation before executing destructive operations
"""

from typing import Dict, Any, Optional


class DesktopPermissionLayer:
    """Evaluates safety policies and permissions for desktop OS actions."""

    DESTRUCTIVE_ACTIONS = {
        "close_app",
        "delete_file",
        "overwrite_file",
        "move_system_file",
        "kill_process",
    }

    def evaluate_permission(
        self, action: str, params: Optional[Dict[str, Any]] = None, is_confirmed: bool = False
    ) -> Dict[str, Any]:
        """Evaluates whether a desktop action is permitted or requires confirmation."""
        params = params or {}
        action_lower = action.lower().strip()

        if action_lower in self.DESTRUCTIVE_ACTIONS:
            if not is_confirmed:
                return {
                    "allowed": False,
                    "requires_confirmation": True,
                    "risk_level": "DESTRUCTIVE",
                    "action": action,
                    "params": params,
                    "prompt": f"⚠️ Action '{action}' is potentially destructive. Please confirm execution for parameters: {params}",
                }

        return {
            "allowed": True,
            "requires_confirmation": False,
            "risk_level": "DESTRUCTIVE" if action_lower in self.DESTRUCTIVE_ACTIONS else "SAFE",
            "action": action,
            "params": params,
            "prompt": "Action cleared for execution.",
        }


# Global Singleton Instance
desktop_permissions = DesktopPermissionLayer()
