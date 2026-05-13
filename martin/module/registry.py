"""Martin Module — Module registry.

Discovers, loads, and manages modules.

Usage:
    from martin.module import ModuleRegistry

    ModuleRegistry.discover("modules/")
    ModuleRegistry.load_all()
    ModuleRegistry.install_all()
"""

from __future__ import annotations

import sys
import importlib
from pathlib import Path
from typing import Any

from .manifest import Manifest


class Module:
    """Represents a single module."""

    def __init__(self, name: str, path: Path, manifest: Manifest):
        self.name = name
        self.path = path
        self.manifest = manifest
        self.loaded: bool = False
        self.installed: bool = False
        self.error: str | None = None

    def __repr__(self):
        status = "loaded" if self.loaded else "pending"
        return f"<Module {self.name} ({self.manifest.version}) [{status}]>"


class ModuleRegistry:
    """Global module registry. Singleton."""

    _modules: dict[str, Module] = {}
    _ordered: list[Module] = []
    _discovered: bool = False

    @classmethod
    def discover(cls, modules_dir: str | Path) -> list[Module]:
        """Scan directory for modules (subdirs with manifest.py).

        Returns list of discovered Module objects.
        """
        cls._modules.clear()
        cls._ordered = []
        cls._discovered = True

        base = Path(modules_dir)
        if not base.exists():
            return []

        for entry in sorted(base.iterdir()):
            if not entry.is_dir() or entry.name.startswith("_"):
                continue
            try:
                manifest = Manifest.load(entry)
                if manifest is None:
                    continue
                mod = Module(name=entry.name, path=entry, manifest=manifest)
                cls._modules[entry.name] = mod
            except ValueError as exc:
                # Log but continue — bad module shouldn't block discovery
                import traceback
                traceback.print_exc()

        return list(cls._modules.values())

    @classmethod
    def get(cls, name: str) -> Module | None:
        return cls._modules.get(name)

    @classmethod
    def all(cls) -> list[Module]:
        return list(cls._modules.values())

    @classmethod
    def names(cls) -> list[str]:
        return list(cls._modules.keys())

    @classmethod
    def resolve_dependencies(cls) -> list[Module]:
        """Topological sort by manifest.depends."""
        if not cls._modules:
            return []

        visited: set[str] = set()
        result: list[Module] = []

        def _visit(name: str, stack: set[str]) -> None:
            if name in visited:
                return
            mod = cls._modules.get(name)
            if mod is None:
                # Missing dependency — warn and continue
                import warnings
                warnings.warn(f"Module '{name}' not found (depends: {stack})")
                return
            if name in stack:
                raise ValueError(f"Circular dependency: {stack} -> {name}")
            for dep in mod.manifest.depends:
                _visit(dep, stack | {name})
            visited.add(name)
            result.append(mod)

        for name in sorted(cls._modules.keys()):
            _visit(name, set())

        cls._ordered = result
        return result

    @classmethod
    def load_module(cls, mod: Module) -> bool:
        """Import a single module into Python runtime.

        Adds module dir to sys.path, imports __init__.py.
        This triggers __init_subclass__ for ORM models and any module init code.
        """
        if mod.loaded:
            return True

        try:
            mod_path = str(mod.path.parent)
            if mod_path not in sys.path:
                sys.path.insert(0, mod_path)

            importlib.import_module(mod.name)
            mod.loaded = True
            mod.error = None

            # Import data files
            for data_file in mod.manifest.data:
                data_path = mod.path / data_file
                if data_path.exists():
                    spec = importlib.util.spec_from_file_location(
                        f"{mod.name}.{data_file.replace('/', '.').replace('.py', '')}",
                        str(data_path),
                    )
                    if spec and spec.loader:
                        spec.loader.exec_module(importlib.util.module_from_spec(spec))

            return True
        except Exception as exc:
            mod.error = str(exc)
            import traceback
            traceback.print_exc()
            return False

    @classmethod
    def load_all(cls) -> list[Module]:
        """Load all modules in dependency order. Returns list of loaded modules."""
        if not cls._ordered:
            cls.resolve_dependencies()

        loaded = []
        for mod in cls._ordered:
            if cls.load_module(mod):
                loaded.append(mod)

        return loaded

    @classmethod
    def install_module(cls, mod: Module) -> bool:
        """Install a module: create DB tables for its models."""
        if not mod.loaded:
            if not cls.load_module(mod):
                return False

        try:
            from ..orm.model import create_all_tables
            create_all_tables()
            mod.installed = True
            return True
        except Exception as exc:
            mod.error = str(exc)
            import traceback
            traceback.print_exc()
            return False

    @classmethod
    def install_all(cls) -> list[Module]:
        """Install all loaded modules. Returns list of installed modules."""
        installed = []
        for mod in cls._ordered:
            if cls.install_module(mod):
                installed.append(mod)
        return installed

    @classmethod
    def load_and_install(cls, modules_dir: str | Path,
                         module_names: list[str] | None = None) -> list[Module]:
        """Full pipeline: discover → load → install.

        Args:
            modules_dir: Directory to scan for modules.
            module_names: Only load these modules (and their deps). None = all.

        Returns:
            List of successfully installed modules.
        """
        cls.discover(modules_dir)
        if module_names:
            # Filter to requested modules only
            cls._modules = {
                n: m for n, m in cls._modules.items()
                if n in module_names
            }

        if not cls._modules:
            return []

        cls.resolve_dependencies()
        loaded = cls.load_all()
        cls.install_all()
        return loaded

    @classmethod
    def reset(cls) -> None:
        """Clear registry. Used in tests."""
        cls._modules.clear()
        cls._ordered = []
        cls._discovered = False
