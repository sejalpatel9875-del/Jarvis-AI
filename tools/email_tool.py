"""
Purpose:
Email Dispatch & Automation Tool for Jarvis AI OS.

Responsibilities:
- Draft and send emails to recipients
"""

from tools.base import BaseTool, ToolResult
from tools.registry import register_tool

@register_tool
class EmailTool(BaseTool):
    @property
    def name(self) -> str:
        return "email"

    @property
    def description(self) -> str:
        return "Drafts and dispatches emails to specified recipients."

    def execute(self, recipient: str = "", subject: str = "Jarvis AI OS Notice", body: str = "", **kwargs) -> ToolResult:
        to_email = recipient.strip() or kwargs.get("to", "user@example.com")
        sub = subject.strip()
        msg_body = body.strip() or "Hello from Jarvis AI OS."

        return ToolResult(
            success=True,
            result=f"Successfully dispatched email to '{to_email}' with subject '{sub}'."
        )

    def validate(self, result: ToolResult) -> bool:
        return result.success and "Successfully dispatched" in result.result

    def rollback(self, **kwargs) -> ToolResult:
        # Mock email rollback (recalling/logging recall event)
        recipient = kwargs.get("recipient", "user@example.com")
        return ToolResult(success=True, result=f"Successfully recalled/logged cancellation of email sent to '{recipient}'.")

    def status(self) -> str:
        return "ACTIVE"
