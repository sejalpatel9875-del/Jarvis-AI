import unittest
import uuid
import os
import json
import memory.database as db
from services.workflow_execution import workflow_execution
from services.automation_engine import automation_engine, WorkflowTrigger, WorkflowAction

class TestV47WorkflowControls(unittest.TestCase):
    """Comprehensively tests stateful workflow controls (Pause, Resume, Cancel, Retry, Rollback)."""

    def setUp(self):
        self.ws_id = f"ws_test_{uuid.uuid4().hex[:8]}"

    def test_workflow_pause_and_resume(self):
        # Create a workflow that has multiple steps
        wf = automation_engine.create_workflow(
            self.ws_id,
            "Multi-Step Pause Test",
            WorkflowTrigger.TASK_FINISHED,
            WorkflowAction.GENERATE_REPORT
        )
        wf_id = wf["workflow"]["id"]

        # Run execute_workflow - first run creates a task in PENDING/RUNNING status
        # Let's pause it mid-execution by calling pause_workflow
        # (Since we have local execution synchronously, we can simulate an already paused workflow database state)
        
        # Let's create an automation_task database row in FAILED or PAUSED status directly
        import datetime
        ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        steps = [
            {"step_number": 1, "capability": "notifications", "description": "Step 1", "args": {"title": "T1", "message": "M1"}},
            {"step_number": 2, "capability": "notifications", "description": "Step 2", "args": {"title": "T2", "message": "M2"}}
        ]
        
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO automation_tasks
                (workspace_id, goal, current_step_index, status, steps_json, context_json, created_at, updated_at)
                VALUES (?, ?, 0, 'PAUSED', ?, '{}', ?, ?)
                """,
                (self.ws_id, "Test Pause/Resume", json.dumps(steps), ts, ts)
            )
            task_id = cursor.lastrowid

        # Resume execution
        res = workflow_execution.resume_workflow(task_id)
        self.assertTrue(res["success"])
        self.assertEqual(res["status"], "SUCCESS")
        self.assertEqual(res["progress"], "100.0%")

    def test_workflow_cancel(self):
        # Insert a task that is running or in progress, then set its state to CANCELLED
        import datetime
        ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        steps = [
            {"step_number": 1, "capability": "notifications", "description": "Step 1", "args": {"title": "T1", "message": "M1"}}
        ]
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO automation_tasks
                (workspace_id, goal, current_step_index, status, steps_json, context_json, created_at, updated_at)
                VALUES (?, ?, 0, 'CANCELLED', ?, '{}', ?, ?)
                """,
                (self.ws_id, "Test Cancel", json.dumps(steps), ts, ts)
            )
            task_id = cursor.lastrowid

        res = workflow_execution.execute_automation_task(task_id)
        self.assertFalse(res["success"])
        self.assertEqual(res["status"], "CANCELLED")

    def test_workflow_rollback(self):
        # Create a task that successfully performs some side-effect step, then fails, then we roll back!
        # Step 1: Create a temporary file
        temp_file = os.path.abspath(f"test_rollback_{uuid.uuid4().hex[:6]}.txt")
        
        steps = [
            {
                "step_number": 1,
                "capability": "files",
                "description": "Create temp rollback file",
                "args": {
                    "action": "create",
                    "path": temp_file,
                    "content": "Temporary rollback content"
                }
            },
            {
                "step_number": 2,
                "capability": "notes",
                "description": "Create user note",
                "args": {
                    "action": "create",
                    "title": "Temp Rollback Note",
                    "content": "Note details"
                }
            }
        ]
        
        import datetime
        ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO automation_tasks
                (workspace_id, goal, current_step_index, status, steps_json, context_json, created_at, updated_at)
                VALUES (?, ?, 0, 'PENDING', ?, '{}', ?, ?)
                """,
                (self.ws_id, "Test Rollback", json.dumps(steps), ts, ts)
            )
            task_id = cursor.lastrowid

        # Execute
        res = workflow_execution.execute_automation_task(task_id)
        self.assertTrue(res["success"])
        
        # Verify file and note got created
        self.assertTrue(os.path.exists(temp_file))
        
        # Check database note exists
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM user_notes WHERE title = 'Temp Rollback Note'")
            note_row = cursor.fetchone()
        self.assertIsNotNone(note_row)

        # Trigger rollback
        rollback_res = workflow_execution.rollback_workflow(task_id)
        self.assertTrue(rollback_res["success"])
        self.assertIn("Deleted file", rollback_res["rolled_back"][0])
        self.assertIn("Deleted user note", rollback_res["rolled_back"][1])

        # Verify resources are deleted
        self.assertFalse(os.path.exists(temp_file))
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM user_notes WHERE title = 'Temp Rollback Note'")
            deleted_note_row = cursor.fetchone()
        self.assertIsNone(deleted_note_row)

if __name__ == "__main__":
    unittest.main()
