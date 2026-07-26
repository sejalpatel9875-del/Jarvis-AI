"""
Unit tests for WorkflowExecutionEngine and WorkflowSchedulerService.
"""

import unittest
import uuid
from services.workflow_execution import workflow_execution, WorkflowExecutionEngine
from services.workflow_scheduler import workflow_scheduler, WorkflowSchedulerService


class TestWorkflowExecutionEngine(unittest.TestCase):
    """Test cases for WorkflowExecutionEngine service."""

    def test_execute_workflow_success(self):
        """Test successful execution of a workflow."""
        wf_id = f"wf_test_{uuid.uuid4().hex[:8]}"
        ws_id = f"ws_test_{uuid.uuid4().hex[:8]}"

        result = workflow_execution.execute_workflow(
            workflow_id=wf_id,
            payload={"workspace_id": ws_id, "retry_count": 1},
        )

        self.assertIn("execution_id", result)
        self.assertEqual(result["workflow_id"], wf_id)
        self.assertEqual(result["workspace_id"], ws_id)
        self.assertEqual(result["status"], "SUCCESS")
        self.assertIsInstance(result["duration_ms"], float)
        self.assertEqual(result["retry_count"], 1)
        self.assertIsNone(result["error_message"])
        self.assertIn("executed_at", result)

    def test_execute_workflow_simulated_error(self):
        """Test execution failure when simulate_error flag is set."""
        wf_id = f"wf_fail_{uuid.uuid4().hex[:8]}"
        ws_id = f"ws_fail_{uuid.uuid4().hex[:8]}"

        result = workflow_execution.execute_workflow(
            workflow_id=wf_id,
            payload={
                "workspace_id": ws_id,
                "simulate_error": True,
                "error_message": "Custom failure error",
            },
        )

        self.assertEqual(result["status"], "FAILED")
        self.assertEqual(result["error_message"], "Custom failure error")

    def test_get_execution_history(self):
        """Test fetching execution history filtered by workspace_id."""
        ws_id = f"ws_hist_{uuid.uuid4().hex[:8]}"

        # Execute 3 workflows for this workspace
        for i in range(3):
            workflow_execution.execute_workflow(
                workflow_id=f"wf_step_{i}",
                payload={"workspace_id": ws_id},
            )

        history = workflow_execution.get_execution_history(ws_id, limit=10)
        self.assertEqual(len(history), 3)
        self.assertEqual(history[0]["workspace_id"], ws_id)
        self.assertEqual(history[0]["status"], "SUCCESS")

    def test_empty_workspace_history(self):
        """Test fetching execution history for empty workspace."""
        empty_history = workflow_execution.get_execution_history("nonexistent_workspace")
        self.assertEqual(empty_history, [])


class TestWorkflowSchedulerService(unittest.TestCase):
    """Test cases for WorkflowSchedulerService service."""

    def test_schedule_workflow(self):
        """Test scheduling a workflow job."""
        wf_id = f"wf_sched_{uuid.uuid4().hex[:8]}"
        cron_expr = "*/15 * * * *"

        result = workflow_scheduler.schedule_workflow(
            workflow_id=wf_id,
            cron_expression=cron_expr,
        )

        self.assertTrue(result["success"])
        self.assertIn("id", result)
        self.assertEqual(result["workflow_id"], wf_id)
        self.assertEqual(result["cron_expression"], cron_expr)
        self.assertTrue(result["is_active"])
        self.assertIn("next_run_at", result)

    def test_schedule_workflow_validation(self):
        """Test validation error for empty workflow_id or cron_expression."""
        res1 = workflow_scheduler.schedule_workflow(workflow_id="", cron_expression="* * * * *")
        self.assertFalse(res1["success"])
        self.assertIn("error", res1)

        res2 = workflow_scheduler.schedule_workflow(workflow_id="wf_1", cron_expression="")
        self.assertFalse(res2["success"])
        self.assertIn("error", res2)

    def test_list_scheduled_jobs(self):
        """Test listing scheduled jobs."""
        wf_id = f"wf_list_{uuid.uuid4().hex[:8]}"
        workflow_scheduler.schedule_workflow(wf_id, "0 0 * * *", is_active=True)

        jobs = workflow_scheduler.list_scheduled_jobs()
        self.assertIsInstance(jobs, list)
        matching = [j for j in jobs if j["workflow_id"] == wf_id]
        self.assertGreaterEqual(len(matching), 1)
        self.assertTrue(matching[0]["is_active"])


if __name__ == "__main__":
    unittest.main()
