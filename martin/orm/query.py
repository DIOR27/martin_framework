"""Martin ORM — Domain query parser.

Converts Odoo-style domains to SQL WHERE clauses.

Domain syntax:
    [("field", "op", value)]                     # AND by default
    [("field1", "=", "x"), ("field2", ">", 5)]   # AND between items
    ["|", ("field1", "=", "x"), ("field2", "=", "y")]  # OR
    ["!", ("field", "=", "x")]                   # NOT

Operators: =, !=, >, >=, <, <=, like, ilike, in, not in, =like, =ilike
"""

from __future__ import annotations

from typing import Any

_OPERATORS = {
    "=": "=",
    "!=": "!=",
    ">": ">",
    ">=": ">=",
    "<": "<",
    "<=": "<=",
    "like": "LIKE",
    "ilike": "LIKE",
    "in": "IN",
    "not in": "NOT IN",
    "=like": "LIKE",
    "=ilike": "LIKE",
}


class Query:
    """Parsed query with SQL + params."""

    def __init__(self, sql: str, params: list[Any]):
        self.sql = sql
        self.params = params

    def __str__(self):
        return self.sql


def _escape_like(pattern: str) -> str:
    """Escape LIKE wildcards."""
    return pattern.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def _parse_leaf(field: str, op: str, value: Any) -> tuple[str, list[Any]]:
    """Parse a single domain leaf to (sql_fragment, params)."""
    op = str(op).strip().lower()
    sql_op = _OPERATORS.get(op)

    if sql_op is None:
        raise ValueError(f"Unknown operator: {op}")

    field_quoted = f'"{field}"'

    if op in ("like", "=like"):
        return (f'{field_quoted} {sql_op} ?', [f"%{_escape_like(str(value))}%"])

    if op in ("ilike", "=ilike"):
        return (f'LOWER({field_quoted}) {sql_op} ?', [f"%{_escape_like(str(value).lower())}%"])

    if op in ("in", "not in"):
        if not isinstance(value, (list, tuple)):
            value = [value]
        placeholders = ", ".join(["?"] * len(value))
        return (f'{field_quoted} {sql_op} ({placeholders})', list(value))

    return (f'{field_quoted} {sql_op} ?', [value])


def parse(domain: list[Any]) -> Query:
    """Parse domain list to SQL WHERE clause.

    Returns Query(sql, params). Empty domain returns Query("", []).
    """
    if not domain:
        return Query("", [])

    sql_parts: list[str] = []
    params: list[Any] = []
    i = 0

    def _next() -> Any:
        nonlocal i
        if i >= len(domain):
            raise ValueError("Unexpected end of domain")
        item = domain[i]
        i += 1
        return item

    def _parse_group() -> tuple[str, list[Any]]:
        """Parse one group — handles | ! and leaf tuples."""
        token = _next()

        # OR
        if token == "|":
            left_sql, left_params = _parse_group()
            right_sql, right_params = _parse_group()
            return (f"({left_sql} OR {right_sql})", left_params + right_params)

        # NOT
        if token == "!":
            inner_sql, inner_params = _parse_group()
            return (f"(NOT ({inner_sql}))", inner_params)

        # AND (default)
        if token == "&":
            left_sql, left_params = _parse_group()
            right_sql, right_params = _parse_group()
            return (f"({left_sql} AND {right_sql})", left_params + right_params)

        # Leaf tuple
        if isinstance(token, (list, tuple)) and len(token) == 3:
            field, op, value = token
            sql_frag, frag_params = _parse_leaf(str(field), str(op), value)
            return (sql_frag, frag_params)

        raise ValueError(f"Invalid domain token: {token!r}")

    # Parse all groups — implicit AND between them
    groups: list[str] = []
    all_params: list[Any] = []
    try:
        while i < len(domain):
            sql, g_params = _parse_group()
            groups.append(sql)
            all_params.extend(g_params)
    except (IndexError, ValueError) as e:
        raise ValueError(f"Domain parse error: {e}") from e

    if not groups:
        return Query("", [])

    clause = " AND ".join(groups) if len(groups) > 1 else groups[0]
    return Query(clause, all_params)
