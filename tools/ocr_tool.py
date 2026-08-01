from tools.base import BaseTool, ToolResult
from tools.registry import register_tool
import os

@register_tool
class OCRPlugin(BaseTool):
    @property
    def name(self) -> str:
        return "ocr"

    @property
    def description(self) -> str:
        return "Extracts structured text data from images and documents using optical character recognition."

    def execute(self, image_path: str = "", **kwargs) -> ToolResult:
        img_p = image_path or kwargs.get("path") or ""
        if not img_p:
            return ToolResult(success=False, result="No image path provided for OCR.")
        
        # Mock OCR output
        return ToolResult(
            success=True,
            result=f"[OCR Scan of '{os.path.basename(img_p)}']: Extracted: J.A.R.V.I.S. Artificial Intelligence Core v4.9 Active."
        )

    def validate(self, result: ToolResult) -> bool:
        return result.success and "[OCR Scan" in result.result

    def rollback(self, **kwargs) -> ToolResult:
        return ToolResult(success=True, result="No side-effects to roll back for OCR plugin.")

    def status(self) -> str:
        return "ACTIVE"
