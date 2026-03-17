"""
Martin — Navigation Widgets

Widgets que estructuran la navegación de la página.

    NavBar     — barra de navegación superior sticky
    SideMenu   — menú lateral para documentación o paneles
    Footer     — pie de página con zonas left / center / right
    Breadcrumb — ruta de navegación jerárquica
    Tabs       — navegación por pestañas con contenido intercambiable
"""

from ..widget import Widget
from .._context import get_current_path
from .._routing import paths_match


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

    _id_counter = 0

    def __init__(
        self, brand=None, links=None, actions=None, sticky=True, bordered=True, **kwargs
    ):
        self._props = Widget._extract_props(kwargs)
        self.brand = brand
        self.links = links or []
        self.actions = actions or []
        self.sticky = sticky
        self.bordered = bordered
        NavBar._id_counter += 1
        self.uid = f"nav_{NavBar._id_counter}"

    def _default_a11y_attrs(self):
        return {"aria-label": "Barra de navegacion"}

    def render(self):
        uid = self.uid
        sticky_css = "position:sticky; top:0; z-index:100; " if self.sticky else ""
        border_css = "border-bottom:1px solid var(--border); " if self.bordered else ""
        base = (
            f"{sticky_css}{border_css}"
            f"background:var(--surface); "
            f"display:flex; align-items:center; "
            f"padding:0 32px; height:64px; gap:32px; "
            f"max-width:100%; box-sizing:border-box; "
            f"backdrop-filter:blur(12px); "
            f"-webkit-backdrop-filter:blur(12px)"
        )
        inline = self._resolve_props(base)

        # Brand (left)
        brand_html = ""
        if self.brand:
            b = self.brand.render() if isinstance(self.brand, Widget) else self.brand
            brand_html = (
                '<a href="/" aria-label="Inicio" style="flex-shrink:0;text-decoration:none;color:inherit">'
                + b
                + "</a>"
            )

        links_items = "".join(
            (lk.render() if isinstance(lk, Widget) else str(lk))
            for lk in self.links
        )
        actions_items = "".join(
            (a.render() if isinstance(a, Widget) else str(a)) for a in self.actions
        )
        has_menu = bool(links_items or actions_items)

        links_html = ""
        if links_items:
            links_html = (
                f'<nav id="{uid}_links" aria-label="Principal" style="display:flex;align-items:center;gap:24px;'
                f"min-width:0;overflow-x:auto;overflow-y:hidden;white-space:nowrap;flex:1;justify-content:center\">"
                f"{links_items}</nav>"
            )

        actions_html = ""
        if actions_items:
            actions_html = (
                f'<div id="{uid}_actions" style="display:flex;align-items:center;'
                f'gap:8px;flex-shrink:0">{actions_items}</div>'
            )

        menu_html = ""
        burger_html = ""
        if has_menu:
            burger_html = (
                f'<button id="{uid}_burger" type="button" aria-label="Abrir menu" '
                f'aria-controls="{uid}_menu" aria-expanded="false" '
                f'style="display:none;align-items:center;justify-content:center;'
                f'width:38px;height:38px;border:1px solid var(--border);border-radius:10px;'
                f'background:var(--surface);color:var(--text);cursor:pointer;flex-shrink:0;font-size:18px">☰</button>'
            )
            menu_html = (
                f'<div id="{uid}_menu" style="display:flex;align-items:center;gap:18px;'
                f'flex:1;min-width:0;justify-content:space-between">{links_html}{actions_html}</div>'
            )

        css = (
            f"<style>"
            f"#{uid}{{overflow-x:clip}}"
            f"#{uid}_links::-webkit-scrollbar{{display:none}}"
            f"#{uid}_menu{{box-sizing:border-box}}"
            f"@media(max-width:840px){{"
            f"#{uid}{{height:64px!important;min-height:64px;padding:0 14px!important;gap:10px!important;"
            f"justify-content:space-between;position:relative;z-index:120}}"
            f"#{uid}_burger{{display:inline-flex!important}}"
            f"#{uid}_menu{{display:none!important;position:absolute;top:calc(100% + 8px);left:10px;right:10px;"
            f"background:color-mix(in srgb,var(--bg,#0b1020) 88%, var(--surface,#111827) 12%);"
            f"backdrop-filter:none!important;-webkit-backdrop-filter:none!important;"
            f"border:1px solid color-mix(in srgb,var(--border,#334155) 85%, #000 15%);"
            f"border-radius:12px;box-shadow:0 14px 36px rgba(0,0,0,.42);"
            f"padding:12px;flex-direction:column;align-items:stretch;gap:12px;z-index:140}}"
            f"#{uid}[data-mobile-open='1'] #{uid}_menu{{display:flex!important}}"
            f"#{uid}_links{{display:flex!important;flex-direction:column;align-items:stretch;flex:none!important;"
            f"justify-content:flex-start!important;white-space:normal!important;overflow:visible!important;gap:6px!important}}"
            f"#{uid}_links > *{{display:block;width:100%}}"
            f"#{uid}_menu a{{display:block;color:var(--text)!important;padding:10px 10px;border-radius:8px}}"
            f"#{uid}_actions{{display:flex;flex-direction:column;align-items:stretch;justify-content:flex-start;gap:8px}}"
            f"#{uid}_actions > *{{width:100%}}"
            f"}}"
            f"</style>"
        )

        js = ""
        if has_menu:
            js = (
                f"<script>(function(){{"
                f'var root=document.getElementById("{uid}");'
                f'var btn=document.getElementById("{uid}_burger");'
                f"if(!root||!btn||root.dataset.martinNavBound)return;"
                f'root.dataset.martinNavBound="1";'
                f"function isMobile(){{return window.matchMedia&&window.matchMedia('(max-width:840px)').matches;}}"
                f"function closeMenu(){{root.setAttribute('data-mobile-open','0');btn.setAttribute('aria-expanded','false');}}"
                f"function toggleMenu(){{"
                f"  if(!isMobile())return;"
                f"  var open=root.getAttribute('data-mobile-open')==='1';"
                f"  if(open)closeMenu();"
                f"  else{{root.setAttribute('data-mobile-open','1');btn.setAttribute('aria-expanded','true');}}"
                f"}}"
                f"btn.addEventListener('click',function(e){{e.stopPropagation();toggleMenu();}});"
                f"document.addEventListener('click',function(e){{if(!isMobile())return;if(!root.contains(e.target))closeMenu();}});"
                f"document.addEventListener('keydown',function(e){{if(e.key==='Escape')closeMenu();}});"
                f"window.addEventListener('resize',function(){{if(!isMobile())closeMenu();}});"
                f"}})();</script>"
            )

        return f'{css}<header id="{uid}" data-mobile-open="0" role="banner" style="{inline}">{brand_html}{menu_html}{burger_html}</header>{js}'


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

    def _default_a11y_attrs(self):
        return {"aria-label": "Pestanas"}

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
                f'role="tab" aria-selected="{"true" if active else "false"}" '
                f'aria-controls="{pid}" tabindex="{"0" if active else "-1"}" '
                f'style="{btn_base};{active_style if active else inactive_style}">'
                f"{lbl_html}</button>"
            )
            panels += (
                f'<div id="{pid}" role="tabpanel" aria-labelledby="{tid}" '
                f'aria-hidden="{"false" if active else "true"}" style="display:{display};padding-top:16px">'
                f"{content_html}</div>"
            )

        wrapper_style = extra or "width:100%"
        tablist_label = self._get_universal_attrs().get("aria-label") or "Pestanas"
        tabs_bar = (
            f'<div id="{uid}_tablist" role="tablist" aria-label="{tablist_label}" style="display:flex;border-bottom:1px solid var(--border);gap:4px">'
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
                f'      b.setAttribute("aria-selected",active?"true":"false");'
                f'      b.tabIndex=active?0:-1;'
                f"    }}"
                f'    if(p){{p.style.display=active?"block":"none";p.setAttribute("aria-hidden",active?"false":"true");}}'
                f"  }}"
                f'  var ab=document.getElementById("{uid}_t"+i);if(ab)ab.focus();'
            f"}};"
            f'var list=document.getElementById("{uid}_tablist");'
            f'if(list&&!list.dataset.martinTabsBound){{'
            f'  list.dataset.martinTabsBound="1";'
            f'  list.addEventListener("keydown",function(e){{'
            f'    if(e.key!=="ArrowRight"&&e.key!=="ArrowLeft")return;'
            f'    var i=0;for(var j=0;j<{n};j++){{var b=document.getElementById("{uid}_t"+j);if(b&&b.getAttribute("aria-selected")==="true"){{i=j;break;}}}}'
            f'    var next=e.key==="ArrowRight"?(i+1)%{n}:(i-1+{n})%{n};'
            f'    window.{uid}_go(next);'
            f'    e.preventDefault();'
            f'  }});'
            f'}}'
            f"}})();</script>"
        )

        return f'<div style="{wrapper_style}">' + tabs_bar + panels + js + "</div>"


# =============================================================================
# SideMenu
# =============================================================================


class SideMenu(Widget):
    """
    Menú lateral vertical con links.

        SideMenu(
            title="Widgets",
            items=[
                ("Text", "#widget-text"),
                ("Button", "#widget-button"),
                ("Form", "/forms"),
            ],
        )

    Parámetros:
        title       str       título opcional del menú
        items       list      lista de (label, href) o dict {"label","href"}
        sticky      bool      fija el menú durante scroll (default: True)
        top         int       offset superior en px para sticky
        width       int|str   ancho del menú
        bordered    bool      borde del contenedor (default: True)
    """

    def __init__(
        self,
        title=None,
        items=None,
        sticky=True,
        top=84,
        width=260,
        bordered=True,
        id=None,
        class_name=None,
        **kwargs,
    ):
        self._props = Widget._extract_props(kwargs)
        self.title = title
        self.items = items or []
        self.sticky = sticky
        self.top = top
        self.width = width
        self.bordered = bordered
        self.id = id
        self.class_name = class_name

    @staticmethod
    def _item_parts(item):
        if isinstance(item, (tuple, list)):
            if not item:
                return None, None
            label = item[0]
            href = item[1] if len(item) > 1 else "#"
            return label, href
        if isinstance(item, dict):
            return item.get("label"), item.get("href", "#")
        return str(item), "#"

    def render(self):
        sticky_css = (
            f"position:sticky;top:{self.top}px;align-self:flex-start;" if self.sticky else ""
        )
        width_css = f"width:{self.width}px;" if isinstance(self.width, (int, float)) else f"width:{self.width};"
        border_css = "border:1px solid var(--border);" if self.bordered else ""
        base = (
            f"{sticky_css}{width_css}{border_css}"
            "background:var(--surface);border-radius:12px;padding:14px;"
            "display:flex;flex-direction:column;gap:10px"
        )
        inline = self._resolve_props(base)
        attrs = self._attrs(style=inline, id=self.id, **{"class": self.class_name})

        title_html = ""
        if self.title:
            title_html = (
                f'<div style="font-size:13px;font-weight:700;color:var(--text);'
                f'letter-spacing:.02em;text-transform:uppercase">{self.title}</div>'
            )

        current_path = get_current_path()
        links = []
        for item in self.items:
            label, href = self._item_parts(item)
            if label is None:
                continue

            is_active = paths_match(current_path, href)
            label_html = label.render() if isinstance(label, Widget) else str(label)
            active_css = "color:var(--accent);font-weight:600;background:rgba(99,102,241,.10);" if is_active else ""
            aria_current = ' aria-current="page"' if is_active else ""
            links.append(
                f'<a href="{href}"{aria_current} style="display:block;padding:8px 10px;'
                f'border-radius:8px;text-decoration:none;color:var(--text-muted);'
                f'font-size:14px;line-height:1.35;transition:all .18s;{active_css}">{label_html}</a>'
            )

        links_html = "".join(links)
        return f"<aside{attrs}>{title_html}<nav>{links_html}</nav></aside>"
