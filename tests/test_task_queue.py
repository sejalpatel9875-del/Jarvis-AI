"""
Unit tests for Task Queue Subsystem.
"""

import unittest
from services.task_queue import task_queue, TaskStatus

class TestTaskQueue(unittest.TestCase):
    def test_create_and_update_task(self):
        """Verify TaskQueue creates tasks and tracks progress accurately."""
        t = task_queue.create_task("Generate weekly report", ["Research", "Summarize", "Send Email"])
        self.assertEqual(t.status, TaskStatus.PENDING)
        self.assertEqual(t.progress, 0.0)

        task_queue.update_progress(t.task_id, 1, result="Research Done")
        updated = task_queue.get_task(t.task_id)
        self.assertIsNotNone(updated)
        self.assertEqual(updated.status, TaskStatus.RUNNING)
        self.assertGreater(updated.progress, 0.0)

if __name__ == "__main__":
    unittest.main()
