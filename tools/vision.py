"""
Purpose:
Vision Intelligence Tool for Jarvis ToolRegistry.

Responsibilities:
- Provide desktop screenshot capture and OCR text extraction to Planner Agent
- Register under capability Capability.VISION_ANALYSIS

Dependencies:
- tools/base.py
- tools/registry.py
- services/vision.py
"""

from tools.base import BaseTool, ToolResult
from tools.registry import register_tool
from services.vision import vision_service

@register_tool
class VisionTool(BaseTool):
    @property
    def name(self) -> str:
        return "vision"

    @property
    def description(self) -> str:
        return "Captures desktop screenshots, extracts text on screen via OCR, and diagnoses visual errors."

    def execute(self, action: str = "screenshot", **kwargs) -> ToolResult:
        act = action.lower().strip()

        try:
            if act in ["screenshot", "snap", "capture"]:
                snap_path = vision_service.capture_screenshot()
                return ToolResult(
                    success=True,
                    result=f"Desktop screenshot captured successfully: '{snap_path}'"
                )
            elif act in ["ocr", "read_screen", "analyze", "text"]:
                analysis = vision_service.analyze_screen()
                result_str = (
                    f"Screenshot Captured: {analysis['screenshot_path']}\n"
                    f"Extracted Screen Text:\n\"{analysis['extracted_text']}\""
                )
                return ToolResult(success=True, result=result_str)
            else:
                return ToolResult(success=False, result=f"Unknown vision action '{act}'.")
        except Exception as e:
            return ToolResult(success=False, result=f"Vision tool error: {str(e)}")
