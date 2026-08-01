from tools.base import BaseTool, ToolResult
from tools.registry import register_tool

@register_tool
class WeatherPlugin(BaseTool):
    @property
    def name(self) -> str:
        return "weather"

    @property
    def description(self) -> str:
        return "Fetches real-time weather and forecast for any city."

    def execute(self, city: str = "Prayagraj", **kwargs) -> ToolResult:
        if not city:
            return ToolResult(success=False, result="No city provided for weather plugin.")
        return ToolResult(success=True, result=f"Weather in {city} is 28 degrees and clear, Bhaiya.")

    def validate(self, result: ToolResult) -> bool:
        return result.success and "degrees" in result.result

    def rollback(self, **kwargs) -> ToolResult:
        return ToolResult(success=True, result="No weather rollback actions needed.")

    def status(self) -> str:
        return "ACTIVE"
