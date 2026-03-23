"""Unified widget schema registry for MARTIN runtime and Studio."""

from __future__ import annotations

from copy import deepcopy


UNIVERSAL_WIDGET_PROPS = [
    {"name": "style", "type": "style", "default": None, "group": "style"},
    {"name": "padding", "type": "integer", "default": None, "group": "style"},
    {"name": "margin", "type": "integer", "default": None, "group": "style"},
    {"name": "width", "type": "string", "default": None, "group": "style"},
    {"name": "height", "type": "string", "default": None, "group": "style"},
    {"name": "color", "type": "string", "default": None, "group": "style"},
    {"name": "background", "type": "string", "default": None, "group": "style"},
    {"name": "radius", "type": "integer", "default": None, "group": "style"},
    {"name": "shadow", "type": "string", "default": None, "group": "style"},
    {"name": "opacity", "type": "float", "default": None, "group": "style"},
    {"name": "hidden", "type": "boolean", "default": None, "group": "style"},
    {"name": "visible", "type": "condition", "default": True, "group": "state", "editor": {"type": "condition"}},
    {"name": "readonly", "type": "condition", "default": False, "group": "state", "editor": {"type": "condition"}},
    {"name": "disabled", "type": "condition", "default": False, "group": "state", "editor": {"type": "condition"}},
    {"name": "url", "type": "string", "default": None, "group": "link"},
    {"name": "url_target", "type": "string", "default": None, "group": "link"},
    {"name": "role", "type": "string", "default": None, "group": "a11y"},
    {"name": "tabindex", "type": "integer", "default": None, "group": "a11y"},
    {"name": "floating", "type": "boolean", "default": None, "group": "floating"},
    {
        "name": "float_position",
        "type": "enum",
        "default": "bottom-right",
        "group": "floating",
        "options": ["bottom-right", "bottom-left", "top-right", "top-left"],
    },
    {"name": "float_offset", "type": "integer", "default": 20, "group": "floating"},
    {"name": "float_gap", "type": "integer", "default": 12, "group": "floating"},
    {"name": "float_z_index", "type": "integer", "default": 999, "group": "floating"},
]


_WIDGET_SCHEMAS: dict[str, dict] = {}


def schema_param(
    name: str,
    *,
    type: str = "string",
    default=None,
    required: bool = False,
    group: str = "props",
    annotation: str = "",
    structural: bool = False,
    options: list | None = None,
    editor: dict | None = None,
) -> dict:
    payload = {
        "name": name,
        "type": type,
        "annotation": annotation,
        "required": bool(required),
        "default": default,
        "group": group,
        "structural": bool(structural),
    }
    if options is not None:
        payload["options"] = list(options)
    if editor is not None:
        payload["editor"] = dict(editor)
    return payload


def register_widget_schema(
    name: str,
    *,
    category: str | None = None,
    summary: str | None = None,
    doc: str | None = None,
    params: list[dict] | None = None,
    preset_props: dict | None = None,
    accepts_children: bool | None = None,
    has_content_slot: bool | None = None,
    module: str | None = None,
) -> dict:
    schema = {
        "name": str(name),
        "category": category,
        "summary": summary or "",
        "doc": doc or "",
        "params": [deepcopy(param) for param in (params or [])],
        "preset_props": dict(preset_props or {}),
        "accepts_children": accepts_children,
        "has_content_slot": has_content_slot,
        "module": module,
    }
    _WIDGET_SCHEMAS[str(name)] = schema
    return schema


def get_widget_schema(name: str) -> dict | None:
    schema = _WIDGET_SCHEMAS.get(str(name))
    return deepcopy(schema) if schema else None


def list_widget_schemas() -> list[dict]:
    return [deepcopy(item) for item in _WIDGET_SCHEMAS.values()]


register_widget_schema(
    "Button",
    category="input",
    summary="Clickable action with variants and optional links.",
    params=[
        schema_param("label", type="string", default="Button", group="content"),
        schema_param(
            "variant",
            type="enum",
            default="primary",
            group="props",
            options=["primary", "secondary", "ghost", "danger", "link"],
        ),
        schema_param("href", type="string", default=None, group="link"),
        schema_param("target", type="enum", default="_self", group="link", options=["_self", "_blank"]),
        schema_param("on_click", type="string", default=None, group="events"),
        schema_param("type", type="enum", default="button", group="props", options=["button", "submit", "reset"]),
    ],
    preset_props={"label": "Button", "variant": "primary"},
    accepts_children=False,
    has_content_slot=True,
)

register_widget_schema(
    "Icon",
    category="media",
    summary="Icon widget with provider, variant and icon name.",
    params=[
        schema_param("icon", type="string", default=None, group="content", editor={"type": "icon_value"}),
        schema_param("name", type="string", default=None, group="content", editor={"type": "icon_name"}),
        schema_param(
            "provider",
            type="enum",
            default="none",
            group="props",
            options=["none", "fontawesome", "bootstrap-icons", "material-symbols", "material-icons", "mdi", "custom"],
            editor={
                "type": "icon_provider",
                "options": ["none", "fontawesome", "bootstrap-icons", "material-symbols", "material-icons", "mdi", "custom"],
            },
        ),
        schema_param("variant", type="string", default=None, group="props"),
        schema_param("size", type="integer", default=None, group="style"),
    ],
    preset_props={"name": "star", "provider": "none"},
)

register_widget_schema(
    "Counter",
    category="utility",
    summary="Count down, count up or show remaining time from Python.",
    params=[
        schema_param("to", type="string", default=None, group="content"),
        schema_param("from_", type="string", default=None, group="content"),
        schema_param("mode", type="enum", default="countdown", group="props", options=["countdown", "countup", "remaining"]),
        schema_param("format", type="enum", default="full", group="props", options=["full", "human", "clock"]),
        schema_param("prefix", type="string", default="", group="content"),
        schema_param("suffix", type="string", default="", group="content"),
        schema_param("completed_text", type="string", default="Completed", group="content"),
        schema_param("tick", type="integer", default=1000, group="props"),
    ],
    preset_props={"to": "2026-12-31 23:59:59", "mode": "countdown", "format": "human"},
)

register_widget_schema(
    "ScrollToTop",
    category="utility",
    summary="Floating action button that scrolls to the top.",
    params=[
        schema_param("icon", type="string", default="↑", group="content", editor={"type": "icon_widget"}),
        schema_param("content", type="string", default=None, group="content"),
        schema_param("title", type="string", default="Back to top", group="content"),
        schema_param("show_after", type="integer", default=240, group="props"),
        schema_param("target", type="string", default=None, group="props"),
        schema_param("size", type="integer", default=48, group="style"),
        schema_param("shape", type="enum", default="circle", group="style", options=["circle", "square", "pill"]),
    ],
    preset_props={"icon": "↑", "show_after": 240},
)

register_widget_schema(
    "WhatsAppButton",
    category="utility",
    summary="Floating WhatsApp entry point with phone, message and icon.",
    params=[
        schema_param("phone", type="string", default="", group="content", required=True),
        schema_param("message", type="string", default="", group="content"),
        schema_param("icon", type="string", default=None, group="content", editor={"type": "icon_widget"}),
        schema_param("title", type="string", default="WhatsApp", group="content"),
        schema_param("show_label", type="boolean", default=False, group="props"),
        schema_param("shape", type="enum", default="circle", group="style", options=["circle", "square", "pill"]),
        schema_param("size", type="integer", default=48, group="style"),
        schema_param("action", type="string", default=None, group="events"),
    ],
    preset_props={"phone": "593999999999", "message": "Hola Martin"},
)

register_widget_schema(
    "Toast",
    category="feedback",
    summary="Floating toast notification with variants, auto-dismiss and stacking.",
    params=[
        schema_param("message", type="string", default="", group="content"),
        schema_param("title", type="string", default=None, group="content"),
        schema_param("variant", type="enum", default="info", group="props", options=["info", "success", "warning", "error"]),
        schema_param("icon", type="string", default=None, group="content", editor={"type": "icon_widget"}),
        schema_param("duration", type="integer", default=4000, group="props"),
        schema_param("closable", type="boolean", default=True, group="props"),
        schema_param("position", type="enum", default="bottom-right", group="floating", options=["bottom-right", "bottom-left", "top-right", "top-left"]),
        schema_param("max_width", type="integer", default=360, group="style"),
    ],
    preset_props={"title": "Saved", "message": "Changes were saved successfully.", "variant": "success", "duration": 4000},
)

register_widget_schema(
    "ToastCenter",
    category="feedback",
    summary="Global toast runtime to trigger notifications from widgets, backend or custom actions.",
    params=[
        schema_param("items", type="array", default=[], group="content"),
    ],
    preset_props={"items": [{"message": "Ready to notify", "variant": "info", "position": "top-right"}]},
)

register_widget_schema(
    "Select",
    category="input",
    summary="Selectable dropdown with optional search and custom menu UI.",
    params=[
        schema_param("options", type="array", default=[], group="content"),
        schema_param("value", type="string", default=None, group="content"),
        schema_param("search", type="boolean", default=False, group="props"),
        schema_param("placeholder", type="string", default="Seleccionar...", group="content"),
        schema_param("name", type="string", default=None, group="identity"),
        schema_param("id", type="string", default=None, group="identity"),
    ],
    preset_props={
        "options": [["starter", "Starter"], ["pro", "Pro"], ["enterprise", "Enterprise"]],
        "value": "starter",
        "placeholder": "Choose a plan",
        "search": True,
    },
)

register_widget_schema(
    "Uploader",
    category="input",
    summary="Advanced uploader with drag and drop, queue, progress and backend-ready uploads.",
    params=[
        schema_param("label", type="string", default=None, group="content"),
        schema_param("name", type="string", default="file", group="identity"),
        schema_param("accept", type="string", default="*", group="props"),
        schema_param("multiple", type="boolean", default=True, group="props"),
        schema_param("drag_drop", type="boolean", default=True, group="props"),
        schema_param("upload_url", type="string", default=None, group="link"),
        schema_param("auto_upload", type="boolean", default=False, group="props"),
        schema_param("max_files", type="integer", default=None, group="props"),
        schema_param("max_size_mb", type="float", default=None, group="props"),
        schema_param("chunk_size_mb", type="float", default=None, group="props"),
        schema_param("layout", type="enum", default="list", group="props", options=["list", "gallery"]),
        schema_param("show_preview", type="boolean", default=True, group="props"),
        schema_param("helper_text", type="string", default=None, group="content"),
        schema_param("button_label", type="string", default="Seleccionar archivos", group="content"),
        schema_param("upload_label", type="string", default="Subir archivos", group="content"),
        schema_param("empty_text", type="string", default="Arrastra archivos aquí o selecciónalos para empezar.", group="content"),
        schema_param("headers", type="object", default=None, group="props"),
        schema_param("on_change", type="string", default=None, group="events"),
        schema_param("on_success", type="string", default=None, group="events"),
        schema_param("on_error", type="string", default=None, group="events"),
        schema_param("id", type="string", default=None, group="identity"),
    ],
    preset_props={
        "label": "Subir activos",
        "accept": "image/*,.pdf",
        "multiple": True,
        "max_files": 4,
        "max_size_mb": 8,
        "layout": "gallery",
        "show_preview": True,
    },
)

register_widget_schema(
    "LanguageSelector",
    category="navigation",
    summary="Language selector with locale labels, flags and persistence.",
    params=[
        schema_param("locales", type="array", default=[], group="content"),
        schema_param("value", type="string", default="es_ES", group="content"),
        schema_param("path", type="string", default=None, group="content"),
        schema_param("default_locale", type="string", default=None, group="props"),
        schema_param("fallback_locale", type="string", default=None, group="props"),
        schema_param("storage_key", type="string", default="martin.locale", group="props"),
        schema_param("query_param", type="string", default="lang", group="props"),
        schema_param("update_url", type="boolean", default=True, group="props"),
        schema_param("persist", type="boolean", default=True, group="props"),
        schema_param("search", type="boolean", default=True, group="props"),
        schema_param("name", type="string", default=None, group="identity"),
        schema_param("id", type="string", default=None, group="identity"),
        schema_param("placeholder", type="string", default="Idioma", group="content"),
        schema_param("on_change", type="string", default=None, group="events"),
    ],
    preset_props={"path": "locales", "value": "es_ES", "search": True},
)

register_widget_schema(
    "DataGrid",
    category="data",
    summary="Advanced data grid with resize, reorder, grouping and virtual scroll.",
    params=[
        schema_param("rows", type="array", default=[], group="content"),
        schema_param("columns", type="array", default=[], group="structure"),
        schema_param("searchable", type="boolean", default=True, group="props"),
        schema_param("sortable", type="boolean", default=True, group="props"),
        schema_param("resizable", type="boolean", default=True, group="props"),
        schema_param("reorderable", type="boolean", default=True, group="props"),
        schema_param("freeze_columns", type="array", default=[], group="props"),
        schema_param("group_by", type="string", default=None, group="props"),
        schema_param("virtual_scroll", type="boolean", default=True, group="props"),
        schema_param("row_height", type="integer", default=40, group="props"),
        schema_param("height", type="integer", default=420, group="style"),
        schema_param("overscan", type="integer", default=8, group="props"),
    ],
    preset_props={
        "columns": [{"key": "name", "label": "Name"}, {"key": "role", "label": "Role"}],
        "rows": [{"name": "Martin", "role": "Framework"}, {"name": "Studio", "role": "Editor"}],
    },
)

register_widget_schema(
    "Form",
    category="advanced",
    summary="Advanced form wrapper with validation hooks and submit handling.",
    params=[
        schema_param("children", type="array", default=[], group="structure", structural=True),
        schema_param("child", type="string", default=None, group="structure", structural=True),
        schema_param("id", type="string", default=None, group="identity"),
        schema_param("schema", type="object", default=None, group="props"),
        schema_param("on_submit", type="string", default="", group="events"),
        schema_param("validate_on_input", type="boolean", default=True, group="props"),
        schema_param("validate_on_blur", type="boolean", default=True, group="props"),
        schema_param("prevent_default", type="boolean", default=True, group="props"),
        schema_param("method", type="enum", default="post", group="props", options=["get", "post"]),
        schema_param("action", type="string", default="", group="link"),
    ],
    preset_props={"id": "demo_form", "method": "post"},
    accepts_children=True,
)

register_widget_schema(
    "Calendar",
    category="compound",
    summary="Interactive calendar with month, week and day views.",
    params=[
        schema_param(
            "events",
            type="array",
            default=[],
            group="content",
            editor={
                "type": "collection",
                "item_label": "Event",
                "fields": [
                    {"name": "title", "label": "Title", "type": "string", "required": True},
                    {"name": "date", "label": "Date", "type": "date", "required": True},
                    {"name": "start_time", "label": "Start time", "type": "time"},
                    {"name": "end_time", "label": "End time", "type": "time"},
                    {"name": "color", "label": "Color", "type": "color"},
                ],
            },
        ),
        schema_param("initial_view", type="enum", default="month", group="props", options=["month", "week", "day"]),
        schema_param("initial_date", type="string", default=None, group="content"),
        schema_param("range_select", type="boolean", default=False, group="props"),
        schema_param("editable", type="boolean", default=False, group="props"),
        schema_param("on_date_click", type="string", default=None, group="events"),
        schema_param("on_event_click", type="string", default=None, group="events"),
        schema_param("on_event_create", type="string", default=None, group="events"),
        schema_param("on_event_update", type="string", default=None, group="events"),
        schema_param("on_event_delete", type="string", default=None, group="events"),
        schema_param("show_views", type="boolean", default=True, group="props"),
        schema_param("show_today", type="boolean", default=True, group="props"),
        schema_param("first_day", type="integer", default=1, group="props"),
        schema_param("locale", type="string", default="es", group="props"),
        schema_param("height", type="integer", default=600, group="style"),
        schema_param("accent", type="string", default="var(--accent)", group="style"),
        schema_param("event_colors", type="array", default=[], group="props"),
    ],
    preset_props={
        "events": [
            {"title": "Launch", "date": "2026-03-20", "color": "#6366f1"},
            {"title": "Demo", "date": "2026-03-25", "start_time": "10:00", "end_time": "11:00", "color": "#10b981"},
        ],
        "initial_view": "month",
        "editable": True,
        "height": 540,
    },
)

register_widget_schema(
    "WizardStep",
    category="advanced",
    summary="Single step used inside a Wizard flow.",
    params=[
        schema_param("title", type="string", default="", group="content"),
        schema_param("description", type="string", default="", group="content"),
        schema_param("child", type="string", default=None, group="structure", structural=True),
        schema_param("children", type="array", default=[], group="structure", structural=True),
    ],
    preset_props={"title": "Step title", "description": "Explain this step."},
    accepts_children=True,
    has_content_slot=True,
)

register_widget_schema(
    "Wizard",
    category="advanced",
    summary="Multi-step widget flow with progress and next/back actions.",
    params=[
        schema_param("children", type="array", default=[], group="structure", structural=True),
        schema_param("child", type="string", default=None, group="structure", structural=True),
        schema_param("initial_step", type="integer", default=0, group="props"),
        schema_param("show_progress", type="boolean", default=True, group="props"),
        schema_param("show_actions", type="boolean", default=True, group="props"),
        schema_param("previous_label", type="string", default="Back", group="content"),
        schema_param("next_label", type="string", default="Next", group="content"),
        schema_param("finish_label", type="string", default="Finish", group="content"),
        schema_param("on_finish", type="string", default="", group="events"),
    ],
    preset_props={"initial_step": 0, "show_progress": True, "show_actions": True},
    accepts_children=True,
)

register_widget_schema(
    "ResourceForm",
    category="advanced",
    summary="Convention-based form widget connected to backend resources.",
    params=[
        schema_param("resource", type="string", default="leads", group="content", required=True),
        schema_param(
            "fields",
            type="array",
            default=[],
            group="content",
            editor={
                "type": "collection",
                "item_label": "Field",
                "fields": [
                    {"name": "name", "label": "Name", "type": "string", "required": True},
                    {"name": "label", "label": "Label", "type": "string"},
                    {"name": "type", "label": "Type", "type": "enum", "options": ["text", "email", "textarea", "select", "checkbox", "number", "date", "time"]},
                    {"name": "placeholder", "label": "Placeholder", "type": "string"},
                    {"name": "value", "label": "Default value", "type": "string"},
                    {"name": "required", "label": "Required", "type": "boolean"},
                    {"name": "options", "label": "Options JSON", "type": "json"},
                ],
            },
        ),
        schema_param("endpoint", type="string", default=None, group="link"),
        schema_param("title", type="string", default=None, group="content"),
        schema_param("submit_label", type="string", default="Guardar", group="content"),
        schema_param("target", type="string", default=None, group="content"),
        schema_param("method", type="enum", default="POST", group="props", options=["POST", "PUT", "PATCH"]),
        schema_param("button_variant", type="enum", default="primary", group="props", options=["primary", "secondary", "ghost", "danger", "link"]),
        schema_param("helper_text", type="string", default="", group="content"),
    ],
    preset_props={
        "resource": "leads",
        "title": "Nuevo lead",
        "submit_label": "Guardar lead",
        "fields": [
            {"name": "nombre", "label": "Nombre", "type": "text", "required": True},
            {"name": "email", "label": "Email", "type": "email", "required": True},
        ],
    },
)

register_widget_schema(
    "ResourceEditor",
    category="advanced",
    summary="Editable resource form that loads one record and updates it.",
    params=[
        schema_param("resource", type="string", default="leads", group="content", required=True),
        schema_param("record_id", type="string", default="1", group="content", required=True),
        schema_param(
            "fields",
            type="array",
            default=[],
            group="content",
            editor={
                "type": "collection",
                "item_label": "Field",
                "fields": [
                    {"name": "name", "label": "Name", "type": "string", "required": True},
                    {"name": "label", "label": "Label", "type": "string"},
                    {"name": "type", "label": "Type", "type": "enum", "options": ["text", "email", "textarea", "select", "checkbox", "number", "date", "time"]},
                    {"name": "placeholder", "label": "Placeholder", "type": "string"},
                    {"name": "required", "label": "Required", "type": "boolean"},
                    {"name": "options", "label": "Options JSON", "type": "json"},
                ],
            },
        ),
        schema_param("endpoint", type="string", default=None, group="link"),
        schema_param("detail_endpoint", type="string", default=None, group="link"),
        schema_param("title", type="string", default=None, group="content"),
        schema_param("submit_label", type="string", default="Actualizar", group="content"),
        schema_param("target", type="string", default=None, group="content"),
        schema_param("method", type="enum", default="PATCH", group="props", options=["POST", "PUT", "PATCH"]),
        schema_param("button_variant", type="enum", default="primary", group="props", options=["primary", "secondary", "ghost", "danger", "link"]),
        schema_param("helper_text", type="string", default="", group="content"),
    ],
    preset_props={
        "resource": "leads",
        "record_id": "1",
        "title": "Editar lead",
        "submit_label": "Actualizar lead",
        "fields": [
            {"name": "nombre", "label": "Nombre", "type": "text", "required": True},
            {"name": "email", "label": "Email", "type": "email", "required": True},
            {"name": "plan", "label": "Plan", "type": "select", "options": [["starter", "Starter"], ["pro", "Pro"], ["enterprise", "Enterprise"]]},
        ],
    },
)

register_widget_schema(
    "ResourceTable",
    category="advanced",
    summary="Convention-based resource table with refresh and backend fetch.",
    params=[
        schema_param("resource", type="string", default="leads", group="content", required=True),
        schema_param(
            "columns",
            type="array",
            default=[],
            group="structure",
            editor={
                "type": "collection",
                "item_label": "Column",
                "fields": [
                    {"name": "key", "label": "Key", "type": "string", "required": True},
                    {"name": "label", "label": "Label", "type": "string"},
                    {"name": "width", "label": "Width", "type": "integer"},
                ],
            },
        ),
        schema_param("rows", type="array", default=[], group="content"),
        schema_param("endpoint", type="string", default=None, group="link"),
        schema_param("title", type="string", default=None, group="content"),
        schema_param("helper_text", type="string", default="", group="content"),
        schema_param("searchable", type="boolean", default=True, group="props"),
        schema_param("refresh_label", type="string", default="Refrescar", group="content"),
        schema_param("height", type="integer", default=340, group="style"),
        schema_param("selectable", type="boolean", default=False, group="props"),
        schema_param("id_field", type="string", default="id", group="content"),
        schema_param("selection_label", type="string", default="Sel.", group="content"),
        schema_param("search_param", type="string", default="q", group="content"),
    ],
    preset_props={
        "resource": "leads",
        "title": "Leads",
        "columns": [{"key": "nombre", "label": "Nombre"}, {"key": "estado", "label": "Estado"}],
        "rows": [{"id": "1", "nombre": "Martin", "estado": "Nuevo"}],
    },
)

register_widget_schema(
    "ResourceDetails",
    category="advanced",
    summary="Convention-based detail view connected to backend resources.",
    params=[
        schema_param("resource", type="string", default="leads", group="content", required=True),
        schema_param("endpoint", type="string", default=None, group="link"),
        schema_param("title", type="string", default=None, group="content"),
        schema_param("record_id", type="string", default=None, group="content"),
        schema_param(
            "fields",
            type="array",
            default=[],
            group="content",
            editor={
                "type": "collection",
                "item_label": "Field",
                "fields": [
                    {"name": "name", "label": "Field name", "type": "string", "required": True},
                    {"name": "label", "label": "Display label", "type": "string"},
                ],
            },
        ),
        schema_param("empty_text", type="string", default="Sin datos", group="content"),
    ],
    preset_props={"resource": "leads", "title": "Lead details", "fields": ["nombre", "email", "estado"]},
)

register_widget_schema(
    "ResourceCardList",
    category="advanced",
    summary="Convention-based card list connected to backend resource collections.",
    params=[
        schema_param("resource", type="string", default="leads", group="content", required=True),
        schema_param("endpoint", type="string", default=None, group="link"),
        schema_param("title", type="string", default=None, group="content"),
        schema_param("subtitle_field", type="string", default=None, group="content"),
        schema_param("badge_field", type="string", default=None, group="content"),
        schema_param("columns", type="integer", default=3, group="style"),
        schema_param("empty_text", type="string", default="Sin elementos", group="content"),
    ],
    preset_props={"resource": "leads", "title": "Lead cards", "subtitle_field": "email", "badge_field": "estado", "columns": 3},
)

register_widget_schema(
    "ResourceFilters",
    category="advanced",
    summary="Declarative filter bar that refreshes a ResourceTable by target id.",
    params=[
        schema_param("target", type="string", default=None, group="content", required=True),
        schema_param(
            "filters",
            type="array",
            default=[],
            group="content",
            editor={
                "type": "collection",
                "item_label": "Filter",
                "fields": [
                    {"name": "name", "label": "Name", "type": "string", "required": True},
                    {"name": "label", "label": "Label", "type": "string"},
                    {"name": "type", "label": "Type", "type": "enum", "options": ["text", "select"]},
                    {"name": "placeholder", "label": "Placeholder", "type": "string"},
                    {"name": "value", "label": "Default value", "type": "string"},
                    {"name": "options", "label": "Options JSON", "type": "json"},
                    {"name": "search", "label": "Searchable select", "type": "boolean"},
                ],
            },
        ),
        schema_param("title", type="string", default=None, group="content"),
        schema_param("button_label", type="string", default="Aplicar filtros", group="content"),
    ],
    preset_props={"target": "leads_table", "filters": [{"name": "estado", "type": "select"}]},
)

register_widget_schema(
    "ResourceActions",
    category="advanced",
    summary="Declarative action bar for resource-oriented backend actions.",
    params=[
        schema_param(
            "actions",
            type="array",
            default=[],
            group="content",
            editor={
                "type": "collection",
                "item_label": "Action",
                "fields": [
                    {"name": "label", "label": "Label", "type": "string", "required": True},
                    {"name": "variant", "label": "Variant", "type": "enum", "options": ["primary", "secondary", "ghost", "danger", "link"]},
                    {"name": "on_click", "label": "JS action", "type": "string"},
                    {"name": "url", "label": "API URL", "type": "string"},
                    {"name": "method", "label": "HTTP method", "type": "enum", "options": ["GET", "POST", "PUT", "PATCH", "DELETE"]},
                    {"name": "backend_method", "label": "Backend method", "type": "string"},
                    {"name": "target", "label": "Target id", "type": "string"},
                    {"name": "body", "label": "Body JSON", "type": "json"},
                    {"name": "params", "label": "Params JSON", "type": "json"},
                ],
            },
        ),
        schema_param("title", type="string", default=None, group="content"),
    ],
    preset_props={"actions": [{"label": "Refrescar", "variant": "secondary"}]},
)

register_widget_schema(
    "ResourceBulkActions",
    category="advanced",
    summary="Bulk actions bound to the current selection of a selectable ResourceTable.",
    params=[
        schema_param("target", type="string", default=None, group="content", required=True),
        schema_param("title", type="string", default=None, group="content"),
        schema_param("empty_message", type="string", default="Selecciona al menos un registro.", group="content"),
        schema_param(
            "actions",
            type="array",
            default=[],
            group="content",
            editor={
                "type": "collection",
                "item_label": "Bulk action",
                "fields": [
                    {"name": "label", "label": "Label", "type": "string", "required": True},
                    {"name": "variant", "label": "Variant", "type": "enum", "options": ["primary", "secondary", "ghost", "danger", "link"]},
                    {"name": "url", "label": "API URL", "type": "string"},
                    {"name": "method", "label": "HTTP method", "type": "enum", "options": ["GET", "POST", "PUT", "PATCH", "DELETE"]},
                    {"name": "backend_method", "label": "Backend method", "type": "string"},
                    {"name": "target", "label": "Target id", "type": "string"},
                    {"name": "body", "label": "Body JSON", "type": "json"},
                    {"name": "confirm_message", "label": "Confirm message", "type": "string"},
                ],
            },
        ),
    ],
    preset_props={"target": "leads_table", "actions": [{"label": "Marcar seguimiento", "variant": "secondary", "url": "/api/resources/leads/bulk", "method": "POST"}]},
)

register_widget_schema(
    "ResourceToolbar",
    category="advanced",
    summary="Search and action toolbar for resource-oriented tables.",
    params=[
        schema_param("target", type="string", default=None, group="content", required=True),
        schema_param("title", type="string", default=None, group="content"),
        schema_param("search_placeholder", type="string", default="Buscar registros...", group="content"),
        schema_param("search_param", type="string", default="q", group="content"),
        schema_param("show_selected_count", type="boolean", default=True, group="props"),
        schema_param(
            "actions",
            type="array",
            default=[],
            group="content",
            editor={
                "type": "collection",
                "item_label": "Toolbar action",
                "fields": [
                    {"name": "label", "label": "Label", "type": "string", "required": True},
                    {"name": "variant", "label": "Variant", "type": "enum", "options": ["primary", "secondary", "ghost", "danger", "link"]},
                    {"name": "on_click", "label": "JS action", "type": "string"},
                ],
            },
        ),
    ],
    preset_props={"target": "leads_table", "title": "Toolbar", "actions": [{"label": "Refrescar", "variant": "secondary", "on_click": "window['leads_table_refresh']&&window['leads_table_refresh']()"}]},
)

register_widget_schema(
    "ResourceCreateButton",
    category="advanced",
    summary="Quick create button that posts data to a convention-based resource save endpoint.",
    params=[
        schema_param("resource", type="string", default="leads", group="content", required=True),
        schema_param("label", type="string", default="Crear", group="content"),
        schema_param("endpoint", type="string", default=None, group="link"),
        schema_param("target", type="string", default=None, group="content"),
        schema_param("variant", type="enum", default="primary", group="props", options=["primary", "secondary", "ghost", "danger", "link"]),
        schema_param("body", type="object", default=None, group="content"),
    ],
    preset_props={"resource": "leads", "label": "Crear lead demo", "body": {"nombre": "Lead rápido", "email": "demo@martin.dev"}},
)

register_widget_schema(
    "ResourceDuplicateButton",
    category="advanced",
    summary="Duplicate an existing record through a resource-oriented endpoint.",
    params=[
        schema_param("resource", type="string", default="leads", group="content", required=True),
        schema_param("record_id", type="string", default="1", group="content", required=True),
        schema_param("label", type="string", default="Duplicar", group="content"),
        schema_param("endpoint", type="string", default=None, group="link"),
        schema_param("target", type="string", default=None, group="content"),
        schema_param("variant", type="enum", default="secondary", group="props", options=["primary", "secondary", "ghost", "danger", "link"]),
        schema_param("body", type="object", default=None, group="content"),
    ],
    preset_props={"resource": "leads", "record_id": "1", "label": "Duplicar lead"},
)

register_widget_schema(
    "ResourceDeleteButton",
    category="advanced",
    summary="Delete button for convention-based resources with confirmation and toast-aware backend calls.",
    params=[
        schema_param("resource", type="string", default="leads", group="content", required=True),
        schema_param("record_id", type="string", default="1", group="content", required=True),
        schema_param("label", type="string", default="Eliminar", group="content"),
        schema_param("endpoint", type="string", default=None, group="link"),
        schema_param("target", type="string", default=None, group="content"),
        schema_param("variant", type="enum", default="danger", group="props", options=["primary", "secondary", "ghost", "danger", "link"]),
        schema_param("confirm_message", type="string", default="¿Eliminar este registro?", group="content"),
    ],
    preset_props={"resource": "leads", "record_id": "2", "label": "Eliminar lead"},
)

register_widget_schema(
    "ResourceView",
    category="advanced",
    summary="Composite resource module combining forms, actions, filters, tables and details.",
    params=[
        schema_param("resource", type="string", default="leads", group="content", required=True),
        schema_param("title", type="string", default=None, group="content"),
        schema_param("helper_text", type="string", default="", group="content"),
        schema_param("table_id", type="string", default=None, group="identity"),
        schema_param("show_form", type="boolean", default=True, group="props"),
        schema_param("show_table", type="boolean", default=True, group="props"),
        schema_param("show_toolbar", type="boolean", default=True, group="props"),
        schema_param("show_bulk_actions", type="boolean", default=False, group="props"),
        schema_param("show_details", type="boolean", default=True, group="props"),
        schema_param("show_cards", type="boolean", default=False, group="props"),
        schema_param("columns", type="array", default=[], group="structure", editor={"type": "collection", "item_label": "Column", "fields": [
            {"name": "key", "label": "Key", "type": "string", "required": True},
            {"name": "label", "label": "Label", "type": "string"},
            {"name": "width", "label": "Width", "type": "integer"},
        ]}),
        schema_param("form_fields", type="array", default=[], group="content", editor={"type": "collection", "item_label": "Field", "fields": [
            {"name": "name", "label": "Name", "type": "string", "required": True},
            {"name": "label", "label": "Label", "type": "string"},
            {"name": "type", "label": "Type", "type": "enum", "options": ["text", "email", "textarea", "select", "checkbox", "number", "date", "time"]},
            {"name": "required", "label": "Required", "type": "boolean"},
            {"name": "options", "label": "Options JSON", "type": "json"},
        ]}),
        schema_param("filters", type="array", default=[], group="content", editor={"type": "collection", "item_label": "Filter", "fields": [
            {"name": "name", "label": "Name", "type": "string", "required": True},
            {"name": "label", "label": "Label", "type": "string"},
            {"name": "type", "label": "Type", "type": "enum", "options": ["text", "select"]},
            {"name": "options", "label": "Options JSON", "type": "json"},
        ]}),
        schema_param("actions", type="array", default=[], group="content", editor={"type": "collection", "item_label": "Action", "fields": [
            {"name": "label", "label": "Label", "type": "string", "required": True},
            {"name": "variant", "label": "Variant", "type": "enum", "options": ["primary", "secondary", "ghost", "danger", "link"]},
            {"name": "on_click", "label": "JS action", "type": "string"},
            {"name": "url", "label": "API URL", "type": "string"},
            {"name": "backend_method", "label": "Backend method", "type": "string"},
        ]}),
        schema_param("toolbar_actions", type="array", default=[], group="content", editor={"type": "collection", "item_label": "Toolbar action", "fields": [
            {"name": "label", "label": "Label", "type": "string", "required": True},
            {"name": "variant", "label": "Variant", "type": "enum", "options": ["primary", "secondary", "ghost", "danger", "link"]},
            {"name": "on_click", "label": "JS action", "type": "string"},
        ]}),
        schema_param("bulk_actions", type="array", default=[], group="content", editor={"type": "collection", "item_label": "Bulk action", "fields": [
            {"name": "label", "label": "Label", "type": "string", "required": True},
            {"name": "variant", "label": "Variant", "type": "enum", "options": ["primary", "secondary", "ghost", "danger", "link"]},
            {"name": "url", "label": "API URL", "type": "string"},
            {"name": "method", "label": "HTTP method", "type": "enum", "options": ["GET", "POST", "PUT", "PATCH", "DELETE"]},
            {"name": "backend_method", "label": "Backend method", "type": "string"},
            {"name": "body", "label": "Body JSON", "type": "json"},
            {"name": "confirm_message", "label": "Confirm message", "type": "string"},
        ]}),
        schema_param("detail_fields", type="array", default=[], group="content", editor={"type": "collection", "item_label": "Detail field", "fields": [
            {"name": "name", "label": "Field name", "type": "string", "required": True},
            {"name": "label", "label": "Display label", "type": "string"},
        ]}),
    ],
    preset_props={
        "resource": "leads",
        "title": "Lead workspace",
        "show_cards": True,
        "show_bulk_actions": True,
        "columns": [{"key": "nombre", "label": "Nombre"}, {"key": "estado", "label": "Estado"}],
        "form_fields": [{"name": "nombre", "label": "Nombre", "type": "text", "required": True}, {"name": "email", "label": "Email", "type": "email", "required": True}],
        "filters": [{"name": "estado", "label": "Estado", "type": "select", "options": [["Nuevo", "Nuevo"], ["Calificado", "Calificado"]]}],
        "actions": [{"label": "Refrescar", "variant": "secondary", "on_click": "window['leads_table_refresh']&&window['leads_table_refresh']()"}],
        "toolbar_actions": [{"label": "Nuevo rápido", "variant": "ghost", "on_click": "console.log('nuevo rápido')"}],
        "bulk_actions": [{"label": "Marcar seguimiento", "variant": "secondary", "url": "/api/resources/leads/bulk", "method": "POST"}],
        "detail_fields": [{"name": "nombre", "label": "Nombre"}, {"name": "email", "label": "Email"}],
    },
)
