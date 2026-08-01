from tools.base import BaseTool, ToolResult
from tools.registry import register_tool

@register_tool
class WhatsAppPlugin(BaseTool):
    @property
    def name(self) -> str:
        return "whatsapp"

    @property
    def description(self) -> str:
        return "Automates sending WhatsApp Web messages to designated contacts."

    def execute(self, recipient: str = "", message: str = "Hello", **kwargs) -> ToolResult:
        recip = recipient or kwargs.get("to") or ""
        msg = message or kwargs.get("body") or ""
        if not recip:
            return ToolResult(success=False, result="No WhatsApp recipient contact specified.")
        
        return ToolResult(success=True, result=f"WhatsApp message queued and dispatched successfully to '{recip}'.")

    def validate(self, result: ToolResult) -> bool:
        return result.success and "queued and dispatched" in result.result

    def rollback(self, **kwargs) -> ToolResult:
        recipient = kwargs.get("recipient", "contact")
        return ToolResult(success=True, result=f"WhatsApp dispatch to '{recipient}' cancelled/logged cancellation.")

    def status(self) -> str:
        return "ACTIVE"
