"""Martin Module System.

Core for modular ERP architecture. Supports Odoo-style module discovery,
dependency resolution, and lifecycle management.

Usage:
    from martin.module import ModuleRegistry

    # Discover modules in directory
    ModuleRegistry.discover("modules/")

    # Load all (topological order by depends)
    ModuleRegistry.load_all()

    # Create DB tables for all module models
    ModuleRegistry.install_all()

    # Or do it in one call:
    ModuleRegistry.load_and_install("modules/")
"""

from .registry import ModuleRegistry, Module
from .manifest import Manifest
from .hook import register_hook, resolve_hooks, has_hooks, clear_hooks, list_hooks, extend

__all__ = [
    "ModuleRegistry",
    "Module",
    "Manifest",
    "register_hook",
    "resolve_hooks",
    "has_hooks",
    "clear_hooks",
    "list_hooks",
    "extend",
]
