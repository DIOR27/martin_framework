"""Martin Module — Scaffold templates for `martin module create`."""

from pathlib import Path

MODULE_MANIFEST = '''manifest = {{
    "name": "{name}",
    "version": "1.0.0",
    "depends": ["base"],
    "category": "",
    "description": "{description}",
    "data": [],
    "demo": [],
}}
'''

MODULE_INIT = '''"""{} module."""
from . import models  # noqa: F401
'''

MODEL_INIT = '''"""{} module - models."""
from . import {}  # noqa: F401
'''

MODEL_TEMPLATE = '''"""{} model definition."""

from martin.orm import Model, Char, Text, Boolean, Integer, Float, Date, Selection


class {}(Model):
    """{} record."""

    _name = "{}"
    _description = "{}"

    _fields = {{
        "name": Char(required=True, label="Name"),
    }}
'''

VIEW_INIT = '''"""{} module - views."""
'''

MANIFEST_BASE = '''manifest = {{
    "name": "Base",
    "version": "1.0.0",
    "depends": [],
    "category": "Core",
    "description": "Core module. Required by all other modules.",
    "data": [],
    "demo": [],
}}
'''

BASE_MODEL_TEMPLATE = '''"""User model for authentication and session management."""

from martin.orm import Model, Char, Boolean


class User(Model):
    """System user."""

    _name = "user"
    _description = "User"

    _fields = {{
        "name": Char(required=True, label="Name"),
        "email": Char(label="Email"),
        "active": Boolean(default=True, label="Active"),
    }}
'''


def render_module(name: str, description: str = "") -> dict[str, str]:
    """Generate scaffold files for a new module.

    Returns dict of relative_path -> content.
    """
    cls_name = name.capitalize()
    files = {
        "__init__.py": MODULE_INIT.format(name),
        "manifest.py": MODULE_MANIFEST.format(name=name, description=description or f"{cls_name} module"),
        "models/__init__.py": MODEL_INIT.format(name, name),
        "models/{}.py".format(name): MODEL_TEMPLATE.format(cls_name, cls_name, cls_name, name, cls_name),
        "views/__init__.py": VIEW_INIT.format(name),
    }
    return files


def render_base_module() -> dict[str, str]:
    """Generate scaffold files for the base module."""
    return {
        "__init__.py": "# Base module\n",
        "manifest.py": MANIFEST_BASE,
        "models/__init__.py": "from .user import User\n\n__all__ = [\"User\"]\n",
        "models/user.py": BASE_MODEL_TEMPLATE,
    }


def write_module(target_dir: str | Path, name: str, description: str = "") -> Path:
    """Write module scaffold to disk.

    Returns path to created module directory.
    """
    base = Path(target_dir) / name
    base.mkdir(parents=True, exist_ok=True)

    for rel_path, content in render_module(name, description).items():
        file_path = base / rel_path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding="utf-8")

    return base


def write_base_module(target_dir: str | Path) -> Path:
    """Write base module scaffold to disk."""
    base = Path(target_dir) / "base"
    base.mkdir(parents=True, exist_ok=True)

    for rel_path, content in render_base_module().items():
        file_path = base / rel_path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding="utf-8")

    return base
