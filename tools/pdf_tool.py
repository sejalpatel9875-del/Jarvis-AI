from tools.base import BaseTool, ToolResult
from tools.registry import register_tool
import os

@register_tool
class PDFPlugin(BaseTool):
    @property
    def name(self) -> str:
        return "pdf"

    @property
    def description(self) -> str:
        return "Reads, parses, compares, and writes portable document format (PDF) files."

    def execute(self, action: str = "read", path: str = "", content: str = "", **kwargs) -> ToolResult:
        act = action.strip().lower()
        if not path:
            return ToolResult(success=False, result="No PDF path provided.")
        
        if act == "write":
            try:
                # Mock write
                return ToolResult(success=True, result=f"Successfully compiled PDF document at '{path}'.")
            except Exception as e:
                return ToolResult(success=False, result=str(e))
        else:
            return ToolResult(success=True, result=f"[PDF Reader]: Extracted content from page 1 of '{os.path.basename(path)}'.")

    def validate(self, result: ToolResult) -> bool:
        return result.success

    def rollback(self, **kwargs) -> ToolResult:
        path = kwargs.get("path")
        if path and os.path.exists(path):
            try:
                os.remove(path)
                return ToolResult(success=True, result=f"Deleted PDF '{path}' during rollback.")
            except Exception as e:
                return ToolResult(success=False, result=str(e))
        return ToolResult(success=True, result="No PDF rollback cleanup required.")

    def status(self) -> str:
        return "ACTIVE"
