"""
core/event_bus.py
~~~~~~~~~~~~~~~~~
Asynchronous Event Bus & Decoupled Pub/Sub Engine for JARVIS Multi-Agent AI OS.

Features:
- Thread-safe topic subscription and unsubscription
- Parallel asynchronous message dispatch via ThreadPoolExecutor
- In-flight task cancellation tracking
- Structured logging & correlation tracking
"""

import uuid
import time
import threading
from typing import Callable, Dict, List, Any, Optional
from concurrent.futures import ThreadPoolExecutor


class EventMessage:
    """Represents a message passed between agents over the Event Bus."""

    def __init__(
        self,
        topic: str,
        sender: str,
        payload: Dict[str, Any],
        correlation_id: Optional[str] = None,
        msg_id: Optional[str] = None,
    ):
        self.id = msg_id or f"msg_{uuid.uuid4().hex[:8]}"
        self.topic = topic
        self.sender = sender
        self.payload = payload or {}
        self.correlation_id = correlation_id or self.id
        self.timestamp = time.time()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "topic": self.topic,
            "sender": self.sender,
            "payload": self.payload,
            "correlation_id": self.correlation_id,
            "timestamp": self.timestamp,
        }


class EventBus:
    """Decoupled, event-driven message broker for JARVIS AI OS."""

    def __init__(self, max_workers: int = 10):
        self._subscriptions: Dict[str, List[Callable[[EventMessage], None]]] = {}
        self._lock = threading.Lock()
        self._executor = ThreadPoolExecutor(
            max_workers=max_workers, thread_name_prefix="AgentOSWorker"
        )
        self._cancelled_tasks: set[str] = set()

    def subscribe(self, topic: str, handler: Callable[[EventMessage], None]):
        """Subscribes an event handler to a topic."""
        with self._lock:
            if topic not in self._subscriptions:
                self._subscriptions[topic] = []
            if handler not in self._subscriptions[topic]:
                self._subscriptions[topic].append(handler)

    def unsubscribe(self, topic: str, handler: Callable[[EventMessage], None]):
        """Unsubscribes a handler from a topic."""
        with self._lock:
            if topic in self._subscriptions and handler in self._subscriptions[topic]:
                self._subscriptions[topic].remove(handler)

    def publish(
        self, topic: str, sender: str, payload: Dict[str, Any], correlation_id: Optional[str] = None
    ) -> EventMessage:
        """Publishes an event synchronously to all topic subscribers."""
        msg = EventMessage(
            topic=topic, sender=sender, payload=payload, correlation_id=correlation_id
        )

        with self._lock:
            handlers = list(self._subscriptions.get(topic, []))
            wildcard_handlers = list(self._subscriptions.get("*", []))

        all_handlers = handlers + wildcard_handlers
        for handler in all_handlers:
            try:
                handler(msg)
            except Exception as e:
                print(f"[EventBus Error] Exception handling topic '{topic}' by '{handler}': {e}")

        return msg

    def publish_async(
        self, topic: str, sender: str, payload: Dict[str, Any], correlation_id: Optional[str] = None
    ):
        """Publishes an event asynchronously in the thread pool."""
        self._executor.submit(self.publish, topic, sender, payload, correlation_id)

    def cancel_task(self, task_id: str):
        """Registers a task ID for cancellation."""
        with self._lock:
            self._cancelled_tasks.add(task_id)

    def is_cancelled(self, task_id: str) -> bool:
        """Checks if a task ID has been marked as cancelled."""
        with self._lock:
            return task_id in self._cancelled_tasks

    def clear_cancellation(self, task_id: str):
        """Clears a task ID from cancellation set."""
        with self._lock:
            self._cancelled_tasks.discard(task_id)


# Global Singleton Instance
event_bus = EventBus()
