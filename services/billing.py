"""
Billing and quota enforcement service for J.A.R.V.I.S. AI OS.

Defines plan tiers with daily query limits and exposes helpers to check
whether a user is still within their quota. Relies on the
:pymod:`services.analytics` singleton for live usage data.
"""

from typing import Any, Dict, Tuple

from services.analytics import analytics


# ------------------------------------------------------------------ #
# Plan tier definitions
# ------------------------------------------------------------------ #

PLAN_TIERS: Dict[str, Dict[str, Any]] = {
    "free": {
        "label": "Free",
        "queries_per_day": 100,
        "description": "Basic access with up to 100 queries per day.",
    },
    "pro": {
        "label": "Pro",
        "queries_per_day": 1_000,
        "description": "Professional tier with up to 1,000 queries per day.",
    },
    "business": {
        "label": "Business",
        "queries_per_day": 10_000,
        "description": "Business tier with up to 10,000 queries per day.",
    },
    "enterprise": {
        "label": "Enterprise",
        "queries_per_day": -1,  # unlimited
        "description": "Enterprise tier with unlimited queries.",
    },
}


class BillingService:
    """Billing and quota-enforcement service.

    Uses the shared :class:`~services.analytics.UsageAnalytics` singleton
    to look up a user's current query count, then compares it against the
    daily limit defined for their plan tier.

    Note:
        The current implementation tracks queries cumulatively (not
        per-day). A production deployment should reset or bucket counts
        on a calendar-day boundary. This version is suitable for MVP /
        demo use and can be extended with a daily-reset mechanism.
    """

    def __init__(self) -> None:
        """Initialise the billing service."""
        self._plans = PLAN_TIERS

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def check_quota(
        self, user_id: str, plan: str = "free"
    ) -> Tuple[bool, int]:
        """Check whether *user_id* is within their daily query quota.

        Args:
            user_id: Unique identifier for the user.
            plan: Plan tier key (case-insensitive). Must be one of
                ``free``, ``pro``, ``business``, or ``enterprise``.

        Returns:
            A tuple of ``(allowed, remaining)`` where *allowed* is
            ``True`` when the user may still issue queries and
            *remaining* is the number of queries left before the limit
            is reached.  For the ``enterprise`` plan *remaining* is
            always ``-1`` (unlimited).

        Raises:
            ValueError: If *plan* is not a recognised tier.
        """
        plan_key = plan.lower()
        if plan_key not in self._plans:
            raise ValueError(
                f"Unknown plan '{plan}'. "
                f"Valid plans: {', '.join(self._plans)}"
            )

        plan_info = self._plans[plan_key]
        limit = plan_info["queries_per_day"]

        # Enterprise has no cap.
        if limit == -1:
            return True, -1

        user_stats = analytics.get_user_stats(user_id)
        used = user_stats["total_queries"]
        remaining = max(0, limit - used)
        allowed = remaining > 0

        return allowed, remaining

    def get_plan_info(self, plan: str) -> Dict[str, Any]:
        """Return metadata for a plan tier.

        Args:
            plan: Plan tier key (case-insensitive).

        Returns:
            A dictionary containing ``label``, ``queries_per_day``, and
            ``description`` for the requested plan.

        Raises:
            ValueError: If *plan* is not a recognised tier.
        """
        plan_key = plan.lower()
        if plan_key not in self._plans:
            raise ValueError(
                f"Unknown plan '{plan}'. "
                f"Valid plans: {', '.join(self._plans)}"
            )

        return dict(self._plans[plan_key])


# Module-level singleton – import and use throughout the application.
billing = BillingService()
