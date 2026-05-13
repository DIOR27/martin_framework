"""Martin ORM — Auto-migration.

Ensures DB schema matches model definitions.
For now: create missing tables, add missing columns.
"""

from __future__ import annotations

from .model import Model, create_all_tables
from .registry import ModelRegistry


def migrate_model(model_class: type[Model]) -> None:
    """Ensure table exists with correct columns for one model."""
    model_class._ensure_table()


def migrate_all() -> None:
    """Ensure tables exist for ALL registered models."""
    create_all_tables()


def migrate(name: str) -> None:
    """Migrate a single model by name."""
    model = ModelRegistry.get(name)
    if model is None:
        raise ValueError(f"Model '{name}' not registered")
    migrate_model(model)
