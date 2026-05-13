"""Martin ORM — Object-Relational Mapping for ERP modules.

Usage:
    from martin.orm import Model, Char, Text, Integer, Boolean, Selection
    from martin.orm import create_all_tables, migrate_all

    class Contact(Model):
        _name = "contact"
        _fields = {
            "name": Char(required=True),
            "email": Char(),
        }

    Contact.create({"name": "John"})
    Contact.search([("name", "ilike", "john")])
"""

from .fields import (
    Field,
    Char,
    Text,
    Integer,
    Float,
    Boolean,
    Date,
    DateTime,
    Selection,
    Many2one,
)
from .model import Model, create_all_tables
from .migration import migrate_all, migrate, migrate_model
from .registry import ModelRegistry
from .backend import Backend, get_backend, set_backend
from .query import Query, parse
from .backend_bridge import auto_register_model, auto_register_all

__all__ = [
    # Fields
    "Field", "Char", "Text", "Integer", "Float", "Boolean",
    "Date", "DateTime", "Selection", "Many2one",
    # Model
    "Model",
    "create_all_tables",
    "migrate_all", "migrate", "migrate_model",
    "ModelRegistry",
    "Backend", "get_backend", "set_backend",
    "Query", "parse",
    # Backend Bridge
    "auto_register_model", "auto_register_all",
]
