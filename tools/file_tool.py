"""
Purpose:
Workspace File Manager Tool for Jarvis AI OS.

Responsibilities:
- Create, read, edit, and explore workspace files
"""

import os
from tools.base import BaseTool, ToolResult
from tools.registry import register_tool

@register_tool
class FileTool(BaseTool):
    @property
    def name(self) -> str:
        return "file_manager"

    @property
    def description(self) -> str:
        return "Creates, reads, edits, and explores files in the project workspace."

    def execute(self, action: str = "list", path: str = ".", content: str = "", **kwargs) -> ToolResult:
        act = action.lower().strip()
        target_path = os.path.abspath(path)

        try:
            if act == "create" or act == "write":
                with open(target_path, "w", encoding="utf-8") as f:
                    f.write(content)
                return ToolResult(success=True, result=f"Successfully created file '{path}'.")
            elif act == "read":
                if not os.path.exists(target_path):
                    return ToolResult(success=False, result=f"File '{path}' does not exist.")
                with open(target_path, "r", encoding="utf-8") as f:
                    data = f.read(2000)  # Read up to 2000 chars
                return ToolResult(success=True, result=f"File '{path}' content:\n{data}")
            else:
                files = os.listdir(target_path if os.path.isdir(target_path) else os.path.dirname(target_path))
                return ToolResult(success=True, result=f"Files in '{path}': {', '.join(files[:15])}")
        except Exception as e:
            return ToolResult(success=False, result=f"File operation error: {str(e)}")
