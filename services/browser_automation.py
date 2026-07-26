"""
Purpose:
Playwright & Resilient Web Browser Automation Engine for Jarvis AI OS.

Responsibilities:
- Headless and headed web browsing (Playwright / requests / BeautifulSoup)
- Webpage text extraction, screenshot capture, and web form interactions

Dependencies:
- services/logger.py
"""

import os
import re
import tempfile
import time
import requests
from typing import Dict, Any, Optional

class BrowserAutomationService:
    """Web Browser Automation Engine."""

    @staticmethod
    def fetch_webpage_text(url: str) -> str:
        """
        Fetches and extracts clean visible text from any web URL.
        Uses Playwright if available, or fallback requests reader.
        """
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "https://" + url

        try:
            from playwright.sync_api import sync_playwright
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(url, timeout=15000)
                text = page.inner_text("body")
                browser.close()
                clean = re.sub(r'\s+', ' ', text).strip()
                if clean:
                    return clean[:4000]
        except Exception:
            pass

        # Fallback requests reader
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            resp = requests.get(url, headers=headers, timeout=10)
            html = resp.text
            text = re.sub(r'<script.*?>.*?</script>', ' ', html, flags=re.DOTALL)
            text = re.sub(r'<style.*?>.*?</style>', ' ', text, flags=re.DOTALL)
            text = re.sub(r'<[^>]+>', ' ', text)
            clean = re.sub(r'\s+', ' ', text).strip()
            return clean[:3000]
        except Exception as e:
            return f"Failed to fetch webpage '{url}': {str(e)}"

    @staticmethod
    def capture_webpage_screenshot(url: str, save_path: Optional[str] = None) -> str:
        """Captures a screenshot of a specific web URL using Playwright."""
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "https://" + url

        if not save_path:
            temp_dir = tempfile.gettempdir()
            filename = f"web_snap_{int(time.time())}.png"
            save_path = os.path.join(temp_dir, filename)

        try:
            from playwright.sync_api import sync_playwright
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(url, timeout=15000)
                page.screenshot(path=save_path, full_page=False)
                browser.close()
                return save_path
        except Exception as e:
            return f"Playwright screenshot fallback for '{url}': {str(e)}"

# Global Browser Automation Service Singleton
browser_service = BrowserAutomationService()
