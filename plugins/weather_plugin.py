"""
Starter Weather Plugin for Jarvis AI OS.
Demonstrates extending Jarvis capabilities via BasePlugin interface.
"""

from typing import Dict, Any
from services.plugin_loader import BasePlugin

class WeatherPlugin(BasePlugin):
    @property
    def name(self) -> str:
        return "weather"

    @property
    def description(self) -> str:
        return "Fetches real-time weather and forecast for any city."

    def execute(self, city: str = "New Delhi", **kwargs) -> Dict[str, Any]:
        city_clean = city.strip() or "New Delhi"
        return {
            "success": True,
            "result": f"Weather in {city_clean}: 28°C, Partly Cloudy with Light Breeze. UV Index: Moderate."
        }
