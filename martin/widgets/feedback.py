"""
Martin — Feedback Widgets

Widgets para comunicar estado al usuario.

    Badge  — etiqueta de estado o categoría, pequeña y llamativa
    Alert  — mensaje de alerta o notificación inline
"""

from ..widget import Widget


# =============================================================================
# Badge
# =============================================================================


class Badge(Widget):
    """
    Etiqueta de estado o categoría. Pequeña y llamativa.

        Badge("Nuevo")
        Badge("Pro", background="var(--accent)", color="#fff")
        Badge("Beta", background="#f59e0b", radius=4)
        Badge("v2.0", background="var(--surface-2)", color="var(--text)", radius=4)

    Por defecto usa el color de acento del tema con texto blanco.
    """

    def __init__(self, label=None, child=None, children=None, **kwargs):
        self._props = Widget._extract_props(kwargs)
        self.label = label
        self.child = child
        self.children = children
        # Defaults de color si no se proporcionaron
        if not self._props.get("background"):
            self._props["background"] = "var(--accent)"
        if not self._props.get("color"):
            self._props["color"] = "#ffffff"

    def render(self):
        base = (
            "display:inline-block; padding:2px 10px; border-radius:9999px; "
            "font-size:12px; font-weight:600; white-space:nowrap"
        )
        inline = self._resolve_props(base)
        inner = self._resolve_inner(self.label, self.child, self.children)
        return self._wrap_url(f'<span style="{inline}">{inner}</span>')


# =============================================================================
# Alert
# =============================================================================


class Alert(Widget):
    """
    Mensaje de alerta o notificación inline.

        Alert("Guardado correctamente.", variant="success")
        Alert("Email inválido.", variant="error")
        Alert("Recuerda completar todos los campos.", variant="warning")
        Alert("Tienes 3 mensajes nuevos.", variant="info")

    Variantes: "info" | "success" | "warning" | "error"

    Acepta title para mayor claridad:
        Alert("El archivo fue eliminado.", variant="error", title="Error")

    Acepta icon personalizado:
        Alert("Proceso completado.", variant="success", icon="🎉")
    """

    VARIANTS = {
        "info": {
            "bg": "rgba(59,130,246,0.1)",
            "border": "rgba(59,130,246,0.3)",
            "icon": "ℹ️",
            "color": "#3b82f6",
        },
        "success": {
            "bg": "rgba(34,197,94,0.1)",
            "border": "rgba(34,197,94,0.3)",
            "icon": "✅",
            "color": "#22c55e",
        },
        "warning": {
            "bg": "rgba(234,179,8,0.1)",
            "border": "rgba(234,179,8,0.3)",
            "icon": "⚠️",
            "color": "#eab308",
        },
        "error": {
            "bg": "rgba(239,68,68,0.1)",
            "border": "rgba(239,68,68,0.3)",
            "icon": "❌",
            "color": "#ef4444",
        },
    }

    def __init__(self, message="", variant="info", title=None, icon=None, **kwargs):
        self._props = Widget._extract_props(kwargs)
        self.message = message
        self.variant = variant
        self.title = title
        self.icon = icon

    def render(self):
        v = self.VARIANTS.get(self.variant, self.VARIANTS["info"])
        ico = self.icon if self.icon is not None else v["icon"]
        base = (
            f"display:flex; align-items:flex-start; gap:12px; "
            f"padding:14px 16px; border-radius:10px; "
            f"background:{v['bg']}; border:1px solid {v['border']}"
        )
        inline = self._resolve_props(base)

        title_html = (
            f'<div style="font-weight:700;font-size:14px;color:{v["color"]};'
            f'margin-bottom:4px;">{self.title}</div>'
            if self.title
            else ""
        )

        return (
            f'<div style="{inline}">'
            f'<span style="font-size:18px;flex-shrink:0;margin-top:1px">{ico}</span>'
            f'<div style="font-size:14px;color:var(--text);line-height:1.5">'
            f"{title_html}{self.message}</div>"
            f"</div>"
        )
