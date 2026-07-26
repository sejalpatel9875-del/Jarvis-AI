"""
Purpose:
Global Unified Enterprise Search Engine for Jarvis AI OS (Sprint v4.7).

Responsibilities:
- Search across workspace leads, deals, workflows, and activity feed
"""

from typing import Dict, Any, List
from services.crm_engine import crm_engine
from services.deal_pipeline import deal_pipeline
from services.automation_engine import automation_engine
from services.activity_feed import activity_feed


class GlobalSearchEngine:
    """Global Enterprise Unified Search Engine."""

    def __init__(
        self,
        crm_engine_service=crm_engine,
        deal_pipeline_service=deal_pipeline,
        automation_engine_service=automation_engine,
        activity_feed_service=activity_feed
    ):
        """Initializes GlobalSearchEngine with default or injected service singletons."""
        self.crm_engine = crm_engine_service
        self.deal_pipeline = deal_pipeline_service
        self.automation_engine = automation_engine_service
        self.activity_feed = activity_feed_service

    def search_all(self, workspace_id: str = "default", query: str = "") -> Dict[str, Any]:
        """Searches across workspace leads, deals, workflows, and activity feed for matching query terms.

        Args:
            workspace_id: Target workspace identifier. Defaults to 'default'.
            query: Search query string. Defaults to ''.

        Returns:
            Dict containing query, workspace_id, leads, deals, workflows, activity_feed, total_matches.
        """
        q = (query or "").lower().strip()

        # 1. Search Leads
        all_leads = self.crm_engine.list_leads(workspace_id)
        matching_leads = [
            l for l in all_leads
            if not q or q in l.get("name", "").lower() or q in l.get("email", "").lower() or q in l.get("company", "").lower() or q in l.get("status", "").lower()
        ]

        # 2. Search Deals
        if hasattr(self.deal_pipeline, "list_deals"):
            all_deals = self.deal_pipeline.list_deals(workspace_id)
        else:
            all_deals = []
        matching_deals = [
            d for d in all_deals
            if not q or q in d.get("title", "").lower() or q in d.get("stage", "").lower()
        ]

        # 3. Search Workflows
        all_workflows = self.automation_engine.list_workflows(workspace_id)
        matching_workflows = [
            w for w in all_workflows
            if not q or q in w.get("name", "").lower() or q in w.get("trigger_type", "").lower() or q in w.get("action_type", "").lower()
        ]

        # 4. Search Activity Feed
        all_activities = self.activity_feed.get_activity_feed(workspace_id, limit=100)
        matching_activities = [
            a for a in all_activities
            if not q or q in a.get("action", "").lower() or q in a.get("details", "").lower() or q in a.get("actor_name", "").lower()
        ]

        total_matches = len(matching_leads) + len(matching_deals) + len(matching_workflows) + len(matching_activities)

        return {
            "query": query,
            "workspace_id": workspace_id,
            "leads": matching_leads,
            "deals": matching_deals,
            "workflows": matching_workflows,
            "activity_feed": matching_activities,
            "total_matches": total_matches
        }


# Global Singleton
global_search = GlobalSearchEngine()
