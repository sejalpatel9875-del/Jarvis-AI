"""
Purpose:
Asynchronous Task Queue & Workflow Subsystem for Jarvis AI OS.

Responsibilities:
- Manage background tasks with progress tracking (0% -> 100%)
- Maintain Task models (task_id, description, status, progress, result)
- Thread-safe background worker execution

Dependencies:
- uuid, time, threading
- services/logger.py
"""

import uuid
import time
import threading
from typing import Dict, Any, List, Optional
from services.logger import logger

class TaskStatus:
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class TaskModel:
    def __init__(self, description: str, steps: List[str]):
        self.task_id = str(uuid.uuid4())[:8]
        self.description = description
        self.steps = steps
        self.current_step_index = 0
        self.status = TaskStatus.PENDING
        self.progress = 0.0
        self.result = ""
        self.error = ""
        self.created_at = time.time()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "description": self.description,
            "status": self.status,
            "progress": round(self.progress, 1),
            "current_step": self.steps[self.current_step_index] if self.current_step_index < len(self.steps) else "Done",
            "total_steps": len(self.steps),
            "result": self.result,
            "error": self.error
        }

class TaskQueueService:
    """Thread-safe Task Queue Engine."""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(TaskQueueService, cls).__new__(cls)
                cls._instance._tasks: Dict[str, TaskModel] = {}
            return cls._instance

    def create_task(self, description: str, steps: List[str]) -> TaskModel:
        task = TaskModel(description, steps)
        with self._lock:
            self._tasks[task.task_id] = task
        logger.info("TASK_QUEUE", f"Created task '{task.task_id}': {description}")
        return task

    def get_task(self, task_id: str) -> Optional[TaskModel]:
        with self._lock:
            return self._tasks.get(task_id)

    def list_tasks(self) -> List[Dict[str, Any]]:
        with self._lock:
            return [task.to_dict() for task in self._tasks.values()]

    def update_progress(self, task_id: str, step_index: int, result: str = ""):
        with self._lock:
            task = self._tasks.get(task_id)
            if task:
                task.status = TaskStatus.RUNNING
                task.current_step_index = step_index
                task.progress = min(100.0, (step_index / max(1, len(task.steps))) * 100.0)
                if result:
                    task.result = result
                if step_index >= len(task.steps):
                    task.status = TaskStatus.COMPLETED
                    task.progress = 100.0
                logger.info("TASK_QUEUE", f"Task '{task_id}' progress: {task.progress}%")

# Global Task Queue Singleton
task_queue = TaskQueueService()
