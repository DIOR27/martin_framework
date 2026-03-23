"""
Martin conditional expressions for widget props.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


class ConditionExpr:
    def to_payload(self) -> dict:
        raise NotImplementedError

    def __and__(self, other):
        return ConditionGroup("and", [self, ensure_condition(other)])

    def __or__(self, other):
        return ConditionGroup("or", [self, ensure_condition(other)])

    def __invert__(self):
        return ConditionNot(self)

    def __bool__(self):  # pragma: no cover - defensive
        raise TypeError("Condition expressions cannot be evaluated directly in Python.")


@dataclass
class Field(ConditionExpr):
    input_id: str
    source: str = "auto"

    def __post_init__(self):
        self.input_id = str(self.input_id or "").strip()
        self.source = str(self.source or "auto").strip().lower() or "auto"

    def to_payload(self) -> dict:
        return {
            "__martin_expr__": "Field",
            "input_id": self.input_id,
            "source": self.source,
        }

    def _comparison(self, operator: str, other):
        return ConditionCompare(self, operator, other)

    def __eq__(self, other):  # type: ignore[override]
        return self._comparison("==", other)

    def __ne__(self, other):  # type: ignore[override]
        return self._comparison("!=", other)

    def __gt__(self, other):
        return self._comparison(">", other)

    def __ge__(self, other):
        return self._comparison(">=", other)

    def __lt__(self, other):
        return self._comparison("<", other)

    def __le__(self, other):
        return self._comparison("<=", other)

    def contains(self, other):
        return self._comparison("contains", other)

    def startswith(self, other):
        return self._comparison("starts_with", other)

    def endswith(self, other):
        return self._comparison("ends_with", other)


@dataclass
class ConditionCompare(ConditionExpr):
    left: Any
    operator: str
    right: Any

    def to_payload(self) -> dict:
        return {
            "__martin_expr__": "Condition",
            "operator": str(self.operator or "=="),
            "left": serialize_condition(self.left),
            "right": serialize_condition(self.right),
        }


@dataclass
class ConditionGroup(ConditionExpr):
    operator: str
    items: list[Any]

    def to_payload(self) -> dict:
        return {
            "__martin_expr__": "ConditionGroup",
            "operator": str(self.operator or "and"),
            "items": [serialize_condition(item) for item in self.items],
        }


@dataclass
class ConditionNot(ConditionExpr):
    expr: Any

    def to_payload(self) -> dict:
        return {
            "__martin_expr__": "ConditionNot",
            "expr": serialize_condition(self.expr),
        }


def ensure_condition(value):
    if isinstance(value, ConditionExpr):
        return value
    if isinstance(value, bool):
        return value
    raise TypeError("Expected a condition expression or boolean value.")


def serialize_condition(value):
    if isinstance(value, ConditionExpr):
        return value.to_payload()
    if isinstance(value, list):
        return [serialize_condition(item) for item in value]
    if isinstance(value, tuple):
        return [serialize_condition(item) for item in value]
    if isinstance(value, dict):
        return {str(key): serialize_condition(item) for key, item in value.items()}
    return value

