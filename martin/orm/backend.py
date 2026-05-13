"""Martin ORM — SQLite backend.

Abstracted for future PostgreSQL support. Add new backend by subclassing.
"""

from __future__ import annotations

import sqlite3
import threading
from pathlib import Path


class Backend:
    """Abstract DB backend. SQLite implementation."""

    def __init__(self, db_path: str = "martin.db"):
        self.db_path = str(db_path)
        self._local = threading.local()

    @property
    def conn(self) -> sqlite3.Connection:
        """Thread-local connection."""
        if not hasattr(self._local, "_conn") or self._local._conn is None:
            self._local._conn = sqlite3.connect(self.db_path)
            self._local._conn.execute("PRAGMA journal_mode=WAL")
            self._local._conn.execute("PRAGMA foreign_keys=ON")
            self._local._conn.row_factory = sqlite3.Row
        return self._local._conn

    def execute(self, sql: str, params: tuple | list | None = None) -> sqlite3.Cursor:
        return self.conn.execute(sql, params or [])

    def execute_many(self, sql: str, seq: list[tuple]) -> sqlite3.Cursor:
        return self.conn.executemany(sql, seq)

    def fetchone(self, sql: str, params: tuple | list | None = None):
        return self.conn.execute(sql, params or []).fetchone()

    def fetchall(self, sql: str, params: tuple | list | None = None) -> list[sqlite3.Row]:
        return self.conn.execute(sql, params or []).fetchall()

    def commit(self):
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()

    def table_exists(self, table_name: str) -> bool:
        row = self.fetchone(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (table_name,),
        )
        return row is not None

    def table_columns(self, table_name: str) -> list[str]:
        try:
            rows = self.fetchall(f"PRAGMA table_info(\"{table_name}\")")
            return [str(row["name"]) for row in rows]
        except Exception:
            return []

    def create_table(self, table_name: str, columns: dict[str, str]) -> None:
        """Create table. columns: {name: sql_type}."""
        cols = ", ".join(
            f'"{name}" {type_}'
            for name, type_ in [("id", "INTEGER PRIMARY KEY AUTOINCREMENT"), *columns.items()]
        )
        sql = f"CREATE TABLE IF NOT EXISTS \"{table_name}\" ({cols})"
        self.execute(sql)
        self.commit()

    def add_columns(self, table_name: str, columns: dict[str, str]) -> None:
        """Add missing columns. Safe to call multiple times."""
        existing = set(self.table_columns(table_name))
        for name, type_ in columns.items():
            if name not in existing:
                self.execute(f'ALTER TABLE "{table_name}" ADD COLUMN "{name}" {type_}')
        self.commit()

    def insert(self, table_name: str, values: dict) -> int:
        cols = ", ".join(f'"{k}"' for k in values)
        placeholders = ", ".join(["?"] * len(values))
        sql = f'INSERT INTO "{table_name}" ({cols}) VALUES ({placeholders})'
        cur = self.execute(sql, tuple(values.values()))
        self.commit()
        return cur.lastrowid

    def update(self, table_name: str, values: dict, ids: list[int]) -> int:
        if not ids:
            return 0
        set_clause = ", ".join(f'"{k}"=?' for k in values)
        placeholders = ", ".join(["?"] * len(ids))
        sql = f'UPDATE "{table_name}" SET {set_clause} WHERE id IN ({placeholders})'
        cur = self.execute(sql, tuple(values.values()) + tuple(ids))
        self.commit()
        return cur.rowcount

    def delete(self, table_name: str, ids: list[int]) -> int:
        if not ids:
            return 0
        placeholders = ", ".join(["?"] * len(ids))
        sql = f'DELETE FROM "{table_name}" WHERE id IN ({placeholders})'
        cur = self.execute(sql, tuple(ids))
        self.commit()
        return cur.rowcount

    def search(self, table_name: str, where: str = "", params: tuple | None = None,
               limit: int | None = None, offset: int | None = None,
               order_by: str | None = None) -> list[sqlite3.Row]:
        sql = f'SELECT * FROM "{table_name}"'
        if where:
            sql += f" WHERE {where}"
        if order_by:
            sql += f" ORDER BY {order_by}"
        if limit is not None:
            sql += f" LIMIT {limit}"
        if offset is not None:
            sql += f" OFFSET {offset}"
        return self.fetchall(sql, params)

    def search_count(self, table_name: str, where: str = "", params: tuple | None = None) -> int:
        sql = f'SELECT COUNT(*) as cnt FROM "{table_name}"'
        if where:
            sql += f" WHERE {where}"
        row = self.fetchone(sql, params)
        return int(row["cnt"]) if row else 0

    def read(self, table_name: str, ids: list[int]) -> list[sqlite3.Row]:
        if not ids:
            return []
        placeholders = ", ".join(["?"] * len(ids))
        return self.fetchall(f'SELECT * FROM "{table_name}" WHERE id IN ({placeholders})', tuple(ids))

    def close(self):
        if hasattr(self._local, "_conn") and self._local._conn:
            self._local._conn.close()
            self._local._conn = None


# Global default backend
_default_backend: Backend | None = None


def get_backend() -> Backend:
    global _default_backend
    if _default_backend is None:
        _default_backend = Backend()
    return _default_backend


def set_backend(backend: Backend) -> None:
    global _default_backend
    _default_backend = backend
