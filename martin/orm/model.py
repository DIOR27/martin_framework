"""Martin ORM — Model base class.

Usage:
    class Contact(Model):
        _name = "contact"
        _description = "Contact"
        _fields = {
            "name": Char(required=True, label="Name"),
            "email": Char(label="Email"),
            "phone": Char(label="Phone"),
            "active": Boolean(default=True, label="Active"),
        }

    # CRUD
    Contact.create({"name": "John", "email": "john@test.com"})
    Contact.search([("name", "ilike", "john")])
    Contact.read([1, 2])
    Contact.write([1], {"email": "new@test.com"})
    Contact.unlink([1])
"""

from __future__ import annotations

from typing import Any

from .backend import get_backend, Backend
from .fields import Field
from .query import parse as parse_domain
from .registry import ModelRegistry


class Model:
    """Base class for all ORM models."""

    _name: str = ""
    _description: str = ""
    _fields: dict[str, Field] = {}
    _db_table: str = ""  # auto: derived from _name

    @classmethod
    def _table_name(cls) -> str:
        if cls._db_table:
            return cls._db_table
        return cls._name.replace(".", "_")

    @classmethod
    def _backend(cls) -> Backend:
        return get_backend()

    @classmethod
    def _columns(cls) -> dict[str, str]:
        """Return {field_name: sql_type} for all fields."""
        cols = {}
        for name, field in cls._fields.items():
            if isinstance(field, Field):
                cols[name] = field.to_column_type()
            else:
                cols[name] = "TEXT"
        return cols

    @classmethod
    def _ensure_table(cls) -> None:
        """Create table + add missing columns."""
        backend = cls._backend()
        table = cls._table_name()
        columns = cls._columns()
        if not backend.table_exists(table):
            backend.create_table(table, columns)
        else:
            backend.add_columns(table, columns)

    @classmethod
    def _apply_defaults(cls, values: dict) -> dict:
        """Fill missing values with field defaults."""
        result = dict(values)
        for name, field in cls._fields.items():
            if name not in result and isinstance(field, Field) and field.default is not None:
                result[name] = field.default
        return result

    @classmethod
    def _process_values(cls, values: dict) -> dict:
        """Apply defaults + convert Python values to DB values."""
        values = cls._apply_defaults(values)
        result = {}
        for key, val in values.items():
            field = cls._fields.get(key)
            if isinstance(field, Field):
                result[key] = field.py_to_db(val)
            else:
                result[key] = val
        return result

    @classmethod
    def _row_to_dict(cls, row) -> dict[str, Any]:
        """Convert sqlite3.Row to dict with proper types."""
        if row is None:
            return {}
        result = dict(row)
        for key, field in cls._fields.items():
            if key in result and isinstance(field, Field):
                result[key] = field.db_to_py(result[key])
        return result

    # ── CRUD ────────────────────────────────────────────────────────────

    @classmethod
    def create(cls, values: dict) -> int:
        """Create record. Returns new ID."""
        cls._ensure_table()
        processed = cls._process_values(values)
        return cls._backend().insert(cls._table_name(), processed)

    @classmethod
    def read(cls, ids: int | list[int]) -> list[dict[str, Any]]:
        """Read records by ID(s). Returns list of dicts."""
        if isinstance(ids, int):
            ids = [ids]
        if not ids:
            return []
        rows = cls._backend().read(cls._table_name(), ids)
        return [cls._row_to_dict(r) for r in rows]

    @classmethod
    def write(cls, ids: int | list[int], values: dict) -> int:
        """Update records. Returns count of affected rows."""
        if isinstance(ids, int):
            ids = [ids]
        if not ids or not values:
            return 0
        processed = cls._process_values(values)
        return cls._backend().update(cls._table_name(), processed, ids)

    @classmethod
    def unlink(cls, ids: int | list[int]) -> int:
        """Delete records. Returns count of deleted rows."""
        if isinstance(ids, int):
            ids = [ids]
        return cls._backend().delete(cls._table_name(), ids)

    @classmethod
    def search(cls, domain: list | None = None, *,
               limit: int | None = None, offset: int | None = None,
               order_by: str | None = None) -> list[dict[str, Any]]:
        """Search records by domain. Returns list of dicts."""
        query = parse_domain(domain or [])
        rows = cls._backend().search(
            cls._table_name(),
            where=query.sql,
            params=tuple(query.params) if query.params else None,
            limit=limit,
            offset=offset,
            order_by=order_by or "id DESC",
        )
        return [cls._row_to_dict(r) for r in rows]

    @classmethod
    def search_count(cls, domain: list | None = None) -> int:
        """Count records matching domain."""
        query = parse_domain(domain or [])
        return cls._backend().search_count(
            cls._table_name(),
            where=query.sql,
            params=tuple(query.params) if query.params else None,
        )

    @classmethod
    def browse(cls, ids: int | list[int]) -> list[dict[str, Any]]:
        """Alias for read()."""
        return cls.read(ids)

    @classmethod
    def search_read(cls, domain: list | None = None, *,
                    limit: int | None = None, offset: int | None = None,
                    order_by: str | None = None) -> list[dict[str, Any]]:
        """Search + return records. Equivalent to search()."""
        return cls.search(domain, limit=limit, offset=offset, order_by=order_by)

    @classmethod
    def __init_subclass__(cls, **kwargs):
        """Auto-register model in registry."""
        super().__init_subclass__(**kwargs)
        name = getattr(cls, "_name", None)
        if name:
            ModelRegistry.register(cls)


def create_all_tables() -> None:
    """Ensure tables exist for all registered models."""
    for model in ModelRegistry.all():
        model._ensure_table()
