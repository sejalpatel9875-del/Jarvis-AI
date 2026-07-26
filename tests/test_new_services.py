"""
Unit tests for ReportGeneratorService and KnowledgeTimelineService.
"""

import unittest
import uuid
from services.report_generator import report_generator, ReportGeneratorService
from services.knowledge_timeline import knowledge_timeline, KnowledgeTimelineService


class TestReportGeneratorService(unittest.TestCase):
    """Test cases for ReportGeneratorService."""

    def test_generate_executive_report_structure(self):
        """Test executive report generation contains all required sections and key formats."""
        title = "Q3 Product Architecture Strategy"
        topic = "Microservices Migration"
        context = "Evaluating monolithic codebase decomposition into independent microservices."

        result = report_generator.generate_executive_report(title=title, topic=topic, context_text=context)

        self.assertEqual(result["title"], title)
        self.assertEqual(result["topic"], topic)
        self.assertEqual(result["export_format"], "markdown")
        self.assertIn("timestamp", result)

        md = result["markdown_content"]
        self.assertIn(f"# {title}", md)
        self.assertIn("## Summary", md)
        self.assertIn("## Key Insights", md)
        self.assertIn("## Risks & Challenges", md)
        self.assertIn("## Recommendations", md)
        self.assertIn(context, md)

    def test_generate_executive_report_default_context(self):
        """Test executive report generation when context_text is omitted."""
        service = ReportGeneratorService()
        result = service.generate_executive_report(title="Executive Summary", topic="Security Audit")

        self.assertEqual(result["title"], "Executive Summary")
        self.assertEqual(result["export_format"], "markdown")

        md = result["markdown_content"]
        self.assertIn("## Summary", md)
        self.assertIn("## Key Insights", md)
        self.assertIn("## Risks & Challenges", md)
        self.assertIn("## Recommendations", md)


class TestKnowledgeTimelineService(unittest.TestCase):
    """Test cases for KnowledgeTimelineService."""

    def test_add_and_get_timeline_events(self):
        """Test adding timeline events and retrieving them per workspace."""
        ws_id = f"ws_test_{uuid.uuid4().hex[:8]}"

        # Add event 1
        event1 = knowledge_timeline.add_event(
            workspace_id=ws_id,
            event_type="DECISION",
            title="Adopted FastAPI Framework",
            description="Selected FastAPI for modern async Python REST API endpoints.",
        )
        self.assertIn("id", event1)
        self.assertEqual(event1["workspace_id"], ws_id)
        self.assertEqual(event1["event_type"], "DECISION")
        self.assertEqual(event1["title"], "Adopted FastAPI Framework")

        # Add event 2
        event2 = knowledge_timeline.add_event(
            workspace_id=ws_id,
            event_type="MILESTONE",
            title="v1.0 Release",
            description="Initial version deployed to production.",
        )
        self.assertEqual(event2["title"], "v1.0 Release")

        # Retrieve timeline
        timeline = knowledge_timeline.get_timeline(ws_id, limit=10)
        self.assertEqual(len(timeline), 2)
        # Event 2 should be first due to DESC timestamp order
        self.assertEqual(timeline[0]["id"], event2["id"])
        self.assertEqual(timeline[1]["id"], event1["id"])

    def test_get_timeline_empty_and_limit(self):
        """Test retrieving timeline for a nonexistent workspace and limit parameter."""
        ws_id = f"ws_empty_{uuid.uuid4().hex[:8]}"
        empty_timeline = knowledge_timeline.get_timeline(ws_id)
        self.assertEqual(empty_timeline, [])

        # Add 3 events and check limit parameter
        for i in range(5):
            knowledge_timeline.add_event(ws_id, "LOG", f"Log event {i}")

        limited = knowledge_timeline.get_timeline(ws_id, limit=3)
        self.assertEqual(len(limited), 3)


if __name__ == "__main__":
    unittest.main()
