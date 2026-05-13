"""Martin ORM — Model registry.

Collects all Model subclasses. Used by module system to discover models.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .model import Model


class ModelRegistry:
    """Registry of all ORM models."""

    _models: dict[str, type[Model]] = {}

    @classmethod
    def register(cls, model_class: type[Model]) -> None:
        name = getattr(model_class, "_name", None)
        if name:
            cls._models[str(name)] = model_class

    @classmethod
    def get(cls, name: str) -> type[Model] | None:
        return cls._models.get(str(name))

    @classmethod
    def all(cls) -> list[type[Model]]:
        return list(cls._models.values())

    @classmethod
    def names(cls) -> list[str]:
        return list(cls._models.keys())

    @classmethod
    def clear(cls) -> None:
        cls._models.clear()
