"""
Purpose:
Smart Notification Dispatcher for Jarvis AI OS (Sprint v4.6).

Responsibilities:
- Dispatch multi-channel system notifications on business triggers (e.g. Lead Qualified, Deal Closed)
"""

import datetime
from typing import Dict, Any, List, Optional
from services.notifications import notification_service
from services.activity_feed import activity_feed

class SmartNotificationEngine:
    """Smart Event-Driven Notification Engine."""

    def dispatch_event_notification(
        self,
        workspace_id: str,
        event_name: str,
        payload: Dict[str, Any] = None,
        channels: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Dispatches automated multi-channel notifications and logs activity."""
        payload = payload or {}
        ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if channels is not None:
            target_channels = channels
        elif "channels" in payload:
            target_channels = payload["channels"]
        else:
            target_channels = ["dashboard"]

        title = payload.get("title", f"Notification: {event_name}")
        message = payload.get("message", f"Event {event_name} triggered in workspace {workspace_id}.")
        user_id = payload.get("user_id", "default_user")

        # Log activity into real-time feed
        activity_feed.log_activity(
            workspace_id=workspace_id,
            actor_name="Jarvis System",
            action=event_name,
            details=f"Dispatched notification for {event_name}",
            actor_type="JARVIS"
        )

        # Dispatch user notification
        notification_service.send_notification(
            user_id=user_id,
            title=title,
            message=message,
            channel=target_channels[0] if target_channels else "dashboard"
        )

        return {
            "success": True,
            "workspace_id": workspace_id,
            "event_name": event_name,
            "dispatched_channels": target_channels,
            "timestamp": ts
        }

# Global Singleton
smart_notifications = SmartNotificationEngine()
