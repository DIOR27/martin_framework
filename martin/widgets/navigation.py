"""
Martin — Navigation Widgets

Widgets que estructuran la navegación de la página.

    NavBar     — barra de navegación superior sticky
    Footer     — pie de página con zonas left / center / right
    Breadcrumb — ruta de navegación jerárquica
    Tabs       — navegación por pestañas con contenido intercambiable
"""

from ..widget import Widget


# =============================================================================
# NavBar
# =============================================================================


class NavBar(Widget):
    """
    Barra de navegación superior. Un pilar de cualquier sitio.

        NavBar(
            brand=Heading("MiSitio", level=3),
            links=[
                Link("Inicio",    href="/"),
                Link("Productos", href="/productos"),
                Link("Contacto",  href="/contacto"),
            ],
            actions=[
                Button("Login",    href="/login",    variant="ghost"),
                Button("Registro", href="/registro"),
            ],
        )

    Parámetros:
        brand      Widget   logo o nombre del sitio (izquierda)
        links      list     lista de Link o cualquier widget (centro)
        actions    list     botones o widgets (derecha)
        sticky     bool     fija el header al scroll (default: True)
        bordered   bool     borde inferior (default: True)
    """

    def __init__(
        self, brand=None, links=None, actions=None, sticky=True, bordered=True, **kwargs
    ):
        self._props = Widget._extract_props(kwargs)
        self.brand = brand
        self.links = links or []
        self.actions = actions or []
        self.sticky = sticky
        self.bordered = bordered

    def render(self):
        sticky_css = "position:sticky; top:0; z-index:100; " if self.sticky else ""
        border_css = "border-bottom:1px solid var(--border); " if self.bordered else ""
        base = (
            f"{sticky_css}{border_css}"
            f"background:var(--surface); "
            f"display:flex; align-items:center; "
            f"padding:0 32px; height:64px; gap:32px; "
            f"backdrop-filter:blur(12px); "
            f"-webkit-backdrop-filter:blur(12px)"
        )
        inline = self._resolve_props(base)

        # Brand (left)
        brand_html = ""
        if self.brand:
            b = self.brand.render() if isinstance(self.brand, Widget) else self.brand
            brand_html = (
                '<a href="/" style="flex-shrink:0;text-decoration:none;color:inherit">'
                + b
                + "</a>"
            )

        # Links (center)
        links_html = ""
        if self.links:
            items = "".join(
                (lk.render() if isinstance(lk, Widget) else str(lk))
                for lk in self.links
            )
            links_html = (
                f'<nav style="display:flex;align-items:center;gap:24px;'
                f'flex:1;justify-content:center">{items}</nav>'
            )

        # Actions (right)
        actions_html = ""
        if self.actions:
            items = "".join(
                (a.render() if isinstance(a, Widget) else str(a)) for a in self.actions
            )
            actions_html = (
                f'<div style="display:flex;align-items:center;'
                f'gap:8px;flex-shrink:0">{items}</div>'
            )

        return (
            f'<header style="{inline}">{brand_html}{links_html}{actions_html}</header>'
        )


# =============================================================================
# Footer
# =============================================================================


class Footer(Widget):
    """
    Pie de página. Cierre natural de cualquier página.

        Footer(
            left=Text("© 2025 MiEmpresa"),
            right=Row([
                Link("Privacidad", href="/privacidad"),
                Link("Términos",   href="/terminos"),
            ], gap=16),
        )

        # Solo texto centrado:
        Footer(center=Text("Hecho con Martin Framework"))

    Parámetros:
        left     Widget   contenido izquierdo
        center   Widget   contenido central
        right    Widget   contenido derecho
        bordered bool     borde superior (default: True)
    """

    def __init__(self, left=None, center=None, right=None, bordered=True, **kwargs):
        self._props = Widget._extract_props(kwargs)
        self.left = left
        self.center = center
        self.right = right
        self.bordered = bordered

    def render(self):
        border_css = "border-top:1px solid var(--border); " if self.bordered else ""
        base = (
            f"{border_css}padding:24px 32px; "
            f"display:flex; align-items:center; justify-content:space-between; "
            f"background:var(--surface); gap:16px; flex-wrap:wrap"
        )
        inline = self._resolve_props(base)

        def _r(w):
            return (w.render() if isinstance(w, Widget) else str(w)) if w else ""

        left_html = f"<div>{_r(self.left)}</div>" if self.left else "<div></div>"
        center_html = (
            f'<div style="text-align:center">{_r(self.center)}</div>'
            if self.center
            else ""
        )
        right_html = f"<div>{_r(self.right)}</div>" if self.right else "<div></div>"

        return f'<footer style="{inline}">{left_html}{center_html}{right_html}</footer>'


# =============================================================================
# Breadcrumb
# =============================================================================


class Breadcrumb(Widget):
    """
    Ruta de navegación. Muestra dónde está el usuario en la jerarquía.

        Breadcrumb([
            ("Inicio",    "/"),
            ("Productos", "/productos"),
            ("Zapatillas", None),    # último ítem sin link
        ])

        # O con widgets directos:
        Breadcrumb([Link("Inicio", "/"), Text(" / "), Text("Actual")])

    Separador por defecto: "/"
    """

    def __init__(self, items=None, separator="/", **kwargs):
        self._props = Widget._extract_props(kwargs)
        self.items = items or []
        self.separator = separator

    def render(self):
        base = "display:flex; align-items:center; gap:8px; flex-wrap:wrap"
        inline = self._resolve_props(base)
        sep = (
            f'<span style="color:var(--text-muted);font-size:13px">'
            f"{self.separator}</span>"
        )
        parts = []
        for i, item in enumerate(self.items):
            if isinstance(item, Widget):
                parts.append(item.render())
            elif isinstance(item, (tuple, list)):
                label = item[0]
                href = item[1] if len(item) > 1 else None
                is_last = i == len(self.items) - 1
                if href and not is_last:
                    parts.append(
                        f'<a href="{href}" style="color:var(--accent);'
                        f'font-size:13px;text-decoration:none;">{label}</a>'
                    )
                else:
                    weight = "600" if is_last else "400"
                    parts.append(
                        f'<span style="color:var(--text);font-size:13px;'
                        f'font-weight:{weight}">{label}</span>'
                    )
            else:
                parts.append(
                    f'<span style="font-size:13px;color:var(--text)">{item}</span>'
                )

        html = sep.join(parts)
        return f'<nav aria-label="breadcrumb" style="{inline}">{html}</nav>'


# =============================================================================
# Tabs
# =============================================================================


class Tabs(Widget):
    """
    Navegación por pestañas. Muestra un contenido a la vez.

        Tabs([
            ("General",  Column([Text("Contenido general...")])),
            ("Avanzado", Column([Text("Opciones avanzadas...")])),
            ("Sobre mí", Column([Avatar(initials="JD"), Text("Juan Díaz")])),
        ])

    Cada ítem es una tupla (label, widget_contenido).
    El primer tab está activo por defecto; puedes cambiarlo con `default`.

    Parámetros:
        tabs     list   lista de tuplas (label, contenido)
        default  int    índice del tab activo inicial (default: 0)
    """

    _id_counter = 0

    def __init__(self, tabs=None, default=0, **kwargs):
        self._props = Widget._extract_props(kwargs)
        self.tabs = tabs or []
        self.default = default
        Tabs._id_counter += 1
        self.uid = f"tabs_{Tabs._id_counter}"

    def render(self):
        uid = self.uid
        extra = self._resolve_props()
        n = len(self.tabs)

        btn_base = (
            "padding:8px 20px; border:none; cursor:pointer; font-size:14px; "
            "font-weight:500; border-radius:8px 8px 0 0; transition:all .2s"
        )
        active_style = (
            "background:var(--surface); color:var(--text); "
            "border-bottom:2px solid var(--accent)"
        )
        inactive_style = (
            "background:transparent; color:var(--text-muted); "
            "border-bottom:2px solid transparent"
        )

        btns = ""
        panels = ""

        for i, (label, content) in enumerate(self.tabs):
            tid = f"{uid}_t{i}"
            pid = f"{uid}_p{i}"
            active = i == self.default

            lbl_html = label.render() if isinstance(label, Widget) else label
            content_html = (
                content.render() if isinstance(content, Widget) else str(content)
            )
            display = "block" if active else "none"

            btns += (
                f'<button id="{tid}" onclick="{uid}_go({i})" '
                f'style="{btn_base};{active_style if active else inactive_style}">'
                f"{lbl_html}</button>"
            )
            panels += (
                f'<div id="{pid}" style="display:{display};padding-top:16px">'
                f"{content_html}</div>"
            )

        wrapper_style = extra or "width:100%"
        tabs_bar = (
            f'<div style="display:flex;border-bottom:1px solid var(--border);gap:4px">'
            f"{btns}</div>"
        )

        js = (
            f"<script>(function(){{"
            f"window.{uid}_go=function(i){{"
            f"  for(var j=0;j<{n};j++){{"
            f'    var b=document.getElementById("{uid}_t"+j);'
            f'    var p=document.getElementById("{uid}_p"+j);'
            f"    var active=j===i;"
            f"    if(b){{"
            f'      b.style.color=active?"var(--text)":"var(--text-muted)";'
            f'      b.style.background=active?"var(--surface)":"transparent";'
            f'      b.style.borderBottom=active?"2px solid var(--accent)":"2px solid transparent";'
            f"    }}"
            f'    if(p)p.style.display=active?"block":"none";'
            f"  }}"
            f"}};"
            f"}})();</script>"
        )

        return f'<div style="{wrapper_style}">' + tabs_bar + panels + js + "</div>"
