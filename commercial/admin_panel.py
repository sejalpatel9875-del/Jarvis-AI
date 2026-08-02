"""
commercial/admin_panel.py
~~~~~~~~~~~~~~~~~~~~~~~~~
Super-Admin Control Panel Service for JARVIS AI OS.
"""

from typing import Dict, List, Any
from commercial.subscriptions import subscription_manager, TIER_LIMITS
from commercial.feature_flags import feature_flags
from commercial.backups import backup_manager


class SuperAdminPanel:
    """Provides administrative controls for SaaS organization management."""

    def override_usage_limit(self, org_id: str, new_limit: int) -> Dict[str, Any]:
        """Overrides the daily API call limit for a specific organization."""
        sub = subscription_manager.get_subscription(org_id)
        sub["limits"]["max_api_calls_per_day"] = new_limit
        return {"success": True, "org_id": org_id, "new_daily_limit": new_limit}

    def suspend_organization(self, org_id: str, reason: str = "Policy Violation") -> Dict[str, Any]:
        """Suspends an organization account."""
        sub = subscription_manager.get_subscription(org_id)
        sub["status"] = "SUSPENDED"
        return {"success": True, "org_id": org_id, "status": "SUSPENDED", "reason": reason}

    def reactivate_organization(self, org_id: str) -> Dict[str, Any]:
        """Reactivates a suspended organization account."""
        sub = subscription_manager.get_subscription(org_id)
        sub["status"] = "ACTIVE"
        return {"success": True, "org_id": org_id, "status": "ACTIVE"}

    def get_system_admin_summary(self) -> Dict[str, Any]:
        """Returns executive overview of all SaaS organizations, backups, and feature flags."""
        return {
            "total_organizations": len(subscription_manager.org_subscriptions),
            "feature_flags": feature_flags.global_killswitches,
            "disaster_recovery": backup_manager.get_disaster_recovery_status(),
        }


# Singleton Instance
admin_panel = SuperAdminPanel()
