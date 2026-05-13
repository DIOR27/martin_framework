"""Martin ORM — Backend Bridge.

Auto-registers REST endpoints for ORM models on a martin.backend.Backend.
Resource* widgets work with ZERO config per model.

Usage:
    from martin.backend import Backend
    from martin.orm import auto_register_model, Model, Char

    class Contact(Model):
        _name = "contact"
        _fields = {"name": Char(required=True)}

    backend = Backend()
    auto_register_model(backend, Contact)  # ← one line
    backend.mount(app)
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..backend.backend import Backend
    from .model import Model


def auto_register_model(backend: Backend, model_class: type[Model]) -> None:
    """Auto-register REST endpoints for a single model.

    Registers:
        GET    /api/resources/{resource}/search   → model.search()
        POST   /api/resources/{resource}/save     → model.create()
        PATCH  /api/resources/{resource}/update   → model.write()
        POST   /api/resources/{resource}/delete   → model.unlink()
        GET    /api/resources/{resource}/detail   → model.read()
        GET    /api/resources/{resource}/list     → model.search() (paginated)
    """
    resource = model_class._name.replace(".", "_")

    @backend.get(f"/resources/{resource}/search")
    def _search(req):
        domain = _parse_json_param(req, "domain", [])
        limit = _parse_int_param(req, "limit", 80)
        offset = _parse_int_param(req, "offset", 0)
        order_by = req.query.get("order_by") or "id DESC"
        records = model_class.search(domain, limit=limit, offset=offset, order_by=order_by)
        total = model_class.search_count(domain)
        return {
            "data": records,
            "total": total,
            "limit": limit,
            "offset": offset,
        }

    @backend.post(f"/resources/{resource}/save")
    def _create(req):
        data = req.json(default={}, silent=True) or {}
        record_id = model_class.create(data)
        record = model_class.read(record_id)
        return {"id": record_id, "data": record[0] if record else {}}

    @backend.route(f"/resources/{resource}/update", methods=["PATCH"])
    def _update(req):
        data = req.json(default={}, silent=True) or {}
        ids = data.pop("ids", [])
        if not ids and "id" in data:
            ids = [data.pop("id")]
        if not ids:
            return {"error": "No ids provided", "updated": 0}, 400
        updated = model_class.write(ids, data)
        return {"updated": updated, "ids": ids}

    @backend.post(f"/resources/{resource}/delete")
    def _delete(req):
        data = req.json(default={}, silent=True) or {}
        ids = data.get("ids", [data.get("id")]) if isinstance(data, dict) else data
        if not ids:
            return {"error": "No ids provided", "deleted": 0}, 400
        deleted = model_class.unlink(ids)
        return {"deleted": deleted}

    @backend.get(f"/resources/{resource}/detail")
    def _detail(req):
        record_id = _parse_int_param(req, "id", 0)
        if not record_id:
            return {"error": "No id provided"}, 400
        records = model_class.read(record_id)
        return {"data": records[0] if records else None}

    @backend.get(f"/resources/{resource}/list")
    def _list(req):
        page = _parse_int_param(req, "page", 1)
        per_page = _parse_int_param(req, "per_page", 10)
        domain = _parse_json_param(req, "domain", [])
        offset = (page - 1) * per_page
        records = model_class.search(domain, limit=per_page, offset=offset)
        total = model_class.search_count(domain)
        return {
            "data": records,
            "total": total,
            "page": page,
            "per_page": per_page,
            "pages": max(1, -(-total // per_page)),
        }


def auto_register_all(backend: Backend) -> None:
    """Auto-register ALL registered models on a backend.

    Call after all modules are loaded.
    """
    from .registry import ModelRegistry

    for model_class in ModelRegistry.all():
        auto_register_model(backend, model_class)


def _parse_int_param(req, name: str, default: int = 0) -> int:
    raw = req.query.get(name) if hasattr(req, "query") else None
    if raw is not None:
        try:
            return int(raw)
        except (ValueError, TypeError):
            pass
    return default


def _parse_json_param(req, name: str, default=None):
    raw = req.query.get(name) if hasattr(req, "query") else None
    if raw:
        try:
            return json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            pass
    return default
