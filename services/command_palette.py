"""
Purpose:
Command Palette Shortcuts Service for Jarvis AI OS (Sprint v4.7).

Responsibilities:
- Quick action registry for Ctrl + K command palette
"""

from typing import Dict, Any, List

class CommandPaletteService:
    """Command Palette Shortcuts Registry Engine."""

    def get_available_commands(self, role: str = "owner") -> List[Dict[str, Any]]:
        """Returns list of context-aware quick action commands."""
        commands = [
            {
                "id": "global_search",
                "title": "Global Enterprise Search",
                "shortcut": "Ctrl + K",
                "category": "Navigation",
                "action": "open_search_modal"
            },
            {
                "id": "create_lead",
                "title": "Create New Lead",
                "shortcut": "Ctrl + Shift + L",
                "category": "CRM",
                "action": "open_create_lead"
            },
            {
                "id": "upload_document",
                "title": "Upload & Ingest Document",
                "shortcut": "Ctrl + Shift + U",
                "category": "Knowledge",
                "action": "open_upload_modal"
            },
            {
                "id": "run_workflow",
                "title": "Build & Run Automation Workflow",
                "shortcut": "Ctrl + Shift + W",
                "category": "Automation",
                "action": "open_workflow_builder"
            },
            {
                "id": "manage_api_keys",
                "title": "Manage Workspace API Keys",
                "shortcut": "Ctrl + Shift + K",
                "category": "Settings",
                "action": "open_api_keys"
            },
            {
                "id": "open_dashboard",
                "title": "Open CEO Dashboard",
                "shortcut": "Ctrl + Shift + D",
                "category": "Navigation",
                "action": "navigate_dashboard"
            }
        ]

        role_lower = role.lower()
        if role_lower in ["viewer", "guest"]:
            # Viewer/Guest role: only Navigation and Knowledge
            commands = [c for c in commands if c["category"] not in ["Automation", "CRM", "Settings"]]

        return commands

# Global Singleton
command_palette = CommandPaletteService()
