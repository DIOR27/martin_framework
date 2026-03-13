"""
Martin — Layout Widgets

Los contenedores son la columna vertebral de cualquier página.
Todo lo que agrupa, organiza o posiciona otros widgets vive aquí.

    Container  — div genérico, el bloque más básico
    Row        — hijos en fila horizontal (flexbox row)
    Column     — hijos en columna vertical (flexbox column)
    Grid       — cuadrícula CSS grid
    Stack      — superposición de hijos (position: absolute)
    Card       — tarjeta con fondo, borde y sombra del tema
    Section    — bloque de sección de página (<section>)
    Spacer     — espacio flexible o fijo
    Divider    — línea separadora horizontal o vertical
"""

from ..widget import Widget


# =============================================================================
# Container
# =============================================================================


class Container(Widget):
    """
    El contenedor más básico. Cualquier cosa dentro de un div.

        Container(Text("Hola"), padding=16, radius=8, background="var(--surface)")

    Acepta un hijo o lista de hijos:
        Container(child=Text("Solo uno"))
        Container(children=[Text("A"), Text("B")])

    Útil para darle estilos a un bloque sin semántica adicional.
    """

    def __init__(
        self,
        *args,
        child=None,
        children=None,
        tag="div",
        id=None,
        class_name=None,
        **kwargs,
    ):
        self._props = Widget._extract_props(kwargs)
        self.id = id
        self.class_name = class_name
        self.tag = tag
        # Primer arg posicional se trata como child
        if args:
            child = args[0] if len(args) == 1 else None
            if len(args) > 1:
                children = list(args)
        if child is not None and children is None:
            children = [child]
        self.children = children or []

    def render(self):
        inline = self._resolve_props()
        inner = self._render_children(self.children)
        attrs = self._attrs(
            style=inline or None, id=self.id, **{"class": self.class_name}
        )
        return self._wrap_url(f"<{self.tag}{attrs}>{inner}</{self.tag}>")


# =============================================================================
# Row
# =============================================================================


class Row(Widget):
    """
    Coloca hijos en fila horizontal (flexbox row).

        Row([Button("A"), Button("B")], gap=12, align="center")
        Row([...], justify="space-between", wrap=True)

    Parámetros clave:
        gap       int    espacio entre hijos (px)
        align     str    align-items: "center" | "flex-start" | "flex-end" | "stretch"
        justify   str    justify-content: "flex-start" | "space-between" | "center" | ...
        wrap      bool   flex-wrap: permite que los hijos salten de línea
    """

    def __init__(
        self,
        children=None,
        gap=8,
        align="center",
        justify="flex-start",
        wrap=False,
        id=None,
        class_name=None,
        **kwargs,
    ):
        self._props = Widget._extract_props(kwargs)
        self.children = children or []
        self.gap = gap
        self.align = align
        self.justify = justify
        self.wrap = wrap
        self.id = id
        self.class_name = class_name

    def render(self):
        base = (
            f"display:flex; flex-direction:row; gap:{self.gap}px; "
            f"align-items:{self.align}; justify-content:{self.justify}"
            + ("; flex-wrap:wrap" if self.wrap else "")
        )
        inline = self._resolve_props(base)
        inner = self._render_children(self.children)
        attrs = self._attrs(style=inline, id=self.id, **{"class": self.class_name})
        return self._wrap_url(f"<div{attrs}>{inner}</div>")


# =============================================================================
# Column
# =============================================================================


class Column(Widget):
    """
    Coloca hijos en columna vertical (flexbox column).

        Column([Heading("Titulo"), Text("Desc"), Button("CTA")], gap=16, padding=32)

    Parámetros clave:
        gap       int    espacio entre hijos (px)
        align     str    align-items: "stretch" | "center" | "flex-start" | "flex-end"
        justify   str    justify-content: "flex-start" | "center" | "space-between" | ...
    """

    def __init__(
        self,
        children=None,
        gap=8,
        align="stretch",
        justify="flex-start",
        id=None,
        class_name=None,
        **kwargs,
    ):
        self._props = Widget._extract_props(kwargs)
        self.children = children or []
        self.gap = gap
        self.align = align
        self.justify = justify
        self.id = id
        self.class_name = class_name

    def render(self):
        base = (
            f"display:flex; flex-direction:column; gap:{self.gap}px; "
            f"align-items:{self.align}; justify-content:{self.justify}"
        )
        inline = self._resolve_props(base)
        inner = self._render_children(self.children)
        attrs = self._attrs(style=inline, id=self.id, **{"class": self.class_name})
        return self._wrap_url(f"<div{attrs}>{inner}</div>")


# =============================================================================
# Grid
# =============================================================================


class Grid(Widget):
    """
    Cuadrícula de elementos (CSS grid).

        Grid([Card(...), Card(...), Card(...)], columns=3, gap=24)
        Grid([...], columns="repeat(auto-fill, minmax(280px, 1fr))", gap=16)

    Parámetros clave:
        columns   int | str   número de columnas o string CSS
        gap       int         espacio entre celdas (px)
    """

    def __init__(
        self, children=None, columns=2, gap=16, id=None, class_name=None, **kwargs
    ):
        self._props = Widget._extract_props(kwargs)
        self.children = children or []
        self.columns = columns
        self.gap = gap
        self.id = id
        self.class_name = class_name

    def render(self):
        cols = (
            self.columns
            if isinstance(self.columns, str)
            else f"repeat({self.columns}, 1fr)"
        )
        base = f"display:grid; grid-template-columns:{cols}; gap:{self.gap}px"
        inline = self._resolve_props(base)
        inner = self._render_children(self.children)
        attrs = self._attrs(style=inline, id=self.id, **{"class": self.class_name})
        return f"<div{attrs}>{inner}</div>"


# =============================================================================
# Stack
# =============================================================================


class Stack(Widget):
    """
    Apila hijos uno encima del otro (position: absolute).
    El primer hijo define el tamaño; los siguientes se superponen.

        Stack([
            Image("fondo.jpg"),
            Column([Heading("Texto encima")], style="justify-content:center"),
        ])
    """

    def __init__(self, children=None, id=None, class_name=None, **kwargs):
        self._props = Widget._extract_props(kwargs)
        self.children = children or []
        self.id = id
        self.class_name = class_name

    def render(self):
        inline = self._resolve_props("position:relative")
        parts = []
        for i, child in enumerate(self.children):
            rendered = child.render() if isinstance(child, Widget) else str(child)
            if i == 0:
                parts.append(rendered)
            else:
                parts.append(
                    f'<div style="position:absolute;top:0;left:0;width:100%;height:100%">'
                    f"{rendered}</div>"
                )
        attrs = self._attrs(style=inline, id=self.id, **{"class": self.class_name})
        return f'<div{attrs}>{"".join(parts)}</div>'


# =============================================================================
# Card
# =============================================================================


class Card(Widget):
    """
    Tarjeta con fondo, borde y sombra. Base para cualquier bloque destacado.
    Usa variables CSS del tema (funciona en dark y light mode).

        Card([
            Heading("Titulo"),
            Text("Descripcion"),
            Button("Ver mas"),
        ], padding=24, radius=16)

        Card([...], shadow=True, background="var(--surface-2)")

    Por defecto:
        background  var(--surface)    — se adapta al tema
        border      var(--border)     — se adapta al tema
        radius      12px
        padding     ninguno (agrega el que necesites)
    """

    def __init__(self, children=None, child=None, id=None, class_name=None, **kwargs):
        self._props = Widget._extract_props(kwargs)
        self.id = id
        self.class_name = class_name
        if child is not None and children is None:
            children = [child]
        self.children = children or []

    def render(self):
        base = (
            "background:var(--surface); border:1px solid var(--border); "
            "border-radius:12px; overflow:visible"
        )
        inline = self._resolve_props(base)
        inner = self._render_children(self.children)
        attrs = self._attrs(style=inline, id=self.id, **{"class": self.class_name})
        return self._wrap_url(f"<div{attrs}>{inner}</div>")


# =============================================================================
# Section
# =============================================================================


class Section(Widget):
    """
    Bloque de sección de página. La unidad natural para estructurar contenido.
    Equivale a <section> con padding vertical generoso.

        Section([
            Heading("Características", level=2),
            Grid([Card(...), Card(...), Card(...)], columns=3),
        ], id="features", padding=80)

        Section([...], background="var(--surface)", id="pricing")

    Parámetros clave:
        id          str   anchor de la sección (para navegación)
        background  str   color o gradiente de fondo

    Por defecto tiene padding vertical de 80px y es ancho completo.
    """

    def __init__(self, children=None, child=None, id=None, class_name=None, **kwargs):
        self._props = Widget._extract_props(kwargs)
        self.id = id
        self.class_name = class_name
        if child is not None and children is None:
            children = [child]
        self.children = children or []
        # Default vertical padding
        if self._props.get("padding") is None:
            self._props["padding"] = 80

    def render(self):
        base = "width:100%; box-sizing:border-box"
        inline = self._resolve_props(base)
        inner = self._render_children(self.children)
        attrs = self._attrs(style=inline, id=self.id, **{"class": self.class_name})
        return f"<section{attrs}>{inner}</section>"


# =============================================================================
# Spacer
# =============================================================================


class Spacer(Widget):
    """
    Espacio flexible o fijo entre widgets.

        Row([Text("izq"), Spacer(), Text("der")])   # empuja al extremo
        Column([...], children=[..., Spacer(32)])    # 32px fijo
    """

    def __init__(self, size=None):
        self._props = {}
        self.size = size

    def render(self):
        if self.size:
            return f'<div style="width:{self.size}px;height:{self.size}px;flex-shrink:0"></div>'
        return '<div style="flex:1"></div>'


# =============================================================================
# Divider
# =============================================================================


class Divider(Widget):
    """
    Línea separadora horizontal o vertical.

        Divider()                         # horizontal, color del tema
        Divider(vertical=True, margin=8)  # vertical
        Divider(color="var(--border)", thickness=2)
    """

    def __init__(self, color=None, thickness=1, vertical=False, **kwargs):
        self._props = Widget._extract_props(kwargs)
        self.color = color or "var(--border)"
        self.thickness = thickness
        self.vertical = vertical

    def render(self):
        if self.vertical:
            base = (
                f"width:{self.thickness}px; height:100%; "
                f"background:{self.color}; flex-shrink:0"
            )
        else:
            base = (
                f"height:{self.thickness}px; width:100%; "
                f"background:{self.color}; margin:4px 0"
            )
        inline = self._resolve_props(base)
        return f'<div style="{inline}"></div>'
