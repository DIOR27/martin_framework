"""Martin ORM — Field types."""

from __future__ import annotations


class Field:
    """Base field."""

    def __init__(self, *, required=False, default=None, label="", help_text="", index=False, unique=False):
        self.required = required
        self.default = default
        self.label = label or ""
        self.help_text = help_text or ""
        self.index = index
        self.unique = unique

    def to_column_type(self) -> str:
        raise NotImplementedError

    def db_default(self):
        if self.default is not None:
            if isinstance(self.default, bool):
                return "1" if self.default else "0"
            return repr(self.default)
        return "NULL"

    def py_to_db(self, value):
        if value is None:
            return None
        if isinstance(self.default, bool) and not isinstance(value, bool):
            return bool(value)
        return value

    def db_to_py(self, value):
        if value is None:
            return bool(self.default) if isinstance(self.default, bool) else None
        if isinstance(value, bool):
            return value
        if isinstance(value, int):
            return bool(value)
        if isinstance(self.default, int):
            return int(value)
        if isinstance(self.default, float):
            return float(value)
        return value


class Char(Field):
    sql = "VARCHAR"

    def __init__(self, max_length=255, **kwargs):
        super().__init__(**kwargs)
        self.max_length = max_length

    def to_column_type(self) -> str:
        return f"VARCHAR({self.max_length})"

    def py_to_db(self, value):
        if value is None:
            return None
        return str(value)


class Text(Field):
    sql = "TEXT"

    def to_column_type(self) -> str:
        return "TEXT"

    def py_to_db(self, value):
        if value is None:
            return None
        return str(value)


class Integer(Field):
    sql = "INTEGER"

    def to_column_type(self) -> str:
        return "INTEGER"

    def py_to_db(self, value):
        if value is None:
            return None
        return int(value)

    def db_to_py(self, value):
        if value is None:
            return None
        return int(value)


class Float(Field):
    sql = "REAL"

    def to_column_type(self) -> str:
        return "REAL"

    def py_to_db(self, value):
        if value is None:
            return None
        return float(value)

    def db_to_py(self, value):
        if value is None:
            return None
        return float(value)


class Boolean(Field):
    sql = "INTEGER"

    def to_column_type(self) -> str:
        return "INTEGER"

    def py_to_db(self, value):
        if value is None:
            return None
        return 1 if value else 0

    def db_to_py(self, value):
        if value is None:
            return bool(self.default) if isinstance(self.default, bool) else False
        return bool(value)


class Date(Field):
    sql = "TEXT"

    def to_column_type(self) -> str:
        return "TEXT"


class DateTime(Field):
    sql = "TEXT"

    def to_column_type(self) -> str:
        return "TEXT"


class Selection(Field):
    sql = "VARCHAR"

    def __init__(self, selection=None, **kwargs):
        super().__init__(**kwargs)
        self.selection = selection or []

    def to_column_type(self) -> str:
        return "VARCHAR(64)"

    def py_to_db(self, value):
        if value is None:
            return None
        return str(value)


class Many2one(Field):
    """Reference to another model. Stores INTEGER FK."""

    sql = "INTEGER"

    def __init__(self, model_name: str, **kwargs):
        super().__init__(**kwargs)
        self.model_name = model_name

    def to_column_type(self) -> str:
        return "INTEGER"

    def py_to_db(self, value):
        if value is None:
            return None
        return int(value)

    def db_to_py(self, value):
        if value is None:
            return None
        return int(value)
