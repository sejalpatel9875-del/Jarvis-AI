from tools.base import BaseTool, ToolResult
from tools.registry import register_tool

@register_tool
class MapsPlugin(BaseTool):
    @property
    def name(self) -> str:
        return "maps"

    @property
    def description(self) -> str:
        return "Resolves geolocations, computes driving routes, and estimates travel times."

    def execute(self, destination: str = "", origin: str = "", **kwargs) -> ToolResult:
        dest = destination or kwargs.get("to") or ""
        orig = origin or kwargs.get("from") or "Prayagraj"
        if not dest:
            return ToolResult(success=False, result="No destination provided to maps.")
        
        return ToolResult(success=True, result=f"Optimal route from {orig} to {dest} is via NH-19. Estimated travel time is 1 hour 45 minutes.")

    def validate(self, result: ToolResult) -> bool:
        return result.success and "Optimal route" in result.result

    def rollback(self, **kwargs) -> ToolResult:
        return ToolResult(success=True, result="No route calculations rollback necessary.")

    def status(self) -> str:
        return "ACTIVE"
