"""Martin Module — Manifest parser.

Each module MUST have a manifest.py with:

manifest = {
    "name": "Contacts",           # Human-readable name
    "version": "1.0.0",           # Semver
    "depends": ["base"],           # Module dependencies
    "category": "CRM",            # Category for grouping
    "description": "",            # Optional description
    "data": ["views/contact.py"], # Python files to load
    "demo": ["data/demo.py"],     # Demo data files
}
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class Manifest:
    """Validated module manifest."""

    name: str = ""
    version: str = "1.0.0"
    depends: list[str] = field(default_factory=list)
    category: str = ""
    description: str = ""
    data: list[str] = field(default_factory=list)
    demo: list[str] = field(default_factory=list)

    @classmethod
    def load(cls, module_dir: str | Path) -> Manifest | None:
        """Load manifest from module directory.

        Looks for manifest.py in the module directory.
        Returns None if no manifest found (directory is not a module).
        """
        mod_path = Path(module_dir)
        manifest_file = mod_path / "manifest.py"
        if not manifest_file.exists():
            return None

        ns: dict[str, Any] = {}
        try:
            exec(manifest_file.read_text(encoding="utf-8"), ns)
        except Exception as exc:
            raise ValueError(f"Failed to parse manifest at {manifest_file}: {exc}") from exc

        raw = ns.get("manifest", {})
        if not isinstance(raw, dict):
            raise ValueError(f"Invalid manifest at {manifest_file}: must define 'manifest' dict")

        return cls(
            name=str(raw.get("name", mod_path.name)),
            version=str(raw.get("version", "1.0.0")),
            depends=[str(d).strip() for d in raw.get("depends", []) if d],
            category=str(raw.get("category", "")),
            description=str(raw.get("description", "")),
            data=[str(d) for d in raw.get("data", []) if d],
            demo=[str(d) for d in raw.get("demo", []) if d],
        )

    @property
    def module_name(self) -> str:
        """Filesystem module name (directory basename)."""
        return self.name.lower().replace(" ", "_")
