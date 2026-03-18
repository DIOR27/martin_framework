"""Studio metadata helpers for MARTIN tooling."""

from __future__ import annotations

import inspect
import json
from pathlib import Path

from .widget import Widget
from . import widgets as _widgets


UNIVERSAL_PROPS = [
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
    {"name": "url", "type": "string", "default": None, "group": "link"},
    {"name": "url_target", "type": "string", "default": None, "group": "link"},
    {"name": "role", "type": "string", "default": None, "group": "a11y"},
    {"name": "tabindex", "type": "integer", "default": None, "group": "a11y"},
]


WIDGET_CATEGORIES = {
    "Container": "layout",
    "Row": "layout",
    "Column": "layout",
    "Grid": "layout",
    "Stack": "layout",
    "Card": "layout",
    "Section": "layout",
    "Spacer": "layout",
    "Divider": "layout",
    "Text": "text",
    "Heading": "text",
    "Paragraph": "text",
    "Link": "text",
    "Code": "text",
    "Image": "media",
    "Video": "media",
    "Icon": "media",
    "IconPack": "media",
    "Avatar": "media",
    "Button": "input",
    "TextField": "input",
    "TextArea": "input",
    "Checkbox": "input",
    "Select": "input",
    "MultiSelect": "input",
    "Slider": "input",
    "ColorPicker": "input",
    "DatePicker": "input",
    "RadioGroup": "input",
    "NumberInput": "input",
    "TimePicker": "input",
    "ProgressBar": "input",
    "Rating": "input",
    "FileInput": "input",
    "FormGroup": "input",
    "Badge": "feedback",
    "Alert": "feedback",
    "NavBar": "navigation",
    "SideMenu": "navigation",
    "Footer": "navigation",
    "Breadcrumb": "navigation",
    "Tabs": "navigation",
    "Table": "data",
    "DataGrid": "data",
    "Modal": "overlay",
    "CommandPalette": "advanced",
    "Drawer": "advanced",
    "SplitPane": "advanced",
    "Skeleton": "advanced",
    "EmptyState": "advanced",
    "ErrorState": "advanced",
    "Form": "advanced",
    "JSWidgetAdapter": "advanced",
    "Raw": "utility",
    "Script": "utility",
    "Stylesheet": "utility",
    "StyleTag": "utility",
    "ThemeToggle": "utility",
    "SafeArea": "utility",
    "CookieBanner": "utility",
    "CookieCategory": "utility",
    "WordCloud": "compound",
    "Map": "compound",
    "Timeline": "compound",
    "Hero": "marketing",
    "Gallery": "marketing",
    "Carousel": "marketing",
    "Accordion": "marketing",
    "Testimonials": "marketing",
    "SlideCarousel": "marketing",
    "Pricing": "marketing",
    "FAQ": "marketing",
    "Chart": "compound",
    "Calendar": "compound",
}


ENUMS = {
    "Button.variant": sorted(getattr(_widgets.Button, "VARIANTS", {}).keys()),
    "Link.target": ["_self", "_blank"],
    "Row.align": ["stretch", "center", "flex-start", "flex-end", "baseline"],
    "Row.justify": [
        "flex-start",
        "center",
        "flex-end",
        "space-between",
        "space-around",
        "space-evenly",
    ],
    "Column.align": ["stretch", "center", "flex-start", "flex-end"],
    "Column.justify": [
        "flex-start",
        "center",
        "flex-end",
        "space-between",
        "space-around",
        "space-evenly",
    ],
    "Hero.align": ["center", "left", "right"],
    "Hero.layout": ["centered", "split"],
    "Hero.actions_direction": ["row", "column"],
    "Drawer.side": ["left", "right"],
    "Code.theme": ["auto", "dark", "light"],
}


IGNORED_PARAMS = {"self", "kwargs", "args"}
STRUCTURAL_PARAMS = {"child", "children"}


def _clean_doc(doc: str | None) -> str:
    if not doc:
        return ""
    return inspect.cleandoc(doc).strip()


def _first_sentence(doc: str | None) -> str:
    text = _clean_doc(doc)
    if not text:
        return ""
    return text.splitlines()[0].strip()


def _safe_default(value):
    if value is inspect._empty:
        return None
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if isinstance(value, (list, tuple)) and all(
        isinstance(item, (str, int, float, bool)) or item is None for item in value
    ):
        return list(value)
    if isinstance(value, dict) and all(
        isinstance(k, str)
        and (isinstance(v, (str, int, float, bool)) or v is None)
        for k, v in value.items()
    ):
        return dict(value)
    return None


def _annotation_name(annotation) -> str:
    if annotation is inspect._empty:
        return ""
    if isinstance(annotation, str):
        return annotation
    return getattr(annotation, "__name__", str(annotation))


def _infer_type(widget_name: str, param_name: str, annotation, default):
    enum_key = f"{widget_name}.{param_name}"
    if enum_key in ENUMS:
        return "enum"

    if annotation in (bool, "bool") or isinstance(default, bool):
        return "boolean"
    if annotation in (int, "int") or isinstance(default, int):
        return "integer"
    if annotation in (float, "float") or isinstance(default, float):
        return "float"
    if annotation in (list, tuple, "list", "tuple") or isinstance(default, (list, tuple)):
        return "array"
    if annotation in (dict, "dict") or isinstance(default, dict):
        return "object"

    lowered = param_name.lower()
    if lowered in {"disabled", "checked", "hidden", "wrap", "search", "overlay"}:
        return "boolean"
    if lowered.endswith("_id") or lowered in {"id", "name", "href", "placeholder", "title"}:
        return "string"
    if lowered in {"gap", "padding", "margin", "radius", "width", "height", "rows", "columns"}:
        return "integer"
    if lowered in {"content", "label", "subtitle", "description", "text"}:
        return "string"
    return "string"


def _parameter_group(name: str) -> str:
    lowered = name.lower()
    if lowered in {"content", "label", "title", "subtitle", "text", "placeholder"}:
        return "content"
    if lowered in {"id", "class_name", "name", "href", "target"}:
        return "identity"
    if lowered in {"children", "child", "items", "columns", "rows"}:
        return "structure"
    return "props"


def _describe_parameter(widget_name: str, param: inspect.Parameter) -> dict:
    default = _safe_default(param.default)
    annotation = _annotation_name(param.annotation)
    prop_type = _infer_type(widget_name, param.name, param.annotation, param.default)
    result = {
        "name": param.name,
        "type": prop_type,
        "annotation": annotation,
        "required": param.default is inspect._empty,
        "default": default,
        "group": _parameter_group(param.name),
        "structural": param.name in STRUCTURAL_PARAMS,
    }
    enum_key = f"{widget_name}.{param.name}"
    if enum_key in ENUMS:
        result["options"] = ENUMS[enum_key]
    return result


def get_widget_catalog() -> dict:
    widget_names = [name for name in getattr(_widgets, "__all__", []) if hasattr(_widgets, name)]
    widgets = []

    for name in widget_names:
        cls = getattr(_widgets, name)
        if not inspect.isclass(cls) or not issubclass(cls, Widget):
            continue

        signature = inspect.signature(cls.__init__)
        params = []
        has_content_slot = False
        accepts_children = False
        for param in signature.parameters.values():
            if param.name in IGNORED_PARAMS:
                continue
            if param.kind in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD):
                continue
            described = _describe_parameter(name, param)
            params.append(described)
            if param.name in {"content", "label", "title"}:
                has_content_slot = True
            if param.name in STRUCTURAL_PARAMS:
                accepts_children = True

        widgets.append(
            {
                "name": name,
                "category": WIDGET_CATEGORIES.get(name, "other"),
                "module": cls.__module__,
                "doc": _clean_doc(cls.__doc__),
                "summary": _first_sentence(cls.__doc__),
                "accepts_children": accepts_children,
                "has_content_slot": has_content_slot,
                "params": params + [dict(prop) for prop in UNIVERSAL_PROPS],
            }
        )

    widgets.sort(key=lambda item: (item["category"], item["name"]))
    categories = sorted({item["category"] for item in widgets})
    return {
        "version": 1,
        "widget_count": len(widgets),
        "categories": categories,
        "widgets": widgets,
    }


def describe_widget(name: str) -> dict | None:
    for widget in get_widget_catalog()["widgets"]:
        if widget["name"] == name:
            return widget
    return None


def export_widget_catalog_json(path: str | Path) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(get_widget_catalog(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return target

