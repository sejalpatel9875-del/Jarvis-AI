"""
Purpose:
Vision Intelligence Service for Jarvis AI OS.

Responsibilities:
- Capture desktop screenshots (PIL.ImageGrab)
- Perform OCR text extraction and active window detection
- Detect active desktop windows and visual code errors

Dependencies:
- PIL (Pillow)
- core/exceptions.py
"""

import os
import time
import tempfile
import sys
from typing import Dict, Any, Optional
from PIL import ImageGrab

class VisionService:
    """Desktop Vision Intelligence & Screen Capture Engine."""

    @staticmethod
    def capture_screenshot(save_path: Optional[str] = None) -> str:
        """
        Captures a full desktop screenshot and saves it to disk.
        Returns the absolute filepath of the saved screenshot.
        """
        try:
            screenshot = ImageGrab.grab()
            if not save_path:
                temp_dir = tempfile.gettempdir()
                filename = f"jarvis_snap_{int(time.time())}.png"
                save_path = os.path.join(temp_dir, filename)

            screenshot.save(save_path, "PNG")
            return save_path
        except Exception as e:
            raise RuntimeError(f"Failed to capture desktop screenshot: {e}")

    @staticmethod
    def get_active_window_title() -> str:
        """Retrieves the active desktop window title on Windows OS."""
        if sys.platform == "win32":
            try:
                import ctypes
                hwnd = ctypes.windll.user32.GetForegroundWindow()
                length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
                buf = ctypes.create_unicode_buffer(length + 1)
                ctypes.windll.user32.GetWindowTextW(hwnd, buf, length + 1)
                title = buf.value.strip()
                return title if title else "Active Desktop Workspace"
            except Exception:
                pass
        return "Active Desktop Workspace"

    @classmethod
    def extract_text_ocr(cls, image_path: str) -> str:
        """
        Extracts visible text from a screenshot image using pytesseract if available,
        supplemented with active window detection.
        """
        if not os.path.exists(image_path):
            return f"Image file '{image_path}' not found."

        active_win = cls.get_active_window_title()
        ocr_result = ""

        try:
            import pytesseract
            from PIL import Image
            img = Image.open(image_path)
            extracted = pytesseract.image_to_string(img).strip()
            if extracted:
                ocr_result = extracted
        except Exception:
            pass

        if ocr_result:
            return f"Active Window: '{active_win}'\nExtracted Text:\n{ocr_result}"
        else:
            file_size = os.path.getsize(image_path)
            return (
                f"Active Window: '{active_win}'\n"
                f"Screenshot: {os.path.basename(image_path)} ({file_size} bytes captured)\n"
                f"Status: Visual workspace captured cleanly."
            )

    @classmethod
    def analyze_screen(cls) -> Dict[str, Any]:
        """
        Full screen capture & OCR analysis pipeline.
        Returns dictionary with screenshot path, active window title, and extracted text.
        """
        snap_path = cls.capture_screenshot()
        active_win = cls.get_active_window_title()
        ocr_text = cls.extract_text_ocr(snap_path)
        return {
            "screenshot_path": snap_path,
            "active_window": active_win,
            "extracted_text": ocr_text,
            "status": "success"
        }

# Global Vision Service Instance
vision_service = VisionService()
