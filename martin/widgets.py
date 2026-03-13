"""
Martin — Widgets

Filosofia: todo es un Widget. Cada widget acepta props universales:
    style, padding, margin, width, height,
    color, background, radius, shadow, opacity, hidden,
    url, url_target, id, class_name

Widgets pilar (bloques base para componer cualquier UI):
    Contenedores : Container, Row, Column, Grid, Stack, Card, Section
    Texto        : Text, Heading, Paragraph, Link, Code
    Media        : Image, Video, Icon, Avatar
    Interaccion  : Button, TextField, Checkbox, Select, MultiSelect
    Feedback     : Badge, Alert
    Navegacion   : NavBar, Footer, Tabs, Breadcrumb
    Datos        : Table
    Overlay      : Modal
    Layout util  : Spacer, Divider
    Especiales   : Raw, ThemeToggle, CookieBanner
    Compuestos   : Hero, Timeline, Gallery, Carousel, WordCloud, Map
"""
from .widget import Widget
from .styles import resolve_styles, Border, Padding, Margin, Shadow, Size, Background


# =============================================================================
# LAYOUT — los contenedores son la columna vertebral de cualquier pagina
# =============================================================================

class Container(Widget):
    """
    El contenedor mas basico. Cualquier cosa dentro de un div.

        Container(Text("Hola"), padding=16, radius=8, background="var(--surface)")

    Acepta un hijo o lista de hijos:
        Container(child=Text("Solo uno"))
        Container(children=[Text("A"), Text("B")])

    Util para darle estilos a un bloque sin semántica adicional.
    """
    def __init__(self, *args, child=None, children=None,
                 tag="div", id=None, class_name=None, **kwargs):
        self._props     = Widget._extract_props(kwargs)
        self.id         = id
        self.class_name = class_name
        self.tag        = tag
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
        inner  = self._render_children(self.children)
        attrs  = self._attrs(style=inline or None, id=self.id, **{"class": self.class_name})
        return self._wrap_url(f"<{self.tag}{attrs}>{inner}</{self.tag}>")


class Row(Widget):
    """
    Coloca hijos en fila horizontal (flexbox row).

        Row([Button("A"), Button("B")], gap=12, align="center")
        Row([...], justify="space-between", wrap=True)

    Parametros clave:
        gap       int    espacio entre hijos (px)
        align     str    align-items: "center" | "flex-start" | "flex-end" | "stretch"
        justify   str    justify-content: "flex-start" | "space-between" | "center" | ...
        wrap      bool   flex-wrap: permite que los hijos salten de linea
    """
    def __init__(self, children=None, gap=8, align="center",
                 justify="flex-start", wrap=False, id=None, class_name=None, **kwargs):
        self._props     = Widget._extract_props(kwargs)
        self.children   = children or []
        self.gap        = gap
        self.align      = align
        self.justify    = justify
        self.wrap       = wrap
        self.id         = id
        self.class_name = class_name

    def render(self):
        base = (f"display:flex; flex-direction:row; gap:{self.gap}px; "
                f"align-items:{self.align}; justify-content:{self.justify}"
                + ("; flex-wrap:wrap" if self.wrap else ""))
        inline = self._resolve_props(base)
        inner  = self._render_children(self.children)
        attrs  = self._attrs(style=inline, id=self.id, **{"class": self.class_name})
        return self._wrap_url(f"<div{attrs}>{inner}</div>")


class Column(Widget):
    """
    Coloca hijos en columna vertical (flexbox column).

        Column([Heading("Titulo"), Text("Desc"), Button("CTA")], gap=16, padding=32)

    Parametros clave:
        gap       int    espacio entre hijos (px)
        align     str    align-items: "stretch" | "center" | "flex-start" | "flex-end"
        justify   str    justify-content: "flex-start" | "center" | "space-between" | ...
    """
    def __init__(self, children=None, gap=8, align="stretch",
                 justify="flex-start", id=None, class_name=None, **kwargs):
        self._props     = Widget._extract_props(kwargs)
        self.children   = children or []
        self.gap        = gap
        self.align      = align
        self.justify    = justify
        self.id         = id
        self.class_name = class_name

    def render(self):
        base = (f"display:flex; flex-direction:column; gap:{self.gap}px; "
                f"align-items:{self.align}; justify-content:{self.justify}")
        inline = self._resolve_props(base)
        inner  = self._render_children(self.children)
        attrs  = self._attrs(style=inline, id=self.id, **{"class": self.class_name})
        return self._wrap_url(f"<div{attrs}>{inner}</div>")


class Grid(Widget):
    """
    Cuadricula de elementos (CSS grid).

        Grid([Card(...), Card(...), Card(...)], columns=3, gap=24)
        Grid([...], columns="repeat(auto-fill, minmax(280px, 1fr))", gap=16)

    Parametros clave:
        columns   int | str   numero de columnas o string CSS
        gap       int         espacio entre celdas (px)
    """
    def __init__(self, children=None, columns=2, gap=16, id=None, class_name=None, **kwargs):
        self._props     = Widget._extract_props(kwargs)
        self.children   = children or []
        self.columns    = columns
        self.gap        = gap
        self.id         = id
        self.class_name = class_name

    def render(self):
        cols   = self.columns if isinstance(self.columns, str) else f"repeat({self.columns}, 1fr)"
        base   = f"display:grid; grid-template-columns:{cols}; gap:{self.gap}px"
        inline = self._resolve_props(base)
        inner  = self._render_children(self.children)
        attrs  = self._attrs(style=inline, id=self.id, **{"class": self.class_name})
        return f"<div{attrs}>{inner}</div>"


class Stack(Widget):
    """
    Apila hijos uno encima del otro (position: absolute).
    El primer hijo define el tamanio; los siguientes se superponen.

        Stack([
            Image("fondo.jpg"),
            Column([Heading("Texto encima")], style="justify-content:center"),
        ])
    """
    def __init__(self, children=None, id=None, class_name=None, **kwargs):
        self._props     = Widget._extract_props(kwargs)
        self.children   = children or []
        self.id         = id
        self.class_name = class_name

    def render(self):
        inline = self._resolve_props("position:relative")
        parts  = []
        for i, child in enumerate(self.children):
            rendered = child.render() if isinstance(child, Widget) else str(child)
            if i == 0:
                parts.append(rendered)
            else:
                parts.append(
                    f'<div style="position:absolute;top:0;left:0;width:100%;height:100%">'
                    f'{rendered}</div>'
                )
        attrs = self._attrs(style=inline, id=self.id, **{"class": self.class_name})
        return f'<div{attrs}>{"".join(parts)}</div>'


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
        self._props     = Widget._extract_props(kwargs)
        self.id         = id
        self.class_name = class_name
        if child is not None and children is None:
            children = [child]
        self.children = children or []

    def render(self):
        base   = ("background:var(--surface); border:1px solid var(--border); "
                  "border-radius:12px; overflow:hidden")
        inline = self._resolve_props(base)
        inner  = self._render_children(self.children)
        attrs  = self._attrs(style=inline, id=self.id, **{"class": self.class_name})
        return self._wrap_url(f"<div{attrs}>{inner}</div>")


class Section(Widget):
    """
    Bloque de seccion de pagina. La unidad natural para estructurar contenido.
    Equivale a <section> con padding vertical generoso.

        Section([
            Heading("Caracteristicas", level=2),
            Grid([Card(...), Card(...), Card(...)], columns=3),
        ], id="features", padding=80)

        Section([...], background="var(--surface)", id="pricing")

    Parametros clave:
        id          str   anchor de la seccion (para navegacion)
        background  str   color o gradiente de fondo

    Por defecto tiene padding vertical de 80px y es ancho completo.
    """
    def __init__(self, children=None, child=None, id=None, class_name=None, **kwargs):
        self._props     = Widget._extract_props(kwargs)
        self.id         = id
        self.class_name = class_name
        if child is not None and children is None:
            children = [child]
        self.children = children or []
        # Default vertical padding
        if self._props.get("padding") is None:
            self._props["padding"] = 80

    def render(self):
        base   = "width:100%; box-sizing:border-box"
        inline = self._resolve_props(base)
        inner  = self._render_children(self.children)
        attrs  = self._attrs(style=inline, id=self.id, **{"class": self.class_name})
        return f"<section{attrs}>{inner}</section>"


class Spacer(Widget):
    """
    Espacio flexible o fijo entre widgets.

        Row([Text("izq"), Spacer(), Text("der")])   # empuja al extremo
        Column([...], children=[..., Spacer(32)])    # 32px fijo
    """
    def __init__(self, size=None):
        self._props = {}
        self.size   = size

    def render(self):
        if self.size:
            return f'<div style="width:{self.size}px;height:{self.size}px;flex-shrink:0"></div>'
        return '<div style="flex:1"></div>'


class Divider(Widget):
    """
    Linea separadora horizontal o vertical.

        Divider()                         # horizontal, color del tema
        Divider(vertical=True, margin=8)  # vertical
        Divider(color="var(--border)", thickness=2)
    """
    def __init__(self, color=None, thickness=1, vertical=False, **kwargs):
        self._props    = Widget._extract_props(kwargs)
        self.color     = color or "var(--border)"
        self.thickness = thickness
        self.vertical  = vertical

    def render(self):
        if self.vertical:
            base = (f"width:{self.thickness}px; height:100%; "
                    f"background:{self.color}; flex-shrink:0")
        else:
            base = (f"height:{self.thickness}px; width:100%; "
                    f"background:{self.color}; margin:4px 0")
        inline = self._resolve_props(base)
        return f'<div style="{inline}"></div>'


# =============================================================================
# TEXT — para todo lo que sea palabras
# =============================================================================

class Text(Widget):
    """
    Texto en linea (span). El widget de texto mas comun.

        Text("Hola mundo")
        Text("Subtitulo", color="var(--text-muted)", style=TextStyle(size=14))

    Para parrafos largos usa Paragraph.
    Para titulos usa Heading.
    """
    def __init__(self, content=None, id=None, child=None, children=None, **kwargs):
        self._props   = Widget._extract_props(kwargs)
        self.content  = content
        self.id       = id
        self.child    = child
        self.children = children

    def render(self):
        inline = self._resolve_props()
        attrs  = self._attrs(style=inline or None, id=self.id)
        inner  = self._resolve_inner(self.content, self.child, self.children)
        return self._wrap_url(f"<span{attrs}>{inner}</span>")


class Heading(Widget):
    """
    Titulo semantico. Usa level para jerarquia (h1-h6).

        Heading("Bienvenido")              # h1 por defecto
        Heading("Seccion", level=2)        # h2
        Heading("Subtitulo", level=3, color="var(--text-muted)")

    Combina con GradientText para titulos llamativos:
        Heading(GradientText.aurora("Titulo"), level=1)
    """
    def __init__(self, content=None, level=1, id=None, child=None, children=None, **kwargs):
        self._props   = Widget._extract_props(kwargs)
        self.content  = content
        self.level    = max(1, min(6, level))
        self.id       = id
        self.child    = child
        self.children = children

    def render(self):
        inline = self._resolve_props()
        tag    = f"h{self.level}"
        attrs  = self._attrs(style=inline or None, id=self.id)
        inner  = self._resolve_inner(self.content, self.child, self.children)
        return self._wrap_url(f"<{tag}{attrs}>{inner}</{tag}>")


class Paragraph(Widget):
    """
    Parrafo de texto (<p>). Para bloques de texto de una o varias lineas.

        Paragraph("Esta es una descripcion mas larga del producto...")
        Paragraph("Texto", style=TextStyle(size=16, leading=1.8), color="var(--text-muted)")
    """
    def __init__(self, content=None, id=None, child=None, children=None, **kwargs):
        self._props   = Widget._extract_props(kwargs)
        self.content  = content
        self.id       = id
        self.child    = child
        self.children = children

    def render(self):
        inline = self._resolve_props("margin:0; line-height:1.6")
        attrs  = self._attrs(style=inline or None, id=self.id)
        inner  = self._resolve_inner(self.content, self.child, self.children)
        return self._wrap_url(f"<p{attrs}>{inner}</p>")


class Link(Widget):
    """
    Enlace (<a>). Para navegacion interna o externa.

        Link("Ver mas", href="/productos")
        Link("GitHub", href="https://github.com", target="_blank")
        Link(Button("Ir"), href="/ruta")    # cualquier widget como hijo
    """
    def __init__(self, content=None, href="#", target=None, child=None, children=None, **kwargs):
        self._props   = Widget._extract_props(kwargs)
        self.content  = content
        self.href     = href
        self.target   = target
        self.child    = child
        self.children = children

    def render(self):
        inline = self._resolve_props("color:var(--accent); text-decoration:underline")
        attrs  = self._attrs(href=self.href, target=self.target, style=inline or None)
        inner  = self._resolve_inner(self.content, self.child, self.children)
        return f"<a{attrs}>{inner}</a>"


class Code(Widget):
    """
    Codigo inline o en bloque con syntax highlighting, copia y edicion.

    Inline:
        Code("print('hola')")
        Code("npm install", color="var(--accent)")

    Bloque:
        Code("def fn():\\n    return 42", language="python")
        Code(
            content="SELECT * FROM users",
            language="sql",
            copy=True,
            line_numbers=True,
            filename="query.sql",
            max_height=400,
        )

    Editable:
        Code("x = 1\\ny = 2", language="python", editable=True, id="editor")

    Parametros:
        content      str     el codigo
        language     str     python|javascript|typescript|html|css|json|sql|bash|rust|go|...
        block        bool    fuerza modo bloque aunque no haya language
        copy         bool    boton copiar (default True si block o language)
        line_numbers bool    numeros de linea (default False)
        filename     str     etiqueta en la cabecera del bloque
        theme        str     dark|light|auto (default auto, sigue al tema)
        max_height   int     altura max con scroll en px
        editable     bool    textarea editable con fuente monoespaciada
        id           str     id del elemento HTML
    """

    _id_counter = 0

    def __init__(self, content="", language=None, block=False,
                 copy=None, line_numbers=False, filename=None,
                 theme="auto", max_height=None,
                 editable=False, id=None, **kwargs):
        self._props       = Widget._extract_props(kwargs)
        self.content      = content
        self.language     = language
        self.block        = block
        self.copy         = copy if copy is not None else bool(language or block)
        self.line_numbers = line_numbers
        self.filename     = filename
        self.theme        = theme
        self.max_height   = max_height
        self.editable     = editable
        Code._id_counter += 1
        self.uid = id or f"code_{Code._id_counter}"

    @staticmethod
    def _esc(text):
        return (str(text)
                .replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;"))

    def _prism_assets(self):
        return (
            '<link id="_prism_css" rel="stylesheet" '
            'href="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/themes/prism-tomorrow.min.css" '
            'crossorigin="anonymous"/>'
            '<script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/prism.min.js" '
            'crossorigin="anonymous"></script>'
            '<script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/plugins/autoloader/prism-autoloader.min.js" '
            'crossorigin="anonymous"></script>'
            '<style id="_prism_light">'
            '.prism-light pre[class*="language-"],.prism-light code[class*="language-"]{background:#f8f8f8!important;color:#383a42!important;text-shadow:none!important}'
            '.prism-light .token.comment{color:#a0a1a7!important}'
            '.prism-light .token.keyword{color:#a626a4!important}'
            '.prism-light .token.string{color:#50a14f!important}'
            '.prism-light .token.number{color:#986801!important}'
            '.prism-light .token.function{color:#4078f2!important}'
            '@media(prefers-color-scheme:light){'
            '.prism-auto pre[class*="language-"],.prism-auto code[class*="language-"]{background:#f8f8f8!important;color:#383a42!important;text-shadow:none!important}'
            '.prism-auto .token.comment{color:#a0a1a7!important}'
            '.prism-auto .token.keyword{color:#a626a4!important}'
            '.prism-auto .token.string{color:#50a14f!important}'
            '.prism-auto .token.number{color:#986801!important}'
            '.prism-auto .token.function{color:#4078f2!important}'
            '}</style>'
            '<script>(function(){if(window._prismOK)return;window._prismOK=true;})();</script>'
        )

    def _copy_btn(self, content):
        import json as _j
        uid = self.uid
        c_js = _j.dumps(content)
        btn_id = uid + "_copy"
        btn_js = _j.dumps(btn_id)
        return (
            f'<button id="{btn_id}" title="Copiar" '
            f'style="background:none;border:1px solid rgba(128,128,128,0.25);'
            f'border-radius:5px;cursor:pointer;font-size:11px;'
            f'color:var(--text-muted);padding:3px 10px;'
            f'transition:all .15s;font-family:inherit;white-space:nowrap" '
            f'onmouseover="this.style.borderColor=\'var(--accent)\';this.style.color=\'var(--accent)\'" '
            f'onmouseout="this.style.borderColor=\'rgba(128,128,128,0.25)\';this.style.color=\'var(--text-muted)\'" '
            f'>Copiar</button>'
            f'<script>(function(){{'
            f'  var btn=document.getElementById({btn_js});'
            f'  if(!btn||btn.dataset.copyBound==="1")return;'
            f'  btn.dataset.copyBound="1";'
            f'  var txt={c_js};'
            f'  function ok(){{'
            f'    btn.textContent="\u2713 Copiado";'
            f'    btn.style.color="#22c55e";btn.style.borderColor="#22c55e";'
            f'    setTimeout(function(){{btn.textContent="Copiar";btn.style.color="";btn.style.borderColor="";}},2000);'
            f'  }}'
            f'  function fallback(){{'
            f'    var t=document.createElement("textarea");t.value=txt;'
            f'    document.body.appendChild(t);t.select();'
            f'    document.execCommand("copy");document.body.removeChild(t);ok();'
            f'  }}'
            f'  btn.addEventListener("click",function(){{'
            f'    if(navigator.clipboard&&window.isSecureContext){{'
            f'      navigator.clipboard.writeText(txt).then(ok).catch(fallback);'
            f'    }}else{{fallback();}}'
            f'  }});'
            f'}})();</script>'
        )
    def render(self):
        import json as _j
        uid     = self.uid
        content = str(self.content)
        escaped = self._esc(content)
        extra   = self._resolve_props()
        is_block = bool(self.block or self.language or self.editable)

        # Inline
        if not is_block:
            base = (
                "display:inline;padding:2px 6px;border-radius:4px;"
                "font-family:\'Fira Code\',\'Cascadia Code\',monospace;font-size:0.875em;"
                "background:var(--surface-2,rgba(128,128,128,0.12));"
                "color:var(--accent,#6366f1)"
            )
            inline = self._resolve_props(base)
            id_attr    = f' id="{uid}"'
            style_attr = f' style="{inline}"' if inline else ""
            return self._wrap_url(f"<code{id_attr}{style_attr}>{escaped}</code>")

        # Block
        prism = self._prism_assets()
        lang_class  = f"language-{self.language}" if self.language else ""
        theme_class = f"prism-{self.theme}"
        mono_font   = "\'Fira Code\',\'Cascadia Code\',\'JetBrains Mono\',monospace"
        scroll_css  = f"max-height:{self.max_height}px;overflow-y:auto;" if self.max_height else ""
        bg          = "#1e1e2e"

        # Header bar
        header_html = ""
        if self.filename or self.copy:
            fname_html = (
                f'<span style="font-family:monospace;font-size:12px;'
                f'color:rgba(205,214,244,0.55);letter-spacing:0.02em">{self.filename}</span>'
                if self.filename else "<span></span>"
            )
            copy_part = self._copy_btn(content) if self.copy else ""
            header_html = (
                f'<div style="display:flex;align-items:center;justify-content:space-between;'
                f'padding:8px 14px;border-bottom:1px solid rgba(255,255,255,0.06);'
                f'background:rgba(0,0,0,0.2)">{fname_html}{copy_part}</div>'
            )

        # Editable textarea
        if self.editable:
            n_rows = max(str(content).count("\n") + 1, 3)
            wrapper_style = (
                f"border-radius:10px;overflow:hidden;border:1px solid var(--border);background:{bg}"
            )
            if extra:
                wrapper_style += ";" + extra
            ta_style = (
                f"width:100%;box-sizing:border-box;padding:16px;"
                f"font-family:{mono_font};font-size:13px;line-height:1.6;"
                f"background:transparent;border:none;color:#cdd6f4;"
                f"outline:none;resize:vertical;tab-size:4;{scroll_css}"
            )
            return (
                prism
                + f'<div class="{theme_class}" style="{wrapper_style}">'
                + header_html
                + f'<textarea id="{uid}" rows="{n_rows}" '
                + 'spellcheck="false" autocorrect="off" autocapitalize="off" '
                + f'style="{ta_style}">'
                + escaped
                + '</textarea></div>'
            )

        # Display block
        wrapper_style = (
            f"border-radius:10px;overflow:hidden;"
            f"border:1px solid var(--border,rgba(128,128,128,0.2));background:{bg}"
        )
        if extra:
            wrapper_style += ";" + extra

        pre_style = (
            f"margin:0;padding:16px;"
            f"font-family:{mono_font};font-size:13px;"
            f"line-height:1.6;overflow-x:auto;background:transparent;{scroll_css}"
        )

        # Line numbers
        if self.line_numbers:
            lines = content.split("\n")
            nums_html = "".join(
                f'<span style="display:block;color:rgba(205,214,244,0.28);'
                f'user-select:none;text-align:right">{i+1}</span>'
                for i in range(len(lines))
            )
            gutter = (
                f'<div style="font-family:{mono_font};font-size:13px;'
                f'line-height:1.6;padding:16px 14px 16px 16px;'
                f'background:rgba(0,0,0,0.18);'
                f'border-right:1px solid rgba(255,255,255,0.06);'
                f'flex-shrink:0;user-select:none;min-width:2em">'
                + nums_html + '</div>'
            )
            inner = (
                '<div style="display:flex;overflow:hidden">'
                + gutter
                + f'<pre style="{pre_style}"><code class="{lang_class}">{escaped}</code></pre>'
                + '</div>'
            )
        else:
            inner = f'<pre style="{pre_style}"><code class="{lang_class}">{escaped}</code></pre>'

        hl_js = (
            f'<script>(function(){{'
            f'function _hl(){{'
            f'  if(typeof Prism==="undefined"){{setTimeout(_hl,120);return;}}'
            f'  var w=document.getElementById({_j.dumps(uid)});'
            f'  if(w){{var c=w.querySelector("code");if(c){{Prism.highlightElement(c);return;}}}}'
            f'  Prism.highlightAll();'
            f'}}_hl();'
            f'}})();</script>'
        )

        return (
            prism
            + f'<div id="{uid}" class="{theme_class}" style="{wrapper_style}">'
            + header_html
            + inner
            + '</div>'
            + hl_js
        )


class Button(Widget):
    """
    Boton interactivo. El widget de accion principal.

        Button("Guardar")
        Button("Cancelar", variant="ghost")
        Button("Eliminar", variant="danger", radius=8)

        # Con enlace:
        Button("Ver docs", href="/docs")

        # Con accion JS directa:
        Button("Click", on_click="alert('hola')")

        # Con llamada a API:
        Button("Enviar", on_click=ApiCall("/api/datos", body={"key": Ref("campo")}))

    Variantes: "primary" | "secondary" | "danger" | "ghost" | "link"
    """
    VARIANTS = {
        "primary":   "background:var(--accent); color:#fff; border:none",
        "secondary": "background:var(--surface-2); color:var(--text); border:1px solid var(--border)",
        "danger":    "background:var(--danger,#ef4444); color:#fff; border:none",
        "ghost":     "background:transparent; color:var(--text); border:1px solid var(--border)",
        "link":      "background:transparent; color:var(--accent); border:none; text-decoration:underline",
    }

    def __init__(self, label="", variant="primary", href=None, disabled=False,
                 id=None, class_name=None, on_click=None, **kwargs):
        self._props     = Widget._extract_props(kwargs)
        self.label      = label
        self.variant    = variant
        self.href       = href
        self.disabled   = disabled
        self.id         = id
        self.class_name = class_name
        self.on_click   = on_click  # str JS | ApiCall

    def render(self):
        import uuid as _uuid
        base   = (self.VARIANTS.get(self.variant, self.VARIANTS["primary"])
                  + "; padding:8px 16px; border-radius:6px; cursor:pointer; "
                    "font-size:14px; font-weight:500; display:inline-flex; "
                    "align-items:center; gap:6px; text-decoration:none; "
                    "transition:opacity .2s")
        inline = self._resolve_props(base)
        inner  = self.label.render() if isinstance(self.label, Widget) else self.label

        btn_id = self.id or (
            "btn_" + _uuid.uuid4().hex[:8] if self.on_click else None
        )

        if self.href:
            attrs = self._attrs(href=self.href, style=inline, id=btn_id,
                                **{"class": self.class_name})
            return self._wrap_url(f"<a{attrs}>{inner}</a>")

        attrs = self._attrs(style=inline, disabled=self.disabled,
                            id=btn_id, **{"class": self.class_name})
        html  = f"<button{attrs}>{inner}</button>"

        if self.on_click and btn_id:
            # on_click puede ser string JS o ApiCall
            if isinstance(self.on_click, str):
                js_body = self.on_click
            else:
                js_body = self.on_click.to_js(btn_id)
            html += (
                "<script>"
                "document.getElementById(" + repr(btn_id) + ").addEventListener('click',function(){"
                + js_body +
                "});"
                "</script>"
            )

        return self._wrap_url(html)


class Image(Widget):
    """
    Imagen responsive.

        Image("/foto.jpg")
        Image("/foto.jpg", radius=12, width=300, height=200)
        Image("/foto.jpg", url="/galeria", url_target="_self")

    Acepta cualquier prop universal: shadow, radius, width, height, etc.
    """
    def __init__(self, src, alt="", id=None, class_name=None, **kwargs):
        self._props     = Widget._extract_props(kwargs)
        self.src        = src
        self.alt        = alt
        self.id         = id
        self.class_name = class_name

    def render(self):
        inline = self._resolve_props()
        attrs  = self._attrs(src=self.src, alt=self.alt,
                             style=inline or None, id=self.id,
                             **{"class": self.class_name})
        return self._wrap_url(f"<img{attrs}>")


class Video(Widget):
    """
    Video HTML5.

        Video("/clip.mp4")
        Video("/clip.mp4", autoplay=True, muted=True, loop=True)
    """
    def __init__(self, src, controls=True, autoplay=False, loop=False, muted=False, **kwargs):
        self._props    = Widget._extract_props(kwargs)
        self.src       = src
        self.controls  = controls
        self.autoplay  = autoplay
        self.loop      = loop
        self.muted     = muted

    def render(self):
        inline = self._resolve_props()
        attrs  = self._attrs(controls=self.controls, autoplay=self.autoplay,
                             loop=self.loop, muted=self.muted, style=inline or None)
        return f'<video{attrs}><source src="{self.src}"></video>'


class Icon(Widget):
    """
    Icono (emoji, caracter especial, SVG inline, etc.)

        Icon("🚀")
        Icon("🚀", size=32, margin=8)
        Icon("<svg ...>", size=24)
    """
    def __init__(self, icon=None, size=20, child=None, children=None, **kwargs):
        self._props   = Widget._extract_props(kwargs)
        self.icon     = icon
        self.size     = size
        self.child    = child
        self.children = children

    def render(self):
        base   = (f"font-size:{self.size}px; line-height:1; "
                  f"display:inline-flex; align-items:center")
        inline = self._resolve_props(base)
        inner  = self._resolve_inner(self.icon, self.child, self.children)
        return f'<span style="{inline}" aria-hidden="true">{inner}</span>'


class Avatar(Widget):
    """
    Avatar circular con imagen o iniciales.

        Avatar("/user.jpg")                                    # con imagen
        Avatar(initials="JD")                                  # con iniciales
        Avatar(initials="AB", background="#6366f1", color="#fff", width=48)

    Por defecto: 40x40px, circular.
    """
    def __init__(self, src=None, initials=None, **kwargs):
        self._props = Widget._extract_props(kwargs)
        self.src      = src
        self.initials = initials
        if not self._props.get("width"):           self._props["width"]  = 40
        if not self._props.get("height"):          self._props["height"] = 40
        if self._props.get("radius") is None:      self._props["radius"] = 999

    def render(self):
        base   = ("overflow:hidden; display:inline-flex; align-items:center; "
                  "justify-content:center; flex-shrink:0")
        inline = self._resolve_props(base)
        w      = self._props.get("width", 40)
        if self.src:
            return (f'<div style="{inline}">'
                    f'<img src="{self.src}" alt="" '
                    f'style="width:100%;height:100%;object-fit:cover"></div>')
        fs  = (w // 3) if isinstance(w, (int, float)) else 14
        bg  = self._props.get("background") or "var(--surface-2)"
        col = self._props.get("color") or "var(--text)"
        return (f'<div style="{inline};background:{bg};color:{col};'
                f'font-weight:600;font-size:{fs}px">'
                f'{self.initials or "?"}</div>')


# =============================================================================
# INTERACTION — botones e inputs
# =============================================================================


class TextField(Widget):
    """
    Campo de texto.

        TextField(placeholder="Tu nombre")
        TextField(placeholder="Email", type="email", name="email", width="100%")
        TextField(placeholder="Buscar", id="search_input", radius=999)
    """
    def __init__(self, placeholder="", value="", type="text",
                 name=None, id=None, disabled=False, **kwargs):
        self._props      = Widget._extract_props(kwargs)
        self.placeholder = placeholder
        self.value       = value
        self.type        = type
        self.name        = name
        self.id          = id
        self.disabled    = disabled

    def render(self):
        base  = ("padding:8px 12px; border:1px solid var(--border); border-radius:6px; "
                 "font-size:14px; outline:none; width:100%; box-sizing:border-box; "
                 "background:var(--input-bg,var(--surface)); color:var(--text); "
                 "transition:border-color .2s")
        inline = self._resolve_props(base)
        attrs  = self._attrs(type=self.type, placeholder=self.placeholder,
                             value=self.value or None, name=self.name,
                             style=inline, id=self.id, disabled=self.disabled)
        return f"<input{attrs}>"


class TextArea(Widget):
    """
    Campo de texto multilinea.

    Basico:
        TextArea(placeholder="Escribe tu mensaje...")

    Con opciones:
        TextArea(
            value="Hola mundo",
            rows=6,
            placeholder="Descripcion...",
            id="desc_field",
            name="descripcion",
            max_length=500,
        )

    Auto-resize:
        TextArea(placeholder="...", auto_resize=True)

    Monoespaciado:
        TextArea(placeholder="Pega tu JSON aqui...", monospace=True)

    Parametros:
        placeholder  str   texto de ayuda
        value        str   valor inicial
        rows         int   filas visibles (default: 4)
        name         str   nombre para formularios
        id           str   id del elemento
        disabled     bool  desactiva el campo
        readonly     bool  solo lectura
        resize       bool  permite redimensionar (default True)
        auto_resize  bool  crece con el contenido (default False)
        max_length   int   max de caracteres — activa contador
        show_count   bool  muestra contador aunque no haya max_length
        monospace    bool  fuente monoespaciada (default False)
    """

    _id_counter = 0

    def __init__(self, placeholder="", value="", rows=4,
                 name=None, id=None, disabled=False, readonly=False,
                 resize=True, auto_resize=False,
                 max_length=None, show_count=False,
                 monospace=False, **kwargs):
        self._props      = Widget._extract_props(kwargs)
        self.placeholder = placeholder
        self.value       = value
        self.rows        = rows
        self.name        = name
        self.disabled    = disabled
        self.readonly    = readonly
        self.resize      = resize
        self.auto_resize = auto_resize
        self.max_length  = max_length
        self.show_count  = show_count or (max_length is not None)
        self.monospace   = monospace
        TextArea._id_counter += 1
        self.uid = id or f"ta_{TextArea._id_counter}"

    def render(self):
        import json as _j
        uid   = self.uid
        extra = self._resolve_props()

        resize_val = "none" if (not self.resize or self.auto_resize) else "vertical"
        font_extra = (
            "font-family:\'Fira Code\',\'Cascadia Code\',monospace;"
            if self.monospace else ""
        )
        base = (
            f"width:100%;box-sizing:border-box;"
            f"padding:10px 12px;"
            f"border:1px solid var(--border-input,var(--border));"
            f"border-radius:8px;"
            f"font-size:14px;line-height:1.6;"
            f"outline:none;"
            f"background:var(--input-bg,var(--surface));"
            f"color:var(--text);"
            f"resize:{resize_val};"
            f"transition:border-color .2s;"
            f"{font_extra}"
        )
        inline = self._resolve_props(base)

        parts = [f'id="{uid}"', f'rows="{self.rows}"', f'style="{inline}"']
        if self.name:
            parts.append(f'name="{self.name}"')
        if self.placeholder:
            p = self.placeholder.replace('"', '&quot;')
            parts.append(f'placeholder="{p}"')
        if self.max_length:
            parts.append(f'maxlength="{self.max_length}"')
        if self.disabled:
            parts.append("disabled")
        if self.readonly:
            parts.append("readonly")
        parts.append('spellcheck="false"')

        escaped_val = (
            str(self.value).replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
            if self.value else ""
        )
        ta_html = f'<textarea {" ".join(parts)}>{escaped_val}</textarea>'

        auto_js = ""
        if self.auto_resize:
            auto_js = (
                f'<script>(function(){{'
                f'var el=document.getElementById({_j.dumps(uid)});'
                f'if(!el)return;'
                f'function _fit(){{el.style.height="auto";el.style.height=(el.scrollHeight+2)+"px";}}'
                f'el.addEventListener("input",_fit);_fit();'
                f'}})();</script>'
            )

        counter_html = ""
        if self.show_count:
            lim_js   = _j.dumps(self.max_length)
            init_len = len(str(self.value)) if self.value else 0
            init_txt = f"{init_len}" + (f"/{self.max_length}" if self.max_length else "") + " car."
            counter_html = (
                f'<div id="{uid}_ct" style="text-align:right;font-size:11px;'
                f'color:var(--text-muted);margin-top:3px">{init_txt}</div>'
                f'<script>(function(){{'
                f'var el=document.getElementById({_j.dumps(uid)});'
                f'var ct=document.getElementById({_j.dumps(uid+"_ct")});'
                f'var lim={lim_js};'
                f'if(!el||!ct)return;'
                f'el.addEventListener("input",function(){{'
                f'  var n=el.value.length;'
                f'  ct.textContent=n+(lim?"/"+lim:"")+" car.";'
                f'  ct.style.color=(lim&&n>=lim)?"var(--danger,#ef4444)":'
                f'                 (lim&&n>lim*0.85)?"#f59e0b":'
                f'                 "var(--text-muted)";'
                f'}});'
                f'}})();</script>'
            )

        wrapper_style = "width:100%"
        if extra:
            wrapper_style += ";" + extra

        return (
            f'<div style="{wrapper_style}">'
            + ta_html
            + counter_html
            + auto_js
            + '</div>'
        )

class Checkbox(Widget):
    """
    Casilla de verificacion con etiqueta.

        Checkbox("Aceptar terminos")
        Checkbox("Activo", checked=True, name="active")
    """
    def __init__(self, label="", checked=False, name=None, id=None, **kwargs):
        self._props  = Widget._extract_props(kwargs)
        self.label   = label
        self.checked = checked
        self.name    = name
        self.id      = id

    def render(self):
        base     = "display:flex; align-items:center; gap:8px; color:var(--text); cursor:pointer"
        inline   = self._resolve_props(base)
        checked  = " checked" if self.checked else ""
        name_a   = f' name="{self.name}"' if self.name else ""
        id_a     = f' id="{self.id}"' if self.id else ""
        return (f'<label style="{inline}">'
                f'<input type="checkbox"{checked}{name_a}{id_a}>'
                f'<span>{self.label}</span></label>')


# =============================================================================
# FEEDBACK — comunicar estado al usuario
# =============================================================================

class Badge(Widget):
    """
    Etiqueta de estado o categoria. Pequena y llamativa.

        Badge("Nuevo")
        Badge("Pro", background="var(--accent)", color="#fff")
        Badge("Beta", background="#f59e0b", radius=4)

    Por defecto usa el color de acento del tema.
    """
    def __init__(self, label=None, child=None, children=None, **kwargs):
        self._props   = Widget._extract_props(kwargs)
        self.label    = label
        self.child    = child
        self.children = children
        if not self._props.get("background"): self._props["background"] = "var(--accent)"
        if not self._props.get("color"):      self._props["color"]      = "#ffffff"

    def render(self):
        base   = ("display:inline-block; padding:2px 10px; border-radius:9999px; "
                  "font-size:12px; font-weight:600; white-space:nowrap")
        inline = self._resolve_props(base)
        inner  = self._resolve_inner(self.label, self.child, self.children)
        return self._wrap_url(f'<span style="{inline}">{inner}</span>')


class Alert(Widget):
    """
    Mensaje de alerta o notificacion inline.

        Alert("Guardado correctamente.", variant="success")
        Alert("Email invalido.", variant="error")
        Alert("Recuerda completar todos los campos.", variant="warning")
        Alert("Tienes 3 mensajes nuevos.", variant="info")

    Variantes: "info" | "success" | "warning" | "error"
    Acepta title para mayor claridad:
        Alert("El archivo fue eliminado.", variant="error", title="Error")
    """
    VARIANTS = {
        "info":    {"bg": "rgba(59,130,246,0.1)",  "border": "rgba(59,130,246,0.3)",  "icon": "ℹ️",  "color": "#3b82f6"},
        "success": {"bg": "rgba(34,197,94,0.1)",   "border": "rgba(34,197,94,0.3)",   "icon": "✅", "color": "#22c55e"},
        "warning": {"bg": "rgba(234,179,8,0.1)",   "border": "rgba(234,179,8,0.3)",   "icon": "⚠️", "color": "#eab308"},
        "error":   {"bg": "rgba(239,68,68,0.1)",   "border": "rgba(239,68,68,0.3)",   "icon": "❌", "color": "#ef4444"},
    }

    def __init__(self, message="", variant="info", title=None, icon=None, **kwargs):
        self._props  = Widget._extract_props(kwargs)
        self.message = message
        self.variant = variant
        self.title   = title
        self.icon    = icon

    def render(self):
        v      = self.VARIANTS.get(self.variant, self.VARIANTS["info"])
        ico    = self.icon if self.icon is not None else v["icon"]
        base   = (f"display:flex; align-items:flex-start; gap:12px; "
                  f"padding:14px 16px; border-radius:10px; "
                  f"background:{v['bg']}; border:1px solid {v['border']}")
        inline = self._resolve_props(base)
        title_html = (
            f'<div style="font-weight:700;font-size:14px;color:{v["color"]};'
            f'margin-bottom:4px;">{self.title}</div>'
            if self.title else ""
        )
        return (
            f'<div style="{inline}">'
            f'<span style="font-size:18px;flex-shrink:0;margin-top:1px">{ico}</span>'
            f'<div style="font-size:14px;color:var(--text);line-height:1.5">'
            f'{title_html}{self.message}</div>'
            f'</div>'
        )


# =============================================================================
# NAVIGATION — estructura de la pagina
# =============================================================================

class NavBar(Widget):
    """
    Barra de navegacion superior. Un pilar de cualquier sitio.

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

    Parametros:
        brand      Widget  logo o nombre del sitio (izquierda)
        links      list    lista de Link o cualquier widget (centro)
        actions    list    botones o widgets (derecha)
        sticky     bool    fija el header al scroll (default: True)
        bordered   bool    borde inferior (default: True)
    """
    def __init__(self, brand=None, links=None, actions=None,
                 sticky=True, bordered=True, **kwargs):
        self._props  = Widget._extract_props(kwargs)
        self.brand   = brand
        self.links   = links   or []
        self.actions = actions or []
        self.sticky  = sticky
        self.bordered = bordered

    def render(self):
        sticky_css = "position:sticky; top:0; z-index:100; " if self.sticky else ""
        border_css = "border-bottom:1px solid var(--border); " if self.bordered else ""
        base = (f"{sticky_css}{border_css}"
                f"background:var(--surface); "
                f"display:flex; align-items:center; "
                f"padding:0 32px; height:64px; gap:32px; "
                f"backdrop-filter:blur(12px); "
                f"-webkit-backdrop-filter:blur(12px)")
        inline = self._resolve_props(base)

        brand_html = ""
        if self.brand:
            b = self.brand.render() if isinstance(self.brand, Widget) else self.brand
            brand_html = ('<a href="/" style="flex-shrink:0;text-decoration:none;color:inherit">'
                          + b + '</a>')

        links_html = ""
        if self.links:
            items = "".join(
                (lk.render() if isinstance(lk, Widget) else str(lk))
                for lk in self.links
            )
            links_html = (f'<nav style="display:flex;align-items:center;gap:24px;'
                          f'flex:1;justify-content:center">{items}</nav>')

        actions_html = ""
        if self.actions:
            items = "".join(
                (a.render() if isinstance(a, Widget) else str(a))
                for a in self.actions
            )
            actions_html = (f'<div style="display:flex;align-items:center;'
                            f'gap:8px;flex-shrink:0">{items}</div>')

        return f'<header style="{inline}">{brand_html}{links_html}{actions_html}</header>'


class Footer(Widget):
    """
    Pie de pagina. Cierre natural de cualquier pagina.

        Footer(
            left=Text("© 2025 MiEmpresa"),
            right=Row([
                Link("Privacidad", href="/privacidad"),
                Link("Terminos",   href="/terminos"),
            ], gap=16),
        )

        # Solo texto centrado:
        Footer(center=Text("Hecho con Martin Framework"))

    Parametros:
        left    Widget  contenido izquierdo
        center  Widget  contenido central
        right   Widget  contenido derecho
        bordered bool   borde superior (default: True)
    """
    def __init__(self, left=None, center=None, right=None,
                 bordered=True, **kwargs):
        self._props  = Widget._extract_props(kwargs)
        self.left    = left
        self.center  = center
        self.right   = right
        self.bordered = bordered

    def render(self):
        border_css = "border-top:1px solid var(--border); " if self.bordered else ""
        base = (f"{border_css}padding:24px 32px; "
                f"display:flex; align-items:center; justify-content:space-between; "
                f"background:var(--surface); gap:16px; flex-wrap:wrap")
        inline = self._resolve_props(base)

        def _r(w):
            return (w.render() if isinstance(w, Widget) else str(w)) if w else ""

        left_html   = f'<div>{_r(self.left)}</div>'   if self.left   else '<div></div>'
        center_html = (f'<div style="text-align:center">{_r(self.center)}</div>'
                       if self.center else "")
        right_html  = f'<div>{_r(self.right)}</div>'  if self.right  else '<div></div>'

        return f'<footer style="{inline}">{left_html}{center_html}{right_html}</footer>'


class Breadcrumb(Widget):
    """
    Ruta de navegacion. Muestra donde esta el usuario en la jerarquia.

        Breadcrumb([
            ("Inicio",    "/"),
            ("Productos", "/productos"),
            ("Zapatillas",None),           # ultimo item, sin link
        ])

        # O con widgets directos:
        Breadcrumb([Link("Inicio","/"), Text(" / "), Text("Actual")])

    Separador por defecto: "/"
    """
    def __init__(self, items=None, separator="/", **kwargs):
        self._props    = Widget._extract_props(kwargs)
        self.items     = items or []
        self.separator = separator

    def render(self):
        base   = "display:flex; align-items:center; gap:8px; flex-wrap:wrap"
        inline = self._resolve_props(base)
        sep    = (f'<span style="color:var(--text-muted);font-size:13px">'
                  f'{self.separator}</span>')
        parts  = []
        for i, item in enumerate(self.items):
            if isinstance(item, Widget):
                parts.append(item.render())
            elif isinstance(item, (tuple, list)):
                label, href = item[0], (item[1] if len(item) > 1 else None)
                is_last = (i == len(self.items) - 1)
                if href and not is_last:
                    parts.append(
                        f'<a href="{href}" style="color:var(--accent);'
                        f'font-size:13px;text-decoration:none;">{label}</a>'
                    )
                else:
                    parts.append(
                        f'<span style="color:var(--text);font-size:13px;'
                        f'font-weight:{"600" if is_last else "400"}">{label}</span>'
                    )
            else:
                parts.append(f'<span style="font-size:13px;color:var(--text)">{item}</span>')
        html = sep.join(parts)
        return f'<nav aria-label="breadcrumb" style="{inline}">{html}</nav>'


class Tabs(Widget):
    """
    Navegacion por pestanas. Muestra un contenido a la vez.

        Tabs([
            ("General",  Column([Text("Contenido general...")])),
            ("Avanzado", Column([Text("Opciones avanzadas...")])),
            ("Sobre mi", Column([Avatar(initials="JD"), Text("Juan Diaz")])),
        ])

    Cada item es una tupla (label, widget_contenido).
    El primer tab esta activo por defecto.
    """
    _id_counter = 0

    def __init__(self, tabs=None, default=0, **kwargs):
        self._props  = Widget._extract_props(kwargs)
        self.tabs    = tabs or []
        self.default = default
        Tabs._id_counter += 1
        self.uid = f"tabs_{Tabs._id_counter}"

    def render(self):
        uid    = self.uid
        extra  = self._resolve_props()
        n      = len(self.tabs)

        # Tab buttons
        btn_base = ("padding:8px 20px; border:none; cursor:pointer; font-size:14px; "
                    "font-weight:500; border-radius:8px 8px 0 0; transition:all .2s")
        btns = ""
        panels = ""
        for i, (label, content) in enumerate(self.tabs):
            tid   = f"{uid}_t{i}"
            pid   = f"{uid}_p{i}"
            active = i == self.default
            active_style = (f"background:var(--surface); color:var(--text); "
                            f"border-bottom:2px solid var(--accent)")
            inactive_style = ("background:transparent; color:var(--text-muted); "
                              "border-bottom:2px solid transparent")
            lbl_html = label.render() if isinstance(label, Widget) else label
            btns += (
                f'<button id="{tid}" onclick="{uid}_go({i})" '
                f'style="{btn_base};{active_style if active else inactive_style}">'
                f'{lbl_html}</button>'
            )
            content_html = content.render() if isinstance(content, Widget) else str(content)
            display = "block" if active else "none"
            panels += (
                f'<div id="{pid}" style="display:{display};padding-top:16px">'
                f'{content_html}</div>'
            )

        wrapper_style = extra or "width:100%"
        tabs_bar = (f'<div style="display:flex;border-bottom:1px solid var(--border);'
                    f'gap:4px">{btns}</div>')

        js = (
            f'<script>(function(){{'
            f'window.{uid}_go=function(i){{'
            f'  for(var j=0;j<{n};j++){{'
            f'    var b=document.getElementById("{uid}_t"+j);'
            f'    var p=document.getElementById("{uid}_p"+j);'
            f'    var active=j===i;'
            f'    if(b){{b.style.color=active?"var(--text)":"var(--text-muted)";'
            f'           b.style.background=active?"var(--surface)":"transparent";'
            f'           b.style.borderBottom=active?"2px solid var(--accent)":"2px solid transparent";}}'
            f'    if(p)p.style.display=active?"block":"none";'
            f'  }}'
            f'}};'
            f'}})();</script>'
        )

        return f'<div style="{wrapper_style}">{tabs_bar}{panels}{js}</div>'


# =============================================================================
# DATA — para mostrar informacion estructurada
# =============================================================================

class Table(Widget):
    """
    Tabla de datos interactiva con sort por columna, busqueda por columna y paginacion.

    Uso basico:
        Table(
            headers=["Nombre", "Email", "Rol"],
            rows=[
                ["Ana Garcia",  "ana@email.com",  "Admin"],
                ["Pedro Lopez", "pedro@email.com","Editor"],
            ],
        )

    Con todas las funciones:
        Table(
            headers=[...], rows=[...],
            searchable=True,   # barra de busqueda global + filtro por columna
            sortable=True,     # click en cabecera para ordenar asc/desc
            page_size=10,      # paginacion
        )

    Con widgets en celdas (funcionales, no participan en sort/search):
        Table(
            headers=["Usuario", "Estado", "Accion"],
            rows=[[Row([Avatar(initials="AG"), Text("Ana")]), Badge("Activo"), Button("Ver")]],
        )
    """

    _id_counter = 0

    def __init__(self, headers=None, rows=None,
                 striped=True, bordered=True,
                 searchable=False, sortable=False,
                 page_size=None, **kwargs):
        self._props     = Widget._extract_props(kwargs)
        self.headers    = headers or []
        self.rows       = rows    or []
        self.striped    = striped
        self.bordered   = bordered
        self.searchable = searchable
        self.sortable   = sortable
        self.page_size  = page_size
        Table._id_counter += 1
        self.uid = f"tbl_{Table._id_counter}"

    def render(self):
        import json as _j
        uid = self.uid
        border_cell = "border:1px solid var(--border);" if self.bordered else ""
        base  = "width:100%;border-collapse:collapse;font-size:14px"
        extra = self._resolve_props()
        wrapper_style = "width:100%;overflow-x:auto"
        if extra:
            wrapper_style += ";" + extra

        ncols = len(self.headers)

        # ── thead ─────────────────────────────────────────────────────────────
        th_base = (f"{border_cell}padding:10px 16px;text-align:left;"
                   f"background:var(--surface-2,var(--surface));"
                   f"color:var(--text);font-weight:600;white-space:nowrap;"
                   f"user-select:none")
        if self.sortable:
            th_base += ";cursor:pointer;transition:background .15s"

        ths = ""
        for i, h in enumerate(self.headers):
            sort_attr = f' data-col="{i}"' if self.sortable else ""
            icon_span = (f'<span id="{uid}_si{i}" style="margin-left:5px;'
                         f'font-size:10px;color:var(--text-muted)">⇅</span>'
                         if self.sortable else "")
            # Per-column search input under header
            col_search = ""
            if self.searchable:
                col_search = (
                    f'<input type="text" placeholder="Filtrar..." '
                    f'data-col-search="{i}" '
                    f'oninput="{uid}_colFilter(this,{i})" '
                    f'onclick="event.stopPropagation()" '
                    f'style="display:block;margin-top:6px;width:100%;'
                    f'box-sizing:border-box;padding:4px 8px;font-size:12px;'
                    f'border:1px solid var(--border);border-radius:5px;'
                    f'background:var(--surface);color:var(--text);outline:none;'
                    f'font-weight:400"/>'
                )
            ths += (f'<th style="{th_base}"{sort_attr}>'
                    f'<div style="display:flex;align-items:center">{h}{icon_span}</div>'
                    f'{col_search}</th>')
        thead = f"<thead><tr>{ths}</tr></thead>" if self.headers else ""

        # ── tbody ─────────────────────────────────────────────────────────────
        td_style = f"{border_cell}padding:10px 16px;color:var(--text);vertical-align:middle"

        def _to_plain(cell):
            """Extrae texto plano de una celda (str o Widget) para sort/search."""
            import re as _re
            if isinstance(cell, Widget):
                h = cell.render()
                # Strip HTML tags and collapse whitespace
                t = _re.sub(r'<[^>]+>', ' ', h)
                t = t.replace('&amp;','&').replace('&lt;','<').replace('&gt;','>').replace('&nbsp;',' ')
                return ' '.join(t.split())
            return str(cell)

        rows_data = []  # (plain_text[], html[])
        for row in self.rows:
            plain, html = [], []
            for cell in row:
                plain.append(_to_plain(cell))
                html.append(cell.render() if isinstance(cell, Widget) else str(cell))
            rows_data.append((plain, html))

        tbody_rows = ""
        for i, (plain, html_cells) in enumerate(rows_data):
            stripe = (f"background:var(--surface-2,rgba(0,0,0,0.03))"
                      if self.striped and i % 2 == 1 else "")
            cells = "".join(
                f'<td style="{td_style};{stripe}" data-v="{_j.dumps(plain[ci])}">'
                f'{html_cells[ci]}</td>'
                for ci in range(len(html_cells))
            )
            tbody_rows += f'<tr id="{uid}_r{i}">{cells}</tr>'
        tbody = f"<tbody id='{uid}_tbody'>{tbody_rows}</tbody>"

        rows_plain_js = _j.dumps([p for p, _ in rows_data])

        # ── global search bar ─────────────────────────────────────────────────
        global_search = ""
        if self.searchable:
            global_search = (
                f'<div style="margin-bottom:10px">'
                f'<input id="{uid}_gsearch" type="text" placeholder="Buscar en toda la tabla..."'
                f' oninput="{uid}_globalFilter(this.value)"'
                f' style="padding:7px 12px;border:1px solid var(--border);border-radius:7px;'
                f'font-size:13px;width:100%;box-sizing:border-box;background:var(--surface);'
                f'color:var(--text);outline:none"/>'
                f'</div>'
            )

        # ── pagination bar ────────────────────────────────────────────────────
        pagination_html = ""
        if self.page_size:
            pagination_html = (
                f'<div id="{uid}_pgbar" style="display:flex;align-items:center;'
                f'justify-content:space-between;margin-top:10px;gap:8px;flex-wrap:wrap">'
                f'<span id="{uid}_pginfo" style="font-size:12px;color:var(--text-muted)"></span>'
                f'<div style="display:flex;gap:4px">'
                f'<button onclick="{uid}_pg(-1)" id="{uid}_pgprev"'
                f' style="padding:4px 14px;border:1px solid var(--border);border-radius:6px;'
                f'background:var(--surface);color:var(--text);cursor:pointer;font-size:13px">&#8592;</button>'
                f'<button onclick="{uid}_pg(1)" id="{uid}_pgnext"'
                f' style="padding:4px 14px;border:1px solid var(--border);border-radius:6px;'
                f'background:var(--surface);color:var(--text);cursor:pointer;font-size:13px">&#8594;</button>'
                f'</div></div>'
            )

        # ── JS ────────────────────────────────────────────────────────────────
        needs_js = self.searchable or self.sortable or bool(self.page_size)
        js = ""
        if needs_js:
            n  = len(rows_data)
            ps = self.page_size or n or 1

            js = (
                f'<script>(function(){{'
                f'var uid={_j.dumps(uid)};'
                f'var _data={rows_plain_js};'
                f'var _n={n};'
                f'var _ps={ps};'
                f'var _page=0;'
                f'var _sortCol=-1,_sortAsc=true;'
                f'var _globalQ="";'
                f'var _colQ=new Array({ncols}).fill("");'
                f'var _order=[];'
                f'for(var _i=0;_i<_n;_i++)_order.push(_i);'

                # match: row must pass global AND all active column filters
                f'function _match(idx){{'
                f'  var row=_data[idx];'
                f'  if(_globalQ){{' 
                f'    var gq=_globalQ.toLowerCase();'
                f'    var found=false;'
                f'    for(var c=0;c<row.length;c++){{if(row[c].toLowerCase().indexOf(gq)>=0){{found=true;break;}}}}'
                f'    if(!found)return false;'
                f'  }}'
                f'  for(var c=0;c<_colQ.length;c++){{'
                f'    if(!_colQ[c])continue;'
                f'    var v=(row[c]||"").toLowerCase();'
                f'    if(v.indexOf(_colQ[c].toLowerCase())<0)return false;'
                f'  }}'
                f'  return true;'
                f'}}'

                # apply: filter + sort
                f'function _apply(){{'
                f'  var filtered=[];'
                f'  for(var i=0;i<_n;i++)if(_match(i))filtered.push(i);'
                f'  if(_sortCol>=0){{'
                f'    var asc=_sortAsc,col=_sortCol;'
                f'    filtered.sort(function(a,b){{'
                f'      var va=(_data[a][col]||"").trim();'
                f'      var vb=(_data[b][col]||"").trim();'
                f'      var na=Number(va),nb=Number(vb);'
                f'      if(va!==""&&vb!==""&&!isNaN(na)&&!isNaN(nb))return asc?na-nb:nb-na;'
                f'      return asc?va.localeCompare(vb,"es",{{sensitivity:"base"}}):'
                f'               vb.localeCompare(va,"es",{{sensitivity:"base"}});'
                f'    }});'
                f'  }}'
                f'  _order=filtered;'
                f'  _page=0;'
                f'  _render();'
                f'}}'

                # render visible slice
                f'function _render(){{'
                f'  var tbody=document.getElementById(uid+"_tbody");'
                f'  if(!tbody)return;'
                f'  var allRows=tbody.querySelectorAll("tr");'
                f'  for(var i=0;i<allRows.length;i++)allRows[i].style.display="none";'
                f'  var start=_page*_ps,end=Math.min(start+_ps,_order.length);'
                f'  var vis=[];'
                f'  for(var i=start;i<end;i++){{'
                f'    var r=document.getElementById(uid+"_r"+_order[i]);'
                f'    if(r){{r.style.display="";vis.push(r);}}'
                f'  }}'
            )

            if self.striped:
                js += (
                    f'  vis.forEach(function(r,idx){{'
                    f'    r.querySelectorAll("td").forEach(function(td){{'
                    f'      td.style.background=idx%2===1?"var(--surface-2,rgba(0,0,0,0.03))":"";'
                    f'    }});'
                    f'  }});'
                )

            if self.page_size:
                js += (
                    f'  var info=document.getElementById(uid+"_pginfo");'
                    f'  var total=_order.length;'
                    f'  if(info)info.textContent=total===0?"Sin resultados":'
                    f'    "Mostrando "+(start+1)+"\u2013"+end+" de "+total;'
                    f'  var prev=document.getElementById(uid+"_pgprev");'
                    f'  var next=document.getElementById(uid+"_pgnext");'
                    f'  if(prev)prev.disabled=_page===0;'
                    f'  if(next)next.disabled=end>=_order.length;'
                )

            if self.sortable:
                js += (
                    f'  for(var c=0;c<{ncols};c++){{'
                    f'    var si=document.getElementById(uid+"_si"+c);'
                    f'    if(!si)continue;'
                    f'    if(c===_sortCol){{si.textContent=_sortAsc?" \u25b2":" \u25bc";si.style.color="var(--accent)";}}'
                    f'    else{{si.textContent="\u21c5";si.style.color="var(--text-muted)";}}'
                    f'  }}'
                )

            js += f'}}'  # end _render

            # public APIs
            if self.searchable:
                js += (
                    f'window[uid+"_globalFilter"]=function(q){{_globalQ=q;_apply();}};'
                    f'window[uid+"_colFilter"]=function(el,c){{_colQ[c]=el.value;_apply();}};'
                )

            if self.page_size:
                js += (
                    f'window[uid+"_pg"]=function(d){{'
                    f'  var pages=Math.max(1,Math.ceil(_order.length/_ps));'
                    f'  _page=Math.max(0,Math.min(_page+d,pages-1));'
                    f'  _render();'
                    f'}};'
                )

            if self.sortable:
                js += (
                    f'var _thead=document.querySelector("#{uid}_tbody").closest("table").querySelector("thead");'
                    f'if(_thead)_thead.addEventListener("click",function(e){{'
                    f'  var th=e.target.closest("th[data-col]");'
                    f'  if(!th||e.target.tagName==="INPUT")return;'
                    f'  var col=parseInt(th.getAttribute("data-col"));'
                    f'  if(_sortCol===col)_sortAsc=!_sortAsc;'
                    f'  else{{_sortCol=col;_sortAsc=true;}}'
                    f'  _apply();'
                    f'}});'
                )

            js += f'_apply();}})()</script>'

        return (
            f'<div style="{wrapper_style}">'
            + global_search
            + f'<table style="{base}">{thead}{tbody}</table>'
            + pagination_html
            + f'</div>'
            + js
        )


# =============================================================================
# OVERLAY — contenido encima de la pagina
# =============================================================================

class Modal(Widget):
    """
    Ventana modal (overlay). Para confirmaciones, formularios y detalles.

        Modal(
            id="confirm_modal",
            title="Confirmar accion",
            children=[
                Text("¿Estas seguro de que quieres eliminar este elemento?"),
                Row([
                    Button("Cancelar", variant="ghost",
                           on_click="closeModal('confirm_modal')"),
                    Button("Eliminar", variant="danger",
                           on_click="closeModal('confirm_modal')"),
                ], justify="flex-end", gap=8),
            ],
        )

        # Para abrirlo:
        Button("Abrir", on_click="openModal('confirm_modal')")

    Se incluyen las funciones JS globales openModal(id) y closeModal(id).

    Parametros:
        id           str   (requerido) identificador unico del modal
        title        str | Widget  titulo del modal
        children     list  contenido del modal
        close_on_backdrop  bool  cierra al hacer clic fuera (default: True)
        max_width    int   ancho maximo en px (default: 520)
    """
    def __init__(self, id, title=None, children=None, child=None,
                 close_on_backdrop=True, max_width=520, **kwargs):
        self._props         = Widget._extract_props(kwargs)
        self.modal_id       = id
        self.title          = title
        self.close_on_backdrop = close_on_backdrop
        self.max_width      = max_width
        if child is not None and children is None:
            children = [child]
        self.children = children or []

    def render(self):
        mid        = self.modal_id
        max_w      = self.max_width
        extra      = self._resolve_props()

        title_html = ""
        if self.title:
            t = self.title.render() if isinstance(self.title, Widget) else self.title
            title_html = (
                f'<div style="display:flex;align-items:center;justify-content:space-between;'
                f'margin-bottom:20px">'
                f'<div style="font-size:18px;font-weight:700;color:var(--text)">{t}</div>'
                f'<button onclick="closeModal(\'{mid}\')" '
                f'style="background:none;border:none;cursor:pointer;font-size:20px;'
                f'color:var(--text-muted);line-height:1;padding:4px">&#x2715;</button>'
                f'</div>'
            )

        inner = self._render_children(self.children)

        backdrop_click = (f' onclick="if(event.target===this)closeModal(\'{mid}\')"'
                          if self.close_on_backdrop else "")
        box_extra = (f";{extra}" if extra else "")

        html = (
            f'<div id="{mid}" style="display:none;position:fixed;top:0;left:0;'
            f'width:100%;height:100%;background:rgba(0,0,0,0.55);'
            f'backdrop-filter:blur(4px);-webkit-backdrop-filter:blur(4px);'
            f'z-index:99999;align-items:center;justify-content:center"'
            f'{backdrop_click}>'
            f'<div style="background:var(--surface);border:1px solid var(--border);'
            f'border-radius:16px;padding:28px 32px;max-width:{max_w}px;width:90%;'
            f'box-shadow:0 24px 64px rgba(0,0,0,0.4);max-height:85vh;overflow-y:auto{box_extra}">'
            f'{title_html}{inner}'
            f'</div></div>'
            f'<script>'
            f'if(!window.openModal)window.openModal=function(id){{'
            f'  var m=document.getElementById(id);'
            f'  if(m){{m.style.display="flex";}}'
            f'}};'
            f'if(!window.closeModal)window.closeModal=function(id){{'
            f'  var m=document.getElementById(id);'
            f'  if(m){{m.style.display="none";}}'
            f'}};'
            f'document.addEventListener("keydown",function(e){{'
            f'  if(e.key==="Escape"){{'
            f'    var m=document.getElementById("{mid}");'
            f'    if(m&&m.style.display!=="none")closeModal("{mid}");'
            f'  }}'
            f'}});'
            f'</script>'
        )
        return html


# =============================================================================
# UTILITY
# =============================================================================

class Raw(Widget):
    """
    Inyecta HTML arbitrario sin procesamiento.

        Raw('<hr style="border-color:red">')
        Raw('<script>console.log("hola")</script>')

    Util como escape hatch cuando necesitas HTML especifico.
    """
    def __init__(self, html: str):
        self._props = {}
        self.html   = html

    def render(self):
        return self.html


class ThemeToggle(Widget):
    """
    Boton para cambiar entre temas oscuro/claro/auto.

        ThemeToggle()                            # con emojis por defecto
        ThemeToggle(dark_icon="Oscuro", light_icon="Claro")
        ThemeToggle(include_auto=False)          # solo dark/light
        ThemeToggle(radius=8, padding=8)
    """
    def __init__(self, dark_icon="🌙", light_icon="☀️", auto_icon="🌗",
                 include_auto=True, title="Cambiar tema", **kwargs):
        self._props       = Widget._extract_props(kwargs)
        self.dark_icon    = dark_icon
        self.light_icon   = light_icon
        self.auto_icon    = auto_icon
        self.include_auto = include_auto
        self.title        = title

    def render(self):
        base = (
            "background:var(--surface); border:1px solid var(--border); "
            "color:var(--text); cursor:pointer; font-size:16px; "
            "display:inline-flex; align-items:center; justify-content:center; "
            "border-radius:8px; padding:6px 10px; transition:all 0.2s; "
            "user-select:none"
        )
        inline  = self._resolve_props(base)
        initial = self.auto_icon if self.include_auto else self.dark_icon
        uid     = f"_mtt_{id(self) & 0xFFFF}"

        return (
            f'<button id="{uid}" title="{self.title}" style="{inline}" '
            f'onclick="_mttCycle(\'{uid}\')" '
            f'onmouseover="this.style.borderColor=\'var(--accent)\'" '
            f'onmouseout="this.style.borderColor=\'\'">'
            f'{initial}'
            f'</button>'
            f'<script>'
            f'(function(){{'
            f'  var ICONS={{"dark":"{self.dark_icon}","light":"{self.light_icon}","auto":"{self.auto_icon}"}};'
            f'  var NEXT={{"dark":"light","light":{"auto" if self.include_auto else "dark"},"auto":"dark"}};'
            f'  function _mttSync(id){{var t=document.documentElement.getAttribute("data-theme")||"auto";'
            f'    var btn=document.getElementById(id);if(btn)btn.textContent=ICONS[t]||"{initial}";}} '
            f'  window._mttCycle=function(id){{'
            f'    var cur=document.documentElement.getAttribute("data-theme")||"auto";'
            f'    var next=NEXT[cur]||"auto";'
            f'    document.documentElement.setAttribute("data-theme",next);'
            f'    try{{localStorage.setItem("martin-theme",next);}}catch(e){{}}'
            f'    _mttSync(id);'
            f'  }};'
            f'  _mttSync("{uid}");'
            f'  var obs=new MutationObserver(function(){{_mttSync("{uid}");}});'
            f'  obs.observe(document.documentElement,{{attributes:true,attributeFilter:["data-theme"]}});'
            f'}})();'
            f'</script>'
        )


# =============================================================================
# SELECT / MULTISELECT
# =============================================================================

class Select(Widget):
    """
    Select(options=["A","B","C"], radius=8, width="100%")
    Select(options=[("es","Español"),...], search=True, padding=10)
    """
    _id_counter = 0

    def __init__(self, options=None, value=None, search=False,
                 placeholder="Seleccionar...", name=None, id=None, **kwargs):
        self._props = Widget._extract_props(kwargs)
        self.options = options or []
        self.value = value
        self.search = search
        self.placeholder = placeholder
        self.name = name
        Select._id_counter += 1
        self.uid = id or f"pw_select_{Select._id_counter}"

    def _parse_options(self):
        result = []
        for opt in self.options:
            if isinstance(opt, dict):
                result.append((str(opt["value"]), str(opt["label"])))
            elif isinstance(opt, tuple):
                result.append((str(opt[0]), str(opt[1])))
            else:
                result.append((str(opt), str(opt)))
        return result

    def render(self):
        extra = self._resolve_props()
        opts = self._parse_options()
        selected_val = str(self.value) if self.value is not None else ""
        selected_label = next((l for v, l in opts if v == selected_val), self.placeholder)

        if not self.search:
            base = ("padding: 8px 12px; border: 1px solid var(--border-input); border-radius: 6px; "
                    "font-size: 14px; background: var(--input-bg); color: var(--input-color); cursor: pointer; width: 100%")
            inline = f"{base}; {extra}" if extra else base
            opt_tags = "".join(
                f'<option value="{v}"{"selected" if v == selected_val else ""}>{l}</option>'
                for v, l in opts)
            name_attr = f' name="{self.name}"' if self.name else ""
            return f'<select id="{self.uid}" style="{inline}"{name_attr}>{opt_tags}</select>'

        wrapper_style = f"position: relative; width: 100%; font-size: 14px; {extra}"
        hidden_input = (f'<input type="hidden" name="{self.name}" id="{self.uid}_val" value="{selected_val}">'
                        if self.name else f'<input type="hidden" id="{self.uid}_val" value="{selected_val}">')

        uid = self.uid

        def make_opt(v, l):
            sel    = "1" if v == selected_val else "0"
            weight = "600" if v == selected_val else "400"
            # Build onclick safely — no nested f-string escaping
            onclick = "pwSelectPick(\'" + uid + "\',\'" + v + "\',\'" + l.replace("'", "\\'") + "\')"
            return (
                '<div class="pw-opt"'
                ' data-val="' + v + '"'
                ' data-label="' + l + '"'
                ' onclick="' + onclick + '"'
                ' data-sel="' + sel + '"'
                ' style="padding:10px 14px;cursor:pointer;font-size:14px;font-weight:' + weight + '">'
                + l + '</div>'
            )

        opt_items = "".join(make_opt(v, l) for v, l in opts)

        return (
            f'<style>' +
            f'#{uid}_list .pw-opt{{color:var(--text);background:transparent;border-radius:6px;transition:background .12s}}' +
            f'#{uid}_list .pw-opt:hover{{background:var(--surface-2)}}' +
            f'#{uid}_list .pw-opt[data-sel="1"]{{background:rgba(99,102,241,0.15);color:var(--accent);font-weight:600}}' +
            f'</style>' +
            f'<div id="{uid}_wrap" style="{wrapper_style}">' +
            f'  {hidden_input}' +
            f'  <div id="{uid}_btn" onclick="pwSelectToggle(\'{uid}\')" ' +
            f'    style="display:flex;align-items:center;justify-content:space-between;' +
            f'           padding:8px 14px;border:1px solid var(--border-input);border-radius:6px;' +
            f'           background:var(--input-bg);cursor:pointer;user-select:none;gap:8px;transition:border-color .2s">' +
            f'    <span id="{uid}_label" style="color:var(--input-color);flex:1;font-size:14px">{selected_label}</span>' +
            f'    <svg id="{uid}_arrow" width="12" height="12" viewBox="0 0 12 12" ' +
            f'         style="flex-shrink:0;transition:transform .2s;opacity:0.5">' +
            f'      <path d="M2 4l4 4 4-4" stroke="currentColor" stroke-width="1.5" fill="none" stroke-linecap="round"/>' +
            f'    </svg>' +
            f'  </div>' +
            f'  <div id="{uid}_drop" ' +
            f'    style="display:none;position:absolute;top:calc(100% + 6px);left:0;right:0;' +
            f'           z-index:9999;border:1px solid var(--border-input);border-radius:10px;' +
            f'           box-shadow:0 12px 40px rgba(0,0,0,0.25);overflow:hidden;' +
            f'           background:var(--dropdown-bg)">' +
            f'    <div style="padding:8px 8px 6px;border-bottom:1px solid var(--border)">' +
            f'      <input id="{uid}_search" type="text" placeholder="Buscar..."' +
            f'        oninput="pwSelectFilter(\'{uid}\',this.value)"' +
            f'        style="width:100%;padding:7px 10px;border:1px solid var(--border-input);' +
            f'               border-radius:6px;font-size:13px;outline:none;box-sizing:border-box;' +
            f'               background:var(--input-bg);color:var(--input-color)">' +
            f'    </div>' +
            f'    <div id="{uid}_list" style="max-height:220px;overflow-y:auto;padding:6px">' +
            f'      {opt_items}' +
            f'    </div>' +
            f'  </div>' +
            f'</div>' +
            '<script>' +
            '(function(){if(window._pwSelInit)return;window._pwSelInit=true;' +
            'window.pwSelectToggle=function(uid){' +
            '  var d=document.getElementById(uid+"_drop"),' +
            '      a=document.getElementById(uid+"_arrow"),' +
            '      b=document.getElementById(uid+"_btn"),' +
            '      o=d.style.display!=="none";' +
            '  document.querySelectorAll("[id$=_drop]").forEach(function(el){' +
            '    if(el.id!==uid+"_drop"){el.style.display="none";' +
            '      var x=document.getElementById(el.id.replace("_drop","_arrow"));' +
            '      if(x)x.style.transform="";' +
            '      var bx=document.getElementById(el.id.replace("_drop","_btn"));' +
            '      if(bx)bx.style.borderColor="";}' +
            '  });' +
            '  if(o){d.style.display="none";a.style.transform="";b.style.borderColor="";}' +
            '  else{d.style.display="block";a.style.transform="rotate(180deg)";' +
            '    b.style.borderColor="var(--accent)";' +
            '    setTimeout(function(){var s=document.getElementById(uid+"_search");' +
            '      if(s){s.value="";s.focus();pwSelectFilter(uid,"");}},30);}' +
            '};' +
            'window.pwSelectFilter=function(uid,q){' +
            '  document.querySelectorAll("#"+uid+"_list .pw-opt").forEach(function(i){' +
            '    i.style.display=i.getAttribute("data-label").toLowerCase().includes(q.toLowerCase())?"block":"none";' +
            '  });' +
            '};' +
            'window.pwSelectPick=function(uid,val,label){' +
            '  document.getElementById(uid+"_val").value=val;' +
            '  document.getElementById(uid+"_label").textContent=label;' +
            '  document.getElementById(uid+"_drop").style.display="none";' +
            '  document.getElementById(uid+"_arrow").style.transform="";' +
            '  document.getElementById(uid+"_btn").style.borderColor="";' +
            '  document.querySelectorAll("#"+uid+"_list .pw-opt").forEach(function(el){' +
            '    var s=el.getAttribute("data-val")===val;' +
            '    el.setAttribute("data-sel",s?"1":"0");' +
            '    el.style.fontWeight=s?"600":"400";' +
            '  });' +
            '};' +
            'document.addEventListener("click",function(e){' +
            '  if(!e.target.closest("[id$=_wrap]")){' +
            '    document.querySelectorAll("[id$=_drop]").forEach(function(el){' +
            '      el.style.display="none";' +
            '      var a=document.getElementById(el.id.replace("_drop","_arrow"));' +
            '      if(a)a.style.transform="";' +
            '      var b=document.getElementById(el.id.replace("_drop","_btn"));' +
            '      if(b)b.style.borderColor="";' +
            '    });' +
            '  }' +
            '});' +
            '})();</script>'
        )

class MultiSelect(Widget):
    """
    MultiSelect(options=["A","B","C"], values=["A"], radius=8)
    MultiSelect(options=[("py","Python"),...], values=["py"], padding=10)
    """
    _id_counter = 0

    def __init__(self, options=None, values=None, placeholder="Añadir...",
                 name=None, id=None,
                 tag_color="rgba(99,102,241,0.15)",
                 tag_border="rgba(99,102,241,0.35)",
                 tag_text="var(--accent)", **kwargs):
        self._props     = Widget._extract_props(kwargs)
        self.options    = options or []
        self.values     = values or []
        self.placeholder = placeholder
        self.name       = name
        self.tag_color  = tag_color
        self.tag_border = tag_border
        self.tag_text   = tag_text
        MultiSelect._id_counter += 1
        self.uid = id or f"pw_multi_{MultiSelect._id_counter}"

    def _parse_options(self):
        result = []
        for opt in self.options:
            if isinstance(opt, dict):
                result.append((str(opt["value"]), str(opt["label"])))
            elif isinstance(opt, tuple):
                result.append((str(opt[0]), str(opt[1])))
            else:
                result.append((str(opt), str(opt)))
        return result

    def render(self):
        import json as _json
        uid   = self.uid
        extra = self._resolve_props()
        opts  = self._parse_options()
        selected_vals = [str(v) for v in self.values]

        opts_js     = _json.dumps([{"v": v, "l": l} for v, l in opts])
        selected_js = _json.dumps(selected_vals)
        name_js     = _json.dumps(self.name)
        tc_js       = _json.dumps(self.tag_color)
        tb_js       = _json.dumps(self.tag_border)
        tt_js       = _json.dumps(self.tag_text)
        ph_js       = _json.dumps(self.placeholder)

        wrapper_style = "position:relative;width:100%;font-size:14px"
        if extra:
            wrapper_style += ";" + extra

        # Option rows — no inline event handlers, handled via JS delegation
        rows = []
        for v, l in opts:
            display = "none" if v in selected_vals else "block"
            rows.append(
                '<div class="pw-mopt"'
                ' data-val="' + v + '"'
                ' data-label="' + l + '"'
                ' style="display:' + display + ';padding:9px 14px;cursor:pointer;'
                'font-size:14px;color:var(--text);border-radius:6px;transition:background .1s">'
                + l + '</div>'
            )
        opt_rows = "".join(rows)

        # Style block for hover — avoids inline onmouseover
        hover_css = (
            "<style>"
            "#" + uid + "_list .pw-mopt:hover{background:var(--surface-2)}"
            "</style>"
        )

        return (
            hover_css +
            '<div id="' + uid + '_wrap" style="' + wrapper_style + '">'
            '  <div id="' + uid + '_box"'
            '    style="display:flex;flex-wrap:wrap;gap:6px;align-items:center;min-height:42px;'
            '           padding:6px 10px;border:1px solid var(--border-input);border-radius:8px;'
            '           background:var(--input-bg);cursor:text;box-sizing:border-box;transition:border-color .2s">'
            '    <div id="' + uid + '_tags" style="display:contents;flex-wrap:wrap;gap:6px"></div>'
            '    <input id="' + uid + '_input" type="text"'
            '      style="border:none;outline:none;font-size:14px;min-width:100px;flex:1;'
            '             padding:2px 0;background:transparent;color:var(--input-color)">'
            '  </div>'
            '  <div id="' + uid + '_hidden"></div>'
            '  <div id="' + uid + '_drop"'
            '    style="display:none;position:absolute;top:calc(100% + 6px);left:0;right:0;'
            '           z-index:9999;border:1px solid var(--border-input);border-radius:10px;'
            '           box-shadow:0 12px 40px rgba(0,0,0,0.25);overflow:hidden;background:var(--dropdown-bg)">'
            '    <div id="' + uid + '_list"'
            '      style="max-height:220px;overflow-y:auto;padding:6px">'
            '      ' + opt_rows +
            '    </div>'
            '    <div style="padding:6px 12px 8px;border-top:1px solid var(--border);'
            '                display:flex;justify-content:flex-end">'
            '      <span id="' + uid + '_clear"'
            '        style="font-size:12px;color:var(--text-muted);cursor:pointer;user-select:none">'
            '        Limpiar todo'
            '      </span>'
            '    </div>'
            '  </div>'
            '</div>'
            "<script>(function(){"
            "var uid=" + _json.dumps(uid) + ";"
            "var opts=" + opts_js + ";"
            "var name=" + name_js + ";"
            "var tc=" + tc_js + ";"
            "var tb=" + tb_js + ";"
            "var tt=" + tt_js + ";"
            "var ph=" + ph_js + ";"
            "var sel=new Set(" + selected_js + ");"
            "if(!window._pwMultiState)window._pwMultiState={};"
            "window._pwMultiState[uid]=sel;"
            "var box=document.getElementById(uid+'_box');"
            "var input=document.getElementById(uid+'_input');"
            "var drop=document.getElementById(uid+'_drop');"
            "var list=document.getElementById(uid+'_list');"
            "var tags=document.getElementById(uid+'_tags');"
            "var hidden=document.getElementById(uid+'_hidden');"
            "var clearBtn=document.getElementById(uid+'_clear');"
            "function render(){"
            "  box.querySelectorAll('span[data-tag]').forEach(function(t){t.remove();});"
            "  sel.forEach(function(val){"
            "    var opt=opts.find(function(o){return o.v===val;})||{};"
            "    var label=opt.l||val;"
            "    var tag=document.createElement('span');"
            "    tag.setAttribute('data-tag',val);"
            "    tag.style.cssText='display:inline-flex;align-items:center;gap:4px;padding:3px 8px;'"
            "      +'border-radius:9999px;font-size:12px;font-weight:500;flex-shrink:0;'"
            "      +'background:'+tc+';color:'+tt+';border:1px solid '+tb;"
            "    var txt=document.createTextNode(label);"
            "    var x=document.createElement('span');"
            "    x.textContent='×';"
            "    x.style.cssText='cursor:pointer;font-size:15px;line-height:1;opacity:0.6;margin-left:2px';"
            "    x.onmouseover=function(){this.style.opacity='1';};"
            "    x.onmouseout=function(){this.style.opacity='0.6';};"
            "    (function(v){x.onclick=function(e){e.stopPropagation();sel.delete(v);render();showOpt(v);};})(val);"
            "    tag.appendChild(txt);tag.appendChild(x);"
            "    box.insertBefore(tag,input);"
            "  });"
            "  if(name){"
            "    hidden.innerHTML='';"
            "    sel.forEach(function(val){"
            "      var i=document.createElement('input');"
            "      i.type='hidden';i.name=name;i.value=val;"
            "      hidden.appendChild(i);"
            "    });"
            "  }"
            "  input.placeholder=sel.size===0?ph:'';"
            "}"
            "function showOpt(val){"
            "  var el=list.querySelector('[data-val=\"'+val+'\"]');"
            "  if(el)el.style.display='block';"
            "}"
            "function openDrop(){"
            "  drop.style.display='block';"
            "  box.style.borderColor='var(--accent)';"
            "}"
            "function closeDrop(){"
            "  drop.style.display='none';"
            "  box.style.borderColor='';"
            "  input.value='';"
            "  list.querySelectorAll('.pw-mopt').forEach(function(el){"
            "    var v=el.getAttribute('data-val');"
            "    el.style.display=sel.has(v)?'none':'block';"
            "  });"
            "}"
            "list.addEventListener('click',function(e){"
            "  var el=e.target.closest('.pw-mopt');"
            "  if(!el)return;"
            "  var val=el.getAttribute('data-val');"
            "  sel.add(val);"
            "  el.style.display='none';"
            "  input.value='';"
            "  list.querySelectorAll('.pw-mopt').forEach(function(e2){"
            "    var v=e2.getAttribute('data-val');"
            "    e2.style.display=sel.has(v)?'none':'block';"
            "  });"
            "  render();"
            "  input.focus();"
            "});"
            "input.addEventListener('focus',openDrop);"
            "input.addEventListener('input',function(){"
            "  var q=this.value.toLowerCase();"
            "  list.querySelectorAll('.pw-mopt').forEach(function(el){"
            "    var v=el.getAttribute('data-val');"
            "    var match=el.getAttribute('data-label').toLowerCase().includes(q);"
            "    el.style.display=(match&&!sel.has(v))?'block':'none';"
            "  });"
            "});"
            "clearBtn.addEventListener('click',function(){"
            "  sel.clear();"
            "  list.querySelectorAll('.pw-mopt').forEach(function(el){el.style.display='block';});"
            "  render();"
            "  closeDrop();"
            "});"
            "document.addEventListener('click',function(e){"
            "  if(!e.target.closest('#'+uid+'_wrap'))closeDrop();"
            "});"
            "render();"
            "})()</script>"
        )


# ══════════════════════════════════════════════════════════
# UTILITY
# ══════════════════════════════════════════════════════════


# =============================================================================
# API — llamadas al servidor
# =============================================================================

class Ref:
    """
    Referencia a un input por id para usarlo en ApiCall.body.

    Ref("lang_select")          → lee el valor del Select con id="lang_select"
    Ref("areas_multi")          → lee los valores del MultiSelect con id="areas_multi"
    Ref("nombre", label=True)   → lee también el label visible (para Select)
    """
    def __init__(self, input_id, label=False):
        self.input_id = input_id
        self.label    = label

    def to_js(self):
        """Genera el snippet JS que lee el valor de este input."""
        uid = self.input_id
        js  = (
            "(function(){"
            # MultiSelect: tiene _hidden con inputs
            "var mh=document.getElementById('" + uid + "_hidden');"
            "if(mh){"
            "  var vals=[];"
            "  mh.querySelectorAll('input').forEach(function(i){vals.push(i.value);});"
            "  var labels=[];"
            "  var box=document.getElementById('" + uid + "_box');"
            "  if(box)box.querySelectorAll('span[data-tag]').forEach(function(t){"
            "    labels.push(t.childNodes[0].textContent.trim());"
            "  });"
            "  return {valores:vals,etiquetas:labels};"
            "}"
            # Select con búsqueda: tiene _val y _label
            "var sv=document.getElementById('" + uid + "_val');"
            "if(sv){"
            "  var sl=document.getElementById('" + uid + "_label');"
            "  return {valor:sv.value,etiqueta:sl?sl.textContent.trim():sv.value};"
            "}"
            # TextField / input normal
            "var el=document.getElementById('" + uid + "');"
            "if(el)return el.value;"
            "return null;"
            "})()"
        )
        return js


class ApiCall:
    """
    Acción para Button(on_click=...).

    ApiCall('/api/datos')
        → POST automático con todos los inputs del formulario padre

    ApiCall('/api/datos', body={'lang': Ref('lang_select'), 'areas': Ref('areas_multi')})
        → POST con campos específicos

    ApiCall('/api/datos', method='GET')
        → GET sin body

    ApiCall('/api/datos', target='resultado')
        → muestra la respuesta en el ResultBox con id='resultado'

    ApiCall('/api/datos',
            loading='Procesando...',
            on_success='alert("ok")',
            on_error='console.error(err)')
        → callbacks JS custom
    """
    def __init__(self, url, method='POST', body=None, target=None,
                 loading='Enviando...', on_success=None, on_error=None):
        self.url        = url
        self.method     = method.upper()
        self.body       = body    # dict of {key: Ref(...) or literal} | None = auto
        self.target     = target
        self.loading    = loading
        self.on_success = on_success
        self.on_error   = on_error

    def _body_js(self, btn_id):
        """Genera el JS que construye el body del fetch."""
        if self.body is None:
            # Auto: recoge todos los inputs/selects dentro del form padre del botón
            return (
                "(function(){"
                "var btn=document.getElementById('" + btn_id + "');"
                "var form=btn?btn.closest('form,[data-martin-form]'):null;"
                "var scope=form||document;"
                "var data={};"
                # TextFields
                "scope.querySelectorAll('input[name],textarea[name]').forEach(function(el){"
                "  if(el.type==='hidden'&&el.closest('[id$=_hidden]'))return;"  # skip multiselect hiddens
                "  data[el.name]=el.value;"
                "});"
                # Regular selects
                "scope.querySelectorAll('select').forEach(function(el){data[el.name]=el.value;});"
                # Martin Selects (_val hidden inputs)
                "scope.querySelectorAll('[id$=_val]').forEach(function(el){"
                "  var uid=el.id.replace('_val','');"
                "  var lbl=document.getElementById(uid+'_label');"
                "  var key=el.name||uid;"
                "  data[key]={valor:el.value,etiqueta:lbl?lbl.textContent.trim():el.value};"
                "});"
                # Martin MultiSelects (_hidden container)
                "scope.querySelectorAll('[id$=_hidden]').forEach(function(container){"
                "  var uid=container.id.replace('_hidden','');"
                "  var vals=[],labels=[];"
                "  container.querySelectorAll('input').forEach(function(i){vals.push(i.value);});"
                "  var box=document.getElementById(uid+'_box');"
                "  if(box)box.querySelectorAll('span[data-tag]').forEach(function(t){"
                "    labels.push(t.childNodes[0].textContent.trim());"
                "  });"
                "  data[uid]={valores:vals,etiquetas:labels};"
                "});"
                "return data;"
                "})()"
            )
        else:
            # Manual: dict of key → Ref or literal
            import json as _json
            parts = []
            for key, val in self.body.items():
                k = _json.dumps(key)
                if isinstance(val, Ref):
                    parts.append(k + ":" + val.to_js())
                else:
                    parts.append(k + ":" + _json.dumps(val))
            return "{" + ",".join(parts) + "}"

    def to_js(self, btn_id):
        """Genera el handler JS completo para el onclick del botón."""
        import json as _json
        url        = _json.dumps(self.url)
        method     = _json.dumps(self.method)
        loading    = _json.dumps(self.loading)
        target_js  = ("document.getElementById(" + _json.dumps(self.target) + ")")  if self.target else "null"
        body_js    = self._body_js(btn_id)
        on_success = self.on_success or ""
        on_error   = self.on_error   or ""

        has_body   = self.method not in ("GET", "DELETE")

        return (
            "(async function(){"
            "var btn=document.getElementById(" + _json.dumps(btn_id) + ");"
            "if(!btn)return;"
            "var orig=btn.textContent;"
            "btn.textContent=" + loading + ";"
            "btn.disabled=true;"
            "btn.style.opacity='0.7';"
            "var target=" + target_js + ";"
            "if(target)target.setAttribute('data-state','loading');"
            "try{"
            "var fetchOpts={method:" + method + ",headers:{}};"
            + (
                "var bodyData=" + body_js + ";"
                "fetchOpts.body=JSON.stringify(bodyData);"
                "fetchOpts.headers['Content-Type']='application/json';"
                if has_body else ""
            ) +
            "var res=await fetch(" + url + ",fetchOpts);"
            "var data=await res.json();"
            "if(target){"
            "  target.setAttribute('data-state',res.ok?'success':'error');"
            "  target.setAttribute('data-status',res.status);"
            "  target._martinData=data;"
            "  target.dispatchEvent(new CustomEvent('martin:result',{detail:data}));"
            "}"
            + ("(function(result){" + on_success + "})(data);" if on_success else "") +
            "}catch(e){"
            "if(target){"
            "  target.setAttribute('data-state','error');"
            "  target._martinData={error:e.message};"
            "  target.dispatchEvent(new CustomEvent('martin:result',{detail:{error:e.message}}));"
            "}"
            + ("(function(err){" + on_error + "})(e);" if on_error else "") +
            "}finally{"
            "btn.textContent=orig;"
            "btn.disabled=false;"
            "btn.style.opacity='1';"
            "}"
            "})()"
        )


class ResultBox(Widget):
    """
    Muestra la respuesta de un ApiCall.

    ResultBox(id='resultado')
    ResultBox(id='resultado', loading='Procesando...', empty='Presiona el botón.')
    ResultBox(id='resultado', format='json')        # pretty JSON (default)
    ResultBox(id='resultado', format='message')     # muestra data.mensaje
    ResultBox(id='resultado', format='custom',
              template='<b>{nombre}</b> guardado.')  # template con campos del JSON
    """
    def __init__(self, id, loading='Cargando...', empty='',
                 format='json', template=None, **kwargs):
        self._props   = Widget._extract_props(kwargs)
        self.box_id   = id
        self.loading  = loading
        self.empty    = empty
        self.format   = format   # 'json' | 'message' | 'custom'
        self.template = template

    def render(self):
        import json as _json
        extra   = self._resolve_props()
        box_id  = self.box_id
        loading = _json.dumps(self.loading)
        empty   = _json.dumps(self.empty)
        fmt     = _json.dumps(self.format)
        tmpl    = _json.dumps(self.template or "")

        wrapper_style = (
            "border-radius:12px;overflow:hidden;transition:all .3s;"
            "border:1px solid transparent"
        )
        if extra:
            wrapper_style += ";" + extra

        return (
            '<div id="' + box_id + '" data-state="empty"'
            ' style="' + wrapper_style + '">'
            '</div>'
            '<style>'
            '#' + box_id + '[data-state=empty]{display:none}'
            '#' + box_id + '[data-state=loading]{'
            '  display:block;padding:16px;'
            '  border-color:var(--border);background:var(--surface);'
            '  color:var(--text-muted);font-size:14px}'
            '#' + box_id + '[data-state=success]{'
            '  display:block;padding:16px;'
            '  border-color:rgba(52,211,153,0.3);background:var(--surface)}'
            '#' + box_id + '[data-state=error]{'
            '  display:block;padding:16px;'
            '  border-color:rgba(248,113,113,0.3);background:var(--surface)}'
            '</style>'
            '<script>(function(){'
            'var box=document.getElementById(' + _json.dumps(box_id) + ');'
            'if(!box)return;'
            'box.addEventListener("martin:result",function(e){'
            '  var d=e.detail;'
            '  var fmt=' + fmt + ';'
            '  var tmpl=' + tmpl + ';'
            '  var ok=box.getAttribute("data-state")==="success";'
            '  var col=ok?"#34d399":"#f87171";'
            '  var label=ok?"Respuesta del servidor":"Error";'
            '  var content;'
            '  if(fmt==="message"){'
            '    content=\'<p style="margin:0;font-size:15px;color:var(--text)">\'+( d.mensaje||d.message||d.error||JSON.stringify(d))+\'</p>\';'
            '  }else if(fmt==="custom"&&tmpl){'
            '    content=tmpl.replace(/\\{(\\w+)\\}/g,function(_,k){return d[k]!==undefined?d[k]:"?";});'
            '    content=\'<div style="font-size:14px;color:var(--text)">\'+content+\'</div>\';'
            '  }else{'
            '    content=\'<pre style="margin:0;font-family:monospace;font-size:13px;color:var(--text-muted);white-space:pre-wrap">\'+JSON.stringify(d,null,2)+\'</pre>\';'
            '  }'
            '  box.innerHTML='
            '    \'<div style="display:flex;align-items:center;gap:8px;margin-bottom:12px">\''
            '    +\'<span style="width:8px;height:8px;border-radius:50%;background:\'+col+\';flex-shrink:0"></span>\''
            '    +\'<strong style="font-size:13px;color:var(--text)">\'+label+\'</strong>\''
            '    +\'</div>\'+content;'
            '});'
            '})()</script>'
        )


class WordCloud(Widget):
    """
    Nube de palabras interactiva, sin dependencias externas.

    WordCloud(words=["Python", "Martin", "Web"])
    WordCloud(words={"Python": 10, "JS": 4, "Rust": 7})
    WordCloud(words=[("Python", 10), ("JS", 4)], width=700, height=350)

    Opciones:
        width       int     ancho en px          (default: 600)
        height      int     alto en px           (default: 300)
        min_size    int     tamaño mínimo fuente (default: 14)
        max_size    int     tamaño máximo fuente (default: 64)
        colors      list    lista de colores CSS (default: paleta indigo/mint)
        font        str     fuente CSS           (default: "inherit")
        on_click    str     JS ejecutado al hacer click: usa `word` y `weight`.
    """

    _id_counter = 0

    def __init__(self, words=None, width=600, height=300,
                 min_size=12, max_size=72,
                 colors=None, font="inherit", on_click=None, **kwargs):
        self._props   = Widget._extract_props(kwargs)
        self.words    = words or []
        self.width    = width
        self.height   = height
        self.min_size = min_size
        self.max_size = max_size
        self.colors   = colors or [
            "#818cf8", "#34d399", "#fb923c",
            "#f472b6", "#38bdf8", "#a78bfa",
            "#4ade80", "#fbbf24",
        ]
        self.font     = font
        self.on_click = on_click
        WordCloud._id_counter += 1
        self.uid = f"wc_{WordCloud._id_counter}"

    def _parse_words(self):
        w = self.words
        if isinstance(w, dict):
            return list(w.items())
        result = []
        for item in w:
            if isinstance(item, (list, tuple)) and len(item) == 2:
                result.append((str(item[0]), float(item[1])))
            else:
                result.append((str(item), 1.0))
        return result

    def render(self):
        import json as _json

        uid      = self.uid
        pairs    = self._parse_words()
        extra    = self._resolve_props()
        w        = self.width
        h        = self.height

        words_js  = _json.dumps(pairs)
        colors_js = _json.dumps(self.colors)
        min_s     = self.min_size
        max_s     = self.max_size
        font_js   = _json.dumps(self.font)
        on_click  = self.on_click or ""

        wrapper_style = "display:inline-block;max-width:100%;position:relative"
        if extra:
            wrapper_style += ";" + extra

        return (
            '<div style="' + wrapper_style + '">'
            '<canvas id="' + uid + '" width="' + str(w) + '" height="' + str(h) + '"'
            ' style="max-width:100%;border-radius:12px;cursor:default;display:block"></canvas>'
            # Tooltip div — positioned absolute over canvas
            '<div id="' + uid + '_tip"'
            ' style="display:none;position:absolute;pointer-events:none;'
            'padding:5px 10px;background:rgba(0,0,0,0.75);color:#fff;'
            'border-radius:6px;font-size:12px;white-space:nowrap;'
            'transform:translate(-50%,-100%);margin-top:-6px;z-index:99"></div>'
            '</div>'
            '<script>(function(){'
            'var canvas=document.getElementById(' + _json.dumps(uid) + ');'
            'var tip=document.getElementById(' + _json.dumps(uid + "_tip") + ');'
            'if(!canvas)return;'
            'var ctx=canvas.getContext("2d");'
            'var dpr=window.devicePixelRatio||1;'
            'var W=' + str(w) + ',H=' + str(h) + ';'
            'canvas.width=W*dpr;canvas.height=H*dpr;'
            'canvas.style.width=W+"px";canvas.style.height=H+"px";'
            'ctx.scale(dpr,dpr);'
            'var rawWords=' + words_js + ';'
            'var colors=' + colors_js + ';'
            'var minS=' + str(min_s) + ',maxS=' + str(max_s) + ';'
            'var font=' + font_js + ';'
            'if(font==="inherit")font="system-ui,sans-serif";'

            # Logarithmic scale for more visible size contrast
            'var weights=rawWords.map(function(p){return p[1];});'
            'var minW=Math.min.apply(null,weights);'
            'var maxW=Math.max.apply(null,weights);'
            'var logMin=Math.log(minW+1),logMax=Math.log(maxW+1),logRange=logMax-logMin||1;'
            'var words=rawWords.map(function(p,i){'
            '  var logNorm=(Math.log(p[1]+1)-logMin)/logRange;'
            '  var size=Math.round(minS+logNorm*(maxS-minS));'
            '  var col=colors[i%colors.length];'
            '  return {text:p[0],weight:p[1],size:size,color:col};'
            '});'

            'words.sort(function(a,b){return b.size-a.size;});'

            # Collision detection
            'var placed=[];'
            'function overlaps(r){'
            '  for(var i=0;i<placed.length;i++){'
            '    var p=placed[i];'
            '    if(r.x<p.x+p.w+4&&r.x+r.w+4>p.x&&r.y<p.y+p.h+4&&r.y+r.h+4>p.y)return true;'
            '  }'
            '  return false;'
            '}'
            'function tryPlace(word){'
            '  ctx.font="bold "+word.size+"px "+font;'
            '  var tw=ctx.measureText(word.text).width;'
            '  var th=word.size*1.1;'
            '  var cx=W/2,cy=H/2;'
            '  for(var step=0;step<400;step++){'
            '    var angle=step*0.5;'
            '    var r=step*1.1;'
            '    var x=cx+r*Math.cos(angle)-tw/2;'
            '    var y=cy+r*Math.sin(angle)*0.55+th/2;'
            '    if(x<4||y-th<4||x+tw>W-4||y>H-4)continue;'
            '    var rect={x:x,y:y-th,w:tw,h:th};'
            '    if(!overlaps(rect)){placed.push(rect);return {x:x,y:y,w:tw,h:th};}'
            '  }'
            '  return null;'
            '}'

            'var placedWords=[];'
            'words.forEach(function(word){'
            '  var pos=tryPlace(word);'
            '  if(pos)placedWords.push({word:word,pos:pos});'
            '});'

            # Draw function
            'function draw(hitItem){'
            '  ctx.clearRect(0,0,W,H);'
            '  placedWords.forEach(function(item){'
            '    var word=item.word,pos=item.pos;'
            '    var isHit=item===hitItem;'
            '    ctx.save();'
            '    ctx.globalAlpha=(hitItem&&!isHit)?0.35:1;'
            '    if(isHit){'
            '      ctx.shadowColor=word.color;'
            '      ctx.shadowBlur=14;'
            '      ctx.font="bold "+(word.size+3)+"px "+font;'
            '    }else{'
            '      ctx.font="bold "+word.size+"px "+font;'
            '    }'
            '    ctx.fillStyle=word.color;'
            '    ctx.fillText(word.text,pos.x,pos.y);'
            '    ctx.restore();'
            '  });'
            '}'
            'draw(null);'

            # Mousemove — hit detection + tooltip
            'canvas.addEventListener("mousemove",function(e){'
            '  var rect=canvas.getBoundingClientRect();'
            '  var scaleX=W/rect.width,scaleY=H/rect.height;'
            '  var mx=(e.clientX-rect.left)*scaleX;'
            '  var my=(e.clientY-rect.top)*scaleY;'
            '  var hit=null;'
            '  placedWords.forEach(function(item){'
            '    var p=item.pos;'
            '    if(mx>=p.x&&mx<=p.x+p.w&&my>=p.y-p.h&&my<=p.y)hit=item;'
            '  });'
            '  canvas.style.cursor=hit?"pointer":"default";'
            '  draw(hit);'
            '  if(hit&&tip){'
            '    var bRect=canvas.getBoundingClientRect();'
            '    var px=hit.pos.x+hit.pos.w/2;'
            '    var py=hit.pos.y-hit.pos.h;'
            '    var scX=bRect.width/W,scY=bRect.height/H;'
            '    tip.textContent=hit.word.text+" · peso: "+hit.word.weight;'
            '    tip.style.left=(px*scX)+"px";'
            '    tip.style.top=(py*scY)+"px";'
            '    tip.style.display="block";'
            '  }else if(tip){'
            '    tip.style.display="none";'
            '  }'
            '});'

            'canvas.addEventListener("mouseleave",function(){'
            '  draw(null);'
            '  if(tip)tip.style.display="none";'
            '});'

            # Click handler
            + (
                'canvas.addEventListener("click",function(e){'
                '  var rect=canvas.getBoundingClientRect();'
                '  var scaleX=W/rect.width,scaleY=H/rect.height;'
                '  var mx=(e.clientX-rect.left)*scaleX;'
                '  var my=(e.clientY-rect.top)*scaleY;'
                '  placedWords.forEach(function(item){'
                '    var p=item.pos;'
                '    if(mx>=p.x&&mx<=p.x+p.w&&my>=p.y-p.h&&my<=p.y){'
                '      var word=item.word.text;'
                '      var weight=item.word.weight;'
                '      ' + on_click +
                '    }'
                '  });'
                '});'
                if on_click else ""
            ) +
            '})()</script>'
        )


class Map(Widget):
    """
    Mapa interactivo con Leaflet + OpenStreetMap. Sin API key.

    Basico:
        Map(center=(-2.897, -79.004), zoom=14)   # Cuenca, Ecuador

    Con marcadores (dict o tupla):
        Map(markers=[
            {"lat": -2.897, "lon": -79.004, "title": "Cuenca", "icon": "GG"},
            (-0.220,  -78.512, "Quito"),
            (-2.897, -79.004, "Cuenca", "Popup HTML", "#6366f1", "CC"),
        ])

    Parametros:
        center          (lat, lon)    centro del mapa
        zoom            int           nivel de zoom 1-19 (default 13)
        height          int           alto en px (default 480)
        markers         list          marcadores como dict o tupla
        search          bool          barra de busqueda (default True)
        geolocation     bool          boton mi-ubicacion (default True)
        route           bool          linea entre markers (default False)
        route_color     str           color ruta (default "#6366f1")
        route_weight    int           grosor ruta px (default 4)
        tile            str           "osm"|"dark"|"topo"|"cycle" (default "osm")
        on_marker_click str           JS al hacer click en un marker

    Marcador completo (dict):
        {"lat": float, "lon": float,
         "title": str, "popup": str,
         "color": str, "icon": str}
    """

    _id_counter = 0

    _TILES = {
        "osm":   ("https://tile.openstreetmap.org/{z}/{x}/{y}.png",
                  "&copy; <a href='https://www.openstreetmap.org/copyright'>OpenStreetMap</a>"),
        "dark":  ("https://tiles.stadiamaps.com/tiles/alidade_smooth_dark/{z}/{x}/{y}{r}.png",
                  "&copy; Stadia Maps, &copy; OpenStreetMap"),
        "topo":  ("https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png",
                  "&copy; OpenTopoMap"),
        "cycle": ("https://{s}.tile-cyclosm.openstreetmap.fr/cyclosm/{z}/{x}/{y}.png",
                  "&copy; CyclOSM"),
    }

    def __init__(self, center=None, zoom=13, height=480,
                 markers=None, search=True, geolocation=True,
                 route=False, route_color="#6366f1", route_weight=4,
                 tile="osm", on_marker_click=None, **kwargs):
        self._props          = Widget._extract_props(kwargs)
        self.center          = center
        self.zoom            = zoom
        self.height          = height
        self.markers         = markers or []
        self.search          = search
        self.geolocation     = geolocation
        self.route           = route
        self.route_color     = route_color
        self.route_weight    = route_weight
        self.tile            = tile
        self.on_marker_click = on_marker_click
        Map._id_counter += 1
        self.uid = "map_" + str(Map._id_counter)

    def _normalize_markers(self):
        result = []
        for m in self.markers:
            if isinstance(m, dict):
                result.append(m)
            elif isinstance(m, (list, tuple)):
                d = {"lat": float(m[0]), "lon": float(m[1])}
                if len(m) > 2: d["title"]  = str(m[2])
                if len(m) > 3: d["popup"]  = str(m[3])
                if len(m) > 4: d["color"]  = str(m[4])
                if len(m) > 5: d["icon"]   = str(m[5])
                result.append(d)
        return result

    def render(self):
        import json as _j
        uid  = self.uid
        J    = _j.dumps
        mkrs = self._normalize_markers()
        h    = str(self.height)
        extra = self._resolve_props()

        tile_url, tile_attr = self._TILES.get(self.tile, self._TILES["osm"])
        if self.tile not in self._TILES:
            tile_url, tile_attr = self.tile, "&copy; Map contributors"

        # center
        if self.center:
            center_js = J(list(self.center))
        elif mkrs:
            lats = [m["lat"] for m in mkrs]
            lons = [m["lon"] for m in mkrs]
            center_js = J([sum(lats)/len(lats), sum(lons)/len(lons)])
        else:
            center_js = "[40.4168,-3.7038]"

        wrapper_style = (
            "position:relative;border-radius:12px;overflow:hidden;"
            "width:100%;height:" + h + "px;box-shadow:0 4px 24px rgba(0,0,0,0.12)"
        )
        if extra:
            wrapper_style += ";" + extra

        # Search bar HTML (over the map, top-center)
        search_html = ""
        if self.search:
            search_html = (
                '<div id="' + uid + '_sbar" style="'
                'position:absolute;top:10px;left:50%;transform:translateX(-50%);'
                'z-index:1000;display:flex;gap:0;width:min(340px,78%);'
                'box-shadow:0 2px 14px rgba(0,0,0,0.22);border-radius:9px;overflow:hidden">'
                '<input id="' + uid + '_q" type="text" placeholder="Buscar lugar..." '
                'autocomplete="off" '
                'style="flex:1;padding:9px 13px;border:none;font-size:14px;'
                'color:#111;background:#fff;outline:none;min-width:0"/>'
                '<button id="' + uid + '_sbtn" title="Buscar" '
                'style="padding:9px 14px;background:#6366f1;color:#fff;'
                'border:none;cursor:pointer;font-size:17px;line-height:1;'
                'flex-shrink:0;transition:background .2s" '
                'onmouseover="this.style.background=\'#4f46e5\'" '
                'onmouseout="this.style.background=\'#6366f1\'">&#128269;</button>'
                '</div>'
            )

        # Geolocation button (bottom-right, above Leaflet zoom)
        geo_html = ""
        if self.geolocation:
            geo_html = (
                '<button id="' + uid + '_geo" title="Mi ubicaci\u00f3n actual" '
                'style="position:absolute;bottom:86px;right:10px;z-index:1000;'
                'width:34px;height:34px;background:#fff;'
                'border:2px solid rgba(0,0,0,0.25);border-radius:4px;cursor:pointer;'
                'font-size:16px;display:flex;align-items:center;justify-content:center;'
                'box-shadow:0 1px 5px rgba(0,0,0,0.22);transition:background .15s" '
                'onmouseover="this.style.background=\'#f0f0f0\'" '
                'onmouseout="this.style.background=\'#fff\'">'
                '&#x1f3af;</button>'
            )

        # ── JavaScript ────────────────────────────────────────────────────────
        icon_fn = (
            "function _mkIcon(color,icon){"
            "var d=document.createElement('div');"
            "d.style.cssText='width:30px;height:30px;background:'+color+';'"
            "+'border-radius:50% 50% 50% 0;border:3px solid #fff;'"
            "+'box-shadow:0 2px 8px rgba(0,0,0,0.35);transform:rotate(-45deg);'"
            "+'display:flex;align-items:center;justify-content:center;box-sizing:border-box';"
            "if(icon){"
            "var s=document.createElement('span');"
            "s.style.cssText='transform:rotate(45deg);font-size:12px;line-height:1;user-select:none';"
            "s.textContent=icon;d.appendChild(s);}"
            "return d.outerHTML;}"
        )

        search_js = ""
        if self.search:
            search_js = (
                "var _sq=document.getElementById(" + J(uid+"_q") + ");"
                "var _sb=document.getElementById(" + J(uid+"_sbtn") + ");"
                "var _sm=null;"
                "function _doSearch(){"
                "  var q=_sq.value.trim();if(!q)return;"
                "  _sb.disabled=true;_sb.style.opacity='0.6';"
                # Use Nominatim — add User-Agent header is NOT sent by browsers (CORS), 
                # so we use the referer approach which is fine for client-side calls
                "  fetch('https://nominatim.openstreetmap.org/search'+"
                "    '?format=json&limit=1&addressdetails=1&q='+encodeURIComponent(q))"
                "  .then(function(r){return r.json();})"
                "  .then(function(data){"
                "    _sb.disabled=false;_sb.style.opacity='1';"
                "    if(!data||!data.length){"
                "      _sq.style.boxShadow='inset 0 0 0 2px #ef4444';"
                "      setTimeout(function(){_sq.style.boxShadow='';},2500);"
                "      return;"
                "    }"
                "    var r=data[0];"
                "    var lat=parseFloat(r.lat),lon=parseFloat(r.lon);"
                "    if(_sm){_map.removeLayer(_sm);}"
                "    var parts=r.display_name.split(',');"
                "    var name=parts.slice(0,Math.min(2,parts.length)).join(', ');"
                "    _sm=L.marker([lat,lon]).addTo(_map)"
                "      .bindPopup('<b>'+name+'</b><br><small style=\"color:#666\">'+(r.display_name||'')+'</small>')"
                "      .openPopup();"
                "    _map.flyTo([lat,lon],15,{animate:true,duration:1.0});"
                "  })"
                "  .catch(function(e){"
                "    _sb.disabled=false;_sb.style.opacity='1';"
                "    console.warn('Map search error:',e);"
                "  });"
                "}"
                "_sb.addEventListener('click',_doSearch);"
                "_sq.addEventListener('keydown',function(e){"
                "  if(e.key==='Enter'){e.preventDefault();_doSearch();}"
                "});"
            )

        geo_js = ""
        if self.geolocation:
            geo_js = (
                "var _gb=document.getElementById(" + J(uid+"_geo") + ");"
                "var _gLayers=[];"
                # Use Leaflet's built-in map.locate() — more reliable than raw geolocation API
                # It fires locationfound/locationerror events, handles everything cleanly.
                "_gb.addEventListener('click',function(){"
                "  _gb.textContent='\u23f3';_gb.disabled=true;"
                "  _map.locate({"
                "    setView:false,"
                "    enableHighAccuracy:true,"
                "    timeout:15000,"
                "    maximumAge:0"
                "  });"
                "});"
                "_map.on('locationfound',function(e){"
                "  _gb.textContent='\U0001f3af';_gb.disabled=false;"
                "  _gLayers.forEach(function(l){_map.removeLayer(l);});"
                "  _gLayers=[];"
                "  var lat=e.latlng.lat,lon=e.latlng.lng;"
                "  var acc=Math.round(e.accuracy);"
                # accuracy circle
                "  var circle=L.circle(e.latlng,{"
                "    radius:e.accuracy,"
                "    color:'#6366f1',fillColor:'#6366f1',"
                "    fillOpacity:0.08,weight:1.5,opacity:0.35"
                "  }).addTo(_map);"
                # position dot
                "  var dot=L.circleMarker(e.latlng,{"
                "    radius:8,fillColor:'#6366f1',color:'#fff',weight:3,fillOpacity:1"
                "  }).addTo(_map)"
                "   .bindPopup('<b>Tu ubicaci\u00f3n</b><br><small style=\"color:#888\">Precisi\u00f3n: ±'+acc+' m</small>')"
                "   .openPopup();"
                "  _gLayers.push(circle,dot);"
                "  _map.flyTo(e.latlng,16,{animate:true,duration:1.2});"
                "});"
                "_map.on('locationerror',function(e){"
                "  _gb.textContent='\U0001f3af';_gb.disabled=false;"
                "  var msg='No se pudo obtener tu ubicaci\u00f3n.';"
                "  if(e.message&&e.message.indexOf('denied')>=0)"
                "    msg='Permiso denegado. Habilita la ubicaci\u00f3n en tu navegador.';"
                "  else if(e.message&&e.message.indexOf('timeout')>=0)"
                "    msg='Tiempo de espera agotado. Intenta de nuevo.';"
                "  alert(msg);"
                "});"
            )

        click_fn = click_bind = ""
        if self.on_marker_click:
            click_fn   = "function _onMk(marker){" + self.on_marker_click + "}"
            click_bind = "_mk.on('click',function(){_onMk(m);});"

        route_js = ""
        if self.route:
            route_js = (
                "if(_lls.length>1){"
                "  L.polyline(_lls,{"
                "    color:" + J(self.route_color) + ","
                "    weight:" + str(self.route_weight) + ","
                "    opacity:0.85,lineJoin:'round',dashArray:null"
                "  }).addTo(_map);"
                "}"
            )

        autofit = ""
        if not self.center and len(mkrs) > 1:
            autofit = "if(_lls.length>1){_map.fitBounds(_lls,{padding:[48,48]});}"

        init_js = (
            "(function _im(){"
            "if(typeof L==='undefined'){setTimeout(_im,80);return;}"
            "var el=document.getElementById(" + J(uid) + ");"
            "if(!el||el._mi)return;"
            "el._mi=true;"
            # Explicitly set height in case CSS hasn't loaded
            "el.style.height='" + h + "px';"
            "var _map=L.map(el,{"
            "  zoomControl:true,"
            "  scrollWheelZoom:true,"
            "  attributionControl:true"
            "}).setView(" + center_js + "," + str(self.zoom) + ");"
            "L.tileLayer(" + J(tile_url) + ",{"
            "  attribution:" + J(tile_attr) + ","
            "  maxZoom:19,"
            "  crossOrigin:true"
            "}).addTo(_map);"
            + icon_fn
            + click_fn +
            "var _markers=" + J(mkrs) + ";"
            "var _lls=[];"
            "_markers.forEach(function(m){"
            "  var color=m.color||'#6366f1';"
            "  var icon=m.icon||'';"
            "  var _lIcon=L.divIcon({"
            "    html:_mkIcon(color,icon),"
            "    className:'',"
            "    iconSize:[30,30],"
            "    iconAnchor:[15,30],"
            "    popupAnchor:[0,-34]"
            "  });"
            "  var _mk=L.marker([m.lat,m.lon],{icon:_lIcon}).addTo(_map);"
            "  var _ph='';"
            "  if(m.title)_ph+='<b style=\"font-size:13px\">'+m.title+'</b>';"
            "  if(m.popup)_ph+=(m.title?'<br>':'')+m.popup;"
            "  if(_ph)_mk.bindPopup(_ph);"
            + click_bind +
            "  _lls.push([m.lat,m.lon]);"
            "});"
            + route_js
            + autofit
            + search_js
            + geo_js +
            "})();"
        )

        return (
            '<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" crossorigin=""/>'
            + '<div style="' + wrapper_style + '">'
            + '<div id="' + uid + '" style="width:100%;height:' + h + 'px"></div>'
            + search_html
            + geo_html
            + '</div>'
            + '<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" crossorigin=""></script>'
            + '<script>' + init_js + '</script>'
        )


class Timeline(Widget):
    """
    Widget de línea de tiempo vertical.

    Uso básico:
        Timeline(items=[
            TimelineItem(
                title="Lanzamiento v1.0",
                date="Enero 2024",
                description="Primera versión pública del framework.",
                icon="🚀",
                color="#6366f1",
            ),
            TimelineItem(
                title="Nuevo widget Map",
                date="Marzo 2024",
                description="Integración con Leaflet y OpenStreetMap.",
                image="/assets/map.png",
                icon="🗺️",
                color="#34d399",
            ),
        ])

    Opciones Timeline:
        items       list[TimelineItem]   elementos de la línea de tiempo
        line_color  str                  color de la línea vertical  (default: var(--border))
        alt         bool                 alterna lados izq/der en desktop (default: False)

    Opciones TimelineItem:
        title       str     título del evento              (requerido)
        date        str     fecha o período                (opcional)
        description str     texto descriptivo              (opcional)
        icon        str     emoji o texto para el nodo     (default: "●")
        image       str     URL de imagen                  (opcional)
        color       str     color del nodo y acento        (default: var(--accent))
        tag         str     etiqueta pequeña sobre título  (opcional)
    """

    def __init__(self, items=None, line_color=None, alt=False, **kwargs):
        self._props    = Widget._extract_props(kwargs)
        self.items     = items or []
        self.line_color = line_color or "var(--border)"
        self.alt       = alt

    def render(self):
        extra = self._resolve_props()
        line_color = self.line_color
        alt  = self.alt

        # Wrapper CSS
        wrapper_style = (
            f"position:relative;display:flex;flex-direction:column;gap:0;"
            f"{extra}"
        )

        # Línea vertical central (o izquierda si no es alt)
        line_left = "50%" if alt else "20px"
        line_html = (
            f'<div style="position:absolute;top:0;bottom:0;left:{line_left};'
            f'width:2px;background:{line_color};transform:translateX(-50%);z-index:0;'
            f'border-radius:2px"></div>'
        )

        items_html = ""
        for i, item in enumerate(self.items):
            if not isinstance(item, TimelineItem):
                continue
            items_html += item._render(index=i, alt=alt, line_color=line_color)

        return (
            f'<div style="{wrapper_style}">'
            + line_html
            + items_html
            + '</div>'
        )


class TimelineItem:
    """Elemento individual de un Timeline. Ver Timeline para documentación."""

    def __init__(self, title, date=None, description=None,
                 icon="●", image=None, color=None, tag=None):
        self.title       = title
        self.date        = date
        self.description = description
        self.icon        = icon
        self.image       = image
        self.color       = color or "var(--accent)"
        self.tag         = tag

    def _render(self, index=0, alt=False, line_color="var(--border)"):
        import json as _json
        color = self.color
        # En modo alt, los pares van a la derecha, impares a la izquierda
        go_right = (not alt) or (index % 2 == 0)

        # ── Nodo (círculo en la línea) ──────────────────────────────────────
        node_left = "50%" if alt else "20px"
        node_html = (
            f'<div style="position:absolute;left:{node_left};top:24px;'
            f'transform:translate(-50%,-0%);z-index:1;'
            f'width:36px;height:36px;border-radius:50%;'
            f'background:{color};'
            f'border:3px solid var(--bg);'
            f'box-shadow:0 0 0 2px {color},0 2px 8px rgba(0,0,0,0.15);'
            f'display:flex;align-items:center;justify-content:center;'
            f'font-size:16px;line-height:1;flex-shrink:0;">'
            f'{self.icon}</div>'
        )

        # ── Tarjeta de contenido ────────────────────────────────────────────
        if alt:
            if go_right:
                card_margin = "margin-left:calc(50% + 28px);margin-right:0;"
            else:
                card_margin = "margin-right:calc(50% + 28px);margin-left:0;text-align:right;"
        else:
            card_margin = "margin-left:52px;margin-right:0;"

        # Imagen — acepta string URL o widget Image (o cualquier Widget con .render())
        img_html = ""
        if self.image is not None:
            if hasattr(self.image, "render"):
                # Widget (Image, Container, etc.) — se renderiza directamente
                img_html = (
                    '<div style="margin-bottom:12px;border-radius:8px;overflow:hidden;">'
                    + self.image.render()
                    + '</div>'
                )
            else:
                # String URL — comportamiento por defecto
                img_html = (
                    f'<img src="{self.image}" alt="{self.title}" '
                    f'style="width:100%;max-height:180px;object-fit:cover;'
                    f'border-radius:8px;margin-bottom:12px;display:block;">'
                )

        # Tag
        tag_html = ""
        if self.tag:
            tag_html = (
                f'<span style="display:inline-block;font-size:10px;font-weight:700;'
                f'letter-spacing:1px;text-transform:uppercase;'
                f'color:{color};background:rgba(99,102,241,0.10);'
                f'padding:2px 8px;border-radius:999px;margin-bottom:6px;">'
                f'{self.tag}</span><br>'
            )

        # Fecha
        date_html = ""
        if self.date:
            date_html = (
                f'<span style="font-size:12px;font-weight:600;'
                f'color:{color};opacity:0.9;margin-bottom:4px;display:block;">'
                f'{self.date}</span>'
            )

        # Título
        title_html = (
            f'<div style="font-size:15px;font-weight:700;'
            f'color:var(--text);margin-bottom:6px;line-height:1.3;">'
            f'{self.title}</div>'
        )

        # Descripción
        desc_html = ""
        if self.description:
            desc_html = (
                f'<div style="font-size:13px;color:var(--text-muted);'
                f'line-height:1.6;">{self.description}</div>'
            )

        card_html = (
            f'<div style="{card_margin}flex:1;'
            f'background:var(--surface);border:1px solid var(--border);'
            f'border-radius:12px;padding:16px;'
            f'box-shadow:0 2px 8px rgba(0,0,0,0.06);'
            f'border-left:3px solid {color};">'
            + img_html
            + tag_html
            + date_html
            + title_html
            + desc_html
            + '</div>'
        )

        # ── Fila completa ───────────────────────────────────────────────────
        return (
            f'<div style="position:relative;display:flex;'
            f'align-items:flex-start;padding-bottom:24px;min-height:64px;">'
            + node_html
            + card_html
            + '</div>'
        )


# ══════════════════════════════════════════════════════════
# HERO
# ══════════════════════════════════════════════════════════

class Hero(Widget):
    """
    Hero banner de página completa con imagen/video de fondo, contenido
    centrado y soporte para overlay, badge, título, subtítulo, acciones
    y un widget de imagen/media lateral o de fondo.

    Uso básico:
        Hero(
            title="Construye rápido.",
            subtitle="Un framework Python con UI declarativa.",
        )

    Uso completo:
        Hero(
            badge=Badge("v2.0", background=Colors.indigo, color="white"),
            title=Heading("Construye rápido.", level=1,
                          style=[GradientText.aurora(), TextStyle(size=64, weight="800")]),
            subtitle=Paragraph("Un framework Python con UI declarativa estilo Flutter.",
                               style=TextStyle(size=20, color="var(--text-muted)")),
            actions=[
                Button("Empezar", href="/docs", background=Colors.indigo, color="white", radius=12),
                Button("GitHub",  href="https://github.com", radius=12),
            ],
            image=Image("/assets/screenshot.png", radius=16,
                        style="box-shadow:0 32px 80px rgba(0,0,0,0.4)"),
            background=MeshBackground.themed(),
            align="left",          # "center" | "left"
            layout="split",        # "split" | "centered"
            min_height=600,
            overlay=False,
        )

    Fondo con imagen URL:
        Hero(
            title="Bienvenido",
            bg_image="/assets/hero.jpg",
            overlay=True,
            overlay_color="rgba(0,0,0,0.55)",
        )

    Parámetros:
        title           str | Widget     título principal (str genera un <h1> por defecto)
        subtitle        str | Widget     subtítulo o descripción
        badge           str | Widget     etiqueta pequeña encima del título
        actions         list[Widget]     botones / links de acción
        image           str | Widget     imagen o widget media lateral / decorativa
        bg_image        str              URL de imagen de fondo CSS
        bg_video        str              URL de video de fondo (muted, loop, autoplay)
        background      str | StyleBase  fondo del hero (color, MeshBackground, CSS…)
        overlay         bool             capa semitransparente sobre bg_image/bg_video
        overlay_color   str              color del overlay (default: rgba(0,0,0,0.45))
        align           str              "center" | "left" | "right"
        layout          str              "centered" (solo contenido) |
                                         "split"    (contenido + imagen lado a lado)
        min_height      int              alto mínimo en px (default: 520)
        padding         int              padding interno (sobrescribible via kwargs)
    """

    def __init__(
        self,
        title=None,
        subtitle=None,
        badge=None,
        actions=None,
        actions_align=None,       # "center"|"left"|"right" — por defecto sigue a `align`
        actions_direction="row",  # "row" | "column"
        image=None,
        bg_image=None,
        bg_video=None,
        background=None,
        overlay=False,
        overlay_color="rgba(0,0,0,0.45)",
        align="center",
        layout=None,          # None = auto: "split" si hay image, "centered" si no
        min_height=520,
        **kwargs,
    ):
        self._props            = Widget._extract_props(kwargs)
        self.title             = title
        self.subtitle          = subtitle
        self.badge             = badge
        self.actions           = actions or []
        self.actions_align     = actions_align    # None = hereda de align
        self.actions_direction = actions_direction
        self.image             = image
        self.bg_image          = bg_image
        self.bg_video          = bg_video
        self.background        = background
        self.overlay           = overlay
        self.overlay_color     = overlay_color
        self.align             = align  # "center" | "left" | "right"
        self.layout            = layout or ("split" if image else "centered")
        self.min_height        = min_height

    # ── helpers ──────────────────────────────────────────────────────────────

    def _render_node(self, node, default_tag=None, default_style=""):
        """Renderiza un string como widget simple o llama .render() si es Widget."""
        if node is None:
            return ""
        if isinstance(node, Widget):
            return node.render()
        # string → envolver en tag por defecto si se indica
        if default_tag:
            return f'<{default_tag} style="{default_style}">{node}</{default_tag}>'
        return str(node)

    def _background_css(self):
        """Devuelve el CSS de fondo del wrapper externo."""
        from .styles import resolve_styles, StyleBase
        parts = []

        if self.bg_image:
            parts.append(
                f"background-image:url('{self.bg_image}');"
                f"background-size:cover;background-position:center;"
                f"background-repeat:no-repeat;"
            )
        elif self.background is not None:
            if isinstance(self.background, StyleBase):
                parts.append(resolve_styles(self.background))
            else:
                parts.append(str(self.background))
        else:
            parts.append("background:var(--bg-secondary);")

        return " ".join(parts)

    # ── render ────────────────────────────────────────────────────────────────

    def render(self):
        from .styles import resolve_styles

        min_h   = self.min_height
        align   = self.align       # center | left | right
        layout  = self.layout      # centered | split
        text_align = align if align != "right" else "right"

        # ── Fondo ─────────────────────────────────────────────────────────
        bg_css = self._background_css()

        # Props universales (padding, margin, width, etc.) sobre el wrapper
        extra_css = self._resolve_props(
            f"position:relative;min-height:{min_h}px;"
            f"display:flex;flex-direction:column;"
            f"justify-content:center;overflow:hidden;"
        )

        wrapper_open = f'<div style="{extra_css} {bg_css}">'
        wrapper_close = '</div>'

        # ── Video de fondo ────────────────────────────────────────────────
        video_html = ""
        if self.bg_video:
            video_html = (
                '<video autoplay muted loop playsinline '
                'style="position:absolute;top:0;left:0;width:100%;height:100%;'
                'object-fit:cover;z-index:0;">'
                f'<source src="{self.bg_video}">'
                '</video>'
            )

        # ── Overlay ───────────────────────────────────────────────────────
        overlay_html = ""
        if self.overlay and (self.bg_image or self.bg_video):
            overlay_html = (
                f'<div style="position:absolute;top:0;left:0;width:100%;height:100%;'
                f'background:{self.overlay_color};z-index:1;"></div>'
            )

        # ── Contenido ─────────────────────────────────────────────────────
        # Badge
        badge_html = ""
        if self.badge is not None:
            badge_html = (
                '<div style="margin-bottom:16px;">'
                + self._render_node(self.badge,
                    default_tag="span",
                    default_style=(
                        "display:inline-block;font-size:12px;font-weight:700;"
                        "letter-spacing:1px;text-transform:uppercase;"
                        "color:var(--accent);background:rgba(99,102,241,0.12);"
                        "padding:4px 12px;border-radius:999px;"
                    ))
                + '</div>'
            )

        # Título
        title_html = ""
        if self.title is not None:
            title_html = (
                '<div style="margin-bottom:12px;">'
                + self._render_node(self.title,
                    default_tag="h1",
                    default_style=(
                        "font-size:clamp(36px,6vw,72px);font-weight:800;"
                        "line-height:1.1;letter-spacing:-1px;"
                        "color:var(--text);margin:0;"
                    ))
                + '</div>'
            )

        # Subtítulo
        subtitle_html = ""
        if self.subtitle is not None:
            subtitle_html = (
                '<div style="margin-bottom:32px;">'
                + self._render_node(self.subtitle,
                    default_tag="p",
                    default_style=(
                        "font-size:clamp(16px,2vw,20px);line-height:1.6;"
                        "color:var(--text-muted);margin:0;"
                    ))
                + '</div>'
            )

        # Acciones
        actions_html = ""
        if self.actions:
            eff_align = self.actions_align or align
            justify_map = {"center": "center", "left": "flex-start", "right": "flex-end"}
            justify = justify_map.get(eff_align, "center")
            rendered = "".join(
                a.render() if isinstance(a, Widget) else str(a)
                for a in self.actions
            )
            if self.actions_direction == "column":
                align_items = justify_map.get(eff_align, "center")
                actions_html = (
                    f'<div style="display:flex;flex-direction:column;gap:12px;align-items:{align_items};">'
                    + rendered
                    + '</div>'
                )
            else:
                actions_html = (
                    f'<div style="display:flex;flex-wrap:wrap;gap:12px;justify-content:{justify};">'
                    + rendered
                    + '</div>'
                )

        # Columna de texto
        text_col = (
            f'<div style="display:flex;flex-direction:column;'
            f'align-items:{"center" if align=="center" else ("flex-end" if align=="right" else "flex-start")};'
            f'text-align:{text_align};">'
            + badge_html + title_html + subtitle_html + actions_html
            + '</div>'
        )

        # ── Imagen / media ────────────────────────────────────────────────
        image_html = ""
        if self.image is not None:
            rendered_img = self._render_node(
                self.image,
                default_tag="img",
                default_style="max-width:100%;height:auto;display:block;",
            )
            image_html = (
                '<div style="display:flex;align-items:center;justify-content:center;flex-shrink:0;">'
                + rendered_img
                + '</div>'
            )

        # ── Ensamblado según layout ───────────────────────────────────────
        if layout == "split" and image_html:
            # Split: texto izquierda, imagen derecha (o invertido con align=right)
            if align == "right":
                cols = image_html + text_col
            else:
                cols = text_col + image_html

            inner_html = (
                '<div style="'
                'display:grid;'
                'grid-template-columns:1fr 1fr;'
                'gap:48px;'
                'align-items:center;'
                'width:100%;max-width:1100px;'
                'margin:0 auto;'
                'padding:64px 32px;'
                '">'
                + cols
                + '</div>'
                # Responsive: en móvil apila verticalmente
                + '<style>'
                '@media(max-width:768px){'
                '.mn-hero-split{grid-template-columns:1fr!important;}'
                '}'
                '</style>'
            )
            # Re-do with class for responsive
            inner_html = (
                '<div class="mn-hero-split" style="'
                'display:grid;'
                'grid-template-columns:1fr 1fr;'
                'gap:48px;'
                'align-items:center;'
                'width:100%;max-width:1100px;'
                'margin:0 auto;'
                'padding:64px 32px;'
                '">'
                + cols
                + '</div>'
                + '<style>'
                '@media(max-width:768px){'
                '.mn-hero-split{grid-template-columns:1fr!important;}'
                '}'
                '</style>'
            )
        else:
            # Centered: todo centrado verticalmente y en columna
            inner_html = (
                '<div style="'
                'width:100%;max-width:800px;'
                'margin:0 auto;'
                'padding:80px 32px;'
                '">'
                + text_col
                + '</div>'
            )
            if image_html:
                # imagen debajo del texto en centered
                inner_html = (
                    '<div style="'
                    'width:100%;max-width:900px;'
                    'margin:0 auto;'
                    'padding:64px 32px 48px;'
                    'display:flex;flex-direction:column;align-items:center;gap:40px;'
                    '">'
                    + text_col
                    + image_html
                    + '</div>'
                )

        # contenido sobre overlay/video
        content_wrapper = (
            f'<div style="position:relative;z-index:2;width:100%;'
            f'display:flex;justify-content:center;">'
            + inner_html
            + '</div>'
        )

        return (
            wrapper_open
            + video_html
            + overlay_html
            + content_wrapper
            + wrapper_close
        )


# ══════════════════════════════════════════════════════════
# GALLERY
# ══════════════════════════════════════════════════════════

class GalleryItem:
    """
    Elemento individual de una Gallery.

    GalleryItem(
        src="/assets/foto.jpg",       # URL de la imagen (requerido)
        title="Título",               # mostrado en lightbox y tooltip
        description="Descripción",   # mostrado en lightbox
        alt="texto alternativo",
        url="https://...",            # si no hay lightbox, abre este URL
        url_target="_blank",          # "_self" | "_blank"
        span_cols=1,                  # cuántas columnas ocupa (masonry: ignorado)
        span_rows=1,                  # cuántas filas ocupa   (masonry: ignorado)
    )
    """
    def __init__(self, src, title=None, description=None, alt=None,
                 url=None, url_target="_blank", span_cols=1, span_rows=1):
        self.src         = src
        self.title       = title
        self.description = description
        self.alt         = alt or title or ""
        self.url         = url
        self.url_target  = url_target
        self.span_cols   = span_cols
        self.span_rows   = span_rows


class Gallery(Widget):
    """
    Galería de imágenes con lightbox opcional y soporte masonry.

    Uso básico:
        Gallery(items=[
            GalleryItem("/assets/a.jpg", title="Foto A", description="Desc A"),
            GalleryItem("/assets/b.jpg", title="Foto B"),
        ])

    Opciones:
        items        list[GalleryItem]  imágenes de la galería
        columns      int | str          columnas (int = fijo, "auto" = responsive)
                                        default: 3
        rows         int | None         filas máximas visibles (None = todas)
        gap          int                espacio entre items en px  (default: 8)
        masonry      bool               layout masonry (columnas de altura variable)
        img_height   int                alto de cada imagen en px  (default: 220)
                                        ignorado en masonry
        radius       int                radio de esquinas de las imágenes
        lightbox     bool               clic abre lightbox con título/descripción
                                        (default: True)
        object_fit   str                "cover"|"contain"|"fill"  (default: "cover")
    """

    _id_counter = 0

    def __init__(self, items=None, columns=3, rows=None, gap=8,
                 masonry=False, img_height=220, lightbox=True,
                 object_fit="cover", **kwargs):
        self._props      = Widget._extract_props(kwargs)
        self.items       = items or []
        self.columns     = columns
        self.rows        = rows
        self.gap         = gap
        self.masonry     = masonry
        self.img_height  = img_height
        self.lightbox    = lightbox
        self.object_fit  = object_fit
        Gallery._id_counter += 1
        self.uid = f"gal_{Gallery._id_counter}"

    def render(self):
        import json as _json
        uid      = self.uid
        gap      = self.gap
        items    = self.items
        masonry  = self.masonry
        lightbox = self.lightbox
        obj_fit  = self.object_fit
        img_h    = self.img_height
        radius_val = self._props.get("radius") or 0
        radius_css = f"border-radius:{radius_val}px;" if radius_val else ""

        # Resolver columnas
        if self.columns == "auto":
            cols_css = "repeat(auto-fill, minmax(200px, 1fr))"
        else:
            cols_css = f"repeat({self.columns}, 1fr)"

        # ── Estilos del wrapper ──────────────────────────────────────────
        if masonry:
            # CSS columns (multi-column layout) para efecto masonry real
            grid_style = (
                f"column-count:{self.columns};"
                f"column-gap:{gap}px;"
            )
            extra = self._resolve_props()
            wrapper_style = f"{grid_style}{extra}"
        else:
            row_constraint = f"grid-template-rows:repeat({self.rows}, {img_h}px);" if self.rows else ""
            grid_style = (
                f"display:grid;"
                f"grid-template-columns:{cols_css};"
                f"gap:{gap}px;"
                f"{row_constraint}"
            )
            if self.rows:
                grid_style += "overflow:hidden;"
            extra = self._resolve_props()
            wrapper_style = f"{grid_style}{extra}"

        # ── Items HTML ───────────────────────────────────────────────────
        items_html = ""
        lightbox_data = []  # [{src, title, description}]

        for idx, item in enumerate(items):
            if not isinstance(item, GalleryItem):
                continue

            item_radius = radius_css
            img_style = (
                f"width:100%;display:block;"
                f"object-fit:{obj_fit};"
                f"{item_radius}"
            )
            if not masonry:
                img_style += f"height:{img_h}px;"
            else:
                img_style += "height:auto;"

            # span cols/rows en grid (no masonry)
            span_style = ""
            if not masonry:
                if item.span_cols > 1:
                    span_style += f"grid-column:span {item.span_cols};"
                if item.span_rows > 1:
                    span_style += f"grid-row:span {item.span_rows};"

            # cursor
            cursor = "pointer" if (lightbox or item.url) else "default"

            # item wrapper
            if masonry:
                wrapper_item_style = f"break-inside:avoid;margin-bottom:{gap}px;{item_radius}overflow:hidden;cursor:{cursor};"
            else:
                wrapper_item_style = f"{span_style}{item_radius}overflow:hidden;cursor:{cursor};"

            # acción al hacer clic
            if lightbox:
                onclick = f"_galOpen('{uid}',{idx})"
            elif item.url:
                target = item.url_target or "_blank"
                onclick = f"window.open('{item.url}','{target}')"
            else:
                onclick = ""

            onclick_attr = f' onclick="{onclick}"' if onclick else ""

            # hover overlay con título
            overlay_html = ""
            if item.title:
                overlay_html = (
                    f'<div style="position:absolute;bottom:0;left:0;right:0;'
                    f'background:linear-gradient(transparent,rgba(0,0,0,0.65));'
                    f'color:#fff;font-size:13px;font-weight:600;'
                    f'padding:20px 10px 8px;opacity:0;transition:opacity .25s;"'
                    f' class="{uid}_caption">'
                    f'{item.title}</div>'
                )

            items_html += (
                f'<div style="position:relative;{wrapper_item_style}"{onclick_attr}'
                f' onmouseenter="this.querySelector(\'[class*=_caption]\')&&(this.querySelector(\'[class*=_caption]\').style.opacity=1)"'
                f' onmouseleave="this.querySelector(\'[class*=_caption]\')&&(this.querySelector(\'[class*=_caption]\').style.opacity=0)"'
                f'>'
                f'<img src="{item.src}" alt="{item.alt}" style="{img_style}" loading="lazy">'
                f'{overlay_html}'
                f'</div>'
            )

            lightbox_data.append({
                "src":   item.src,
                "title": item.title or "",
                "desc":  item.description or "",
            })

        # ── Lightbox HTML ────────────────────────────────────────────────
        lightbox_html = ""
        lightbox_js   = ""
        if lightbox:
            lightbox_html = (
                f'<div id="{uid}_lb" style="'
                f'display:none;position:fixed;top:0;left:0;width:100%;height:100%;'
                f'background:rgba(0,0,0,0.92);z-index:9999;'
                f'align-items:center;justify-content:center;flex-direction:column;">'

                # Botón cerrar
                f'<button onclick="_galClose(\'{uid}\')" style="'
                f'position:absolute;top:20px;right:24px;'
                f'background:none;border:none;color:#fff;font-size:28px;'
                f'cursor:pointer;line-height:1;z-index:1;">✕</button>'

                # Botón prev
                f'<button onclick="_galPrev(\'{uid}\')" style="'
                f'position:absolute;left:16px;top:50%;transform:translateY(-50%);'
                f'background:rgba(255,255,255,0.1);border:none;color:#fff;'
                f'font-size:28px;width:48px;height:48px;border-radius:50%;'
                f'cursor:pointer;backdrop-filter:blur(8px);">‹</button>'

                # Botón next
                f'<button onclick="_galNext(\'{uid}\')" style="'
                f'position:absolute;right:16px;top:50%;transform:translateY(-50%);'
                f'background:rgba(255,255,255,0.1);border:none;color:#fff;'
                f'font-size:28px;width:48px;height:48px;border-radius:50%;'
                f'cursor:pointer;backdrop-filter:blur(8px);">›</button>'

                # Imagen
                f'<img id="{uid}_lb_img" src="" alt="" style="'
                f'max-width:90vw;max-height:75vh;object-fit:contain;'
                f'border-radius:8px;box-shadow:0 8px 48px rgba(0,0,0,0.6);">'

                # Info
                f'<div id="{uid}_lb_info" style="'
                f'text-align:center;margin-top:16px;max-width:600px;padding:0 24px;">'
                f'<div id="{uid}_lb_title" style="'
                f'color:#fff;font-size:17px;font-weight:700;margin-bottom:6px;"></div>'
                f'<div id="{uid}_lb_desc" style="'
                f'color:rgba(255,255,255,0.7);font-size:14px;line-height:1.6;"></div>'
                f'</div>'

                # Contador
                f'<div id="{uid}_lb_count" style="'
                f'position:absolute;bottom:20px;left:50%;transform:translateX(-50%);'
                f'color:rgba(255,255,255,0.5);font-size:13px;"></div>'

                f'</div>'
            )

            data_js = _json.dumps(lightbox_data)
            lightbox_js = (
                f'(function(){{'
                f'var _d={data_js};'
                f'var _i=0;'
                f'function _show(n){{'
                f'  _i=(n+_d.length)%_d.length;'
                f'  var it=_d[_i];'
                f'  document.getElementById("{uid}_lb_img").src=it.src;'
                f'  document.getElementById("{uid}_lb_title").textContent=it.title;'
                f'  document.getElementById("{uid}_lb_desc").textContent=it.desc;'
                f'  document.getElementById("{uid}_lb_count").textContent=(_i+1)+" / "+_d.length;'
                f'  document.getElementById("{uid}_lb_info").style.display='
                f'    (it.title||it.desc)?"block":"none";'
                f'}}'
                f'window._galOpen=window._galOpen||{{}};'
                f'window._galClose=window._galClose||{{}};'
                f'window._galPrev=window._galPrev||{{}};'
                f'window._galNext=window._galNext||{{}};'
                f'window._galOpen["{uid}"]=function(idx){{'
                f'  _show(idx);'
                f'  var lb=document.getElementById("{uid}_lb");'
                f'  lb.style.display="flex";'
                f'  document.body.style.overflow="hidden";'
                f'}};'
                f'window._galClose["{uid}"]=function(){{'
                f'  document.getElementById("{uid}_lb").style.display="none";'
                f'  document.body.style.overflow="";'
                f'}};'
                f'window._galPrev["{uid}"]=function(){{_show(_i-1);}};'
                f'window._galNext["{uid}"]=function(){{_show(_i+1);}};'
                # Fix onclick attrs to use the registry
                f'document.addEventListener("DOMContentLoaded",function(){{'
                f'  document.querySelectorAll("[onclick]").forEach(function(el){{'
                f'    var oc=el.getAttribute("onclick");'
                f'    if(oc&&oc.includes("_galOpen(\'{uid}\'")){{'
                f'      var m=oc.match(/[0-9]+/);'
                f'      if(m)el.addEventListener("click",function(){{window._galOpen["{uid}"](+m[0]);}});'
                f'    }}'
                f'    if(oc&&oc.includes("_galClose(\'{uid}\'")){{'
                f'      el.addEventListener("click",function(){{window._galClose["{uid}"]();}});'
                f'    }}'
                f'    if(oc&&oc.includes("_galPrev(\'{uid}\'")){{'
                f'      el.addEventListener("click",function(){{window._galPrev["{uid}"]();}});'
                f'    }}'
                f'    if(oc&&oc.includes("_galNext(\'{uid}\'")){{'
                f'      el.addEventListener("click",function(){{window._galNext["{uid}"]();}});'
                f'    }}'
                f'  }});'
                # keyboard nav
                f'  document.addEventListener("keydown",function(e){{'
                f'    var lb=document.getElementById("{uid}_lb");'
                f'    if(!lb||lb.style.display==="none")return;'
                f'    if(e.key==="Escape")window._galClose["{uid}"]();'
                f'    if(e.key==="ArrowLeft")window._galPrev["{uid}"]();'
                f'    if(e.key==="ArrowRight")window._galNext["{uid}"]();'
                f'  }});'
                # close on backdrop click
                f'  document.getElementById("{uid}_lb").addEventListener("click",function(e){{'
                f'    if(e.target===this)window._galClose["{uid}"]();'
                f'  }});'
                f'}});'
                f'}})();'
            )

        # ── Responsive CSS ───────────────────────────────────────────────
        responsive_css = ""
        if not masonry and isinstance(self.columns, int) and self.columns > 2:
            responsive_css = (
                f'<style>'
                f'@media(max-width:640px){{'
                f'#{uid}{{grid-template-columns:repeat(2,1fr)!important;}}'
                f'}}'
                f'@media(max-width:400px){{'
                f'#{uid}{{grid-template-columns:1fr!important;}}'
                f'}}'
                f'</style>'
            )

        # ── Ensamblado ───────────────────────────────────────────────────
        html = (
            responsive_css
            + f'<div id="{uid}" style="{wrapper_style}">'
            + items_html
            + '</div>'
            + lightbox_html
            + (f'<script>{lightbox_js}</script>' if lightbox_js else "")
        )
        return self._wrap_url(html)


# ══════════════════════════════════════════════════════════
# CAROUSEL
# ══════════════════════════════════════════════════════════

class CarouselItem:
    """
    Elemento individual de un Carousel.

    CarouselItem(
        # Slide normal
        child=Card(...),          # cualquier widget como contenido
        # O bien imagen directa
        image="/assets/foto.jpg",
        title="Título del slide",
        subtitle="Subtítulo o descripción",
        # URL al hacer clic (si no hay lightbox u otro handler)
        url=None,
        url_target="_blank",
    )

    Modo brands — basta con:
        CarouselItem(image="/assets/logo.svg", title="Marca X", url="https://...")
    """
    def __init__(self, child=None, image=None, title=None, subtitle=None,
                 url=None, url_target="_blank"):
        self.child      = child
        self.image      = image
        self.title      = title
        self.subtitle   = subtitle
        self.url        = url
        self.url_target = url_target


class Carousel(Widget):
    """
    Carrusel de slides o cinta de marcas (logos).

    ── Modo slides ────────────────────────────────────────────────────────

        Carousel(
            items=[
                CarouselItem(image="/assets/a.jpg", title="Slide 1", subtitle="Desc"),
                CarouselItem(child=Card(children=[Heading("Hola")])),
                CarouselItem(image="/assets/b.jpg", title="Slide 2",
                             url="https://...", url_target="_blank"),
            ],
            mode="slides",
            visible=1,          # cuántos slides se ven a la vez
            gap=16,             # espacio entre slides
            loop=True,          # vuelve al inicio al llegar al final
            autoplay=0,         # 0 = desactivado; ms entre avance automático (ej: 3000)
            arrows=True,        # mostrar flechas prev/next
            dots=True,          # mostrar indicadores de posición
            img_height=320,     # alto de imagen en px (si el item usa image=)
            radius=12,          # radio de esquinas de cada slide
        )

    ── Modo brands ────────────────────────────────────────────────────────

        Carousel(
            items=[
                CarouselItem(image="/assets/logo-a.svg", title="Empresa A",
                             url="https://a.com"),
                CarouselItem(image="/assets/logo-b.png", title="Empresa B"),
            ],
            mode="brands",
            brand_height=48,        # alto de cada logo en px
            brand_filter="grayscale(100%) opacity(0.5)",  # filtro CSS por defecto
            brand_filter_hover=None,  # None = sin filtro al hover (color completo)
            brand_gap=64,           # espacio entre logos
            speed=30,               # segundos para completar un ciclo
            loop=True,              # siempre True en brands, loop infinito
        )

    Parámetros comunes:
        items          list[CarouselItem]
        mode           "slides" | "brands"
        loop           bool
        autoplay       int   ms (solo slides; 0 = desactivado)
        radius         int   border-radius de cada item
        url / url_target     prop universal del widget wrapper
    """

    _id_counter = 0

    def __init__(self, items=None, mode="slides",
                 # slides
                 visible=1, gap=16, loop=True, autoplay=0,
                 arrows=True, dots=True, img_height=320,
                 # brands
                 brand_height=48,
                 brand_filter="grayscale(100%) opacity(0.55)",
                 brand_filter_hover=None,
                 brand_gap=64, speed=30,
                 **kwargs):
        self._props        = Widget._extract_props(kwargs)
        self.items         = items or []
        self.mode          = mode
        self.visible       = visible
        self.gap           = gap
        self.loop          = loop
        self.autoplay      = autoplay
        self.arrows        = arrows
        self.dots          = dots
        self.img_height    = img_height
        self.brand_height  = brand_height
        self.brand_filter  = brand_filter
        self.brand_filter_hover = brand_filter_hover  # None = sin filtro (color)
        self.brand_gap     = brand_gap
        self.speed         = speed
        Carousel._id_counter += 1
        self.uid = f"car_{Carousel._id_counter}"

    # ── helpers ───────────────────────────────────────────────────────────

    def _render_item_content(self, item, radius_css):
        """Renderiza el contenido de un CarouselItem como HTML."""
        if item.child is not None:
            content = item.child.render() if isinstance(item.child, Widget) else str(item.child)
        elif item.image:
            img_style = (
                f"width:100%;height:{self.img_height}px;"
                f"object-fit:cover;display:block;{radius_css}"
            )
            content = f'<img src="{item.image}" alt="{item.title or ""}" style="{img_style}" loading="lazy">'
            if item.title or item.subtitle:
                overlay = (
                    f'<div style="padding:16px 20px;">'
                    + (f'<div style="font-size:16px;font-weight:700;color:var(--text);margin-bottom:4px;">{item.title}</div>' if item.title else "")
                    + (f'<div style="font-size:13px;color:var(--text-muted);line-height:1.5;">{item.subtitle}</div>' if item.subtitle else "")
                    + '</div>'
                )
                content += overlay
        else:
            content = ""
            if item.title:
                content += f'<div style="font-size:18px;font-weight:700;color:var(--text);margin-bottom:8px;">{item.title}</div>'
            if item.subtitle:
                content += f'<div style="font-size:14px;color:var(--text-muted);line-height:1.6;">{item.subtitle}</div>'

        # Wrap en <a> si tiene url
        if item.url:
            rel = ' rel="noopener noreferrer"' if item.url_target == "_blank" else ""
            content = (
                f'<a href="{item.url}" target="{item.url_target}"{rel}'
                f' style="display:block;text-decoration:none;">'
                + content + '</a>'
            )
        return content

    # ── render brands ─────────────────────────────────────────────────────

    def _render_brands(self):
        uid   = self.uid
        items = [i for i in self.items if isinstance(i, CarouselItem) and i.image]
        h     = self.brand_height
        gap   = self.brand_gap
        speed = self.speed
        flt   = self.brand_filter
        flt_h = self.brand_filter_hover if self.brand_filter_hover is not None else "none"
        extra = self._resolve_props()

        def _logo(item):
            img_s = (
                "height:" + str(h) + "px;width:auto;max-width:180px;"
                + "object-fit:contain;display:block;"
                + "filter:" + flt + ";transition:filter .35s ease;"
            )
            me  = "onmouseenter=\"this.querySelector('img').style.filter='" + flt_h + "'\""
            ml  = "onmouseleave=\"this.querySelector('img').style.filter='" + flt + "'\""
            hjs = " " + me + " " + ml
            img = '<img src="' + item.image + '" alt="' + (item.title or "") + '" style="' + img_s + '">'
            s   = "display:inline-flex;align-items:center;flex-shrink:0;padding:0 " + str(gap // 2) + "px;"
            if item.url:
                rel = ' rel="noopener noreferrer"' if item.url_target == "_blank" else ""
                return ('<a href="' + item.url + '" target="' + item.url_target + '"' + rel
                        + ' style="' + s + 'text-decoration:none;"' + hjs + '>' + img + '</a>')
            return '<div style="' + s + '"' + hjs + '>' + img + '</div>'

        logos = "".join(_logo(i) for i in items)
        wrapper_style = "width:100%;overflow:hidden;position:relative;" + extra

        fade = (
            '<div style="position:absolute;top:0;left:0;bottom:0;width:60px;'
            + 'background:linear-gradient(to right,var(--bg,#0d1117),transparent);'
            + 'z-index:2;pointer-events:none;"></div>'
            + '<div style="position:absolute;top:0;right:0;bottom:0;width:60px;'
            + 'background:linear-gradient(to left,var(--bg,#0d1117),transparent);'
            + 'z-index:2;pointer-events:none;"></div>'
        )

        # JS: starts with g1 only, then clones groups until track fills 2x wrapper width.
        # rAF resets pos when it reaches g1.offsetWidth => seamless loop regardless of count.
        js = (
            '<script>(function(){'
            + 'var uid="' + uid + '";'
            + 'var secs=' + str(speed) + ';'
            + 'var track=document.getElementById(uid+"_track");'
            + 'var g1=document.getElementById(uid+"_g1");'
            + 'if(!track||!g1)return;'
            + 'var paused=false,pos=0,last=null,w=0;'
            + 'function fill(){'
            +   'w=g1.offsetWidth;'
            +   'if(w<4)return;'
            +   'var old=track.querySelectorAll("[data-clone]");'
            +   'for(var i=0;i<old.length;i++)old[i].remove();'
            +   'var needed=(track.parentElement?track.parentElement.offsetWidth:800)*2+w;'
            +   'var total=w;'
            +   'while(total<needed){'
            +     'var c=g1.cloneNode(true);'
            +     'c.removeAttribute("id");'
            +     'c.setAttribute("aria-hidden","true");'
            +     'c.setAttribute("data-clone","1");'
            +     'track.appendChild(c);'
            +     'total+=w;'
            +   '}'
            + '}'
            + 'function step(ts){'
            +   'if(!last)last=ts;'
            +   'var dt=Math.min(ts-last,100);'
            +   'if(!paused&&w>0){'
            +     'pos+=dt/1000*(w/secs);'
            +     'if(pos>=w)pos-=w;'
            +     'track.style.transform="translateX(-"+pos.toFixed(2)+"px)";'
            +   '}'
            +   'last=ts;'
            +   'requestAnimationFrame(step);'
            + '}'
            + 'var wrap=document.getElementById(uid);'
            + 'if(wrap){'
            +   'wrap.addEventListener("mouseenter",function(){paused=true;});'
            +   'wrap.addEventListener("mouseleave",function(){paused=false;last=null;});'
            + '}'
            + 'function start(){fill();requestAnimationFrame(step);}'
            + 'if(document.readyState==="loading"){'
            +   'document.addEventListener("DOMContentLoaded",start);'
            + '}else{start();}'
            + 'window.addEventListener("load",function(){fill();});'
            + 'window.addEventListener("resize",function(){pos=0;fill();});'
            + '})();</script>'
        )

        html = (
            '<div id="' + uid + '" style="' + wrapper_style + '">'
            + fade
            + '<div id="' + uid + '_track" style="display:flex;align-items:center;padding:20px 0;will-change:transform;">'
            + '<div id="' + uid + '_g1" style="display:flex;align-items:center;flex-shrink:0;">'
            + logos + '</div>'
            + '</div></div>'
            + js
        )
        return self._wrap_url(html)


        # ── render slides ─────────────────────────────────────────────────────

    def _render_slides(self):
        uid      = self.uid
        items    = [i for i in self.items if isinstance(i, CarouselItem)]
        n        = len(items)
        gap      = self.gap
        visible  = self.visible
        loop     = self.loop
        autoplay = self.autoplay
        arrows   = self.arrows
        dots     = self.dots
        radius_val = self._props.get("radius") or 0
        radius_css = "border-radius:" + str(radius_val) + "px;" if radius_val else ""
        extra    = self._resolve_props()

        # Número de posiciones navegables
        positions = max(n - visible + 1, 1)  # dots count = positions

        slide_width = "calc((100% - " + str(gap * (visible - 1)) + "px) / " + str(visible) + ")"

        # Slides normales
        slides_html = ""
        for idx, item in enumerate(items):
            content_s = self._render_item_content(item, radius_css)
            slides_html += (
                '<div id="' + uid + '_s' + str(idx) + '" style="'
                'flex-shrink:0;width:' + slide_width + ';'
                'background:var(--surface);'
                'border:1px solid var(--border);'
                'overflow:hidden;' + radius_css + '">'
                + content_s + '</div>'
            )

        # Si loop=True, clonamos los primeros `visible` slides al final
        # y los últimos `visible` al inicio → infinite clone technique
        clones_after  = ""
        clones_before = ""
        if loop:
            for idx in range(min(visible, n)):
                content_s = self._render_item_content(items[idx], radius_css)
                clones_after += (
                    '<div data-clone="after" style="'
                    'flex-shrink:0;width:' + slide_width + ';'
                    'background:var(--surface);'
                    'border:1px solid var(--border);'
                    'overflow:hidden;' + radius_css + '">'
                    + content_s + '</div>'
                )
            for idx in range(n - min(visible, n), n):
                content_s = self._render_item_content(items[idx], radius_css)
                clones_before += (
                    '<div data-clone="before" style="'
                    'flex-shrink:0;width:' + slide_width + ';'
                    'background:var(--surface);'
                    'border:1px solid var(--border);'
                    'overflow:hidden;' + radius_css + '">'
                    + content_s + '</div>'
                )

        # Dots: one per navigable position
        dots_html = ""
        if dots and positions > 1:
            dot_items = ""
            for i in range(positions):
                active = "var(--accent)" if i == 0 else "var(--border)"
                scale  = "transform:scale(1.3);" if i == 0 else ""
                dot_items += (
                    '<button id="' + uid + '_dot' + str(i) + '" style="'
                    'width:8px;height:8px;border-radius:50%;border:none;cursor:pointer;'
                    'transition:all .25s;padding:0;background:' + active + ';' + scale + '"></button>'
                )
            dots_html = (
                '<div style="display:flex;justify-content:center;gap:8px;margin-top:16px;">'
                + dot_items + '</div>'
            )

        # Arrows — fuera del viewport con overflow:hidden, dentro del wrapper con overflow:visible
        btn_base = (
            "position:absolute;top:50%;transform:translateY(-50%);"
            "background:var(--surface);border:1px solid var(--border);"
            "color:var(--text);width:40px;height:40px;border-radius:50%;"
            "cursor:pointer;font-size:22px;display:flex;align-items:center;"
            "justify-content:center;z-index:4;transition:background .2s;"
            "box-shadow:0 2px 12px rgba(0,0,0,0.2);"
        )
        arrows_html = ""
        if arrows:
            arrows_html = (
                '<button id="' + uid + '_prev" style="' + btn_base + 'left:-20px;">&#8249;</button>'
                '<button id="' + uid + '_next" style="' + btn_base + 'right:-20px;">&#8250;</button>'
            )

        # Layout: wrapper has overflow:visible so arrows aren't clipped
        # viewport clips the slides track
        wrapper_style = "position:relative;overflow:visible;" + extra
        track_style   = "display:flex;gap:" + str(gap) + "px;will-change:transform;"

        html = (
            '<div style="' + wrapper_style + '">'
            + '<div id="' + uid + '_viewport" style="overflow:hidden;position:relative;">'
            + '<div id="' + uid + '_track" style="' + track_style + '">'
            + (clones_before if loop else "")
            + slides_html
            + (clones_after if loop else "")
            + '</div>'
            + '</div>'
            + arrows_html
            + dots_html
            + '</div>'
        )

        # JS — offset calculation accounts for clone padding when loop=True
        clone_offset = "vis" if loop else "0"

        js = (
            ';(function(){'
            'if(!window._car)window._car={};'
            'var uid="' + uid + '",n=' + str(n) + ',vis=' + str(visible) + ',gap=' + str(gap) + ','
            'loop=' + ('true' if loop else 'false') + ','
            'positions=' + str(positions) + ','
            'autoplay=' + str(autoplay) + ';'
            'var cur=0;'  # cur = index into real slides (0..n-1)
            'var transitioning=false;'
            'var track=document.getElementById(uid+"_track");'
            'var vp=document.getElementById(uid+"_viewport");'

            'function _sw(){'
            '  return vp?(vp.offsetWidth-gap*(vis-1))/vis:0;'
            '}'

            # offset: if loop, track starts with `vis` clone slides before real slides
            'function _offset(idx){'
            '  var sw=_sw();'
            '  var base=loop?vis:0;'
            '  return (base+idx)*(sw+gap);'
            '}'

            'function _updateDots(){'
            '  var disp=((cur%n)+n)%n;'
            '  var dotIdx=Math.min(disp,positions-1);'
            '  for(var i=0;i<positions;i++){'
            '    var d=document.getElementById(uid+"_dot"+i);'
            '    if(d){'
            '      var active=i===dotIdx;'
            '      d.style.background=active?"var(--accent)":"var(--border)";'
            '      d.style.transform=active?"scale(1.3)":"scale(1)";'
            '    }'
            '  }'
            '}'

            'function _moveTo(idx,animate){'
            '  track.style.transition=animate?"transform .4s cubic-bezier(.4,0,.2,1)":"none";'
            '  track.style.transform="translateX(-"+_offset(idx)+"px)";'
            '}'

            'function _go(idx){'
            '  cur=((idx%n)+n)%n;'
            '  _moveTo(cur,true);'
            '  _updateDots();'
            '}'

            # After transition ends, if loop, silently jump when at clone boundary
            'track.addEventListener("transitionend",function(){'
            '  if(!loop){transitioning=false;return;}'
            '  if(cur>=n){cur=cur%n;_moveTo(cur,false);}'
            '  else if(cur<0){cur=((cur%n)+n)%n;_moveTo(cur,false);}'
            '  _updateDots();'
            '  transitioning=false;'
            '});'

            'window._car[uid]={'
            '  go:function(i){_go(i);},'
            '  next:function(){'
            '    if(transitioning)return;'
            '    if(!loop&&cur>=n-vis)return;'
            '    transitioning=true;'
            '    cur=cur+1;'
            '    _moveTo(cur,true);'
            '    _updateDots();'
            '  },'
            '  prev:function(){'
            '    if(transitioning)return;'
            '    if(!loop&&cur<=0)return;'
            '    transitioning=true;'
            '    cur=cur-1;'
            '    _moveTo(cur,true);'
            '    _updateDots();'
            '  }'
            '};'

            # Wire arrows
            'var bp=document.getElementById(uid+"_prev");'
            'var bn=document.getElementById(uid+"_next");'
            'if(bp)bp.addEventListener("click",function(){window._car[uid].prev();});'
            'if(bn)bn.addEventListener("click",function(){window._car[uid].next();});'
            # Wire dots
            '(function(){'
            '  for(var i=0;i<positions;i++){'
            '    (function(idx){'
            '      var d=document.getElementById(uid+"_dot"+idx);'
            '      if(d)d.addEventListener("click",function(){_go(idx);});'
            '    })(i);'
            '  }'
            '})();'

            # Keyboard
            'var root=document.getElementById(uid+"_viewport");'
            'if(root)root.addEventListener("keydown",function(e){'
            '  if(e.key==="ArrowLeft")window._car[uid].prev();'
            '  if(e.key==="ArrowRight")window._car[uid].next();'
            '});'

            # Swipe
            'var tx=0;'
            'if(vp){'
            '  vp.addEventListener("touchstart",function(e){tx=e.touches[0].clientX;},{passive:true});'
            '  vp.addEventListener("touchend",function(e){'
            '    var dx=tx-e.changedTouches[0].clientX;'
            '    if(Math.abs(dx)>40){if(dx>0)window._car[uid].next();else window._car[uid].prev();}'
            '  });'
            '}'

            # Autoplay
            'if(autoplay>0){'
            '  var t=setInterval(function(){window._car[uid].next();},autoplay);'
            '  if(vp){'
            '    vp.addEventListener("mouseenter",function(){clearInterval(t);});'
            '    vp.addEventListener("mouseleave",function(){'
            '      t=setInterval(function(){window._car[uid].next();},autoplay);'
            '    });'
            '  }'
            '}'

            # Init position (accounting for clones at start)
            'function _init(){'
            '  _moveTo(0,false);'
            '  _updateDots();'
            '}'
            'if(document.readyState==="loading"){'
            '  document.addEventListener("DOMContentLoaded",_init);'
            '} else {_init();}'
            'window.addEventListener("resize",function(){_moveTo(cur,false);});'
            '})();'
        )

        return self._wrap_url(html + '<script>' + js + '</script>')


    # ── render ────────────────────────────────────────────────────────────

    def render(self):
        if self.mode == "brands":
            return self._render_brands()
        return self._render_slides()


# == COOKIE BANNER ==


class CookieCategory:
    """
    Categoria individual de cookies para el panel de personalizacion.

        CookieCategory(
            id="analytics",
            label="Analiticas",
            description="Nos ayudan a entender como usas el sitio.",
            default=False,
            required=False,
        )
    """
    def __init__(self, id, label, description="", default=False, required=False):
        self.id          = id
        self.label       = label
        self.description = description
        self.default     = default
        self.required    = required


class CookieBanner(Widget):
    """
    Banner de cookies GDPR con persistencia en localStorage.

    - Si el usuario ya decidio, el banner NO aparece.
    - En modo incognito, localStorage esta vacio -> siempre aparece.
    - Guarda la decision bajo storage_key.
    - Opciones: Aceptar todo / Rechazar todo / Personalizar (categorias).

    Uso basico:
        CookieBanner(
            title="Usamos cookies",
            description="Este sitio usa cookies para mejorar tu experiencia.",
        )

    Con categorias:
        CookieBanner(
            categories=[
                CookieCategory("necessary", "Necesarias",
                               "Requeridas para el funcionamiento.", required=True),
                CookieCategory("analytics", "Analiticas",
                               "Mejoran el sitio.", default=False),
                CookieCategory("marketing", "Marketing",
                               "Anuncios relevantes.", default=False),
            ],
        )

    Parametros:
        title           str     Titulo del banner
        description     str     Texto principal
        categories      list    Lista de CookieCategory
        show_customize  bool    Mostrar boton Personalizar
        position        str     "bottom" | "top" | "modal"
        accept_label    str     Texto boton aceptar
        reject_label    str     Texto boton rechazar
        customize_label str     Texto boton personalizar
        save_label      str     Texto boton guardar
        storage_key     str     Clave localStorage
        on_accept       str     JS ejecutado al aceptar (recibe consent object)
        on_reject       str     JS ejecutado al rechazar
        privacy_url     str     URL politica de privacidad
        privacy_label   str     Texto del enlace
        blur_backdrop   bool    Blur en modo modal
    """

    def __init__(self,
                 title="Usamos cookies",
                 description="Este sitio usa cookies para mejorar tu experiencia y analizar el trafico.",
                 categories=None,
                 show_customize=None,
                 position="bottom",
                 accept_label="Aceptar todo",
                 reject_label="Rechazar todo",
                 customize_label="Personalizar",
                 save_label="Guardar preferencias",
                 storage_key="martin_cookie_consent",
                 on_accept="",
                 on_reject="",
                 privacy_url="",
                 privacy_label="Politica de privacidad",
                 blur_backdrop=True,
                 **kwargs):
        self._props          = Widget._extract_props(kwargs)
        self.title           = title
        self.description     = description
        self.categories      = categories or []
        self.show_customize  = show_customize if show_customize is not None else bool(self.categories)
        self.position        = position
        self.accept_label    = accept_label
        self.reject_label    = reject_label
        self.customize_label = customize_label
        self.save_label      = save_label
        self.storage_key     = storage_key
        self.on_accept       = on_accept
        self.on_reject       = on_reject
        self.privacy_url     = privacy_url
        self.privacy_label   = privacy_label
        self.blur_backdrop   = blur_backdrop

    def render(self):
        import json as _json
        # Use object id for unique uid per instance
        uid      = "ckb" + str(abs(id(self)))[-7:]
        cats     = self.categories
        key      = self.storage_key
        pos      = self.position
        is_modal = pos == "modal"

        # ── Category toggle rows ─────────────────────────────────────────
        cats_html = ""
        if cats:
            rows = ""
            for cat in cats:
                cid     = uid + "c" + cat.id
                checked = cat.default or cat.required
                req_badge = (
                    '<span style="font-size:10px;background:var(--accent);color:#fff;'
                    'padding:1px 6px;border-radius:999px;margin-left:6px;font-weight:600;">'
                    'Requerida</span>'
                ) if cat.required else ""
                desc_html = (
                    '<div style="font-size:12px;color:var(--text-muted);margin-top:2px;'
                    'line-height:1.5;">' + cat.description + '</div>'
                ) if cat.description else ""
                track_bg   = "var(--accent)" if checked else "var(--border)"
                thumb_left = "20px" if checked else "3px"
                cursor     = "default" if cat.required else "pointer"
                toggle_fn  = "" if cat.required else uid + "T('" + cat.id + "')"

                rows += (
                    '<div style="display:flex;align-items:flex-start;gap:12px;'
                    'padding:12px 0;border-bottom:1px solid var(--border);">'
                    '<div style="flex:1;">'
                    '<div style="font-size:14px;font-weight:600;color:var(--text);'
                    'display:flex;align-items:center;">'
                    + cat.label + req_badge +
                    '</div>'
                    + desc_html +
                    '</div>'
                    # Toggle switch
                    '<div style="position:relative;flex-shrink:0;margin-top:2px;">'
                    '<input type="checkbox" id="' + cid + '" '
                    + ('checked ' if checked else '')
                    + ('disabled ' if cat.required else '')
                    + 'data-cat="' + cat.id + '" '
                    'style="opacity:0;position:absolute;width:0;height:0;">'
                    '<div onclick="' + toggle_fn + '" '
                    'style="width:42px;height:24px;border-radius:12px;cursor:' + cursor + ';'
                    'transition:background .25s;background:' + track_bg + ';'
                    'position:relative;" id="' + cid + 'T">'
                    '<div id="' + cid + 'K" style="position:absolute;top:3px;'
                    'left:' + thumb_left + ';width:18px;height:18px;border-radius:50%;'
                    'background:#fff;transition:left .25s;"></div>'
                    '</div>'
                    '</div>'
                    '</div>'
                )

            cats_html = (
                '<div id="' + uid + 'P" style="display:none;margin-top:16px;'
                'border-top:1px solid var(--border);padding-top:8px;">'
                + rows +
                '</div>'
            )

        # ── Privacy link ─────────────────────────────────────────────────
        privacy_html = ""
        if self.privacy_url:
            privacy_html = (
                ' <a href="' + self.privacy_url + '" target="_blank" '
                'rel="noopener noreferrer" '
                'style="color:var(--accent);text-decoration:underline;">'
                + self.privacy_label + '</a>'
            )

        # ── Position / layout ─────────────────────────────────────────────
        if is_modal:
            bdr = "backdrop-filter:blur(4px);" if self.blur_backdrop else ""
            outer_style = (
                "position:fixed;top:0;left:0;width:100%;height:100%;z-index:99998;"
                "background:rgba(0,0,0,0.55);" + bdr +
                "display:flex;align-items:center;justify-content:center;"
            )
            box_style = (
                "background:var(--surface);border:1px solid var(--border);"
                "border-radius:16px;padding:28px 32px;max-width:500px;width:90%;"
                "box-shadow:0 24px 64px rgba(0,0,0,0.4);max-height:85vh;overflow-y:auto;"
            )
            outer_open  = '<div id="' + uid + '" style="' + outer_style + '">'
            inner_open  = '<div style="' + box_style + '">'
            inner_close = '</div>'
            outer_close = '</div>'
        else:
            edge = "bottom:0;border-top:1px solid var(--border);" if pos != "top" else "top:0;border-bottom:1px solid var(--border);"
            outer_style = (
                "position:fixed;" + edge + "left:0;right:0;z-index:99998;"
                "background:var(--surface);padding:20px 32px;"
                "box-shadow:0 -4px 24px rgba(0,0,0,0.12);"
            )
            outer_open  = '<div id="' + uid + '" style="' + outer_style + '">'
            inner_open  = ""
            inner_close = ""
            outer_close = "</div>"

        # ── Buttons ───────────────────────────────────────────────────────
        btn_style_primary = (
            "background:var(--accent);color:#fff;border:none;padding:9px 20px;"
            "border-radius:8px;font-size:14px;font-weight:700;cursor:pointer;"
            "transition:opacity .2s;white-space:nowrap;"
        )
        btn_style_secondary = (
            "background:transparent;color:var(--text-muted);"
            "border:1px solid var(--border);padding:9px 20px;"
            "border-radius:8px;font-size:14px;font-weight:600;cursor:pointer;"
            "transition:border-color .2s;white-space:nowrap;"
        )
        btn_style_outline = (
            "background:transparent;color:var(--accent);"
            "border:1px solid var(--accent);padding:9px 20px;"
            "border-radius:8px;font-size:14px;font-weight:600;cursor:pointer;"
            "white-space:nowrap;"
        )

        btns = (
            '<div style="display:flex;flex-wrap:wrap;gap:10px;margin-top:16px;align-items:center;">'
            '<button onclick="' + uid + 'A()" style="' + btn_style_primary + '">'
            + self.accept_label + '</button>'
            '<button onclick="' + uid + 'R()" style="' + btn_style_secondary + '">'
            + self.reject_label + '</button>'
        )
        if self.show_customize and cats:
            btns += (
                '<button onclick="' + uid + 'C()" style="' + btn_style_outline + '">'
                + self.customize_label + '</button>'
                '<button onclick="' + uid + 'S()" id="' + uid + 'SB" '
                'style="display:none;' + btn_style_primary + '">'
                + self.save_label + '</button>'
            )
        btns += '</div>'

        # ── Content ───────────────────────────────────────────────────────
        layout = "column" if is_modal else "row"
        content_html = (
            '<div style="display:flex;flex-direction:' + layout + ';gap:' + ("16px" if is_modal else "32px") + ';'
            'flex-wrap:wrap;align-items:' + ("flex-start" if is_modal else "center") + ';">'
            '<div style="flex:1;min-width:220px;">'
            '<div style="font-size:15px;font-weight:700;color:var(--text);margin-bottom:6px;">'
            + self.title + '</div>'
            '<div style="font-size:13px;color:var(--text-muted);line-height:1.6;">'
            + self.description + privacy_html + '</div>'
            + cats_html +
            '</div>'
            + btns +
            '</div>'
        )

        banner_html = outer_open + inner_open + content_html + inner_close + outer_close

        # ── JS ────────────────────────────────────────────────────────────
        cats_ids      = [c.id for c in cats]
        cats_required = [c.id for c in cats if c.required]
        on_accept_js  = self.on_accept
        on_reject_js  = self.on_reject

        js = (
            '<script>(function(){'
            'var K="' + key + '",uid="' + uid + '";'
            'var cats=' + _json.dumps(cats_ids) + ';'
            'var req=' + _json.dumps(cats_required) + ';'

            'function hide(){'
            '  var el=document.getElementById(uid);'
            '  if(el)el.style.display="none";'
            '}'
            'function show(){'
            '  var el=document.getElementById(uid);'
            '  if(el)el.style.display="' + ("flex" if is_modal else "block") + '";'
            '}'
            'function save(consent){'
            '  try{localStorage.setItem(K,JSON.stringify(consent));}catch(e){}'
            '}'
            'function decided(){'
            '  try{return localStorage.getItem(K)!==null;}catch(e){return false;}'
            '}'

            # Accept all
            'window.' + uid + 'A=function(){'
            '  var c={decided:true,all:true,cats:{}};'
            '  for(var i=0;i<cats.length;i++)c.cats[cats[i]]=true;'
            '  save(c);hide();'
            + (on_accept_js + '(c);' if on_accept_js else '') +
            '};'

            # Reject all (keep required)
            'window.' + uid + 'R=function(){'
            '  var c={decided:true,all:false,cats:{}};'
            '  for(var i=0;i<cats.length;i++)c.cats[cats[i]]=req.indexOf(cats[i])>=0;'
            '  save(c);hide();'
            + (on_reject_js + '(c);' if on_reject_js else '') +
            '};'

            # Save custom
            'window.' + uid + 'S=function(){'
            '  var c={decided:true,all:false,cats:{}};'
            '  for(var i=0;i<cats.length;i++){'
            '    var el=document.getElementById(uid+"c"+cats[i]);'
            '    c.cats[cats[i]]=el?el.checked:req.indexOf(cats[i])>=0;'
            '  }'
            '  save(c);hide();'
            + (on_accept_js + '(c);' if on_accept_js else '') +
            '};'

            # Toggle customize panel
            'window.' + uid + 'C=function(){'
            '  var p=document.getElementById(uid+"P");'
            '  var sb=document.getElementById(uid+"SB");'
            '  if(!p)return;'
            '  var open=p.style.display!=="none";'
            '  p.style.display=open?"none":"block";'
            '  if(sb)sb.style.display=open?"none":"inline-block";'
            '};'

            # Toggle individual category
            'window.' + uid + 'T=function(catId){'
            '  var el=document.getElementById(uid+"c"+catId);'
            '  var track=document.getElementById(uid+"c"+catId+"T");'
            '  var thumb=document.getElementById(uid+"c"+catId+"K");'
            '  if(!el||el.disabled)return;'
            '  el.checked=!el.checked;'
            '  if(track)track.style.background=el.checked?"var(--accent)":"var(--border)";'
            '  if(thumb)thumb.style.left=el.checked?"20px":"3px";'
            '};'

            # Init
            'function init(){'
            '  if(decided())hide();else show();'
            '}'
            'if(document.readyState==="loading"){'
            '  document.addEventListener("DOMContentLoaded",init);'
            '}else{init();}'

            # Backdrop click closes (modal only) — reject
            + (
                'var bd=document.getElementById(uid);'
                'if(bd)bd.addEventListener("click",function(e){'
                'if(e.target===this)window.' + uid + 'R();});'
                if is_modal else ""
            ) +

            '})();</script>'
        )

        return banner_html + js


class AccordionItem:
    """
    Elemento individual de un Accordion.

        AccordionItem(
            title="¿Cómo funciona?",
            child=Paragraph("El sistema funciona así..."),
            # o bien:
            content="Texto simple de respuesta",
            open=False,  # abierto por defecto
        )
    """
    def __init__(self, title, content=None, child=None, children=None, open=False):
        self.title    = title
        self.content  = content
        self.child    = child
        self.children = children
        self.open     = open


class Accordion(Widget):
    """
    Acordeón: lista de secciones plegables.

    Uso:
        Accordion(items=[
            AccordionItem("¿Qué es MARTIN?",
                          content="MARTIN es un framework Python para construir webs."),
            AccordionItem("¿Cómo instalo?",
                          child=Code("pip install martin", language="bash"), open=True),
            AccordionItem("¿Tiene dark mode?",
                          children=[Text("Sí, completamente."), Badge("Auto")]),
        ])

    Parámetros:
        items        list[AccordionItem]  ítems del acordeón
        multiple     bool    permite varios abiertos a la vez (default: False)
        variant      str     "default" | "bordered" | "separated"
        icon         str     "chevron" | "plus" | "arrow"  — icono del toggle
        radius       int     radio de bordes
    """

    _id_counter = 0

    def __init__(self, items=None, multiple=False, variant="default",
                 icon="chevron", **kwargs):
        self._props   = Widget._extract_props(kwargs)
        self.items    = items or []
        self.multiple = multiple
        self.variant  = variant
        self.icon     = icon
        Accordion._id_counter += 1
        self.uid = f"acc_{Accordion._id_counter}"

    def _icon_svg(self, closed=True):
        if self.icon == "plus":
            if closed:
                return '<svg width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M8 3v10M3 8h10" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>'
            else:
                return '<svg width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M3 8h10" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>'
        elif self.icon == "arrow":
            return '<svg width="14" height="14" viewBox="0 0 14 14" fill="none" style="transition:transform .25s"><path d="M2 5l5 5 5-5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>'
        else:  # chevron (default)
            return '<svg width="16" height="16" viewBox="0 0 16 16" fill="none" style="transition:transform .25s"><path d="M4 6l4 4 4-4" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>'

    def render(self):
        import json as _json
        uid      = self.uid
        multiple = _json.dumps(self.multiple)
        extra    = self._resolve_props()
        radius   = self._props.get("radius", 12)
        r_css    = f"{radius}px"

        # Variant styles
        if self.variant == "separated":
            wrapper_style = f"display:flex;flex-direction:column;gap:8px;{extra}"
            item_base = (f"border:1px solid var(--border);border-radius:{r_css};"
                         f"background:var(--surface);overflow:hidden")
        elif self.variant == "bordered":
            wrapper_style = f"border:1px solid var(--border);border-radius:{r_css};overflow:hidden;{extra}"
            item_base = "border-bottom:1px solid var(--border)"
        else:  # default
            wrapper_style = f"border:1px solid var(--border);border-radius:{r_css};overflow:hidden;{extra}"
            item_base = "border-bottom:1px solid var(--border)"

        items_html = ""
        for i, item in enumerate(self.items):
            iid     = f"{uid}_i{i}"
            is_open = item.open
            is_last = (i == len(self.items) - 1)

            # Resolve content
            if item.children:
                body_html = Widget._render_children(item.children)
            elif item.child is not None:
                body_html = item.child.render() if isinstance(item.child, Widget) else str(item.child)
            elif item.content is not None:
                body_html = item.content.render() if isinstance(item.content, Widget) else str(item.content)
            else:
                body_html = ""

            # Title
            title_html = item.title.render() if isinstance(item.title, Widget) else str(item.title)

            # Border on last item in default/bordered
            item_style = item_base
            if self.variant != "separated" and is_last:
                item_style = item_base.replace("border-bottom:1px solid var(--border)", "")

            icon_id = f"{uid}_ico{i}"
            body_open    = "1" if is_open else "0"
            icon_rot     = "rotate(180deg)" if is_open else "rotate(0deg)"

            items_html += (
                f'<div style="{item_style}">'
                f'  <button id="{iid}_btn" onclick="{uid}_toggle({i})" '
                f'    style="width:100%;display:flex;align-items:center;justify-content:space-between;'
                f'           padding:16px 20px;background:none;border:none;cursor:pointer;'
                f'           text-align:left;gap:12px;color:var(--text);">'
                f'    <span style="font-size:15px;font-weight:600;flex:1">{title_html}</span>'
                f'    <span id="{icon_id}" style="flex-shrink:0;color:var(--text-muted);'
                f'          transform:{icon_rot};transition:transform .25s;display:flex">'
                f'      {self._icon_svg()}'
                f'    </span>'
                f'  </button>'
                f'  <div id="{iid}_body" data-open="{body_open}" style="max-height:0;overflow:hidden;'
                f'       padding:0 20px 0;font-size:14px;color:var(--text-muted);line-height:1.7;'
                f'       opacity:0;transform:translateY(-4px);'
                f'       transition:max-height .28s cubic-bezier(.4,0,.2,1),'
                f'                  opacity .2s ease,transform .2s ease,padding .24s ease;">'
                f'    {body_html}'
                f'  </div>'
                f'</div>'
            )

        n = len(self.items)
        js = f"""
<script>(function(){{
  var uid={_json.dumps(uid)}, n={n}, multi={multiple};
  var TRANS="max-height .28s cubic-bezier(.4,0,.2,1),opacity .2s ease,transform .2s ease,padding .24s ease";

  function bodyEl(i){{ return document.getElementById(uid+"_i"+i+"_body"); }}
  function iconEl(i){{ return document.getElementById(uid+"_ico"+i); }}

  function setOpen(i, open, animate){{
    var b = bodyEl(i), ic = iconEl(i);
    if(!b) return;

    if(!animate) b.style.transition = "none";

    if(open){{
      if(b.style.maxHeight === "none") b.style.maxHeight = b.scrollHeight + "px";
      requestAnimationFrame(function(){{
        b.style.maxHeight = b.scrollHeight + "px";
        b.style.opacity = "1";
        b.style.transform = "translateY(0)";
        b.style.padding = "0 20px 16px";
      }});
      b.setAttribute("data-open", "1");
      if(ic) ic.style.transform = "rotate(180deg)";
    }} else {{
      if(b.style.maxHeight === "none"){{
        b.style.maxHeight = b.scrollHeight + "px";
        b.offsetHeight;
      }}
      b.style.maxHeight = b.scrollHeight + "px";
      requestAnimationFrame(function(){{
        b.style.maxHeight = "0px";
        b.style.opacity = "0";
        b.style.transform = "translateY(-4px)";
        b.style.padding = "0 20px 0";
      }});
      b.setAttribute("data-open", "0");
      if(ic) ic.style.transform = "rotate(0deg)";
    }}

    if(!animate){{
      b.offsetHeight;
      b.style.transition = TRANS;
    }}
  }}

  for(var i = 0; i < n; i++){{
    (function(idx){{
      var b = bodyEl(idx);
      if(!b) return;
      b.style.transition = TRANS;
      b.addEventListener("transitionend", function(e){{
        if(e.propertyName === "max-height" && b.getAttribute("data-open") === "1"){{
          b.style.maxHeight = "none";
        }}
      }});
      var initiallyOpen = b.getAttribute("data-open") === "1";
      setOpen(idx, initiallyOpen, false);
    }})(i);
  }}

  window[uid+"_toggle"] = function(idx){{
    var b = bodyEl(idx);
    if(!b) return;
    var isOpen = b.getAttribute("data-open") === "1";
    if(!multi){{
      for(var j = 0; j < n; j++) if(j !== idx) setOpen(j, false, true);
    }}
    setOpen(idx, !isOpen, true);
  }};
}})();</script>
"""

        return (
            f'<div id="{uid}" style="{wrapper_style}">'
            + items_html
            + f'</div>'
            + js
        )


# ══════════════════════════════════════════════════════════
# TESTIMONIALS
# ══════════════════════════════════════════════════════════

class TestimonialItem:
    """
    Testimonio individual.

        TestimonialItem(
            name="Ana García",
            role="CEO, Empresa X",
            avatar="/assets/ana.jpg",   # URL o None (usa iniciales)
            text="Increíble producto, cambió nuestra forma de trabajar.",
            rating=5,                   # 1-5, None = oculta estrellas
            company_logo="/assets/logo.svg",  # opcional
        )
    """
    def __init__(self, name, text, role=None, avatar=None,
                 rating=None, company_logo=None):
        self.name         = name
        self.text         = text
        self.role         = role
        self.avatar       = avatar
        self.rating       = rating
        self.company_logo = company_logo


class Testimonials(Widget):
    """
    Sección de testimonios. Puede mostrarse en cuadrícula o como carrusel.

    Uso:
        Testimonials(items=[
            TestimonialItem("Ana García", "Excelente producto.", role="CEO", rating=5),
            TestimonialItem("Luis Ruiz",  "Lo recomiendo mucho.", role="Dev", rating=4),
            TestimonialItem("Sara Paz",   "Cambió mi flujo de trabajo.", rating=5),
        ])

        # Como carrusel automático:
        Testimonials(items=[...], mode="carousel", autoplay=True)

    Parámetros:
        items        list[TestimonialItem]
        mode         str   "grid" | "carousel"  (default: "grid")
        columns      int   columnas en modo grid (default: 3)
        autoplay     bool  autoplay en carousel (default: True)
        interval     int   ms entre slides en carousel (default: 5000)
        card_radius  int   radio de las tarjetas
        show_quotes  bool  muestra comillas decorativas (default: True)
        accent       str   color de acento para estrellas y comillas
    """

    _id_counter = 0

    def __init__(self, items=None, mode="grid", columns=3,
                 autoplay=True, interval=5000,
                 card_radius=16, show_quotes=True,
                 accent="var(--accent)", **kwargs):
        self._props      = Widget._extract_props(kwargs)
        self.items       = items or []
        self.mode        = mode
        self.columns     = columns
        self.autoplay    = autoplay
        self.interval    = interval
        self.card_radius = card_radius
        self.show_quotes = show_quotes
        self.accent      = accent
        Testimonials._id_counter += 1
        self.uid = f"tsm_{Testimonials._id_counter}"

    def _render_card(self, item, uid_prefix=""):
        """Render a single testimonial card."""
        # Stars
        stars_html = ""
        if item.rating:
            stars = ""
            for i in range(5):
                color = self.accent if i < item.rating else "var(--border)"
                stars += f'<svg width="14" height="14" viewBox="0 0 14 14" fill="{color}"><path d="M7 1l1.5 3.5L12 5l-2.5 2.5.5 3.5L7 9.5 4 11l.5-3.5L2 5l3.5-.5z"/></svg>'
            stars_html = f'<div style="display:flex;gap:3px;margin-bottom:12px">{stars}</div>'

        # Avatar
        if item.avatar:
            avatar_html = (
                f'<img src="{item.avatar}" alt="{item.name}" '
                f'style="width:44px;height:44px;border-radius:50%;object-fit:cover;flex-shrink:0">'
            )
        else:
            initials = "".join(p[0].upper() for p in item.name.split()[:2])
            avatar_html = (
                f'<div style="width:44px;height:44px;border-radius:50%;'
                f'background:var(--accent);color:#fff;display:flex;align-items:center;'
                f'justify-content:center;font-weight:700;font-size:15px;flex-shrink:0">'
                f'{initials}</div>'
            )

        # Role
        role_html = (
            f'<span style="font-size:12px;color:var(--text-muted)">{item.role}</span>'
            if item.role else ""
        )

        # Company logo
        logo_html = (
            f'<img src="{item.company_logo}" alt="logo" '
            f'style="height:24px;object-fit:contain;opacity:0.6;margin-bottom:8px">'
            if item.company_logo else ""
        )

        # Quote decoration
        quote_html = ""
        if self.show_quotes:
            quote_html = (
                f'<div style="font-size:40px;line-height:1;color:{self.accent};'
                f'opacity:0.3;font-family:Georgia,serif;margin-bottom:4px">&ldquo;</div>'
            )

        return (
            f'<div style="background:var(--surface);border:1px solid var(--border);'
            f'border-radius:{self.card_radius}px;padding:24px;display:flex;'
            f'flex-direction:column;gap:0">'
            + logo_html
            + quote_html
            + stars_html
            + f'<p style="font-size:14px;color:var(--text);line-height:1.7;'
              f'flex:1;margin:0 0 16px">{item.text}</p>'
            + f'<div style="display:flex;align-items:center;gap:12px">'
            + avatar_html
            + f'<div><div style="font-size:14px;font-weight:600;color:var(--text)">{item.name}</div>'
            + role_html
            + f'</div></div>'
            + f'</div>'
        )

    def render(self):
        extra = self._resolve_props()
        uid   = self.uid

        if self.mode == "carousel":
            return self._render_carousel(extra)

        # Grid mode
        cols  = self.columns
        cols_css = f"repeat({cols}, 1fr)"
        grid_style = (
            f"display:grid;grid-template-columns:{cols_css};gap:20px;{extra}"
        )
        cards = "".join(self._render_card(item) for item in self.items)
        responsive = (
            f'<style>'
            f'@media(max-width:768px){{#{uid}{{grid-template-columns:repeat(2,1fr)!important;}}}}'
            f'@media(max-width:480px){{#{uid}{{grid-template-columns:1fr!important;}}}}'
            f'</style>'
        )
        return f'{responsive}<div id="{uid}" style="{grid_style}">{cards}</div>'

    def _render_carousel(self, extra):
        uid      = self.uid
        n        = len(self.items)
        interval = self.interval
        autoplay = self.autoplay

        slides = ""
        for i, item in enumerate(self.items):
            card = self._render_card(item, uid_prefix=uid)
            slides += (
                f'<div id="{uid}_s{i}" style="flex-shrink:0;width:100%;'
                f'padding:4px;box-sizing:border-box">{card}</div>'
            )

        # Dots
        dots_html = ""
        for i in range(n):
            dots_html += (
                f'<span id="{uid}_d{i}" onclick="{uid}_go({i})" '
                f'style="width:8px;height:8px;border-radius:50%;cursor:pointer;'
                f'background:{self.accent if i==0 else "var(--border)"};'
                f'transition:background .3s;display:inline-block"></span>'
            )

        js = (
            f'<script>(function(){{'
            f'  var uid="{uid}",n={n},cur=0,timer=null;'
            f'  function go(idx){{'
            f'    var track=document.getElementById(uid+"_track");'
            f'    if(!track)return;'
            f'    cur=((idx%n)+n)%n;'
            f'    track.style.transform="translateX(-"+cur*100+"%)";\n'
            f'    for(var i=0;i<n;i++){{'
            f'      var d=document.getElementById(uid+"_d"+i);'
            f'      if(d)d.style.background=i===cur?"{self.accent}":"var(--border)";'
            f'    }}'
            f'  }}'
            f'  window[uid+"_go"]=go;'
            f'  window[uid+"_prev"]=function(){{go(cur-1);}};'
            f'  window[uid+"_next"]=function(){{go(cur+1);}};'
            f'  {"timer=setInterval(function(){go(cur+1);},"+str(interval)+");" if autoplay else ""}'
            f'}})();</script>'
        )

        return (
            f'<div id="{uid}" style="position:relative;overflow:hidden;{extra}">'
            f'  <div id="{uid}_track" style="display:flex;transition:transform .45s cubic-bezier(.4,0,.2,1)">'
            + slides
            + f'  </div>'
            f'  <button onclick="{uid}_prev()" style="position:absolute;left:8px;top:50%;transform:translateY(-50%);'
            f'    background:var(--surface);border:1px solid var(--border);border-radius:50%;'
            f'    width:36px;height:36px;cursor:pointer;display:flex;align-items:center;'
            f'    justify-content:center;color:var(--text);font-size:18px;z-index:2">&#8249;</button>'
            f'  <button onclick="{uid}_next()" style="position:absolute;right:8px;top:50%;transform:translateY(-50%);'
            f'    background:var(--surface);border:1px solid var(--border);border-radius:50%;'
            f'    width:36px;height:36px;cursor:pointer;display:flex;align-items:center;'
            f'    justify-content:center;color:var(--text);font-size:18px;z-index:2">&#8250;</button>'
            f'  <div style="display:flex;justify-content:center;gap:8px;margin-top:16px;padding-bottom:8px">'
            + dots_html
            + f'  </div>'
            + f'</div>'
            + js
        )


# ══════════════════════════════════════════════════════════
# SLIDE CAROUSEL (general — acepta cualquier Widget)
# ══════════════════════════════════════════════════════════

class SlideItem:
    """
    Ítem del SlideCarousel general. Acepta cualquier Widget como contenido.

        SlideItem(child=Card([Heading("Hola"), Text("Mundo")]))
        SlideItem(child=Image("/assets/foto.jpg"))
        SlideItem(child=Column([...]))
    """
    def __init__(self, child):
        self.child = child


class SlideCarousel(Widget):
    """
    Carrusel general que acepta cualquier Widget como slide.
    Extensión del Carousel original para contenido arbitrario.

    Uso:
        SlideCarousel(items=[
            SlideItem(Card([Heading("Slide 1"), Text("Descripción")])),
            SlideItem(Column([Image("/assets/a.jpg"), Paragraph("Pie de foto")])),
            SlideItem(child=MyCustomWidget()),
        ])

        # Con múltiples slides visibles:
        SlideCarousel(items=[...], visible=3, gap=16)

    Parámetros:
        items        list[SlideItem | Widget]  slides (acepta también Widgets directos)
        visible      int    slides visibles a la vez (default: 1)
        gap          int    espacio entre slides en px (default: 0)
        loop         bool   bucle infinito (default: True)
        autoplay     bool   avance automático (default: False)
        interval     int    ms entre slides en autoplay (default: 4000)
        arrows       bool   flechas de navegación (default: True)
        dots         bool   indicadores de posición (default: True)
        arrow_style  str    "default" | "minimal" | "pill"
        transition   str    "slide" | "fade"
    """

    _id_counter = 0

    def __init__(self, items=None, visible=1, gap=0,
                 loop=True, autoplay=False, interval=4000,
                 arrows=True, dots=True,
                 arrow_style="default", transition="slide", **kwargs):
        self._props     = Widget._extract_props(kwargs)
        self.items      = items or []
        self.visible    = visible
        self.gap        = gap
        self.loop       = loop
        self.autoplay   = autoplay
        self.interval   = interval
        self.arrows     = arrows
        self.dots       = dots
        self.arrow_style = arrow_style
        self.transition  = transition
        SlideCarousel._id_counter += 1
        self.uid = f"sc_{SlideCarousel._id_counter}"

    def _resolve_item(self, item):
        """Convierte SlideItem o Widget directo a HTML."""
        if isinstance(item, SlideItem):
            child = item.child
            return child.render() if isinstance(child, Widget) else str(child)
        elif isinstance(item, Widget):
            return item.render()
        return str(item)

    def render(self):
        uid      = self.uid
        items    = self.items
        n        = len(items)
        visible  = self.visible
        gap      = self.gap
        loop     = self.loop
        autoplay = self.autoplay
        interval = self.interval
        extra    = self._resolve_props()
        radius   = self._props.get("radius", 0)
        r_css    = f"border-radius:{radius}px;" if radius else ""

        slide_width = f"calc((100% - {gap*(visible-1)}px) / {visible})"

        # Build slides
        slides_html = ""
        for i, item in enumerate(items):
            content = self._resolve_item(item)
            slides_html += (
                f'<div id="{uid}_s{i}" style="flex-shrink:0;width:{slide_width};'
                f'overflow:hidden;{r_css}box-sizing:border-box">'
                + content
                + f'</div>'
            )

        # Clones for infinite loop
        clones_after  = ""
        clones_before = ""
        if loop and n > 0:
            for i in range(min(visible, n)):
                content = self._resolve_item(items[i % n])
                clones_after += (
                    f'<div style="flex-shrink:0;width:{slide_width};overflow:hidden;{r_css}box-sizing:border-box">'
                    + content + '</div>'
                )
                content = self._resolve_item(items[(n - 1 - i) % n])
                clones_before = (
                    f'<div style="flex-shrink:0;width:{slide_width};overflow:hidden;{r_css}box-sizing:border-box">'
                    + content + '</div>'
                ) + clones_before

        positions  = max(n - visible + 1, 1)
        offset     = visible if loop else 0
        gap_css    = f"gap:{gap}px;" if gap else ""

        # Arrows
        arrow_css_base = (
            "position:absolute;top:50%;transform:translateY(-50%);z-index:5;"
            "cursor:pointer;border:none;display:flex;align-items:center;justify-content:center;"
            "transition:opacity .2s"
        )
        if self.arrow_style == "minimal":
            arrow_extra = "background:none;color:var(--text);font-size:28px;padding:4px;opacity:0.7"
        elif self.arrow_style == "pill":
            arrow_extra = ("background:var(--accent);color:#fff;border-radius:999px;"
                           "width:44px;height:44px;font-size:18px;box-shadow:0 4px 16px rgba(0,0,0,0.2)")
        else:
            arrow_extra = ("background:var(--surface);color:var(--text);"
                           "border:1px solid var(--border);border-radius:50%;"
                           "width:40px;height:40px;font-size:20px")

        prev_btn = (
            f'<button onclick="{uid}_prev()" style="{arrow_css_base};{arrow_extra};left:8px">'
            f'&#8249;</button>'
        ) if self.arrows else ""

        next_btn = (
            f'<button onclick="{uid}_next()" style="{arrow_css_base};{arrow_extra};right:8px">'
            f'&#8250;</button>'
        ) if self.arrows else ""

        # Dots
        dots_html = ""
        if self.dots:
            dot_items = ""
            for i in range(positions):
                is_first = (i == 0)
                dot_items += (
                    f'<span id="{uid}_dot{i}" onclick="{uid}_goPos({i})" '
                    f'style="width:{12 if is_first else 8}px;height:8px;border-radius:999px;cursor:pointer;'
                    f'background:{"var(--accent)" if is_first else "var(--border)"};'
                    f'transition:all .3s;display:inline-block"></span>'
                )
            dots_html = (
                f'<div id="{uid}_dots" style="display:flex;justify-content:center;'
                f'gap:6px;margin-top:12px">{dot_items}</div>'
            )

        # JS
        js = (
            f'<script>(function(){{'
            f'  var uid="{uid}",n={n},vis={visible},loop={str(loop).lower()},'
            f'      gap={gap},offset={offset},pos=0,positions={positions};'
            f'  var track=document.getElementById(uid+"_track");'
            f'  var animating=false;'
            f'  function slideWidth(){{'
            f'    var tw=track.parentElement.offsetWidth;'
            f'    return (tw-gap*(vis-1))/vis;'
            f'  }}'
            f'  function setPos(p,animate){{'
            f'    var sw=slideWidth();'
            f'    var x=(p+offset)*(sw+gap);'
            f'    if(animate===false)track.style.transition="none";'
            f'    else track.style.transition="transform .4s cubic-bezier(.4,0,.2,1)";'
            f'    track.style.transform="translateX(-"+x+"px)";'
            f'  }}'
            f'  function updateDots(p){{'
            f'    for(var i=0;i<positions;i++){{'
            f'      var d=document.getElementById(uid+"_dot"+i);'
            f'      if(d){{d.style.background=i===p?"var(--accent)":"var(--border)";'
            f'            d.style.width=i===p?"12px":"8px";}}'
            f'    }}'
            f'  }}'
            f'  function go(newPos){{'
            f'    if(animating)return;'
            f'    pos=((newPos%positions)+positions)%positions;'
            f'    setPos(pos,true);'
            f'    updateDots(pos);'
            f'    if(loop){{'
            f'      animating=true;'
            f'      setTimeout(function(){{'
            f'        if(newPos<0){{setPos(positions-1,false);pos=positions-1;}}'
            f'        else if(newPos>=positions){{setPos(0,false);pos=0;}}'
            f'        animating=false;'
            f'      }},420);'
            f'    }}'
            f'  }}'
            f'  window[uid+"_prev"]=function(){{go(pos-1);}};'
            f'  window[uid+"_next"]=function(){{go(pos+1);}};'
            f'  window[uid+"_goPos"]=function(p){{go(p);}};'
            f'  setPos(0,false);'
            f'  {"setInterval(function(){go(pos+1);},"+str(interval)+");" if autoplay else ""}'
            f'  window.addEventListener("resize",function(){{setPos(pos,false);}});'
            f'}})();</script>'
        )

        return (
            f'<div id="{uid}" style="position:relative;overflow:hidden;{extra}">'
            + prev_btn + next_btn
            + f'  <div id="{uid}_track" style="display:flex;{gap_css}will-change:transform">'
            + (clones_before if loop else "")
            + slides_html
            + (clones_after if loop else "")
            + f'  </div>'
            + f'</div>'
            + dots_html
            + js
        )


# ══════════════════════════════════════════════════════════
# PRICING
# ══════════════════════════════════════════════════════════

class PricingPlan:
    """
    Plan de precios individual.

        PricingPlan(
            name="Pro",
            price=29,
            currency="$",
            period="mes",
            description="Para equipos en crecimiento",
            features=["Feature A", "Feature B", "Feature C"],
            cta_label="Empezar gratis",
            cta_url="/signup",
            featured=True,          # resalta este plan
            badge="Más popular",    # etiqueta opcional
        )
    """
    def __init__(self, name, price, currency="$", period="mes",
                 description=None, features=None,
                 cta_label="Empezar", cta_url="#",
                 featured=False, badge=None,
                 cta_on_click=None,
                 price_yearly=None):   # precio anual opcional para toggle
        self.name         = name
        self.price        = price
        self.currency     = currency
        self.period       = period
        self.description  = description
        self.features     = features or []
        self.cta_label    = cta_label
        self.cta_url      = cta_url
        self.featured     = featured
        self.badge        = badge
        self.cta_on_click = cta_on_click
        self.price_yearly = price_yearly


class Pricing(Widget):
    """
    Sección de planes de precios.

    Uso:
        Pricing(plans=[
            PricingPlan("Gratis", 0, features=["5 proyectos", "1 GB"]),
            PricingPlan("Pro", 29, features=["Ilimitado", "10 GB", "Soporte"],
                        featured=True, badge="Más popular"),
            PricingPlan("Enterprise", 99, features=["Todo lo de Pro", "SLA", "SSO"]),
        ])

        # Con toggle mensual/anual:
        Pricing(plans=[...], toggle=True)

    Parámetros:
        plans        list[PricingPlan]
        columns      int    columnas (default: auto según número de planes)
        toggle       bool   muestra toggle mensual/anual (default: False)
        toggle_discount str  texto del descuento anual (default: "Ahorra 20%")
        accent       str    color de acento
        radius       int    radio de las tarjetas
        check_icon   str    icono SVG/HTML para los features (default: ✓ estilizado)
    """

    _id_counter = 0

    def __init__(self, plans=None, columns=None, toggle=False,
                 toggle_discount="Ahorra 20%",
                 accent="var(--accent)", **kwargs):
        self._props          = Widget._extract_props(kwargs)
        self.plans           = plans or []
        self.columns         = columns or len(plans or [1])
        self.toggle          = toggle
        self.toggle_discount = toggle_discount
        self.accent          = accent
        Pricing._id_counter += 1
        self.uid = f"prc_{Pricing._id_counter}"

    def _check_icon(self):
        return (
            f'<svg width="16" height="16" viewBox="0 0 16 16" fill="none" style="flex-shrink:0">'
            f'<circle cx="8" cy="8" r="7" fill="{self.accent}" opacity="0.15"/>'
            f'<path d="M5 8l2 2 4-4" stroke="{self.accent}" stroke-width="1.8" '
            f'stroke-linecap="round" stroke-linejoin="round"/></svg>'
        )

    def _render_plan(self, plan, uid):
        radius   = self._props.get("radius", 16)
        featured = plan.featured

        card_style = (
            f"background:{'var(--accent)' if featured else 'var(--surface)'};"
            f"border:2px solid {'var(--accent)' if featured else 'var(--border)'};"
            f"border-radius:{radius}px;padding:32px 28px;"
            f"display:flex;flex-direction:column;gap:0;position:relative;"
            f"{'box-shadow:0 20px 60px rgba(99,102,241,0.3);transform:scale(1.03);' if featured else ''}"
        )

        text_color   = "#fff" if featured else "var(--text)"
        muted_color  = "rgba(255,255,255,0.75)" if featured else "var(--text-muted)"
        border_color = "rgba(255,255,255,0.2)" if featured else "var(--border)"

        badge_html = ""
        if plan.badge:
            badge_style = (
                f"position:absolute;top:-12px;left:50%;transform:translateX(-50%);"
                f"background:{'#fff' if featured else 'var(--accent)'};"
                f"color:{'var(--accent)' if featured else '#fff'};"
                f"font-size:11px;font-weight:700;padding:4px 14px;border-radius:999px;"
                f"white-space:nowrap;letter-spacing:.5px"
            )
            badge_html = f'<span style="{badge_style}">{plan.badge}</span>'

        desc_html = (
            f'<p style="font-size:13px;color:{muted_color};margin:8px 0 20px;line-height:1.5">'
            f'{plan.description}</p>'
        ) if plan.description else '<div style="margin-bottom:20px"></div>'

        # Price — with yearly data-attr for toggle
        price_val = plan.price
        price_yearly_val = plan.price_yearly
        price_display = f"{plan.currency}{price_val}" if isinstance(price_val, (int,float)) else str(price_val)
        yearly_attr = f' data-yearly="{plan.currency}{price_yearly_val}"' if price_yearly_val is not None else ""
        monthly_attr = f' data-monthly="{price_display}"'

        price_html = (
            f'<div style="margin-bottom:4px">'
            f'  <span id="{uid}_price_{id(plan)}" {monthly_attr}{yearly_attr} '
            f'    style="font-size:40px;font-weight:800;color:{text_color};line-height:1">'
            f'    {price_display}'
            f'  </span>'
            + (f'<span style="font-size:14px;color:{muted_color};margin-left:4px">/{plan.period}</span>'
               if isinstance(price_val, (int,float)) else "")
            + f'</div>'
        )

        # Features
        features_html = ""
        for feat in plan.features:
            feat_txt = feat.render() if isinstance(feat, Widget) else str(feat)
            features_html += (
                f'<div style="display:flex;align-items:flex-start;gap:10px;'
                f'padding:9px 0;border-bottom:1px solid {border_color}">'
                + self._check_icon()
                + f'<span style="font-size:14px;color:{text_color};line-height:1.5">{feat_txt}</span>'
                + f'</div>'
            )

        # CTA
        cta_style = (
            f"display:block;width:100%;margin-top:24px;padding:12px 20px;"
            # f"border-radius:{radius//2}px;font-size:15px;font-weight:600;"
            f"cursor:pointer;text-align:center;text-decoration:none;"
            f"transition:opacity .2s;box-sizing:border-box;"
            + (f"background:#fff;color:var(--accent);border:none;" if featured
               else f"background:var(--accent);color:#fff;border:none;")
        )
        click_attr = f' onclick="{plan.cta_on_click}"' if plan.cta_on_click else ""
        cta_html = (
            f'<a href="{plan.cta_url}" style="{cta_style}"{click_attr}>'
            f'{plan.cta_label}</a>'
        )

        return (
            f'<div style="{card_style}">'
            + badge_html
            + f'<div style="font-size:18px;font-weight:700;color:{text_color};margin-bottom:6px">{plan.name}</div>'
            + desc_html
            + price_html
            + f'<div style="flex:1">{features_html}</div>'
            + cta_html
            + f'</div>'
        )

    def render(self):
        uid   = self.uid
        extra = self._resolve_props()
        cols  = self.columns

        # Toggle
        toggle_html = ""
        if self.toggle:
            toggle_html = (
                f'<div style="display:flex;align-items:center;justify-content:center;'
                f'gap:12px;margin-bottom:32px">'
                f'  <span id="{uid}_lbl_m" style="font-size:14px;font-weight:600;color:var(--text)">Mensual</span>'
                f'  <div onclick="{uid}_toggleBilling()" id="{uid}_toggle_track" '
                f'    style="width:48px;height:26px;background:var(--border);border-radius:999px;'
                f'           cursor:pointer;position:relative;transition:background .25s">'
                f'    <div id="{uid}_toggle_thumb" '
                f'      style="position:absolute;top:3px;left:3px;width:20px;height:20px;'
                f'             background:#fff;border-radius:50%;transition:left .25s;'
                f'             box-shadow:0 1px 4px rgba(0,0,0,0.2)"></div>'
                f'  </div>'
                f'  <span id="{uid}_lbl_y" style="font-size:14px;color:var(--text-muted)">'
                f'    Anual <span style="font-size:11px;background:var(--accent);color:#fff;'
                f'      padding:2px 8px;border-radius:999px;margin-left:4px">{self.toggle_discount}</span>'
                f'  </span>'
                f'</div>'
                f'<script>(function(){{'
                f'  var uid="{uid}",yearly=false;'
                f'  window[uid+"_toggleBilling"]=function(){{'
                f'    yearly=!yearly;'
                f'    var track=document.getElementById(uid+"_toggle_track");'
                f'    var thumb=document.getElementById(uid+"_toggle_thumb");'
                f'    var lm=document.getElementById(uid+"_lbl_m");'
                f'    var ly=document.getElementById(uid+"_lbl_y");'
                f'    track.style.background=yearly?"var(--accent)":"var(--border)";'
                f'    thumb.style.left=yearly?"25px":"3px";'
                f'    lm.style.color=yearly?"var(--text-muted)":"var(--text)";'
                f'    ly.style.color=yearly?"var(--text)":"var(--text-muted)";'
                f'    document.querySelectorAll("[data-monthly]").forEach(function(el){{'
                f'      el.textContent=yearly?el.getAttribute("data-yearly")||el.getAttribute("data-monthly"):'
                f'                           el.getAttribute("data-monthly");'
                f'    }});'
                f'  }};'
                f'}})();</script>'
            )

        plans_html = "".join(self._render_plan(p, uid) for p in self.plans)

        grid_style = (
            f"display:grid;grid-template-columns:repeat({cols},1fr);"
            f"gap:20px;align-items:center;{extra}"
        )
        responsive = (
            f'<style>'
            f'@media(max-width:768px){{#{uid}_grid{{grid-template-columns:1fr!important;}}}}'
            f'</style>'
        )

        return (
            responsive
            + toggle_html
            + f'<div id="{uid}_grid" style="{grid_style}">'
            + plans_html
            + f'</div>'
        )


# ══════════════════════════════════════════════════════════
# FAQ
# ══════════════════════════════════════════════════════════

class FAQItem:
    """
    Pregunta-respuesta para FAQ.

        FAQItem("¿Puedo cancelar en cualquier momento?",
                "Sí, puedes cancelar tu suscripción en cualquier momento sin penalización.")
        FAQItem("¿Hay prueba gratuita?",
                child=Column([Text("Sí, 14 días gratis."), Button("Probar ahora")]))
    """
    def __init__(self, question, answer=None, child=None, open=False):
        self.question = question
        self.answer   = answer
        self.child    = child
        self.open     = open


class FAQ(Widget):
    """
    Sección de preguntas frecuentes. Construida sobre Accordion.

    Uso:
        FAQ(items=[
            FAQItem("¿Qué es MARTIN?", "Un framework Python para construir webs."),
            FAQItem("¿Cómo instalo?", child=Code("pip install martin")),
        ])

        # Con buscador integrado:
        FAQ(items=[...], searchable=True)

        # Dos columnas:
        FAQ(items=[...], columns=2)

    Parámetros:
        items        list[FAQItem]
        searchable   bool   buscador de preguntas (default: False)
        columns      int    1 o 2 columnas (default: 1)
        variant      str    heredado de Accordion: "default"|"bordered"|"separated"
        multiple     bool   permite varios abiertos (default: False)
    """

    _id_counter = 0

    def __init__(self, items=None, searchable=False, columns=1,
                 variant="separated", multiple=False, **kwargs):
        self._props     = Widget._extract_props(kwargs)
        self.items      = items or []
        self.searchable = searchable
        self.columns    = columns
        self.variant    = variant
        self.multiple   = multiple
        FAQ._id_counter += 1
        self.uid = f"faq_{FAQ._id_counter}"

    def render(self):
        uid   = self.uid
        extra = self._resolve_props()

        # Build AccordionItems from FAQItems
        from martin.widgets import Accordion, AccordionItem
        acc_items = [
            AccordionItem(
                title=item.question,
                content=item.answer,
                child=item.child,
                open=item.open,
            )
            for item in self.items
        ]

        search_html = ""
        if self.searchable:
            search_html = (
                f'<input type="text" placeholder="Buscar preguntas..." '
                f'id="{uid}_search" oninput="{uid}_search_fn(this.value)" '
                f'style="width:100%;padding:10px 16px;margin-bottom:20px;'
                f'border:1px solid var(--border-input);border-radius:999px;'
                f'background:var(--input-bg);color:var(--input-color);'
                f'font-size:14px;outline:none;box-sizing:border-box">'
            )

        if self.columns == 2:
            mid   = len(acc_items) // 2 + len(acc_items) % 2
            left  = acc_items[:mid]
            right = acc_items[mid:]
            acc_left  = Accordion(items=left,  variant=self.variant, multiple=self.multiple)
            acc_right = Accordion(items=right, variant=self.variant, multiple=self.multiple)
            accordion_html = (
                f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:16px">'
                + acc_left.render()
                + acc_right.render()
                + f'</div>'
            )
        else:
            acc = Accordion(items=acc_items, variant=self.variant, multiple=self.multiple)
            accordion_html = acc.render()

        search_js = ""
        if self.searchable:
            search_js = (
                f'<script>(function(){{'
                f'  window["{uid}_search_fn"]=function(q){{'
                f'    q=q.toLowerCase();'
                f'    document.querySelectorAll("#{uid}_content [id^=acc_]>div").forEach(function(item){{'
                f'      var btn=item.querySelector("button");'
                f'      if(!btn)return;'
                f'      var txt=btn.textContent.toLowerCase();'
                f'      item.style.display=txt.includes(q)?"block":"none";'
                f'    }});'
                f'  }};'
                f'}})();</script>'
            )

        return (
            f'<div id="{uid}" style="{extra}">'
            + search_html
            + f'<div id="{uid}_content">'
            + accordion_html
            + f'</div>'
            + f'</div>'
            + search_js
        )


# ══════════════════════════════════════════════════════════
# CHART — Gráficos interactivos con Chart.js
# ══════════════════════════════════════════════════════════

class ChartDataset:
    """
    Dataset de datos para Chart.

        ChartDataset(
            label="Ventas 2024",
            data=[120, 190, 80, 250, 300],
            color="#6366f1",          # color de línea/barras (o lista de colores para pastel)
            fill=False,               # área bajo la línea (para line/area)
        )
    """
    def __init__(self, label, data, color=None, fill=False,
                 border_width=2, point_radius=4,
                 background_color=None):
        self.label            = label
        self.data             = data
        self.color            = color
        self.fill             = fill
        self.border_width     = border_width
        self.point_radius     = point_radius
        self.background_color = background_color  # None = auto


class Chart(Widget):
    """
    Gráfico interactivo usando Chart.js (cargado desde CDN).

    Tipos soportados:
        "bar"        — barras verticales
        "bar_h"      — barras horizontales
        "line"       — líneas
        "area"       — área (línea con fill)
        "pie"        — pastel
        "doughnut"   — dona
        "radar"      — radar / araña
        "scatter"    — dispersión (data = [{x,y},...])
        "bubble"     — burbuja (data = [{x,y,r},...])

    Uso básico:
        Chart(
            type="bar",
            labels=["Ene","Feb","Mar","Abr","May"],
            datasets=[
                ChartDataset("Ventas", [120,190,80,250,300], color="#6366f1"),
                ChartDataset("Gastos", [80,100,70,150,200], color="#f472b6"),
            ],
            title="Resumen mensual",
        )

        # Pastel:
        Chart(
            type="pie",
            labels=["Python","JS","Rust","Go"],
            datasets=[ChartDataset("Uso", [45,30,15,10])],
        )

    Parámetros:
        type         str    tipo de gráfico (ver arriba)
        labels       list   etiquetas del eje X (o sectores para pie/doughnut)
        datasets     list[ChartDataset]
        title        str    título del gráfico
        height       int    altura en px (default: 350)
        legend       bool   mostrar leyenda (default: True)
        grid         bool   mostrar cuadrícula (default: True)
        animated     bool   animación de entrada (default: True)
        responsive   bool   ancho responsive (default: True)
        x_label      str    etiqueta eje X
        y_label      str    etiqueta eje Y
        stacked      bool   barras apiladas (default: False)
        colors       list   paleta de colores por defecto
        tooltip_mode str    "index" | "point" | "nearest"
        download     bool   botón descargar PNG (default: False)
    """

    _id_counter = 0
    DEFAULT_COLORS = [
        "#6366f1", "#f472b6", "#34d399", "#fb923c",
        "#38bdf8", "#a78bfa", "#4ade80", "#fbbf24",
        "#f87171", "#2dd4bf",
    ]

    def __init__(self, type="bar", labels=None, datasets=None,
                 title=None, height=350, legend=True, grid=True,
                 animated=True, responsive=True,
                 x_label=None, y_label=None, stacked=False,
                 colors=None, tooltip_mode="index",
                 download=False, text_color=None, muted_text_color=None, **kwargs):
        self._props       = Widget._extract_props(kwargs)
        self.chart_type   = type
        self.labels       = labels or []
        self.datasets     = datasets or []
        self.title        = title
        self.height       = height
        self.legend       = legend
        self.grid         = grid
        self.animated     = animated
        self.responsive   = responsive
        self.x_label      = x_label
        self.y_label      = y_label
        self.stacked      = stacked
        self.colors       = colors or self.DEFAULT_COLORS
        self.tooltip_mode = tooltip_mode
        self.download     = download
        self.text_color   = text_color
        self.muted_text_color = muted_text_color
        Chart._id_counter += 1
        self.uid = f"chart_{Chart._id_counter}"

    def _resolve_type(self):
        """Map internal type to Chart.js type."""
        if self.chart_type == "bar_h":
            return "bar"
        if self.chart_type == "area":
            return "line"
        return self.chart_type

    def _build_datasets_js(self):
        import json as _json

        def _to_rgba(c, alpha):
            if not isinstance(c, str):
                return c
            s = c.strip()
            if s.startswith(("rgba(", "rgb(", "hsl(", "hsla(")):
                return s
            if s.startswith("#"):
                h = s[1:]
                if len(h) == 3:
                    h = "".join(ch * 2 for ch in h)
                if len(h) == 6:
                    try:
                        r = int(h[0:2], 16)
                        g = int(h[2:4], 16)
                        b = int(h[4:6], 16)
                        return f"rgba({r},{g},{b},{alpha})"
                    except ValueError:
                        return s
            return s

        result = []
        is_pie_like = self.chart_type in ("pie", "doughnut")

        for idx, ds in enumerate(self.datasets):
            color = ds.color or self.colors[idx % len(self.colors)]

            if is_pie_like:
                # Pie: each slice gets its own color
                bg_colors = [self.colors[i % len(self.colors)] for i in range(len(ds.data))]
                d = {
                    "label": ds.label,
                    "data": ds.data,
                    "backgroundColor": bg_colors,
                    "borderWidth": 2,
                    "borderColor": "#060818",
                }
            else:
                fill_val = ds.fill or (self.chart_type == "area")
                # Convert color to rgba for background
                bg_opacity = 0.15 if fill_val else 0.7
                d = {
                    "label": ds.label,
                    "data": ds.data,
                    "borderColor": color,
                    "backgroundColor": (
                        ds.background_color
                        if ds.background_color
                        else _to_rgba(color, bg_opacity)
                    ),
                    "borderWidth": ds.border_width,
                    "pointRadius": ds.point_radius,
                    "fill": fill_val,
                    "tension": 0.4,
                }
                # For bar charts: use color directly as background
                if self.chart_type in ("bar", "bar_h"):
                    d["backgroundColor"] = color

            result.append(d)

        return _json.dumps(result)

    def render(self):
        import json as _json
        uid        = self.uid
        extra      = self._resolve_props()
        cjs_type   = self._resolve_type()
        datasets_js = self._build_datasets_js()
        labels_js  = _json.dumps(self.labels)
        height     = self.height
        text_color_js = _json.dumps(self.text_color or "")
        muted_color_js = _json.dumps(self.muted_text_color or "")

        # Options
        is_horizontal = (self.chart_type == "bar_h")
        is_pie_like   = self.chart_type in ("pie", "doughnut")

        scales_config = "scales:{}" if is_pie_like else (
            f"scales:{{"
            f"  x:{{"
            f"    {'stacked:true,' if self.stacked else ''}"
            f"    grid:{{display:{'true' if self.grid else 'false'},color:'rgba(128,128,128,0.1)'}},"
            f"    ticks:{{color:'var(--text-muted)'}},"
            + (f"    title:{{display:true,text:{_json.dumps(self.x_label or '')},color:'var(--text-muted)'}}" if self.x_label else "")
            + f"  }},"
            f"  y:{{"
            f"    {'stacked:true,' if self.stacked else ''}"
            f"    grid:{{display:{'true' if self.grid else 'false'},color:'rgba(128,128,128,0.1)'}},"
            f"    ticks:{{color:'var(--text-muted)'}},"
            + (f"    title:{{display:true,text:{_json.dumps(self.y_label or '')},color:'var(--text-muted)'}}" if self.y_label else "")
            + f"  }}"
            f"}}"
        )

        indexAxis = '"x"' if not is_horizontal else '"y"'

        options_js = (
            f"{{"
            f"  responsive:{str(self.responsive).lower()},"
            f"  maintainAspectRatio:false,"
            f"  indexAxis:{indexAxis},"
            f"  animation:{{duration:{'800' if self.animated else '0'}}},"
            f"  plugins:{{"
            f"    legend:{{display:{'true' if self.legend else 'false'},"
            f"             labels:{{color:'var(--text)',font:{{size:13}}}}}},"
            f"    tooltip:{{mode:{_json.dumps(self.tooltip_mode)},intersect:false}},"
            + (f"    title:{{display:true,text:{_json.dumps(self.title or '')},color:'var(--text)',"
               f"            font:{{size:15,weight:'600'}},padding:{{bottom:16}}}}" if self.title else "")
            + f"  }},"
            f"  {scales_config}"
            f"}}"
        )

        download_btn = ""
        if self.download:
            download_btn = (
                f'<button onclick="(function(){{var a=document.createElement(\'a\');'
                f'a.download=\'chart.png\';a.href=window[\'_chart_{uid}\'].toBase64Image();'
                f'a.click();}})()" '
                f'style="position:absolute;top:8px;right:8px;background:var(--surface-2);'
                f'border:1px solid var(--border);border-radius:6px;padding:6px 12px;'
                f'font-size:12px;cursor:pointer;color:var(--text)">&#11015; PNG</button>'
            )

        wrapper_style = f"position:relative;{'height:'+str(height)+'px'};width:100%;{extra}"

        js = f"""
<script>
(function(){{
  var cdnUrl="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js";
  var customText={text_color_js};
  var customMuted={muted_color_js};

  function cssVar(name, fallback){{
    var raw=(getComputedStyle(document.documentElement).getPropertyValue(name)||"").trim();
    return raw || fallback;
  }}

  function applyThemeColors(chart){{
    var textColor=customText || cssVar("--text", "#111827");
    var mutedColor=customMuted || cssVar("--text-muted", "#6b7280");
    var gridColor=cssVar("--border", "rgba(128,128,128,0.2)");
    var opts=chart.options||{{}};

    if(opts.plugins&&opts.plugins.legend&&opts.plugins.legend.labels){{
      opts.plugins.legend.labels.color=textColor;
    }}
    if(opts.plugins&&opts.plugins.title){{
      opts.plugins.title.color=textColor;
    }}

    if(opts.scales){{
      ["x","y","r"].forEach(function(axis){{
        var sc=opts.scales[axis];
        if(!sc)return;
        if(sc.ticks) sc.ticks.color=mutedColor;
        if(sc.title) sc.title.color=mutedColor;
        if(sc.grid && sc.grid.display!==false) sc.grid.color=gridColor;
      }});
    }}
  }}

  function init(){{
    var ctx=document.getElementById("{uid}_canvas").getContext("2d");
    var options={options_js};
    var chart=new Chart(ctx,{{
      type:{_json.dumps(cjs_type)},
      data:{{labels:{labels_js},datasets:{datasets_js}}},
      options:options
    }});
    applyThemeColors(chart);
    chart.update("none");

    var obs=new MutationObserver(function(muts){{
      for(var i=0;i<muts.length;i++){{
        if(muts[i].attributeName==="data-theme"){{
          applyThemeColors(chart);
          chart.update("none");
          break;
        }}
      }}
    }});
    obs.observe(document.documentElement,{{attributes:true,attributeFilter:["data-theme"]}});

    window["_chart_{uid}"]=chart;
  }}

  if(window.Chart){{init();}}
  else{{
    var s=document.createElement("script");
    s.src=cdnUrl;
    s.onload=function(){{init();}};
    document.head.appendChild(s);
  }}
}})();
</script>
"""

        return (
            f'<div style="{wrapper_style}">'
            + download_btn
            + f'<canvas id="{uid}_canvas" style="width:100%;height:100%"></canvas>'
            + f'</div>'
            + js
        )


# ══════════════════════════════════════════════════════════
# CALENDAR — Calendario completo con vistas mes/semana/día
# ══════════════════════════════════════════════════════════


class CalendarEvent:
    """
    Evento del calendario.

        CalendarEvent(
            title="Reunión de equipo",
            date="2025-03-15",
            start_time="10:00",
            end_time="11:30",
            color="#6366f1",
            description="Sala B, edificio central",
            all_day=False,
            url="/eventos/123",
        )
    """

    def __init__(
        self,
        title,
        date,
        start_time=None,
        end_time=None,
        color=None,
        description=None,
        all_day=False,
        url=None,
    ):
        self.title = title
        self.date = date
        self.start_time = start_time
        self.end_time = end_time
        self.color = color
        self.description = description
        self.all_day = all_day
        self.url = url


class Calendar(Widget):
    """
    Calendario interactivo completo con vistas mes, semana y día.
    Soporta gestión de eventos (crear, editar, eliminar) con modal integrado.

    Uso básico:
        Calendar(events=[
            CalendarEvent("Reunión", "2025-03-15", start_time="10:00", color="#6366f1"),
            CalendarEvent("Entrega", "2025-03-20", color="#ef4444"),
            CalendarEvent("Vacaciones", "2025-03-22", all_day=True, color="#34d399"),
        ])

        # Con edición habilitada:
        Calendar(events=[...], editable=True)

    Parámetros:
        events             list[CalendarEvent]
        initial_view       "month" | "week" | "day"  (default: "month")
        initial_date       "YYYY-MM-DD"  (default: hoy)
        range_select       bool  — selección de rango en vista mes (default: False)
        editable           bool  — habilita crear/editar/eliminar (default: False)
        on_date_click      str   — JS fn(dateStr) al hacer clic en fecha
        on_event_click     str   — JS fn(event) al hacer clic en evento
        on_event_create    str   — JS fn(event) al crear evento
        on_event_update    str   — JS fn(newEvent, oldEvent) al editar
        on_event_delete    str   — JS fn(event) al eliminar
        show_views         bool  (default: True)
        show_today         bool  (default: True)
        first_day          int   0=domingo, 1=lunes (default: 1)
        locale             "es" | "en"  (default: "es")
        height             int px (default: 600)
        accent             str color de acento (default: "var(--accent)")
        event_colors       list[str] paleta para el picker de color
    """

    _id_counter = 0

    MONTHS_ES = [
        "Enero",
        "Febrero",
        "Marzo",
        "Abril",
        "Mayo",
        "Junio",
        "Julio",
        "Agosto",
        "Septiembre",
        "Octubre",
        "Noviembre",
        "Diciembre",
    ]
    DAYS_ES = ["Dom", "Lun", "Mar", "Mi\u00e9", "Jue", "Vie", "S\u00e1b"]
    MONTHS_EN = [
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
    ]
    DAYS_EN = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]

    DEFAULT_COLORS = [
        "#6366f1",
        "#3b82f6",
        "#06b6d4",
        "#10b981",
        "#84cc16",
        "#f59e0b",
        "#ef4444",
        "#ec4899",
        "#8b5cf6",
        "#64748b",
    ]

    def __init__(
        self,
        events=None,
        initial_view="month",
        initial_date=None,
        range_select=False,
        editable=False,
        on_date_click=None,
        on_event_click=None,
        on_event_create=None,
        on_event_update=None,
        on_event_delete=None,
        show_views=True,
        show_today=True,
        first_day=1,
        locale="es",
        height=600,
        accent="var(--accent)",
        event_colors=None,
        **kwargs,
    ):
        self._props = Widget._extract_props(kwargs)
        self.events = events or []
        self.initial_view = initial_view
        self.initial_date = initial_date
        self.range_select = range_select
        self.editable = editable
        self.on_date_click = on_date_click
        self.on_event_click = on_event_click
        self.on_event_create = on_event_create
        self.on_event_update = on_event_update
        self.on_event_delete = on_event_delete
        self.show_views = show_views
        self.show_today = show_today
        self.first_day = first_day
        self.locale = locale
        self.height = height
        self.accent = accent
        self.event_colors = event_colors or self.DEFAULT_COLORS
        Calendar._id_counter += 1
        self.uid = f"cal_{Calendar._id_counter}"

    def _serialize_events(self):
        import json as _j

        return _j.dumps(
            [
                {
                    "title": ev.title,
                    "date": ev.date,
                    "start_time": ev.start_time or "",
                    "end_time": ev.end_time or "",
                    "color": ev.color or "",
                    "description": ev.description or "",
                    "all_day": ev.all_day,
                    "url": ev.url or "",
                }
                for ev in self.events
            ]
        )

    def render(self):
        import json as _j

        uid = self.uid
        extra = self._resolve_props()
        height = self.height

        months = _j.dumps(self.MONTHS_ES if self.locale == "es" else self.MONTHS_EN)
        days = _j.dumps(self.DAYS_ES if self.locale == "es" else self.DAYS_EN)
        events_js = self._serialize_events()
        first_day = self.first_day
        init_view = _j.dumps(self.initial_view)
        init_date = _j.dumps(self.initial_date or "")
        range_sel = _j.dumps(self.range_select)
        editable = _j.dumps(self.editable)
        accent = _j.dumps(self.accent)
        colors_js = _j.dumps(self.event_colors)
        cb_date = _j.dumps(self.on_date_click or "")
        cb_click = _j.dumps(self.on_event_click or "")
        cb_create = _j.dumps(self.on_event_create or "")
        cb_update = _j.dumps(self.on_event_update or "")
        cb_delete = _j.dumps(self.on_event_delete or "")

        if self.locale == "es":
            lbl = dict(
                new_event="Nuevo evento",
                edit_event="Editar evento",
                title_lbl="T\u00edtulo",
                title_ph="T\u00edtulo del evento",
                date_lbl="Fecha",
                start_lbl="Inicio",
                end_lbl="Fin",
                desc_lbl="Descripci\u00f3n",
                desc_ph="Descripci\u00f3n (opcional)",
                color_lbl="Color",
                allday_lbl="Todo el d\u00eda",
                save="Guardar",
                cancel="Cancelar",
                delete="Eliminar",
                confirm_del="\u00bfEliminar este evento?",
                no_events="No hay eventos.",
                add_tip="Clic en una hora para crear un evento",
                today_lbl="Hoy",
                mas="m\u00e1s",
            )
        else:
            lbl = dict(
                new_event="New event",
                edit_event="Edit event",
                title_lbl="Title",
                title_ph="Event title",
                date_lbl="Date",
                start_lbl="Start",
                end_lbl="End",
                desc_lbl="Description",
                desc_ph="Description (optional)",
                color_lbl="Color",
                allday_lbl="All day",
                save="Save",
                cancel="Cancel",
                delete="Delete",
                confirm_del="Delete this event?",
                no_events="No events.",
                add_tip="Click a time slot to create an event",
                today_lbl="Today",
                mas="more",
            )
        lbl_js = _j.dumps(lbl)

        wrapper_style = (
            f"background:var(--surface);border:1px solid var(--border);"
            f"border-radius:16px;overflow:hidden;display:flex;"
            f"flex-direction:column;height:{height}px;{extra}"
        )

        # ─────────────────────────────────────────────────────────────────
        # JS ARCHITECTURE
        # All dynamic data (date, event id, hour) is passed via data-* attrs.
        # onclick handlers only call:  UID_handler(this)
        # Handlers read: el.dataset.date / el.dataset.eid / el.dataset.hour
        # This completely avoids quote-escaping issues in generated HTML strings.
        #
        # Python f-string rules:
        #   {{ }}  →  { }  in output (JS braces)
        #   {var}  →  interpolated Python variable
        # ─────────────────────────────────────────────────────────────────
        js = f"""
<script>
(function(){{
  var U={_j.dumps(uid)};
  var MONTHS={months};
  var DAYS={days};
  var ACCENT={accent};
  var FD={first_day};
  var RANGE={range_sel};
  var EDIT={editable};
  var COLORS={colors_js};
  var LBL={lbl_js};
  var CB_DATE={cb_date};
  var CB_CLICK={cb_click};
  var CB_CREATE={cb_create};
  var CB_UPDATE={cb_update};
  var CB_DELETE={cb_delete};

  /* ── accent resolver ──────────────────────────────── */
  function A(){{
    if(!ACCENT||ACCENT.indexOf("var(")<0)return ACCENT||"#6366f1";
    var p=ACCENT.replace(/^var\(/,"").replace(/\)$/,"").split(",")[0].trim();
    return(getComputedStyle(document.documentElement).getPropertyValue(p)||"").trim()||"#6366f1";
  }}

  /* ── event store ──────────────────────────────────── */
  var EVTS={events_js}.map(function(e,i){{return Object.assign({{_id:i}},e);}});
  var NID=EVTS.length;
  var EBD={{}};
  function idx(){{
    EBD={{}};
    EVTS.forEach(function(e){{if(!EBD[e.date])EBD[e.date]=[];EBD[e.date].push(e);}});
  }}
  idx();

  /* ── state ────────────────────────────────────────── */
  var NOW=new Date();
  var _id={init_date}?new Date({init_date}):new Date();
  var CY=_id.getFullYear(),CM=_id.getMonth(),CD=_id.getDate();
  var VIEW={init_view};
  var RS=null,RE=null;

  /* ── helpers ──────────────────────────────────────── */
  function pad(n){{return n<10?"0"+n:""+n;}}
  function ds(y,m,d){{return y+"-"+pad(m+1)+"-"+pad(d);}}
  function isToday(y,m,d){{return y===NOW.getFullYear()&&m===NOW.getMonth()&&d===NOW.getDate();}}
  function esc(s){{
    return(s||"").replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;")
                 .replace(/'/g,"&#39;");
  }}
  function G(id){{return document.getElementById(U+"_"+id);}}
  function getEv(id){{for(var i=0;i<EVTS.length;i++)if(EVTS[i]._id===id)return EVTS[i];return null;}}
  function callCb(name,args){{
    if(!name)return;
    try{{
      var f=window[name]||eval("("+name+")");
      if(typeof f=="function")f.apply(null,args);
    }}catch(e){{console.warn("Calendar cb error:",e);}}
  }}

  /* ── layout ───────────────────────────────────────── */
  function layout(){{
    var g=G("grid"),dn=G("daynames");
    if(!g)return;
    if(VIEW==="month"){{
      if(dn)dn.style.display="grid";
      g.style.display="grid";
      g.style.gridTemplateColumns="repeat(7,1fr)";
      g.style.overflowY="auto";
    }}else{{
      if(dn)dn.style.display="none";
      g.style.display="block";
      g.style.gridTemplateColumns="unset";
      g.style.overflowY="hidden";
    }}
  }}

  function renderHeader(){{
    var t="";
    if(VIEW==="month")t=MONTHS[CM]+" "+CY;
    else if(VIEW==="week"){{
      var w=weekDays(CY,CM,CD);
      t=MONTHS[w[0].getMonth()]+" "+w[0].getDate()+
        " \u2013 "+MONTHS[w[6].getMonth()]+" "+w[6].getDate()+", "+w[0].getFullYear();
    }}else t=MONTHS[CM]+" "+CD+", "+CY;
    var h=G("title");if(h)h.textContent=t;
  }}

  function syncBtns(){{
    ["month","week","day"].forEach(function(v){{
      var b=document.getElementById(U+"_vbtn_"+v);if(!b)return;
      var a=A();
      b.style.background=v===VIEW?a:"var(--surface-2,var(--surface))";
      b.style.color=v===VIEW?"#fff":"var(--text)";
      b.style.borderColor=v===VIEW?a:"var(--border)";
    }});
  }}

  /* ══════════════════════════════════════════════════
     MONTH VIEW
     onclick passes data via data-* attributes — no quote issues
  ══════════════════════════════════════════════════ */
  function fdo(y,m){{return((new Date(y,m,1).getDay()-FD)+7)%7;}}

  function renderMonth(){{
    var g=G("grid");if(!g)return;
    var a=A(),off=fdo(CY,CM);
    var dim=new Date(CY,CM+1,0).getDate(),dip=new Date(CY,CM,0).getDate();
    var total=Math.ceil((off+dim)/7)*7,h="";

    for(var i=0;i<total;i++){{
      var cy=CY,cm=CM,cd,out=false;
      if(i<off){{cd=dip-(off-1-i);cm=CM-1;if(cm<0){{cm=11;cy--;}}out=true;}}
      else if(i>=off+dim){{cd=i-off-dim+1;cm=CM+1;if(cm>11){{cm=0;cy++;}}out=true;}}
      else cd=i-off+1;

      var date=ds(cy,cm,cd),evs=EBD[date]||[];
      var isTod=isToday(cy,cm,cd),isRS=date===RS,isRE=date===RE;
      var inR=RS&&RE&&date>=RS&&date<=RE;
      var bg="transparent";
      if(isTod)bg="rgba(99,102,241,.12)";
      if(inR)bg="rgba(99,102,241,.07)";
      if(isRS||isRE)bg=a;
      var dc=(isRS||isRE)?"#fff":(out?"var(--text-muted)":"var(--text)");
      var fw=isTod?"700":"400",br=(isRS||isRE)?"border-radius:8px":"";

      /* event pills */
      var ep="",mx=Math.min(evs.length,3);
      for(var ei=0;ei<mx;ei++){{
        var ec=evs[ei].color||a;
        /* data-eid passed via data attribute — no quote escaping needed */
        ep+="<div onclick='"+U+"_evClick(this)' data-eid='"+evs[ei]._id+"'"
           +" style='font-size:10px;background:"+ec+";color:#fff;border-radius:3px;"
           +"padding:1px 5px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;"
           +"margin-top:2px;cursor:pointer'>"+esc(evs[ei].title)+"</div>";
      }}
      if(evs.length>3)ep+="<div style='font-size:10px;color:var(--text-muted);margin-top:2px'>+"+(evs.length-3)+" "+LBL.mas+"</div>";

      /* add button (editable) — date via data attribute */
      var ab=EDIT
        ?"<div onclick='event.stopPropagation();"+U+"_openCreate(this)'"
         +" data-date='"+date+"' data-hour=''"
         +" class='"+U+"_ab'"
         +" style='font-size:16px;color:var(--text-muted);opacity:0;transition:opacity .15s;"
         +"cursor:pointer;text-align:center;margin-top:2px'>+</div>"
        :"";

      /* cell — date via data attribute */
      h+="<div onclick='"+U+"_dayClick(this)' data-date='"+date+"'"
        +" onmouseenter='"+U+"_cellHover(1)'"
        +" onmouseleave='"+U+"_cellHover(0)'"
        +" style='border:1px solid var(--border);padding:6px 8px;min-height:80px;"
        +"cursor:pointer;background:"+bg+";"+br+";transition:background .15s;box-sizing:border-box'>"
        +"<div style='font-size:13px;font-weight:"+fw+";color:"+dc+"'>"+cd+"</div>"
        +(isTod?"<div style='width:4px;height:4px;border-radius:50%;background:"+a+";margin:1px auto'></div>":"")
        +ep+ab+"</div>";
    }}
    g.innerHTML=h;
  }}

  /* ══════════════════════════════════════════════════
     WEEK VIEW
  ══════════════════════════════════════════════════ */
  function weekDays(y,m,d){{
    var dt=new Date(y,m,d),diff=((dt.getDay()-FD)+7)%7;
    var s=new Date(dt);s.setDate(dt.getDate()-diff);
    var r=[];
    for(var i=0;i<7;i++){{var x=new Date(s);x.setDate(s.getDate()+i);r.push(x);}}
    return r;
  }}
  var HRS=[];for(var _h=0;_h<24;_h++)HRS.push(pad(_h)+":00");

  function renderWeek(){{
    var g=G("grid");if(!g)return;
    var wd=weekDays(CY,CM,CD),a=A();
    var h="<div style='display:grid;grid-template-columns:56px repeat(7,minmax(120px,1fr));"
          +"height:100%;overflow:auto;min-width:860px'>";

    /* header row */
    h+="<div style='background:var(--surface-2,var(--surface));border-bottom:1px solid var(--border)'></div>";
    for(var wi=0;wi<wd.length;wi++){{
      var dt2=wd[wi],tod=isToday(dt2.getFullYear(),dt2.getMonth(),dt2.getDate()),dn=dt2.getDate();
      var dnH=tod
        ?"<span style='background:"+a+";color:#fff;border-radius:50%;width:28px;height:28px;"
          +"display:inline-flex;align-items:center;justify-content:center'>"+dn+"</span>"
        :dn;
      h+="<div style='border-bottom:1px solid var(--border);border-left:1px solid var(--border);"
        +"padding:8px 4px;text-align:center;background:var(--surface-2,var(--surface));"
        +(tod?"color:"+a+";font-weight:700":"color:var(--text-muted)")+";font-size:12px'>"
        +DAYS[dt2.getDay()]+"<br>"
        +"<span style='font-size:18px;font-weight:700'>"+dnH+"</span></div>";
    }}

    /* hour rows */
    for(var hi=0;hi<HRS.length;hi++){{
      var hStr=HRS[hi],hour=parseInt(hStr,10);
      h+="<div style='border-bottom:1px solid var(--border);padding:4px 6px;"
        +"font-size:11px;color:var(--text-muted);text-align:right;white-space:nowrap'>"+hStr+"</div>";
      for(var wi2=0;wi2<wd.length;wi2++){{
        var dt3=wd[wi2],d3=ds(dt3.getFullYear(),dt3.getMonth(),dt3.getDate());
        var dl=EBD[d3]||[],slEv="";
        for(var di=0;di<dl.length;di++){{
          var ev=dl[di];
          if(!ev.start_time||parseInt(ev.start_time.split(":")[0],10)!==hour)continue;
          var ec=ev.color||a;
          slEv+="<div onclick='event.stopPropagation();"+U+"_evClick(this)' data-eid='"+ev._id+"'"
               +" style='background:"+ec+";color:#fff;font-size:11px;border-radius:4px;"
               +"padding:2px 6px;margin-bottom:2px;cursor:pointer;overflow:hidden;"
               +"white-space:nowrap;text-overflow:ellipsis'>"
               +esc(ev.title)+(ev.end_time?" "+ev.start_time+"-"+ev.end_time:"")+"</div>";
        }}
        /* slot cell — date and hour via data attributes */
        h+="<div onclick='"+U+"_dayClick(this)' data-date='"+d3+"' data-hour='"+hStr+"'"
          +" style='border-bottom:1px solid var(--border);border-left:1px solid var(--border);"
          +"padding:2px;min-height:40px;box-sizing:border-box;cursor:pointer'>"+slEv+"</div>";
      }}
    }}
    h+="</div>";
    g.innerHTML=h;
  }}

  /* ══════════════════════════════════════════════════
     DAY VIEW
  ══════════════════════════════════════════════════ */
  function renderDay(){{
    var g=G("grid");if(!g)return;
    var date=ds(CY,CM,CD),dl=EBD[date]||[],a=A(),tod=isToday(CY,CM,CD);
    var h="<div style='overflow-y:auto;height:100%'>";

    h+="<div style='padding:12px 16px;border-bottom:1px solid var(--border);"
      +"background:var(--surface-2,var(--surface));font-size:15px;font-weight:700;color:var(--text)'>"
      +MONTHS[CM]+" "+CD+", "+CY
      +(tod?"<span style='background:"+a+";color:#fff;font-size:11px;"
        +"padding:2px 8px;border-radius:999px;margin-left:8px'>"+LBL.today_lbl+"</span>":"")
      +"</div>";

    if(!dl.length)
      h+="<div style='padding:10px 16px;font-size:12px;color:var(--text-muted)'>"
        +(EDIT?LBL.add_tip:LBL.no_events)+"</div>";

    /* all-day events */
    var ada=[];for(var i=0;i<dl.length;i++)if(dl[i].all_day)ada.push(dl[i]);
    if(ada.length){{
      h+="<div style='padding:8px 16px;border-bottom:1px solid var(--border)'>";
      for(var i=0;i<ada.length;i++){{
        var ec=ada[i].color||a;
        h+="<div onclick='"+U+"_evClick(this)' data-eid='"+ada[i]._id+"'"
          +" style='background:"+ec+";color:#fff;border-radius:6px;padding:6px 12px;"
          +"margin-bottom:4px;font-size:13px;cursor:pointer'>"+esc(ada[i].title)+"</div>";
      }}
      h+="</div>";
    }}

    /* hour slots */
    for(var hi=0;hi<HRS.length;hi++){{
      var hStr=HRS[hi],hour=parseInt(hStr,10),slEv="";
      for(var di=0;di<dl.length;di++){{
        var ev=dl[di];
        if(!ev.start_time||parseInt(ev.start_time.split(":")[0],10)!==hour)continue;
        var ec=ev.color||a;
        slEv+="<div onclick='event.stopPropagation();"+U+"_evClick(this)' data-eid='"+ev._id+"'"
             +" style='background:"+ec+";color:#fff;border-radius:6px;"
             +"padding:8px 12px;margin-bottom:4px;cursor:pointer'>"
             +"<div style='font-weight:600;font-size:13px'>"+esc(ev.title)+"</div>"
             +(ev.start_time?"<div style='font-size:11px;opacity:.85'>"+ev.start_time
               +(ev.end_time?" \u2013 "+ev.end_time:"")+"</div>":"")
             +(ev.description?"<div style='font-size:12px;margin-top:4px;opacity:.85'>"
               +esc(ev.description)+"</div>":"")
             +"</div>";
      }}
      h+="<div style='display:grid;grid-template-columns:64px 1fr;"
        +"border-bottom:1px solid var(--border);min-height:56px'>"
        +"<div style='padding:8px 10px;font-size:12px;color:var(--text-muted);text-align:right'>"+hStr+"</div>"
        +"<div onclick='"+U+"_dayClick(this)' data-date='"+date+"' data-hour='"+hStr+"'"
        +" style='padding:4px 8px;cursor:pointer'>"+slEv+"</div>"
        +"</div>";
    }}
    h+="</div>";
    g.innerHTML=h;
  }}

  /* ══════════════════════════════════════════════════
     MODAL — appended to document.body to escape overflow:hidden
  ══════════════════════════════════════════════════ */
  function rmOv(){{
    var o=document.getElementById(U+"_ov");
    if(o&&o.parentNode)o.parentNode.removeChild(o);
  }}

  function mkOv(inner){{
    rmOv();
    var o=document.createElement("div");
    o.id=U+"_ov";
    o.style.cssText="position:fixed;inset:0;z-index:9999;background:rgba(0,0,0,.55);"
      +"display:flex;align-items:center;justify-content:center;"
      +"padding:16px;box-sizing:border-box";
    o.onclick=function(e){{if(e.target===o)rmOv();}};
    var box=document.createElement("div");
    box.style.cssText="background:var(--surface,#fff);border-radius:16px;padding:24px;"
      +"width:100%;max-width:460px;box-shadow:0 24px 64px rgba(0,0,0,.4);"
      +"max-height:90vh;overflow-y:auto;box-sizing:border-box";
    box.innerHTML=inner;
    o.appendChild(box);
    document.body.appendChild(o);
    setTimeout(function(){{
      var inp=o.querySelector("input[type=text],input[type=date]");
      if(inp)inp.focus();
    }},40);
  }}

  /* ── Info modal ─────────────────────────────────── */
  function showInfo(ev){{
    var a=A(),ec=ev.color||a;
    /* close button uses data-uid to avoid quote issues */
    var h="<div style='display:flex;align-items:center;gap:10px;margin-bottom:16px'>"
      +"<div style='width:12px;height:12px;border-radius:50%;background:"+ec+";flex-shrink:0'></div>"
      +"<span style='font-size:17px;font-weight:700;color:var(--text)'>"+esc(ev.title)+"</span>"
      +"<button onclick='"+U+"_closeOv()' style='margin-left:auto;background:none;border:none;"
      +"font-size:22px;cursor:pointer;color:var(--text-muted);line-height:1'>\u00d7</button>"
      +"</div>"
      +(ev.date?"<div style='font-size:13px;color:var(--text-muted);margin-bottom:6px'>&#128197; "+esc(ev.date)+"</div>":"")
      +(ev.start_time?"<div style='font-size:13px;color:var(--text-muted);margin-bottom:6px'>&#128336; "
        +ev.start_time+(ev.end_time?" \u2013 "+ev.end_time:"")+"</div>":"")
      +(ev.description?"<div style='font-size:13px;color:var(--text);margin-top:8px;line-height:1.6'>"
        +esc(ev.description)+"</div>":"");
    mkOv(h);
  }}

  /* ── Form modal ─────────────────────────────────── */
  function showForm(ev,date,hourStr){{
    var isNew=!ev,a=A(),defColor=isNew?(COLORS[0]||a):(ev.color||a);
    var eid=isNew?null:ev._id;

    /* color swatches */
    var sw="";
    for(var ci=0;ci<COLORS.length;ci++){{
      var c=COLORS[ci],sel=c===defColor?"3px solid var(--text)":"2px solid transparent";
      /* data-color attribute — no quote issues */
      sw+="<div onclick='"+U+"_pickColor(this)' data-color='"+c+"'"
        +" style='display:inline-block;width:22px;height:22px;border-radius:50%;"
        +"background:"+c+";cursor:pointer;outline:"+sel+";transition:outline .1s'></div>";
    }}

    var IS="width:100%;box-sizing:border-box;padding:9px 12px;border:1px solid var(--border);"
          +"border-radius:8px;font-size:14px;background:var(--surface);color:var(--text);outline:none";
    var LS="font-size:12px;font-weight:600;color:var(--text-muted);display:block;margin-bottom:4px";
    var tdDisplay=(ev&&ev.all_day)?"none":"grid";
    var eidJson=isNew?"null":String(eid);

    var h=
      "<div style='display:flex;align-items:center;margin-bottom:20px'>"
      +"<span style='font-size:17px;font-weight:700;color:var(--text)'>"+(isNew?LBL.new_event:LBL.edit_event)+"</span>"
      +"<button onclick='"+U+"_closeOv()' style='margin-left:auto;background:none;border:none;"
      +"font-size:22px;cursor:pointer;color:var(--text-muted);line-height:1'>\u00d7</button>"
      +"</div>"

      +"<div style='margin-bottom:14px'>"
      +"<label style='"+LS+"'>"+LBL.title_lbl+"</label>"
      +"<input id='"+U+"_ft' type='text' placeholder='"+LBL.title_ph+"' value='"+esc(ev?ev.title:"")+"'"
      +" style='"+IS+"'/></div>"

      +"<div style='margin-bottom:14px'>"
      +"<label style='"+LS+"'>"+LBL.date_lbl+"</label>"
      +"<input id='"+U+"_fd' type='date' value='"+(date||"")+"' style='"+IS+"'/></div>"

      +"<div style='margin-bottom:14px;display:flex;align-items:center;gap:8px'>"
      +"<input type='checkbox' id='"+U+"_fad'"+(ev&&ev.all_day?" checked":"")
      +" onchange='"+U+"_toggleAllDay(this)'"
      +" style='width:16px;height:16px;cursor:pointer'/>"
      +"<label for='"+U+"_fad' style='font-size:13px;color:var(--text);cursor:pointer'>"+LBL.allday_lbl+"</label>"
      +"</div>"

      +"<div id='"+U+"_ftimes' style='display:"+tdDisplay+";grid-template-columns:1fr 1fr;gap:12px;margin-bottom:14px'>"
      +"<div><label style='"+LS+"'>"+LBL.start_lbl+"</label>"
      +"<input id='"+U+"_fs' type='time' value='"+(ev?esc(ev.start_time):(hourStr||""))+"' style='"+IS+"'/></div>"
      +"<div><label style='"+LS+"'>"+LBL.end_lbl+"</label>"
      +"<input id='"+U+"_fe' type='time' value='"+(ev?esc(ev.end_time):"")+"' style='"+IS+"'/></div>"
      +"</div>"

      +"<div style='margin-bottom:14px'>"
      +"<label style='"+LS+"'>"+LBL.desc_lbl+"</label>"
      +"<textarea id='"+U+"_fde' rows='2' placeholder='"+LBL.desc_ph+"'"
      +" style='"+IS+";resize:vertical'>"+esc(ev?ev.description:"")+"</textarea></div>"

      +"<div style='margin-bottom:20px'>"
      +"<label style='"+LS+"'>"+LBL.color_lbl+"</label>"
      +"<input type='hidden' id='"+U+"_fc' value='"+defColor+"'/>"
      +"<div id='"+U+"_swatches' style='display:flex;flex-wrap:wrap;gap:8px'>"+sw+"</div></div>"

      +"<div style='display:flex;gap:8px;justify-content:flex-end;align-items:center'>"
      +(!isNew
        ?"<button onclick='"+U+"_evDel(this)' data-eid='"+eid+"'"
         +" style='padding:9px 18px;border-radius:8px;border:1px solid #ef4444;"
         +"background:transparent;color:#ef4444;font-size:13px;font-weight:600;"
         +"cursor:pointer;margin-right:auto'>"+LBL.delete+"</button>"
        :"")
      +"<button onclick='"+U+"_closeOv()'"
      +" style='padding:9px 18px;border-radius:8px;border:1px solid var(--border);"
      +"background:transparent;color:var(--text);font-size:13px;font-weight:600;cursor:pointer'>"+LBL.cancel+"</button>"
      +"<button onclick='"+U+"_evSave(this)' data-eid='"+eidJson+"'"
      +" style='padding:9px 18px;border-radius:8px;border:none;"
      +"background:"+a+";color:#fff;font-size:13px;font-weight:600;cursor:pointer'>"+LBL.save+"</button>"
      +"</div>";

    mkOv(h);
  }}

  /* ══════════════════════════════════════════════════
     PUBLIC API — all registered on window
  ══════════════════════════════════════════════════ */

  /* close overlay */
  window[U+"_closeOv"]=function(){{rmOv();}};

  /* hover on month cells — show/hide + buttons */
  window[U+"_cellHover"]=function(show){{
    var g=G("grid");if(!g)return;
    var ab=g.getElementsByClassName(U+"_ab");
    for(var i=0;i<ab.length;i++)ab[i].style.opacity=show?"1":"0";
  }};

  /* color swatch picker */
  window[U+"_pickColor"]=function(el){{
    var fc=document.getElementById(U+"_fc");
    if(fc)fc.value=el.dataset.color;
    var sw=document.getElementById(U+"_swatches");
    if(sw){{
      var items=sw.children;
      for(var i=0;i<items.length;i++)items[i].style.outline="2px solid transparent";
    }}
    el.style.outline="3px solid var(--text)";
  }};

  /* toggle all-day checkbox */
  window[U+"_toggleAllDay"]=function(el){{
    var td=document.getElementById(U+"_ftimes");
    if(td)td.style.display=el.checked?"none":"grid";
  }};

  /* event click — el has data-eid */
  window[U+"_evClick"]=function(el){{
    var eid=parseInt(el.dataset.eid,10),ev=getEv(eid);
    if(!ev)return;
    if(EDIT){{showForm(ev,ev.date,ev.start_time||"");return;}}
    if(CB_CLICK){{callCb(CB_CLICK,[ev]);return;}}
    if(ev.url){{window.location.href=ev.url;return;}}
    showInfo(ev);
  }};

  /* open create form — el has data-date, data-hour */
  window[U+"_openCreate"]=function(el){{
    if(!EDIT)return;
    showForm(null,el.dataset.date||ds(CY,CM,CD),el.dataset.hour||"");
  }};

  /* day/slot click — el has data-date, optional data-hour */
  window[U+"_dayClick"]=function(el){{
    var date=el.dataset.date,hourStr=el.dataset.hour||"";
    var p=date.split("-");
    CY=parseInt(p[0],10);CM=parseInt(p[1],10)-1;CD=parseInt(p[2],10);

    if(RANGE&&VIEW==="month"){{
      if(!RS||RE){{RS=date;RE=null;}}
      else{{RE=date<RS?RS:date;if(date<RS)RS=date;}}
    }}else if(VIEW!=="day"){{
      VIEW="day";syncBtns();
    }}

    if(EDIT&&VIEW==="day"&&hourStr){{
      /* pass a fake element with dataset */
      window[U+"_openCreate"]({{dataset:{{date:date,hour:hourStr}}}});
      return;
    }}
    if(CB_DATE)callCb(CB_DATE,[hourStr?(date+"T"+hourStr):date]);
    refresh();
  }};

  /* save form — el has data-eid */
  window[U+"_evSave"]=function(el){{
    var eidRaw=el.dataset.eid;
    var tel=document.getElementById(U+"_ft");
    var title=(tel?tel.value:"").trim();
    if(!title){{if(tel){{tel.style.borderColor="#ef4444";tel.focus();}}return;}}
    var date=(document.getElementById(U+"_fd")||{{}}).value||"";
    var allDay=!!(document.getElementById(U+"_fad")||{{}}).checked;
    var start=allDay?"":(document.getElementById(U+"_fs")||{{}}).value||"";
    var end=allDay?"":(document.getElementById(U+"_fe")||{{}}).value||"";
    var desc=(document.getElementById(U+"_fde")||{{}}).value||"";
    var color=(document.getElementById(U+"_fc")||{{}}).value||"";

    if(eidRaw==="null"||eidRaw===null||eidRaw===undefined){{
      var nev={{_id:NID++,title:title,date:date,start_time:start,end_time:end,
               description:desc,color:color,all_day:allDay,url:""}};
      EVTS.push(nev);idx();rmOv();refresh();
      callCb(CB_CREATE,[nev]);
    }}else{{
      var eid=parseInt(eidRaw,10);
      for(var i=0;i<EVTS.length;i++){{
        if(EVTS[i]._id===eid){{
          var old=Object.assign({{}},EVTS[i]);
          Object.assign(EVTS[i],{{title:title,date:date,start_time:start,end_time:end,
            description:desc,color:color,all_day:allDay}});
          idx();rmOv();refresh();
          callCb(CB_UPDATE,[EVTS[i],old]);
          break;
        }}
      }}
    }}
  }};

  /* delete event — el has data-eid */
  window[U+"_evDel"]=function(el){{
    var eid=parseInt(el.dataset.eid,10),ev=getEv(eid);
    if(!ev)return;
    if(!confirm(LBL.confirm_del+" ("+ev.title+")"))return;
    EVTS=EVTS.filter(function(e){{return e._id!==eid;}});
    idx();rmOv();refresh();
    callCb(CB_DELETE,[ev]);
  }};

  /* navigation */
  window[U+"_prev"]=function(){{
    if(VIEW==="month"){{CM--;if(CM<0){{CM=11;CY--;}}}}
    else if(VIEW==="week"){{var d=new Date(CY,CM,CD-7);CY=d.getFullYear();CM=d.getMonth();CD=d.getDate();}}
    else{{var d=new Date(CY,CM,CD-1);CY=d.getFullYear();CM=d.getMonth();CD=d.getDate();}}
    refresh();
  }};
  window[U+"_next"]=function(){{
    if(VIEW==="month"){{CM++;if(CM>11){{CM=0;CY++;}}}}
    else if(VIEW==="week"){{var d=new Date(CY,CM,CD+7);CY=d.getFullYear();CM=d.getMonth();CD=d.getDate();}}
    else{{var d=new Date(CY,CM,CD+1);CY=d.getFullYear();CM=d.getMonth();CD=d.getDate();}}
    refresh();
  }};
  window[U+"_today"]=function(){{
    CY=NOW.getFullYear();CM=NOW.getMonth();CD=NOW.getDate();refresh();
  }};
  window[U+"_setView"]=function(v){{VIEW=v;syncBtns();refresh();}};

  document.addEventListener("keydown",function(e){{if(e.key==="Escape")rmOv();}});

  function refresh(){{
    layout();renderHeader();
    if(VIEW==="month")renderMonth();
    else if(VIEW==="week")renderWeek();
    else renderDay();
    syncBtns();
  }}
  refresh();
}})();
</script>
"""

        # ── toolbar ────────────────────────────────────────────
        view_btns = ""
        if self.show_views:
            vmap = (
                [("month", "Mes"), ("week", "Semana"), ("day", "D\u00eda")]
                if self.locale == "es"
                else [("month", "Month"), ("week", "Week"), ("day", "Day")]
            )
            for vk, vl in vmap:
                act = vk == self.initial_view
                view_btns += (
                    f'<button id="{uid}_vbtn_{vk}" onclick="{uid}_setView(\'{vk}\')" '
                    f'style="padding:6px 14px;font-size:13px;border:1px solid var(--border);'
                    f"border-radius:6px;cursor:pointer;font-weight:500;"
                    f'background:{"var(--accent,#6366f1)" if act else "var(--surface-2,var(--surface))"};'
                    f'color:{"#fff" if act else "var(--text)"}">{vl}</button>'
                )

        today_lbl = "Hoy" if self.locale == "es" else "Today"
        today_btn = (
            (
                f'<button onclick="{uid}_today()" '
                f'style="padding:6px 14px;font-size:13px;border:1px solid var(--border);'
                f"border-radius:6px;cursor:pointer;background:var(--surface-2,var(--surface));"
                f'color:var(--text);font-weight:500">{today_lbl}</button>'
            )
            if self.show_today
            else ""
        )

        new_lbl = "\uff0b Nuevo evento" if self.locale == "es" else "\uff0b New event"
        new_btn = (
            (
                f'<button onclick="{uid}_openCreate(this)" data-date="" data-hour="" '
                f'style="padding:6px 14px;font-size:13px;border:none;'
                f"border-radius:6px;cursor:pointer;background:var(--accent,#6366f1);"
                f'color:#fff;font-weight:500">{new_lbl}</button>'
            )
            if self.editable
            else ""
        )

        # ── day names header ────────────────────────────────────
        day_data = self.DAYS_ES if self.locale == "es" else self.DAYS_EN
        ordered = day_data[self.first_day :] + day_data[: self.first_day]
        day_names_html = "".join(
            f'<div style="padding:8px 0;text-align:center;font-size:12px;'
            f'font-weight:600;color:var(--text-muted)">{dn}</div>'
            for dn in ordered
        )

        return (
            f'<div id="{uid}" style="{wrapper_style}">'
            + f'<div style="display:flex;align-items:center;gap:8px;padding:12px 16px;'
            f'border-bottom:1px solid var(--border);flex-shrink:0;flex-wrap:wrap">'
            + f'<button onclick="{uid}_prev()" style="width:32px;height:32px;display:flex;'
            f"align-items:center;justify-content:center;border:1px solid var(--border);"
            f"border-radius:6px;cursor:pointer;background:var(--surface-2,var(--surface));"
            f'color:var(--text);font-size:18px;line-height:1">&#8249;</button>'
            + f'<button onclick="{uid}_next()" style="width:32px;height:32px;display:flex;'
            f"align-items:center;justify-content:center;border:1px solid var(--border);"
            f"border-radius:6px;cursor:pointer;background:var(--surface-2,var(--surface));"
            f'color:var(--text);font-size:18px;line-height:1">&#8250;</button>'
            + f'<span id="{uid}_title" style="font-size:16px;font-weight:700;color:var(--text);flex:1"></span>'
            + today_btn
            + (
                f'<div style="display:flex;gap:4px">{view_btns}</div>'
                if self.show_views
                else ""
            )
            + new_btn
            + "</div>"
            + f'<div id="{uid}_daynames" style="display:grid;grid-template-columns:repeat(7,1fr);'
            f'border-bottom:1px solid var(--border);flex-shrink:0">{day_names_html}</div>'
            + f'<div id="{uid}_grid" style="flex:1;overflow:auto;'
            f'display:grid;grid-template-columns:repeat(7,1fr)"></div>' + "</div>" + js
        )
