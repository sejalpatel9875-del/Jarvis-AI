"""
Unit tests for J.A.R.V.I.S. v4.4 Enterprise Automation Engine.
"""

import unittest
import uuid
from services.automation_engine import automation_engine, WorkflowTrigger, WorkflowAction
from services.workflow_execution import workflow_execution
from services.workflow_scheduler import workflow_scheduler

class TestV44AutomationPlatform(unittest.TestCase):
    def test_create_and_list_workflows(self):
        ws_id = f"ws_{uuid.uuid4().hex[:6]}"
        wf = automation_engine.create_workflow(ws_id, "Auto Report Workflow", WorkflowTrigger.DOCUMENT_UPLOADED, WorkflowAction.GENERATE_REPORT)
        self.assertTrue(wf["success"])
        wfs = automation_engine.list_workflows(ws_id)
        self.assertEqual(len(wfs), 1)

    def test_workflow_execution(self):
        ws_id = f"ws_{uuid.uuid4().hex[:6]}"
        wf = automation_engine.create_workflow(ws_id, "Test Workflow", WorkflowTrigger.TASK_FINISHED, WorkflowAction.SEND_EMAIL)
        exec_res = workflow_execution.execute_workflow(wf["workflow"]["id"])
        self.assertEqual(exec_res["status"], "SUCCESS")

    def test_workflow_execution_history(self):
        ws_id = f"ws_{uuid.uuid4().hex[:6]}"
        history = workflow_execution.get_execution_history(ws_id)
        self.assertIsInstance(history, list)

    def test_workflow_scheduler(self):
        sch = workflow_scheduler.schedule_workflow(1, "0 9 * * 1")
        self.assertTrue(sch["success"])
        jobs = workflow_scheduler.list_scheduled_jobs()
        self.assertGreaterEqual(len(jobs), 1)

if __name__ == "__main__":
    unittest.main()
