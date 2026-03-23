"""Auto-generated widget documentation helpers based on WidgetSchema."""

from __future__ import annotations

import json
from pathlib import Path

from .widget_schema import list_widget_schemas


def collect_widget_docs():
    schemas = list_widget_schemas()
    docs = []
    for schema in sorted(schemas, key=lambda item: (str(item.get("category") or ""), item["name"])):
        docs.append(
            {
                "name": schema["name"],
                "category": schema.get("category") or "uncategorized",
                "summary": schema.get("summary") or "",
                "params": schema.get("params") or [],
                "preset_props": schema.get("preset_props") or {},
                "accepts_children": bool(schema.get("accepts_children")),
                "has_content_slot": bool(schema.get("has_content_slot")),
            }
        )
    return docs


def generate_widget_docs_markdown(widget_names=None):
    wanted = {str(name) for name in (widget_names or [])}
    rows = [item for item in collect_widget_docs() if not wanted or item["name"] in wanted]
    lines = ["# MARTIN Widget Docs", ""]
    current_category = None
    for item in rows:
        category = item["category"].title()
        if category != current_category:
            if current_category is not None:
                lines.append("")
            lines.extend([f"## {category}", ""])
            current_category = category
        lines.append(f"### {item['name']}")
        lines.append("")
        if item["summary"]:
            lines.append(item["summary"])
            lines.append("")
        lines.append(f"- Accepts children: `{'yes' if item['accepts_children'] else 'no'}`")
        lines.append(f"- Content slot: `{'yes' if item['has_content_slot'] else 'no'}`")
        if item["preset_props"]:
            lines.append(f"- Preset props: `{json.dumps(item['preset_props'], ensure_ascii=False)}`")
        lines.append("")
        if item["params"]:
            lines.append("| Prop | Type | Default | Group | Required |")
            lines.append("| --- | --- | --- | --- | --- |")
            for param in item["params"]:
                default = json.dumps(param.get("default"), ensure_ascii=False)
                lines.append(
                    f"| `{param['name']}` | `{param.get('type', 'string')}` | `{default}` | "
                    f"`{param.get('group', 'props')}` | `{'yes' if param.get('required') else 'no'}` |"
                )
            lines.append("")
    return "\n".join(lines).strip() + "\n"


def generate_widget_docs_json(widget_names=None):
    wanted = {str(name) for name in (widget_names or [])}
    rows = [item for item in collect_widget_docs() if not wanted or item["name"] in wanted]
    return json.dumps(rows, ensure_ascii=False, indent=2) + "\n"


def export_widget_docs(path, format="markdown", widget_names=None):
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    fmt = str(format or "markdown").lower()
    if fmt in {"markdown", "md"}:
        content = generate_widget_docs_markdown(widget_names=widget_names)
    elif fmt == "json":
        content = generate_widget_docs_json(widget_names=widget_names)
    else:
        raise ValueError("Unsupported docs format. Use 'markdown' or 'json'.")
    target.write_text(content, encoding="utf-8")
    return target
