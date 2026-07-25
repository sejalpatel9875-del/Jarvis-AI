"""
Purpose:
YouTube Music Playback Tool for Jarvis.

Responsibilities:
- Direct video ID auto-play on YouTube
- Non-blocking daemon playback

Dependencies:
- tools/base.py
- tools/registry.py
- automation.py
"""

from tools.base import BaseTool, ToolResult
from tools.registry import register_tool
import automation

@register_tool
class MusicTool(BaseTool):
    @property
    def name(self) -> str:
        return "music"

    @property
    def description(self) -> str:
        return "Plays songs directly on YouTube via non-blocking direct video auto-play."

    def execute(self, song_name: str = "", **kwargs) -> ToolResult:
        query = song_name or kwargs.get("query", "") or kwargs.get("song", "")
        if not query:
            return ToolResult(success=False, result="No song name provided.")
            
        res = automation.play_song(query)
        return ToolResult(success=True, result=res or f"Playing '{query}' on YouTube, Boss.")
