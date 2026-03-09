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

These are merged on top of the widget's own base styles automatically.
"""

from .styles import resolve_styles, StyleBase


class Widget:

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
        )
        return {k: kwargs.pop(k, None) for k in keys}

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
                parts.append(f'{attr}="{v}"')
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
