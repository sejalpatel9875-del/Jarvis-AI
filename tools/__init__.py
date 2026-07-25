from tools.base import BaseTool, ToolResult
from tools.registry import tool_registry, register_tool

# Import tool modules to trigger @register_tool decorators
import tools.calculator
import tools.music
import tools.search
import tools.system
import tools.browser
