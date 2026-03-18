"""
Martin plugin registry.
"""

from __future__ import annotations

from typing import Any, Dict


_REGISTRY: Dict[str, Any] = {}


def register_plugin(name: str, plugin: Any):
    key = str(name).strip().lower()
    if not key:
        raise ValueError("Plugin name cannot be empty.")
    _REGISTRY[key] = plugin
    return plugin


def unregister_plugin(name: str):
    _REGISTRY.pop(str(name).strip().lower(), None)


def get_plugin(name: str):
    return _REGISTRY.get(str(name).strip().lower())


def list_plugins():
    return sorted(_REGISTRY.keys())


def apply_plugin(name: str, *args, **kwargs):
    plugin = get_plugin(name)
    if plugin is None:
        raise KeyError(f"Plugin '{name}' is not registered.")
    if hasattr(plugin, "apply") and callable(plugin.apply):
        return plugin.apply(*args, **kwargs)
    if callable(plugin):
        return plugin(*args, **kwargs)
    raise TypeError(f"Plugin '{name}' is not callable and has no .apply() method.")


class PluginRegistry:
    """Object-style registry facade."""

    def register(self, name: str, plugin: Any):
        return register_plugin(name, plugin)

    def unregister(self, name: str):
        unregister_plugin(name)

    def get(self, name: str):
        return get_plugin(name)

    def list(self):
        return list_plugins()

    def apply(self, name: str, *args, **kwargs):
        return apply_plugin(name, *args, **kwargs)

