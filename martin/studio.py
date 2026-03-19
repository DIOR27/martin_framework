"""Studio metadata helpers for MARTIN tooling."""

from __future__ import annotations

import ast
import importlib.util
import inspect
import json
import os
import sys
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

WIDGET_PRESETS = {
    "Container": {"padding": 16},
    "Row": {"gap": 12},
    "Column": {"gap": 16, "padding": 0},
    "Grid": {"columns": 2, "gap": 16},
    "Card": {"padding": 20, "radius": 16},
    "Text": {"content": "Text"},
    "Heading": {"content": "Heading", "level": 2},
    "Paragraph": {"content": "Paragraph"},
    "Link": {"content": "Link", "href": "#"},
    "Code": {"content": "print('Hello, MARTIN')", "language": "python", "block": True},
    "Image": {"src": "/assets/icon.webp", "alt": "Image"},
    "Video": {"src": "https://www.w3schools.com/html/mov_bbb.mp4"},
    "Icon": {"name": "star"},
    "Avatar": {"src": "/assets/icon.webp", "alt": "Avatar"},
    "Button": {"label": "Button", "variant": "primary"},
    "TextField": {"placeholder": "Type here"},
    "TextArea": {"placeholder": "Write something..."},
    "Checkbox": {"label": "Accept terms"},
    "Select": {
        "options": [["starter", "Starter"], ["pro", "Pro"], ["enterprise", "Enterprise"]],
        "value": "starter",
        "placeholder": "Choose a plan",
    },
    "MultiSelect": {
        "options": [["design", "Design"], ["frontend", "Frontend"], ["backend", "Backend"]],
        "values": ["design", "frontend"],
    },
    "Slider": {"min": 0, "max": 100, "value": 60},
    "ColorPicker": {"value": "#6366f1", "label": "Brand color"},
    "DatePicker": {"label": "Event date", "value": "2026-03-18"},
    "RadioGroup": {
        "options": [["monthly", "Monthly"], ["yearly", "Yearly"]],
        "value": "monthly",
    },
    "NumberInput": {"value": 1, "min": 0, "max": 10},
    "TimePicker": {"value": "09:00", "label": "Start time"},
    "ProgressBar": {"value": 72, "label": "Completion"},
    "Rating": {"value": 4},
    "FileInput": {"label": "Upload file"},
    "Badge": {"content": "Badge"},
    "Alert": {"title": "Heads up", "message": "This is an alert example."},
    "NavBar": {"sticky": True, "bordered": True},
    "Footer": {"bordered": True},
    "Breadcrumb": {"items": [["Home", "/"], ["Docs", "/docs"], ["Studio", None]]},
    "Tabs": {
        "items": [
            {"label": "Overview", "content": "Overview content"},
            {"label": "API", "content": "API content"},
        ]
    },
    "Table": {
        "columns": ["Name", "Role", "Status"],
        "rows": [["Martin", "Admin", "Active"], ["Studio", "Editor", "Ready"]],
    },
    "Modal": {"id": "demo_modal", "title": "Modal title"},
    "Raw": {"html": "<div>Raw HTML</div>"},
    "Script": {"code": "console.log('martin studio');"},
    "Stylesheet": {"href": "https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap"},
    "StyleTag": {"css": ".demo { color: var(--accent); }"},
    "ThemeToggle": {},
    "CookieBanner": {"title": "Cookies", "message": "We use cookies to improve the experience."},
    "CookieCategory": {"title": "Analytics", "description": "Anonymous usage metrics."},
    "SafeArea": {},
    "WordCloud": {"words": {"Python": 10, "MARTIN": 9, "Studio": 8, "Widgets": 7, "Preview": 6}},
    "Map": {
        "markers": [
            [-2.897, -79.004, "Cuenca"],
            [-0.220, -78.512, "Quito"],
            [-2.203, -79.890, "Guayaquil"],
        ],
        "route": True,
        "height": 420,
    },
    "Timeline": {
        "items": [
            {"title": "Kickoff", "date": "Q1 2026", "description": "Project started", "icon": "🚀", "color": "#6366f1"},
            {"title": "Studio", "date": "Q2 2026", "description": "Visual editor ready", "icon": "✨", "color": "#10b981"},
        ]
    },
    "Hero": {"title": "Build with MARTIN", "subtitle": "Design and code in one place.", "align": "left", "layout": "centered"},
    "Gallery": {
        "items": [
            {"src": "/assets/art_dog_field_sunrise.svg", "title": "Morning Field"},
            {"src": "/assets/art_dog_hill_breeze.svg", "title": "Hill Breeze"},
            {"src": "/assets/art_dog_day_blossom.svg", "title": "Day Blossom"},
        ]
    },
    "Carousel": {
        "items": [
            {"image": "/assets/art_dog_field_sunrise.svg", "title": "Slide One", "subtitle": "First slide"},
            {"image": "/assets/art_dog_hill_breeze.svg", "title": "Slide Two", "subtitle": "Second slide"},
        ],
        "visible": 1,
        "dots": True,
    },
    "Accordion": {
        "items": [
            {"title": "What is MARTIN?", "content": "A Python-first UI framework.", "open": True},
            {"title": "Can I export static sites?", "content": "Yes, with HTML or split output."},
        ]
    },
    "Testimonials": {
        "items": [
            {"quote": "Fast and expressive.", "name": "Diego", "role": "Founder", "rating": 5},
            {"quote": "Great for rapid prototyping.", "name": "Team", "role": "Builders", "rating": 5},
        ]
    },
    "SlideCarousel": {
        "items": [
            {"title": "First slide", "subtitle": "Visual storytelling"},
            {"title": "Second slide", "subtitle": "Motion and layout"},
        ]
    },
    "Pricing": {
        "plans": [
            {"name": "Starter", "price": 19, "features": ["1 project", "Email support"], "cta_label": "Choose Starter"},
            {"name": "Pro", "price": 49, "features": ["Unlimited projects", "Priority support"], "featured": True, "badge": "Popular"},
        ]
    },
    "FAQ": {
        "items": [
            {"question": "Can I use Python only?", "answer": "Yes, MARTIN is Python-first.", "open": True},
            {"question": "Does it support backend actions?", "answer": "Yes, through martin.backend."},
        ]
    },
    "Chart": {
        "type": "bar",
        "labels": ["Jan", "Feb", "Mar", "Apr"],
        "datasets": [{"label": "Sales", "data": [12, 19, 7, 15], "color": "#6366f1"}],
        "title": "Monthly sales",
    },
    "Calendar": {
        "events": [
            {"title": "Launch", "date": "2026-03-20", "color": "#6366f1"},
            {"title": "Demo", "date": "2026-03-25", "start_time": "10:00", "end_time": "11:00", "color": "#10b981"},
        ],
        "initial_view": "month",
        "editable": True,
        "height": 540,
    },
    "DataGrid": {
        "columns": [{"key": "name", "label": "Name"}, {"key": "role", "label": "Role"}],
        "rows": [{"name": "Martin", "role": "Framework"}, {"name": "Studio", "role": "Editor"}],
    },
    "CommandPalette": {
        "items": [
            {"label": "Open docs", "href": "/docs"},
            {"label": "New page", "action": "console.log('new page')"},
        ]
    },
    "Drawer": {"id": "demo_drawer", "title": "Drawer title"},
    "SplitPane": {"ratio": 0.5},
    "Skeleton": {"lines": 3},
    "EmptyState": {"title": "Nothing here yet", "description": "Add your first widget."},
    "ErrorState": {"title": "Something went wrong", "description": "Try again in a moment."},
    "Form": {"id": "demo_form", "method": "post"},
    "JSWidgetAdapter": {"tag": "div", "script": "console.log('adapter ready')"},
}

PROP_EDITORS = {
    "Calendar.events": {
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
    "WordCloud.words": {
        "type": "key_value",
        "entry_label": "Word",
        "key_label": "Word",
        "value_label": "Weight",
        "key_placeholder": "Python",
        "value_placeholder": "10",
        "value_type": "integer",
    },
}


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

    if param_name in {
        "options",
        "values",
        "items",
        "markers",
        "events",
        "datasets",
        "labels",
        "plans",
        "rows",
        "links",
        "actions",
        "words",
        "schema",
    }:
        if param_name == "words":
            return "object"
        if param_name == "schema":
            return "object"
        return "array"
    if widget_name == "DataGrid" and param_name == "columns":
        return "array"

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
    editor_key = f"{widget_name}.{param.name}"
    if editor_key in PROP_EDITORS:
        result["editor"] = dict(PROP_EDITORS[editor_key])
    return result


def get_widget_preset(name: str) -> dict:
    return dict(WIDGET_PRESETS.get(name, {}))


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
                "preset_props": get_widget_preset(name),
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


def parse_source_file_to_design(path: str | Path) -> dict:
    source_path = Path(path)
    module = ast.parse(source_path.read_text(encoding="utf-8"), filename=str(source_path))
    parser = _StudioAstParser(source_path)
    return parser.parse(module)


def render_source_file_preview_html(path: str | Path) -> str:
    source_path = Path(path).resolve()
    module_name = f"_martin_studio_preview_{source_path.stem}_{abs(hash(str(source_path)))}"
    project_path = str(source_path.parent.parent if source_path.parent.name == "pages" else source_path.parent)
    added_path = False
    if project_path not in sys.path:
        sys.path.insert(0, project_path)
        added_path = True
    try:
        spec = importlib.util.spec_from_file_location(module_name, str(source_path))
        if spec is None or spec.loader is None:
            raise RuntimeError(f"Cannot load module from {source_path}")
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)

        candidate_names = [source_path.stem, "build", "home", "page"]
        candidate = None
        for name in candidate_names:
            fn = getattr(module, name, None)
            if callable(fn):
                candidate = fn
                break
        if candidate is None:
            for value in module.__dict__.values():
                if callable(value) and getattr(value, "__module__", None) == module.__name__:
                    candidate = value
                    break
        if candidate is None:
            raise RuntimeError(f"No render function found in {source_path.name}")

        from .app import App

        app = App(build=candidate, title=source_path.stem, hot_reload=False)
        return app._render("/")
    finally:
        sys.modules.pop(module_name, None)
        if added_path and project_path in sys.path:
            sys.path.remove(project_path)


class _StudioAstParser:
    def __init__(self, source_path: Path):
        self.source_path = source_path
        self.widget_names = {
            name
            for name in getattr(_widgets, "__all__", [])
            if hasattr(_widgets, name) and inspect.isclass(getattr(_widgets, name))
        }
        self.assignments = {}
        self.imported_names = set()
        self._node_counter = 0
        self._local_assignments = {}
        self._loop_vars = set()

    def parse(self, module: ast.Module) -> dict:
        self._index_module(module)
        root_node = self._find_root_widget(module)
        if root_node is None:
            root_node = self._fallback_node("Raw", {"content": f"Unsupported source: {self.source_path.name}"})
        return {
            "version": 1,
            "title": self.source_path.stem,
            "source_file": str(self.source_path),
            "root": root_node,
        }

    def _index_module(self, module: ast.Module):
        for node in module.body:
            if isinstance(node, ast.ImportFrom) and node.module == "martin":
                for alias in node.names:
                    self.imported_names.add(alias.asname or alias.name)
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        self.assignments[target.id] = node.value

    def _find_root_widget(self, module: ast.Module):
        functions = [node for node in module.body if isinstance(node, ast.FunctionDef)]
        preferred_names = [
            self.source_path.stem,
            "home",
            "page",
            "build",
        ]
        ordered = []
        for name in preferred_names:
            ordered.extend(node for node in functions if node.name == name and node not in ordered)
        ordered.extend(node for node in functions if not node.name.startswith("_") and node not in ordered)
        ordered.extend(node for node in functions if node not in ordered)

        for node in ordered:
            self._local_assignments = {}
            for inner in node.body:
                if isinstance(inner, ast.Assign):
                    for target in inner.targets:
                        if isinstance(target, ast.Name):
                            self._local_assignments[target.id] = inner.value
            for inner in node.body:
                if isinstance(inner, ast.Return):
                    candidate = self._extract_return_root(inner.value)
                    if candidate is not None:
                        return candidate
        return None

    def _extract_return_root(self, value):
        if isinstance(value, ast.Tuple) and value.elts:
            return self._convert_expr(value.elts[0])
        return self._convert_expr(value)

    def _convert_expr(self, expr):
        if isinstance(expr, ast.Call):
            return self._convert_call(expr)
        if isinstance(expr, ast.Name):
            assigned = self._local_assignments.get(expr.id)
            if assigned is not None:
                return self._convert_expr(assigned)
            assigned = self.assignments.get(expr.id)
            if assigned is None:
                return self._fallback_node("Raw", {"content": f"Reference: {expr.id}"})
            return self._convert_expr(assigned)
        if isinstance(expr, ast.Constant):
            return self._fallback_node("Text", {"content": expr.value})
        if isinstance(expr, ast.List):
            children = []
            for item in expr.elts:
                child = self._convert_expr(item)
                if child is not None:
                    children.append(child)
            return self._fallback_node("Raw", {"content": f"List[{len(expr.elts)}]"}, children=children)
        if isinstance(expr, ast.ListComp):
            return self._convert_list_comp(expr)
        return None

    def _convert_list_comp(self, expr: ast.ListComp):
        added_loop_vars = []
        for generator in expr.generators:
            for loop_var in self._extract_target_names(generator.target):
                if loop_var not in self._loop_vars:
                    self._loop_vars.add(loop_var)
                    added_loop_vars.append(loop_var)
        try:
            template = self._convert_expr(expr.elt)
        finally:
            for loop_var in added_loop_vars:
                self._loop_vars.discard(loop_var)
        if template is None:
            return self._fallback_node("Raw", {"content": "List comprehension"})
        return self._fallback_node(
            "Column",
            {"gap": 12, "studio_note": "Generated from list comprehension"},
            children=[template],
        )

    def _convert_call(self, call: ast.Call):
        widget_name = self._resolve_called_name(call.func)
        if not widget_name:
            return self._fallback_node("Raw", {"content": "Unsupported call"})

        props = {}
        children = []

        if call.args:
            first = call.args[0]
            if isinstance(first, ast.List):
                children.extend(self._convert_children_list(first))
            else:
                positional = self._literal_value(first)
                key = self._default_content_prop(widget_name)
                if key and positional is not None:
                    props[key] = positional

        for kw in call.keywords:
            if kw.arg is None:
                continue
            if kw.arg == "children" and isinstance(kw.value, ast.List):
                children.extend(self._convert_children_list(kw.value))
                continue
            if kw.arg == "child":
                child_node = self._convert_expr(kw.value)
                if child_node is not None:
                    children.append(child_node)
                continue
            literal = self._literal_value(kw.value)
            if literal is not None:
                props[kw.arg] = literal
            elif isinstance(kw.value, ast.Name):
                props[kw.arg] = f"$ref:{kw.value.id}"
            elif isinstance(kw.value, ast.ListComp):
                props[kw.arg] = "$expr:listcomp"
            elif isinstance(kw.value, ast.Call):
                inner_name = self._resolve_called_name(kw.value.func)
                props[kw.arg] = f"$call:{inner_name or 'unknown'}"

        return {
            "id": self._next_id(),
            "type": widget_name,
            "props": props,
            "children": children,
        }

    def _convert_children_list(self, list_node: ast.List):
        children = []
        for item in list_node.elts:
            child = self._convert_expr(item)
            if child is not None:
                children.append(child)
        return children

    def _resolve_called_name(self, func):
        if isinstance(func, ast.Name):
            name = func.id
            if name in self.widget_names or name in self.imported_names:
                return name
            return name
        if isinstance(func, ast.Attribute):
            return func.attr
        return None

    def _default_content_prop(self, widget_name: str):
        if widget_name in {"Text", "Heading", "Paragraph", "Link", "Code"}:
            return "content"
        if widget_name == "Button":
            return "label"
        if widget_name == "Raw":
            return "html"
        if widget_name == "StyleTag":
            return "css"
        if widget_name == "Stylesheet":
            return "href"
        if widget_name in {"Image", "Video"}:
            return "src"
        if widget_name == "Script":
            return "code"
        return None

    def _literal_value(self, node):
        if isinstance(node, ast.Constant):
            return node.value
        if isinstance(node, ast.Name):
            if node.id in self._loop_vars:
                return "{" + node.id + "}"
            if node.id in self._local_assignments:
                return self._literal_value(self._local_assignments[node.id])
            if node.id in self.assignments:
                return self._literal_value(self.assignments[node.id])
            return "{" + node.id + "}"
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
            operand = self._literal_value(node.operand)
            if isinstance(operand, (int, float)):
                return -operand
        if isinstance(node, ast.List):
            values = []
            for item in node.elts:
                value = self._literal_value(item)
                if value is None:
                    return None
                values.append(value)
            return values
        if isinstance(node, ast.Tuple):
            values = []
            for item in node.elts:
                value = self._literal_value(item)
                if value is None:
                    return None
                values.append(value)
            return values
        if isinstance(node, ast.Dict):
            result = {}
            for key, value in zip(node.keys, node.values):
                key_value = self._literal_value(key)
                value_value = self._literal_value(value)
                if not isinstance(key_value, str) or value_value is None:
                    return None
                result[key_value] = value_value
            return result
        return None

    def _extract_target_names(self, target):
        if isinstance(target, ast.Name):
            return [target.id]
        if isinstance(target, (ast.Tuple, ast.List)):
            names = []
            for item in target.elts:
                names.extend(self._extract_target_names(item))
            return names
        return []

    def _fallback_node(self, widget_type: str, props: dict | None = None, children=None):
        safe_props = dict(props or {})
        if widget_type == "Raw" and "content" in safe_props and "html" not in safe_props:
            safe_props["html"] = safe_props.pop("content")
        return {
            "id": self._next_id(),
            "type": widget_type,
            "props": safe_props,
            "children": children or [],
        }

    def _next_id(self) -> str:
        self._node_counter += 1
        return f"src_{self._node_counter}"
