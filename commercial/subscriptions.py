"""
commercial/subscriptions.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Subscription Tiers & Usage Limits Enforcer for JARVIS AI OS.
Tiers:
- FREE: 100 API calls/day, 1 Seat, 50MB Storage, Basic Agents
- PRO: 10,000 API calls/day, 5 Seats, 5GB Storage, All 8 Agents, Desktop Assistant
- ENTERPRISE: Unlimited API calls, Unlimited Seats, 500GB Storage, MCP Protocol, Dedicated SLA
"""

import time
from typing import Dict, Any, Optional


class SubscriptionTier:
    FREE = "FREE"
    PRO = "PRO"
    ENTERPRISE = "ENTERPRISE"


TIER_LIMITS: Dict[str, Dict[str, Any]] = {
    SubscriptionTier.FREE: {
        "max_api_calls_per_day": 100,
        "max_seats": 1,
        "max_storage_mb": 50,
        "allowed_agents": ["ceo", "developer", "research"],
        "mcp_enabled": False,
        "desktop_assistant_enabled": False,
    },
    SubscriptionTier.PRO: {
        "max_api_calls_per_day": 10000,
        "max_seats": 5,
        "max_storage_mb": 5120,
        "allowed_agents": [
            "ceo",
            "developer",
            "research",
            "automation",
            "memory",
            "voice",
            "planner",
            "validator",
        ],
        "mcp_enabled": False,
        "desktop_assistant_enabled": True,
    },
    SubscriptionTier.ENTERPRISE: {
        "max_api_calls_per_day": 999999999,
        "max_seats": 9999,
        "max_storage_mb": 512000,
        "allowed_agents": [
            "ceo",
            "developer",
            "research",
            "automation",
            "memory",
            "voice",
            "planner",
            "validator",
        ],
        "mcp_enabled": True,
        "desktop_assistant_enabled": True,
    },
}


class SubscriptionManager:
    """Manages organization subscriptions, usage meters, and hard limit enforcement."""

    def __init__(self):
        # org_id -> {tier, usage_today, created_at}
        self.org_subscriptions: Dict[str, Dict[str, Any]] = {}
        self.daily_usage: Dict[str, int] = {}

    def get_subscription(self, org_id: str) -> Dict[str, Any]:
        """Returns subscription details and current limits for an organization."""
        if org_id not in self.org_subscriptions:
            self.org_subscriptions[org_id] = {
                "org_id": org_id,
                "tier": SubscriptionTier.FREE,
                "created_at": int(time.time()),
                "status": "ACTIVE",
            }

        sub = self.org_subscriptions[org_id]
        limits = TIER_LIMITS[sub["tier"]]
        usage_today = self.daily_usage.get(org_id, 0)

        return {
            "org_id": org_id,
            "tier": sub["tier"],
            "status": sub["status"],
            "usage_today": usage_today,
            "limits": limits,
            "has_remaining_quota": usage_today < limits["max_api_calls_per_day"],
        }

    def upgrade_subscription(self, org_id: str, new_tier: str) -> Dict[str, Any]:
        """Upgrades or downgrades an organization's subscription tier."""
        if new_tier not in TIER_LIMITS:
            return {"success": False, "error": f"Invalid subscription tier: {new_tier}"}

        sub = self.get_subscription(org_id)
        sub["tier"] = new_tier
        self.org_subscriptions[org_id] = sub

        return {
            "success": True,
            "org_id": org_id,
            "new_tier": new_tier,
            "limits": TIER_LIMITS[new_tier],
        }

    def increment_and_check_limit(self, org_id: str) -> bool:
        """Increments daily API usage and returns True if under quota."""
        sub = self.get_subscription(org_id)
        max_calls = sub["limits"]["max_api_calls_per_day"]
        current = self.daily_usage.get(org_id, 0)

        if current >= max_calls:
            return False

        self.daily_usage[org_id] = current + 1
        return True


# Singleton Instance
subscription_manager = SubscriptionManager()
