"""
Unit tests for AutomationEngineService, WorkflowTrigger, and WorkflowAction.
"""

import unittest
import uuid
from services.automation_engine import (
    AutomationEngineService,
    WorkflowAction,
    WorkflowTrigger,
    automation_engine,
)


class TestAutomationEngineService(unittest.TestCase):
    """Test cases for AutomationEngineService."""

    def test_enums(self):
        """Test WorkflowTrigger and WorkflowAction enum values."""
        self.assertEqual(WorkflowTrigger.DOCUMENT_UPLOADED.value, "document_uploaded")
        self.assertEqual(WorkflowTrigger.SCHEDULED_CRON.value, "scheduled_cron")
        self.assertEqual(WorkflowTrigger.TASK_FINISHED.value, "task_finished")

        self.assertEqual(WorkflowAction.GENERATE_REPORT.value, "generate_report")
        self.assertEqual(WorkflowAction.SEND_EMAIL.value, "send_email")
        self.assertEqual(WorkflowAction.CREATE_ISSUE.value, "create_issue")
        self.assertEqual(WorkflowAction.INDEX_DOCUMENT.value, "index_document")

    def test_create_and_get_workflow(self):
        """Test workflow creation and retrieval by ID."""
        ws_id = f"ws_test_{uuid.uuid4().hex[:8]}"
        name = "Auto Index Uploaded Docs"
        trigger = WorkflowTrigger.DOCUMENT_UPLOADED
        action = WorkflowAction.INDEX_DOCUMENT
        config = {"extract_metadata": True, "target_folder": "/docs"}

        wf = automation_engine.create_workflow(
            workspace_id=ws_id,
            name=name,
            trigger_type=trigger,
            action_type=action,
            config=config,
        )

        self.assertIn("id", wf)
        self.assertEqual(wf["workspace_id"], ws_id)
        self.assertEqual(wf["name"], name)
        self.assertEqual(wf["trigger_type"], "document_uploaded")
        self.assertEqual(wf["action_type"], "index_document")
        self.assertEqual(wf["config"], config)
        self.assertTrue(wf["is_active"])

        # Fetch using get_workflow
        fetched = automation_engine.get_workflow(wf["id"])
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched["id"], wf["id"])
        self.assertEqual(fetched["name"], name)
        self.assertEqual(fetched["trigger_type"], "document_uploaded")
        self.assertEqual(fetched["action_type"], "index_document")
        self.assertEqual(fetched["config"], config)
        self.assertTrue(fetched["is_active"])

    def test_create_workflow_with_strings_and_default_config(self):
        """Test workflow creation when trigger/action are passed as strings and config is omitted."""
        ws_id = f"ws_test_{uuid.uuid4().hex[:8]}"
        wf = automation_engine.create_workflow(
            workspace_id=ws_id,
            name="Cron Report",
            trigger_type="scheduled_cron",
            action_type="generate_report",
        )

        self.assertEqual(wf["trigger_type"], "scheduled_cron")
        self.assertEqual(wf["action_type"], "generate_report")
        self.assertEqual(wf["config"], {})

    def test_list_workflows(self):
        """Test listing workflows for a specific workspace."""
        ws_id = f"ws_list_{uuid.uuid4().hex[:8]}"

        # Initially empty
        self.assertEqual(automation_engine.list_workflows(ws_id), [])

        # Create two workflows
        wf1 = automation_engine.create_workflow(
            workspace_id=ws_id,
            name="Workflow 1",
            trigger_type=WorkflowTrigger.TASK_FINISHED,
            action_type=WorkflowAction.SEND_EMAIL,
            config={"recipient": "dev@example.com"},
        )
        wf2 = automation_engine.create_workflow(
            workspace_id=ws_id,
            name="Workflow 2",
            trigger_type=WorkflowTrigger.DOCUMENT_UPLOADED,
            action_type=WorkflowAction.CREATE_ISSUE,
            config={"priority": "high"},
        )

        listed = automation_engine.list_workflows(ws_id)
        self.assertEqual(len(listed), 2)
        wf_ids = [w["id"] for w in listed]
        self.assertIn(wf1["id"], wf_ids)
        self.assertIn(wf2["id"], wf_ids)

    def test_get_nonexistent_workflow(self):
        """Test get_workflow returns None for a non-existent ID."""
        self.assertIsNone(automation_engine.get_workflow(99999999))


if __name__ == "__main__":
    unittest.main()
