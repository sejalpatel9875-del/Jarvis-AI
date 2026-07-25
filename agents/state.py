"""
Purpose:
Defines execution state models, capabilities, and data structures for the Planner Agent System.

Responsibilities:
- PlanStep, PlanModel, and ExecutionEvent dataclasses
- StepStatus, PlanStatus, Priority, and Capability enums
- Capability definitions for capability-based tool selection

Dependencies:
- None
"""

import uuid
import datetime
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional

class PlanStatus(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"

class StepStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    RETRYING = "RETRYING"
    SKIPPED = "SKIPPED"

class Priority(int, Enum):
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4

class Capability(str, Enum):
    MATH = "math"
    WEB_SEARCH = "web_search"
    WEB_SCRAPE = "web_scrape"
    SYSTEM_CONTROL = "system_control"
    MUSIC_PLAYBACK = "music_playback"
    DOCUMENT_READ = "document_read"

@dataclass
class ExecutionEvent:
    event_type: str                                # STARTED | RETRYING | SUCCESS | FAILED | SKIPPED
    message: str
    timestamp: str = field(default_factory=lambda: datetime.datetime.now().strftime("%H:%M:%S"))

@dataclass
class PlanStep:
    step_number: int
    description: str
    capability: str                                # e.g. "web_search", "math"
    tool_name: Optional[str] = None                # Name resolved from ToolRegistry
    args: Dict[str, Any] = field(default_factory=dict)
    depends_on: List[int] = field(default_factory=list)  # Step numbers required before execution
    status: StepStatus = StepStatus.PENDING
    result: Optional[str] = None
    error: Optional[str] = None
    confidence: float = 1.0                        # 0.0 to 1.0 confidence score
    estimated_cost: float = 0.0                    # API cost estimate
    estimated_latency: float = 0.0                 # Latency estimate in seconds
    retries: int = 0                               # Retries attempted (max 2)
    history: List[ExecutionEvent] = field(default_factory=list)

    def is_ready(self, completed_step_numbers: List[int]) -> bool:
        """Returns True if all preceding step dependencies are met."""
        return all(dep_id in completed_step_numbers for dep_id in self.depends_on)

    def log_event(self, event_type: str, message: str):
        """Appends an ExecutionEvent entry to step history."""
        self.history.append(ExecutionEvent(event_type=event_type, message=message))

@dataclass
class PlanModel:
    goal: str
    steps: List[PlanStep] = field(default_factory=list)
    plan_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    status: PlanStatus = PlanStatus.PENDING
    priority: Priority = Priority.NORMAL
    current_step_index: int = 0
    final_response: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    def get_completed_step_ids(self) -> List[int]:
        """Returns list of step numbers that executed successfully."""
        return [step.step_number for step in self.steps if step.status == StepStatus.SUCCESS]

    def is_complete(self) -> bool:
        """Returns True if all steps completed successfully."""
        return all(step.status == StepStatus.SUCCESS for step in self.steps)
