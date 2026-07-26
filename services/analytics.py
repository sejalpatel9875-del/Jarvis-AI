"""
Usage analytics service for J.A.R.V.I.S. AI OS.

Provides thread-safe, in-memory tracking of per-user usage statistics
including query counts, estimated token consumption, tool usage, and
agent usage. Designed as a module-level singleton for shared access
across the application.
"""

import threading
from collections import Counter
from typing import Any, Dict, Optional


class UsageAnalytics:
    """Thread-safe, in-memory usage analytics tracker.

    Maintains per-user statistics including total queries, estimated token
    consumption, and frequency counters for tools and agents used. All
    public methods are guarded by a threading lock to ensure safe access
    from concurrent request handlers.

    Attributes:
        _lock: Threading lock for synchronising all read/write access.
        _user_stats: Internal dict mapping user IDs to their stats dicts.
    """

    def __init__(self) -> None:
        """Initialise an empty analytics store with a threading lock."""
        self._lock = threading.Lock()
        self._user_stats: Dict[str, Dict[str, Any]] = {}

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _ensure_user(self, user_id: str) -> Dict[str, Any]:
        """Return the stats dict for *user_id*, creating it if absent.

        This must only be called while ``self._lock`` is held.

        Args:
            user_id: Unique identifier for the user.

        Returns:
            The mutable stats dictionary for the given user.
        """
        if user_id not in self._user_stats:
            self._user_stats[user_id] = {
                "total_queries": 0,
                "total_tokens_estimated": 0,
                "tools_used": Counter(),
                "agents_used": Counter(),
            }
        return self._user_stats[user_id]

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def record_query(
        self,
        user_id: str,
        tokens_est: int = 0,
        tool_name: Optional[str] = None,
        agent_name: Optional[str] = None,
    ) -> None:
        """Record a single query for a user.

        Increments the user's query count, adds the estimated token cost,
        and – when provided – bumps the counters for the tool and agent
        that were involved.

        Args:
            user_id: Unique identifier for the user.
            tokens_est: Estimated number of tokens consumed by this query.
            tool_name: Optional name of the tool invoked during the query.
            agent_name: Optional name of the agent that handled the query.
        """
        with self._lock:
            stats = self._ensure_user(user_id)
            stats["total_queries"] += 1
            stats["total_tokens_estimated"] += tokens_est
            if tool_name:
                stats["tools_used"][tool_name] += 1
            if agent_name:
                stats["agents_used"][agent_name] += 1

    def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        """Return a snapshot of usage statistics for a single user.

        The returned dictionary contains:
        - ``total_queries`` (int): Cumulative number of queries recorded.
        - ``total_tokens_estimated`` (int): Cumulative estimated tokens.
        - ``tools_used`` (dict): Mapping of tool name → invocation count.
        - ``agents_used`` (dict): Mapping of agent name → invocation count.

        If the user has no recorded activity an empty-state dict with
        zeroed counters is returned.

        Args:
            user_id: Unique identifier for the user.

        Returns:
            A plain-dict copy of the user's statistics (safe to mutate).
        """
        with self._lock:
            stats = self._ensure_user(user_id)
            return {
                "user_id": user_id,
                "total_queries": stats["total_queries"],
                "total_tokens_estimated": stats["total_tokens_estimated"],
                "tools_used": dict(stats["tools_used"]),
                "agents_used": dict(stats["agents_used"]),
            }

    def get_global_stats(self) -> Dict[str, Any]:
        """Return aggregated usage statistics across all tracked users.

        The returned dictionary contains:
        - ``total_users`` (int): Number of distinct users recorded.
        - ``total_queries`` (int): Sum of all users' query counts.
        - ``total_tokens_estimated`` (int): Sum of all estimated tokens.
        - ``tools_used`` (dict): Merged tool-name → count across users.
        - ``agents_used`` (dict): Merged agent-name → count across users.

        Returns:
            A plain-dict snapshot of the global statistics.
        """
        with self._lock:
            total_queries = 0
            total_tokens = 0
            tools_agg: Counter = Counter()
            agents_agg: Counter = Counter()

            for stats in self._user_stats.values():
                total_queries += stats["total_queries"]
                total_tokens += stats["total_tokens_estimated"]
                tools_agg.update(stats["tools_used"])
                agents_agg.update(stats["agents_used"])

            return {
                "total_users": len(self._user_stats),
                "total_queries": total_queries,
                "total_tokens_estimated": total_tokens,
                "tools_used": dict(tools_agg),
                "agents_used": dict(agents_agg),
            }


# Module-level singleton – import and use throughout the application.
analytics = UsageAnalytics()
