from tools.base import BaseTool, ToolResult
from tools.registry import tool_registry, register_tool

# Import tool modules to trigger @register_tool decorators
import tools.calculator
import tools.music
import tools.search
import tools.system
import tools.browser
import tools.document
import tools.vision
import tools.github_tool
import tools.email_tool
import tools.file_tool
import tools.calendar_tool
import tools.ocr_tool
import tools.pdf_tool
import tools.weather_tool
import tools.maps
import tools.whatsapp
import tools.terminal_tool
