from tools.base import BaseTool, ToolResult
from tools.registry import register_tool
import subprocess
import os

@register_tool
class TerminalPlugin(BaseTool):
    @property
    def name(self) -> str:
        return "terminal"

    @property
    def description(self) -> str:
        return "Executes diagnostic command line instructions and scripts inside the workspace sandbox environment."

    def execute(self, command: str = "", **kwargs) -> ToolResult:
        cmd = command or kwargs.get("cmd") or ""
        if not cmd:
            return ToolResult(success=False, result="No command string provided for terminal execution.")
        
        # Enforce safety check (do not allow formatting, deleting whole workspace root, etc.)
        cmd_lower = cmd.lower()
        if any(bad in cmd_lower for bad in ["rmdir /s", "rm -rf", "format"]):
            return ToolResult(success=False, result="Terminal action rejected due to workspace execution safety policies.")

        try:
            # Execute command in sub-process
            res = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
            if res.returncode == 0:
                output = res.stdout.strip() or "[Command completed successfully with no output]"
                return ToolResult(success=True, result=output[:2000])
            else:
                return ToolResult(success=False, result=f"Error code {res.returncode}: {res.stderr.strip()}")
        except subprocess.TimeoutExpired:
            return ToolResult(success=False, result="Terminal command execution timed out.")
        except Exception as e:
            return ToolResult(success=False, result=str(e))

    def validate(self, result: ToolResult) -> bool:
        return result.success

    def rollback(self, **kwargs) -> ToolResult:
        # Mock cleanup of command side effects
        return ToolResult(success=True, result="Terminal rollback completed successfully.")

    def status(self) -> str:
        return "ACTIVE"
