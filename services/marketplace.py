"""
Agent Marketplace Service
=========================

Provides a registry-based marketplace for discovering, activating, and
managing AI agents.  Each agent entry carries lightweight metadata
(name, description, category, status, version) so that callers can
browse or search without loading the actual agent implementation.

Usage::

    from services.marketplace import marketplace

    for agent in marketplace.list_agents():
        print(agent["name"], agent["status"])

    marketplace.activate_agent("Research Agent")
"""

from __future__ import annotations

from typing import Dict, List, Optional


class AgentMarketplace:
    """Central registry of marketplace agents.

    The marketplace stores agent metadata in an internal dictionary keyed
    by agent name.  It is **not** responsible for running agents – only
    for cataloguing them and toggling their availability.

    Attributes:
        _registry: Internal mapping of agent name → metadata dict.
    """

    def __init__(self) -> None:
        """Initialise the marketplace with the default set of agents."""

        self._registry: Dict[str, Dict] = {}

        _defaults = [
            {
                "name": "Marketing Agent",
                "description": "Generates marketing strategies, campaign plans, and promotional content.",
                "category": "marketing",
                "status": "active",
                "version": "1.0.0",
            },
            {
                "name": "Sales Agent",
                "description": "Handles lead qualification, pipeline management, and sales outreach drafts.",
                "category": "sales",
                "status": "active",
                "version": "1.0.0",
            },
            {
                "name": "Coding Agent",
                "description": "Assists with code generation, debugging, and technical architecture.",
                "category": "development",
                "status": "active",
                "version": "1.0.0",
            },
            {
                "name": "Research Agent",
                "description": "Performs deep research, summarises papers, and compiles literature reviews.",
                "category": "research",
                "status": "active",
                "version": "1.0.0",
            },
            {
                "name": "Finance Agent",
                "description": "Provides financial analysis, budgeting assistance, and expense tracking.",
                "category": "finance",
                "status": "active",
                "version": "1.0.0",
            },
            {
                "name": "Writing Agent",
                "description": "Drafts long-form content, blog posts, emails, and creative writing.",
                "category": "writing",
                "status": "active",
                "version": "1.0.0",
            },
        ]

        for agent in _defaults:
            self._registry[agent["name"]] = agent

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def list_agents(self) -> List[Dict]:
        """Return a list of all registered agents.

        Returns:
            A list of metadata dicts, one per agent, sorted by name.
        """

        return sorted(self._registry.values(), key=lambda a: a["name"])

    def get_agent(self, name: str) -> Optional[Dict]:
        """Look up a single agent by its exact name.

        Args:
            name: The exact display name of the agent
                  (e.g. ``"Coding Agent"``).

        Returns:
            The agent's metadata dict, or ``None`` if no agent with
            that name is registered.
        """

        return self._registry.get(name)

    def activate_agent(self, name: str) -> Dict:
        """Set an agent's status to ``"active"``.

        Args:
            name: The exact display name of the agent.

        Returns:
            The updated metadata dict.

        Raises:
            KeyError: If the agent is not found in the registry.
        """

        if name not in self._registry:
            raise KeyError(f"Agent '{name}' not found in the marketplace.")

        self._registry[name]["status"] = "active"
        return self._registry[name]

    def deactivate_agent(self, name: str) -> Dict:
        """Set an agent's status to ``"inactive"``.

        Args:
            name: The exact display name of the agent.

        Returns:
            The updated metadata dict.

        Raises:
            KeyError: If the agent is not found in the registry.
        """

        if name not in self._registry:
            raise KeyError(f"Agent '{name}' not found in the marketplace.")

        self._registry[name]["status"] = "inactive"
        return self._registry[name]

    def search_agents(self, query: str) -> List[Dict]:
        """Search agents by a case-insensitive substring match.

        The *query* is matched against the agent's **name**,
        **description**, and **category** fields.

        Args:
            query: The search term (case-insensitive).

        Returns:
            A list of matching metadata dicts, sorted by name.
        """

        query_lower = query.lower()
        results: List[Dict] = []

        for agent in self._registry.values():
            if (
                query_lower in agent["name"].lower()
                or query_lower in agent["description"].lower()
                or query_lower in agent["category"].lower()
            ):
                results.append(agent)

        return sorted(results, key=lambda a: a["name"])


# ------------------------------------------------------------------
# Module-level singleton
# ------------------------------------------------------------------

marketplace = AgentMarketplace()
"""Pre-initialised :class:`AgentMarketplace` instance for convenient
import-and-use access across the application."""
