"""
Martin — Text Widgets

Todo lo que sea palabras vive aquí.

    Text       — texto en línea (<span>), el más común
    Heading    — título semántico h1-h6
    Paragraph  — párrafo de texto (<p>)
    Link       — enlace (<a>)
    Code       — código inline o en bloque con syntax highlighting
"""

import json as _json

from ..widget import Widget
from .._context import get_current_path
from .._routing import paths_match


# =============================================================================
# Text
# =============================================================================


class Text(Widget):
    """
    Texto en línea (span). El widget de texto más común.

        Text("Hola mundo")
        Text("Subtítulo", color="var(--text-muted)", style=TextStyle(size=14))

    Para párrafos largos usa Paragraph.
    Para títulos usa Heading.
    """

    def __init__(self, content=None, id=None, child=None, children=None, **kwargs):
        self._props = Widget._extract_props(kwargs)
        self.content = content
        self.id = id
        self.child = child
        self.children = children

    def render(self):
        inline = self._resolve_props()
        attrs = self._attrs(style=inline or None, id=self.id)
        inner = self._resolve_inner(self.content, self.child, self.children)
        return self._wrap_url(f"<span{attrs}>{inner}</span>")


# =============================================================================
# Heading
# =============================================================================


class Heading(Widget):
    """
    Título semántico. Usa level para jerarquía (h1-h6).

        Heading("Bienvenido")              # h1 por defecto
        Heading("Sección", level=2)        # h2
        Heading("Subtítulo", level=3, color="var(--text-muted)")

    Combina con GradientText para títulos llamativos:
        Heading(GradientText.aurora("Título"), level=1)
    """

    def __init__(
        self, content=None, level=1, id=None, child=None, children=None, **kwargs
    ):
        self._props = Widget._extract_props(kwargs)
        self.content = content
        self.level = max(1, min(6, level))
        self.id = id
        self.child = child
        self.children = children

    def render(self):
        inline = self._resolve_props()
        tag = f"h{self.level}"
        attrs = self._attrs(style=inline or None, id=self.id)
        inner = self._resolve_inner(self.content, self.child, self.children)
        return self._wrap_url(f"<{tag}{attrs}>{inner}</{tag}>")


# =============================================================================
# Paragraph
# =============================================================================


class Paragraph(Widget):
    """
    Párrafo de texto (<p>). Para bloques de texto de una o varias líneas.

        Paragraph("Esta es una descripción más larga del producto...")
        Paragraph("Texto", style=TextStyle(size=16, leading=1.8), color="var(--text-muted)")
    """

    def __init__(self, content=None, id=None, child=None, children=None, **kwargs):
        self._props = Widget._extract_props(kwargs)
        self.content = content
        self.id = id
        self.child = child
        self.children = children

    def render(self):
        inline = self._resolve_props("margin:0; line-height:1.6")
        attrs = self._attrs(style=inline or None, id=self.id)
        inner = self._resolve_inner(self.content, self.child, self.children)
        return self._wrap_url(f"<p{attrs}>{inner}</p>")


# =============================================================================
# Link
# =============================================================================


class Link(Widget):
    """
    Enlace (<a>). Para navegación interna o externa.

        Link("Ver más", href="/productos")
        Link("GitHub", href="https://github.com", target="_blank")
        Link(Button("Ir"), href="/ruta")    # cualquier widget como hijo
    """

    def __init__(
        self,
        content=None,
        href="#",
        target=None,
        child=None,
        children=None,
        auto_active=True,
        class_name=None,
        **kwargs,
    ):
        self._props = Widget._extract_props(kwargs)
        self.content = content
        self.href = href
        self.target = target
        self.child = child
        self.children = children
        self.auto_active = auto_active
        self.class_name = class_name

    def _is_active(self):
        if not self.auto_active:
            return False
        if self.target and self.target != "_self":
            return False
        return paths_match(get_current_path(), self.href)

    def _default_a11y_attrs(self):
        plain = self._to_plain_text(self.content)
        if plain:
            return {"aria-label": plain}
        return {}

    def render(self):
        is_active = self._is_active()
        inline = self._resolve_props("color:var(--accent); text-decoration:underline")
        if is_active:
            inline = (inline + "; " if inline else "") + "color:var(--accent); font-weight:600"

        classes = []
        if self.class_name:
            classes.append(self.class_name)
        if is_active:
            classes.extend(["martin-link-active", "mn-active"])

        attrs = self._attrs(
            href=self.href,
            target=self.target,
            style=inline or None,
            aria_current="page" if is_active else None,
            **{"class": " ".join(classes) or None},
        )
        inner = self._resolve_inner(self.content, self.child, self.children)
        return f"<a{attrs}>{inner}</a>"


# =============================================================================
# Code
# =============================================================================


class Code(Widget):
    """
    Código inline o en bloque con syntax highlighting, copia y edición.

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

    Parámetros:
        content      str     el código
        language     str     python|javascript|typescript|html|css|json|sql|bash|rust|go|...
        block        bool    fuerza modo bloque aunque no haya language
        copy         bool    botón copiar (default True si block o language)
        line_numbers bool    números de línea (default False)
        filename     str     etiqueta en la cabecera del bloque
        theme        str     dark|light|auto (default auto, sigue al tema)
        max_height   int     altura máx con scroll en px
        editable     bool    textarea editable con fuente monoespaciada
        id           str     id del elemento HTML
    """

    _id_counter = 0

    def __init__(
        self,
        content="",
        language=None,
        block=False,
        copy=None,
        line_numbers=False,
        filename=None,
        theme="auto",
        max_height=None,
        editable=False,
        id=None,
        **kwargs,
    ):
        self._props = Widget._extract_props(kwargs)
        self.content = content
        self.language = language
        self.block = block
        self.copy = copy if copy is not None else bool(language or block)
        self.line_numbers = line_numbers
        self.filename = filename
        self.theme = theme
        self.max_height = max_height
        self.editable = editable
        Code._id_counter += 1
        self.uid = id or f"code_{Code._id_counter}"

    # ── helpers ──────────────────────────────────────────────────────────────

    @staticmethod
    def _esc(text):
        return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

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
            '.prism-light pre[class*="language-"],.prism-light code[class*="language-"]'
            "{background:#f8f8f8!important;color:#383a42!important;text-shadow:none!important}"
            ".prism-light .token.comment{color:#a0a1a7!important}"
            ".prism-light .token.keyword{color:#a626a4!important}"
            ".prism-light .token.string{color:#50a14f!important}"
            ".prism-light .token.number{color:#986801!important}"
            ".prism-light .token.function{color:#4078f2!important}"
            "@media(prefers-color-scheme:light){"
            '.prism-auto pre[class*="language-"],.prism-auto code[class*="language-"]'
            "{background:#f8f8f8!important;color:#383a42!important;text-shadow:none!important}"
            ".prism-auto .token.comment{color:#a0a1a7!important}"
            ".prism-auto .token.keyword{color:#a626a4!important}"
            ".prism-auto .token.string{color:#50a14f!important}"
            ".prism-auto .token.number{color:#986801!important}"
            ".prism-auto .token.function{color:#4078f2!important}"
            "}</style>"
            "<script>(function(){if(window._prismOK)return;window._prismOK=true;})();</script>"
        )

    def _copy_btn(self, content):
        uid = self.uid
        c_js = _json.dumps(content)
        btn_id = uid + "_copy"
        btn_js = _json.dumps(btn_id)
        return (
            f'<button id="{btn_id}" title="Copiar" '
            f'style="background:none;border:1px solid rgba(128,128,128,0.25);'
            f"border-radius:5px;cursor:pointer;font-size:11px;"
            f"color:var(--text-muted);padding:3px 10px;"
            f'transition:all .15s;font-family:inherit;white-space:nowrap" '
            f"onmouseover=\"this.style.borderColor='var(--accent)';this.style.color='var(--accent)'\" "
            f"onmouseout=\"this.style.borderColor='rgba(128,128,128,0.25)';this.style.color='var(--text-muted)'\" "
            f">Copiar</button>"
            f"<script>(function(){{"
            f"  var btn=document.getElementById({btn_js});"
            f'  if(!btn||btn.dataset.copyBound==="1")return;'
            f'  btn.dataset.copyBound="1";'
            f"  var txt={c_js};"
            f"  function ok(){{"
            f'    btn.textContent="\u2713 Copiado";'
            f'    btn.style.color="#22c55e";btn.style.borderColor="#22c55e";'
            f'    setTimeout(function(){{btn.textContent="Copiar";'
            f'      btn.style.color="";btn.style.borderColor="";}},2000);'
            f"  }}"
            f"  function fallback(){{"
            f'    var t=document.createElement("textarea");t.value=txt;'
            f"    document.body.appendChild(t);t.select();"
            f'    document.execCommand("copy");document.body.removeChild(t);ok();'
            f"  }}"
            f'  btn.addEventListener("click",function(){{'
            f"    if(navigator.clipboard&&window.isSecureContext){{"
            f"      navigator.clipboard.writeText(txt).then(ok).catch(fallback);"
            f"    }}else{{fallback();}}"
            f"  }});"
            f"}})();</script>"
        )

    # ── render ───────────────────────────────────────────────────────────────

    def render(self):
        uid = self.uid
        content = str(self.content)
        escaped = self._esc(content)
        extra = self._resolve_props()
        is_block = bool(self.block or self.language or self.editable)

        # ── Inline ────────────────────────────────────────────────────────
        if not is_block:
            base = (
                "display:inline;padding:2px 6px;border-radius:4px;"
                "font-family:'Fira Code','Cascadia Code',monospace;font-size:0.875em;"
                "background:var(--surface-2,rgba(128,128,128,0.12));"
                "color:var(--accent,#6366f1)"
            )
            inline = self._resolve_props(base)
            id_attr = f' id="{uid}"'
            style_attr = f' style="{inline}"' if inline else ""
            return self._wrap_url(f"<code{id_attr}{style_attr}>{escaped}</code>")

        # ── Block ────────────────────────────────────────────────────────
        prism = self._prism_assets()
        lang_class = f"language-{self.language}" if self.language else ""
        theme_cls = f"prism-{self.theme}"
        mono_font = "'Fira Code','Cascadia Code','JetBrains Mono',monospace"
        scroll_css = (
            f"max-height:{self.max_height}px;overflow-y:auto;"
            if self.max_height
            else ""
        )
        bg = "#1e1e2e"

        # Header bar (filename + copy button)
        header_html = ""
        if self.filename or self.copy:
            fname_html = (
                f'<span style="font-family:monospace;font-size:12px;'
                f'color:rgba(205,214,244,0.55);letter-spacing:0.02em">{self.filename}</span>'
                if self.filename
                else "<span></span>"
            )
            copy_part = self._copy_btn(content) if self.copy else ""
            header_html = (
                f'<div style="display:flex;align-items:center;justify-content:space-between;'
                f"padding:8px 14px;border-bottom:1px solid rgba(255,255,255,0.06);"
                f'background:rgba(0,0,0,0.2)">{fname_html}{copy_part}</div>'
            )

        # ── Editable textarea ─────────────────────────────────────────────
        if self.editable:
            n_rows = max(content.count("\n") + 1, 3)
            wrapper_style = f"border-radius:10px;overflow:hidden;border:1px solid var(--border);background:{bg}"
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
                + f'<div class="{theme_cls}" style="{wrapper_style}">'
                + header_html
                + f'<textarea id="{uid}" rows="{n_rows}" '
                + 'spellcheck="false" autocorrect="off" autocapitalize="off" '
                + f'style="{ta_style}">'
                + escaped
                + "</textarea></div>"
            )

        # ── Display block ─────────────────────────────────────────────────
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
                f'user-select:none;text-align:right">{i + 1}</span>'
                for i in range(len(lines))
            )
            gutter = (
                f'<div style="font-family:{mono_font};font-size:13px;'
                f"line-height:1.6;padding:16px 14px 16px 16px;"
                f"background:rgba(0,0,0,0.18);"
                f"border-right:1px solid rgba(255,255,255,0.06);"
                f'flex-shrink:0;user-select:none;min-width:2em">' + nums_html + "</div>"
            )
            inner = (
                '<div style="display:flex;overflow:hidden">'
                + gutter
                + f'<pre style="{pre_style}"><code class="{lang_class}">{escaped}</code></pre>'
                + "</div>"
            )
        else:
            inner = f'<pre style="{pre_style}"><code class="{lang_class}">{escaped}</code></pre>'

        hl_js = (
            f"<script>(function(){{"
            f"function _hl(){{"
            f'  if(typeof Prism==="undefined"){{setTimeout(_hl,120);return;}}'
            f"  var w=document.getElementById({_json.dumps(uid)});"
            f'  if(w){{var c=w.querySelector("code");if(c){{Prism.highlightElement(c);return;}}}}'
            f"  Prism.highlightAll();"
            f"}}_hl();"
            f"}})();</script>"
        )

        return (
            prism
            + f'<div id="{uid}" class="{theme_cls}" style="{wrapper_style}">'
            + header_html
            + inner
            + "</div>"
            + hl_js
        )
