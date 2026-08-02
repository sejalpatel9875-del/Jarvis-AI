"""
commercial/feature_flags.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~
Feature Flag Toggle Engine & System Killswitches for JARVIS AI OS.
"""

from typing import Dict, Any, List
from commercial.subscriptions import subscription_manager, TIER_LIMITS


class FeatureFlagEngine:
    """Manages system feature toggles, tier gating, and emergency killswitches."""

    def __init__(self):
        # Global emergency killswitches (flag_name -> enabled_bool)
        self.global_killswitches: Dict[str, bool] = {
            "mcp_access": True,
            "desktop_assistant": True,
            "voice_assistant": True,
            "custom_agents": True,
            "advanced_analytics": True,
        }
        # Organization specific overrides (org_id -> {flag_name: bool})
        self.org_overrides: Dict[str, Dict[str, bool]] = {}

    def is_feature_enabled(self, feature_name: str, org_id: str = "default") -> bool:
        """Evaluates whether a feature is enabled based on killswitches, tier, and overrides."""
        # 1. Check Global Emergency Killswitch
        if not self.global_killswitches.get(feature_name, True):
            return False

        # 2. Check Org Specific Override
        if org_id in self.org_overrides and feature_name in self.org_overrides[org_id]:
            return self.org_overrides[org_id][feature_name]

        # 3. Check Subscription Tier Gating
        sub = subscription_manager.get_subscription(org_id)
        limits = sub["limits"]

        if feature_name == "mcp_access":
            return limits.get("mcp_enabled", False)
        elif feature_name == "desktop_assistant":
            return limits.get("desktop_assistant_enabled", False)

        return True

    def set_global_killswitch(self, feature_name: str, enabled: bool):
        """Toggles a global emergency killswitch."""
        self.global_killswitches[feature_name] = enabled

    def set_org_override(self, org_id: str, feature_name: str, enabled: bool):
        """Sets an organization-specific feature flag override."""
        if org_id not in self.org_overrides:
            self.org_overrides[org_id] = {}
        self.org_overrides[org_id][feature_name] = enabled

    def get_all_flags(self, org_id: str = "default") -> Dict[str, bool]:
        """Returns status of all feature flags for an organization."""
        flags = [
            "mcp_access",
            "desktop_assistant",
            "voice_assistant",
            "custom_agents",
            "advanced_analytics",
        ]
        return {f: self.is_feature_enabled(f, org_id) for f in flags}


# Singleton Instance
feature_flags = FeatureFlagEngine()
