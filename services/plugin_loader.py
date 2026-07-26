"""
Purpose:
Dynamic Plugin Loader Subsystem for Jarvis AI OS.

Responsibilities:
- Abstract BasePlugin interface definition
- Dynamic directory scanning of plugins/*.py
- Dynamic module importing and tool registration into ToolRegistry

Dependencies:
- importlib, inspect, os, glob
- tools/base.py
- tools/registry.py
"""

import os
import sys
import glob
import importlib.util
from abc import ABC, abstractmethod
from typing import Dict, Any, Type, List
from tools.base import BaseTool, ToolResult
from tools.registry import tool_registry

class BasePlugin(ABC):
    """Abstract Interface Contract for external Jarvis Plugins."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Unique plugin identifier name."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Human readable description of plugin capabilities."""
        pass

    @abstractmethod
    def execute(self, **kwargs) -> Dict[str, Any]:
        """Executes plugin logic and returns structured dictionary response."""
        pass

class PluginToolAdapter(BaseTool):
    """Adapts a BasePlugin class into a standard BaseTool for ToolRegistry."""

    def __init__(self, plugin_instance: BasePlugin):
        self._plugin = plugin_instance

    @property
    def name(self) -> str:
        return self._plugin.name

    @property
    def description(self) -> str:
        return self._plugin.description

    def execute(self, **kwargs) -> ToolResult:
        try:
            res = self._plugin.execute(**kwargs)
            success = res.get("success", True) if isinstance(res, dict) else True
            output = res.get("result", str(res)) if isinstance(res, dict) else str(res)
            return ToolResult(success=success, result=output)
        except Exception as e:
            return ToolResult(success=False, result=f"Plugin execution error: {str(e)}")

class PluginLoaderService:
    """Discovers and auto-registers plugins from plugins/ directory."""

    def __init__(self, plugins_dir: str = "plugins"):
        self.plugins_dir = os.path.join(os.getcwd(), plugins_dir)
        self.loaded_plugins: Dict[str, BasePlugin] = {}

    def discover_and_load(self) -> List[str]:
        """Scans plugins/ directory and registers discovered BasePlugin instances into ToolRegistry."""
        os.makedirs(self.plugins_dir, exist_ok=True)
        plugin_files = glob.glob(os.path.join(self.plugins_dir, "*.py"))
        loaded_names = []

        for py_file in plugin_files:
            if os.path.basename(py_file).startswith("__"):
                continue
            
            module_name = f"plugins.{os.path.splitext(os.path.basename(py_file))[0]}"
            try:
                spec = importlib.util.spec_from_file_location(module_name, py_file)
                if spec and spec.loader:
                    mod = importlib.util.module_from_spec(spec)
                    sys.modules[module_name] = mod
                    spec.loader.exec_module(mod)

                    for attr_name in dir(mod):
                        attr = getattr(mod, attr_name)
                        if (
                            isinstance(attr, type)
                            and issubclass(attr, BasePlugin)
                            and attr is not BasePlugin
                        ):
                            instance = attr()
                            self.loaded_plugins[instance.name] = instance
                            adapter = PluginToolAdapter(instance)
                            tool_registry.register(adapter)
                            loaded_names.append(instance.name)
                            print(f"[Plugin Loader] Registered plugin tool '{instance.name}' into ToolRegistry.")
            except Exception as e:
                print(f"[Plugin Loader Error] Failed loading plugin file '{py_file}': {e}")

        return loaded_names

# Global Plugin Loader Singleton
plugin_loader = PluginLoaderService()
