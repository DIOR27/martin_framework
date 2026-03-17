"""
Martin - Widget Base

Every widget automatically accepts:
    style      — StyleBase | list[StyleBase] | str (raw CSS) | None
    padding    — int  or  Padding(...)
    margin     — int  or  Margin(...)
    width      — int (px) or str ("100%", "auto"...)
    height     — int (px) or str
    color      — str  (text color shorthand)
    background — str  (background-color shorthand)
    radius     — int  (border-radius shorthand)
    shadow     — bool | Shadow(...)
    opacity    — float (0.0 – 1.0)
    hidden     — bool (display: none)
    url        — str  wrap widget in <a href="..."> (optional)
    url_target — str  "_self" same tab | "_blank" new tab (default)

These are merged on top of the widget's own base styles automatically.
"""

import html as _html
import re as _re
from functools import wraps as _wraps

from .styles import resolve_styles, StyleBase


class Widget:
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        render = cls.__dict__.get("render")
        if render is None:
            return
        if getattr(render, "_martin_auto_attrs_wrapped", False):
            return

        @_wraps(render)
        def _wrapped_render(self, *args, **kwargs):
            html = render(self, *args, **kwargs)
            return self._apply_universal_attrs(html)

        _wrapped_render._martin_auto_attrs_wrapped = True
        cls.render = _wrapped_render

    @staticmethod
    def _extract_props(kwargs: dict) -> dict:
        """Pop universal style props from kwargs dict (mutates it)."""
        keys = (
            "style",
            "padding",
            "margin",
            "width",
            "height",
            "color",
            "background",
            "radius",
            "shadow",
            "opacity",
            "hidden",
            "url",
            "url_target",
            "attrs",
            "role",
            "tabindex",
        )
        props = {k: kwargs.pop(k, None) for k in keys}

        attrs = {}
        raw_attrs = props.get("attrs")
        if isinstance(raw_attrs, dict):
            attrs.update(raw_attrs)

        if props.get("role") is not None:
            attrs.setdefault("role", props.get("role"))
        if props.get("tabindex") is not None:
            attrs.setdefault("tabindex", props.get("tabindex"))

        for key in list(kwargs.keys()):
            if key.startswith("aria_") or key.startswith("data_"):
                attrs[key.replace("_", "-")] = kwargs.pop(key)

        props["attrs"] = attrs or None
        return props

    def _get_universal_attrs(self) -> dict:
        props = getattr(self, "_props", {}) or {}
        attrs = props.get("attrs")
        attrs = dict(attrs) if isinstance(attrs, dict) else {}
        defaults = self._default_a11y_attrs()
        if isinstance(defaults, dict):
            for key, value in defaults.items():
                if value is None:
                    continue
                attrs.setdefault(key, value)
        return attrs

    def _default_a11y_attrs(self) -> dict:
        """Widget-level defaults that can be overridden by explicit attrs/aria_*."""
        return {}

    @staticmethod
    def _to_plain_text(value) -> str:
        if value is None:
            return ""
        if isinstance(value, Widget):
            return ""
        text = str(value).strip()
        return " ".join(text.split())

    @staticmethod
    def _inject_attrs_into_first_tag(html: str, attrs: dict) -> str:
        if not html or not isinstance(html, str) or not attrs:
            return html

        skip_tags = {"script", "style", "link", "meta"}
        for m in _re.finditer(r"<([a-zA-Z][a-zA-Z0-9:_-]*)(\s[^<>]*?)?>", html):
            tag = (m.group(1) or "").lower()
            if tag in skip_tags:
                continue

            tag_src = html[m.start() : m.end()]
            parts = []
            for key, value in attrs.items():
                if value is None:
                    continue
                attr = str(key).replace("_", "-")
                if _re.search(
                    rf"""\b{_re.escape(attr)}(?:\s*=|\s|/?>)""",
                    tag_src,
                    flags=_re.IGNORECASE,
                ):
                    continue
                if isinstance(value, bool):
                    if value:
                        parts.append(attr)
                else:
                    esc = _html.escape(str(value), quote=True)
                    parts.append(f'{attr}="{esc}"')

            if not parts:
                return html

            insert_at = (
                m.end() - 2 if html[m.end() - 2 : m.end()] == "/>" else m.end() - 1
            )
            return html[:insert_at] + " " + " ".join(parts) + html[insert_at:]

        return html

    def _apply_universal_attrs(self, html: str) -> str:
        attrs = self._get_universal_attrs()
        return self._inject_attrs_into_first_tag(html, attrs)

    def _wrap_url(self, html: str) -> str:
        """If url prop is set, wraps rendered HTML in an <a> tag."""
        props = getattr(self, "_props", {})
        url = props.get("url")
        if not url:
            return html
        target = props.get("url_target") or "_blank"
        href = _html.escape(str(url), quote=True)
        target_esc = _html.escape(str(target), quote=True)
        rel = ' rel="noopener noreferrer"' if target == "_blank" else ""
        return f'<a href="{href}" target="{target_esc}"{rel} style="display:contents;text-decoration:none;">{html}</a>'

    def _resolve_props(self, base_css: str = "") -> str:
        """Merge base_css + any universal props into a single inline CSS string."""
        props = getattr(self, "_props", {})
        parts = [p for p in [base_css] if p]

        style = props.get("style")
        if style is not None:
            parts.append(resolve_styles(style))

        p = props.get("padding")
        if p is not None:
            parts.append(
                f"padding: {p}px" if isinstance(p, (int, float)) else resolve_styles(p)
            )

        m = props.get("margin")
        if m is not None:
            parts.append(
                f"margin: {m}px" if isinstance(m, (int, float)) else resolve_styles(m)
            )

        w = props.get("width")
        if w is not None:
            parts.append(
                f"width: {w}px" if isinstance(w, (int, float)) else f"width: {w}"
            )

        h = props.get("height")
        if h is not None:
            parts.append(
                f"height: {h}px" if isinstance(h, (int, float)) else f"height: {h}"
            )

        c = props.get("color")
        if c is not None:
            parts.append(f"color: {c}")

        bg = props.get("background")
        if bg is not None:
            parts.append(f"background: {bg}")

        r = props.get("radius")
        if r is not None:
            parts.append(f"border-radius: {r}px")

        sh = props.get("shadow")
        if sh is not None:
            if isinstance(sh, bool):
                if sh:
                    parts.append("box-shadow: 0 2px 8px rgba(0,0,0,0.15)")
            else:
                parts.append(resolve_styles(sh))

        op = props.get("opacity")
        if op is not None:
            parts.append(f"opacity: {op}")

        if props.get("hidden"):
            parts.append("display: none")

        return "; ".join(p for p in parts if p)

    @staticmethod
    def _css(*styles) -> str:
        return resolve_styles(*styles)

    @staticmethod
    def _attrs(**kwargs) -> str:
        parts = []
        for k, v in kwargs.items():
            if v is None:
                continue
            attr = k.replace("_", "-")
            if isinstance(v, bool):
                if v:
                    parts.append(attr)
            else:
                escaped = _html.escape(str(v), quote=True)
                parts.append(f'{attr}="{escaped}"')
        return (" " + " ".join(parts)) if parts else ""

    @staticmethod
    def _render_children(children) -> str:
        if not children:
            return ""
        parts = []
        for child in children:
            if isinstance(child, Widget):
                parts.append(child.render())
            elif child is not None:
                parts.append(str(child))
        return "".join(parts)

    @staticmethod
    def _resolve_inner(text=None, child=None, children=None) -> str:
        """
        Resuelve el contenido de un widget hoja.
        Prioridad: children > child > text
        Permite anidar widgets dentro de cualquier widget.
        """
        if children:
            return Widget._render_children(children)
        if child is not None:
            return child.render() if isinstance(child, Widget) else str(child)
        if text is not None:
            return text.render() if isinstance(text, Widget) else str(text)
        return ""

    def render(self) -> str:
        raise NotImplementedError(f"{self.__class__.__name__} must implement render()")

    def __str__(self):
        return self.render()

    def __repr__(self):
        return f"<{self.__class__.__name__}>"
