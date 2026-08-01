from tools.base import BaseTool, ToolResult
from tools.registry import register_tool
from services.calendar_reminders import calendar_reminders
import json

@register_tool
class CalendarPlugin(BaseTool):
    @property
    def name(self) -> str:
        return "calendar"

    @property
    def description(self) -> str:
        return "Schedules and manages calendar reminders and follow-up activities."

    def execute(self, action: str = "create", title: str = "Meeting", due_at: str = "", assignee: str = "me", reminder_id: int = 0, **kwargs) -> ToolResult:
        act = action.strip().lower()
        try:
            if act == "create":
                res = calendar_reminders.create_reminder("default", title, due_at, assignee)
                return ToolResult(success=res.get("success", False), result=json.dumps(res))
            elif act == "list":
                res = calendar_reminders.list_reminders()
                return ToolResult(success=True, result=json.dumps(res))
            elif act == "complete":
                res = calendar_reminders.complete_reminder(reminder_id)
                return ToolResult(success=res.get("success", False), result=json.dumps(res))
            return ToolResult(success=False, result=f"Unknown action: {action}")
        except Exception as e:
            return ToolResult(success=False, result=str(e))

    def validate(self, result: ToolResult) -> bool:
        return result.success

    def rollback(self, **kwargs) -> ToolResult:
        reminder_id = kwargs.get("reminder_id")
        if reminder_id:
            calendar_reminders.complete_reminder(reminder_id) # Set completed or delete
            return ToolResult(success=True, result=f"Rolled back calendar reminder ID {reminder_id}.")
        return ToolResult(success=True, result="No calendar rollback actions needed.")

    def status(self) -> str:
        return "ACTIVE"
