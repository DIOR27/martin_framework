"""
Martin — Widgets
Every widget accepts universal style props:
    style, padding, margin, width, height,
    color, background, radius, shadow, opacity, hidden
"""

from .widget import Widget
from .styles import resolve_styles, Border, Padding, Margin, Shadow, Size, Background


# ══════════════════════════════════════════════════════════
# LAYOUT
# ══════════════════════════════════════════════════════════


class Container(Widget):
    """
    Container(child=Text("hi"), padding=16, radius=8, background="#fff")
    Container(child=Text("hi"), style=[Border(radius=8), Shadow.md()])
    """

    def __init__(
        self, child=None, children=None, tag="div", id=None, class_name=None, **kwargs
    ):
        self._props = Widget._extract_props(kwargs)
        if child and not children:
            children = [child]
        self.children = children or []
        self.tag = tag
        self.id = id
        self.class_name = class_name

    def render(self):
        inline = self._resolve_props()
        inner = self._render_children(self.children)
        attrs = self._attrs(
            style=inline or None, id=self.id, **{"class": self.class_name}
        )
        return f"<{self.tag}{attrs}>{inner}</{self.tag}>"


class Row(Widget):
    """
    Row(children=[...], gap=8, align="center", padding=16, background="#f0f0f0")
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
            f"display: flex; flex-direction: row; gap: {self.gap}px; "
            f"align-items: {self.align}; justify-content: {self.justify}"
            + ("; flex-wrap: wrap" if self.wrap else "")
        )
        inline = self._resolve_props(base)
        inner = self._render_children(self.children)
        attrs = self._attrs(style=inline, id=self.id, **{"class": self.class_name})
        return f"<div{attrs}>{inner}</div>"


class Column(Widget):
    """
    Column(children=[...], gap=12, padding=24, background="#fff", radius=12)
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
            f"display: flex; flex-direction: column; gap: {self.gap}px; "
            f"align-items: {self.align}; justify-content: {self.justify}"
        )
        inline = self._resolve_props(base)
        inner = self._render_children(self.children)
        attrs = self._attrs(style=inline, id=self.id, **{"class": self.class_name})
        return f"<div{attrs}>{inner}</div>"


class Card(Widget):
    """
    Card(children=[...], padding=24, radius=16, shadow=True)
    Card(children=[...], background="#1e1e2e", radius=12, shadow=Shadow.lg())
    """

    def __init__(self, children=None, child=None, id=None, class_name=None, **kwargs):
        self._props = Widget._extract_props(kwargs)
        if child and not children:
            children = [child]
        self.children = children or []
        self.id = id
        self.class_name = class_name

    def render(self):
        base = "background: #ffffff; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.12)"
        inline = self._resolve_props(base)
        inner = self._render_children(self.children)
        attrs = self._attrs(style=inline, id=self.id, **{"class": self.class_name})
        return f"<div{attrs}>{inner}</div>"


class Stack(Widget):
    def __init__(self, children=None, **kwargs):
        self._props = Widget._extract_props(kwargs)
        self.children = children or []

    def render(self):
        inline = self._resolve_props("position: relative")
        parts = []
        for i, child in enumerate(self.children):
            rendered = child.render() if isinstance(child, Widget) else str(child)
            if i == 0:
                parts.append(rendered)
            else:
                parts.append(
                    f'<div style="position:absolute;top:0;left:0;width:100%;height:100%">{rendered}</div>'
                )
        return f'<div style="{inline}">{"".join(parts)}</div>'


class Grid(Widget):
    """
    Grid(children=[...], columns=3, gap=16, padding=24)
    """

    def __init__(self, children=None, columns=2, gap=16, **kwargs):
        self._props = Widget._extract_props(kwargs)
        self.children = children or []
        self.columns = columns
        self.gap = gap

    def render(self):
        cols = (
            self.columns
            if isinstance(self.columns, str)
            else f"repeat({self.columns}, 1fr)"
        )
        base = f"display: grid; grid-template-columns: {cols}; gap: {self.gap}px"
        inline = self._resolve_props(base)
        inner = self._render_children(self.children)
        return f'<div style="{inline}">{inner}</div>'


class Spacer(Widget):
    def __init__(self, size=None):
        self._props = {}
        self.size = size

    def render(self):
        if self.size:
            return f'<div style="width:{self.size}px;height:{self.size}px;flex-shrink:0"></div>'
        return '<div style="flex:1"></div>'


class Divider(Widget):
    def __init__(self, color="#e5e7eb", thickness=1, vertical=False, **kwargs):
        self._props = Widget._extract_props(kwargs)
        self.color = color
        self.thickness = thickness
        self.vertical = vertical

    def render(self):
        if self.vertical:
            base = f"width:{self.thickness}px;height:100%;background:{self.color};flex-shrink:0"
        else:
            base = f"height:{self.thickness}px;width:100%;background:{self.color};margin:4px 0"
        inline = self._resolve_props(base)
        return f'<div style="{inline}"></div>'


# ══════════════════════════════════════════════════════════
# TEXT
# ══════════════════════════════════════════════════════════


class Text(Widget):
    """
    Text("Hola", color="#333", padding=8)
    Text("Hola", style=TextStyle(size=18, weight="bold"))
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
        return f"<span{attrs}>{inner}</span>"


class Heading(Widget):
    """
    Heading("Título", level=1, color="#111", margin=16)
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
        attrs = self._attrs(style=inline or None, id=self.id)
        tag = f"h{self.level}"
        inner = self._resolve_inner(self.content, self.child, self.children)
        return f"<{tag}{attrs}>{inner}</{tag}>"


class Paragraph(Widget):
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
        return f"<p{attrs}>{inner}</p>"


class Link(Widget):
    """
    Link("Click", href="/page", color="#3b82f6")
    """

    def __init__(
        self, content=None, href="#", target=None, child=None, children=None, **kwargs
    ):
        self._props = Widget._extract_props(kwargs)
        self.content = content
        self.href = href
        self.target = target
        self.child = child
        self.children = children

    def render(self):
        inline = self._resolve_props()
        attrs = self._attrs(href=self.href, target=self.target, style=inline or None)
        inner = self._resolve_inner(self.content, self.child, self.children)
        return f"<a{attrs}>{inner}</a>"


class Code(Widget):
    def __init__(self, content, block=False, language=None, **kwargs):
        self._props = Widget._extract_props(kwargs)
        self.content = content
        self.block = block
        self.language = language

    def render(self):
        inline = self._resolve_props()
        if self.block:
            attrs = self._attrs(style=inline or None)
            lang = f' class="language-{self.language}"' if self.language else ""
            return f"<pre{attrs}><code{lang}>{self.content}</code></pre>"
        attrs = self._attrs(style=inline or None)
        return f"<code{attrs}>{self.content}</code>"


# ══════════════════════════════════════════════════════════
# MEDIA
# ══════════════════════════════════════════════════════════


class Image(Widget):
    """
    Image("foto.jpg", radius=12, width=200, height=150)
    Image("foto.jpg", style=[Border(radius=8), Shadow.md()])
    """

    def __init__(self, src, alt="", id=None, class_name=None, **kwargs):
        self._props = Widget._extract_props(kwargs)
        self.src = src
        self.alt = alt
        self.id = id
        self.class_name = class_name

    def render(self):
        inline = self._resolve_props()
        attrs = self._attrs(
            src=self.src,
            alt=self.alt,
            style=inline or None,
            id=self.id,
            **{"class": self.class_name},
        )
        return f"<img{attrs}>"


class Video(Widget):
    def __init__(
        self, src, controls=True, autoplay=False, loop=False, muted=False, **kwargs
    ):
        self._props = Widget._extract_props(kwargs)
        self.src = src
        self.controls = controls
        self.autoplay = autoplay
        self.loop = loop
        self.muted = muted

    def render(self):
        inline = self._resolve_props()
        attrs = self._attrs(
            controls=self.controls,
            autoplay=self.autoplay,
            loop=self.loop,
            muted=self.muted,
            style=inline or None,
        )
        return f'<video{attrs}><source src="{self.src}"></video>'


class Icon(Widget):
    """Icon("🚀", size=24, margin=8)"""

    def __init__(self, icon=None, size=20, child=None, children=None, **kwargs):
        self._props = Widget._extract_props(kwargs)
        self.icon = icon
        self.size = size
        self.child = child
        self.children = children

    def render(self):
        base = f"font-size: {self.size}px; line-height: 1; display:inline-flex; align-items:center"
        inline = self._resolve_props(base)
        inner = self._resolve_inner(self.icon, self.child, self.children)
        return f'<span style="{inline}" aria-hidden="true">{inner}</span>'


# ══════════════════════════════════════════════════════════
# INPUT / INTERACTIVE
# ══════════════════════════════════════════════════════════


class Button(Widget):
    """
    Button("Guardar")
    Button("Guardar", background="#e11d48", color="white", radius=12, padding=16)
    Button("Cancelar", variant="ghost", margin=8)
    """

    VARIANTS = {
        "primary": "background: #3b82f6; color: #fff; border: none",
        "secondary": "background: #f3f4f6; color: #374151; border: 1px solid #d1d5db",
        "danger": "background: #ef4444; color: #fff; border: none",
        "ghost": "background: transparent; color: #374151; border: 1px solid #d1d5db",
        "link": "background: transparent; color: #3b82f6; border: none; text-decoration: underline",
    }

    def __init__(
        self,
        label,
        variant="primary",
        href=None,
        disabled=False,
        id=None,
        class_name=None,
        on_click=None,
        **kwargs,
    ):
        self._props = Widget._extract_props(kwargs)
        self.label = label
        self.variant = variant
        self.href = href
        self.disabled = disabled
        self.id = id
        self.class_name = class_name
        self.on_click = on_click  # ApiCall(...) instance

    def render(self):
        import uuid as _uuid

        base = (
            self.VARIANTS.get(self.variant, self.VARIANTS["primary"])
            + "; padding: 8px 16px; border-radius: 6px; cursor: pointer; "
            "font-size: 14px; font-weight: 500; display: inline-flex; "
            "align-items: center; gap: 6px; text-decoration: none"
        )
        inline = self._resolve_props(base)
        inner = self.label.render() if isinstance(self.label, Widget) else self.label

        # Generate stable id if on_click needs it and none was given
        btn_id = self.id or ("btn_" + _uuid.uuid4().hex[:8] if self.on_click else None)

        if self.href:
            attrs = self._attrs(
                href=self.href, style=inline, id=btn_id, **{"class": self.class_name}
            )
            return f"<a{attrs}>{inner}</a>"

        attrs = self._attrs(
            style=inline,
            disabled=self.disabled,
            id=btn_id,
            **{"class": self.class_name},
        )
        html = f"<button{attrs}>{inner}</button>"

        if self.on_click and btn_id:
            js = self.on_click.to_js(btn_id)
            html += (
                "<script>"
                "document.getElementById("
                + repr(btn_id)
                + ").addEventListener('click',function(){"
                + js
                + "});"
                "</script>"
            )

        return html


class TextField(Widget):
    """
    TextField(placeholder="Nombre", radius=8, padding=12, width="100%")
    """

    def __init__(
        self,
        placeholder="",
        value="",
        type="text",
        name=None,
        id=None,
        disabled=False,
        **kwargs,
    ):
        self._props = Widget._extract_props(kwargs)
        self.placeholder = placeholder
        self.value = value
        self.type = type
        self.name = name
        self.id = id
        self.disabled = disabled

    def render(self):
        base = (
            "padding: 8px 12px; border: 1px solid var(--border-input); border-radius: 6px; "
            "font-size: 14px; outline: none; width: 100%; box-sizing: border-box; "
            "background: var(--input-bg); color: var(--input-color)"
        )
        inline = self._resolve_props(base)
        attrs = self._attrs(
            type=self.type,
            placeholder=self.placeholder,
            value=self.value or None,
            name=self.name,
            style=inline,
            id=self.id,
            disabled=self.disabled,
        )
        return f"<input{attrs}>"


class Checkbox(Widget):
    """Checkbox(label="Aceptar", checked=False, margin=8)"""

    def __init__(self, label="", checked=False, name=None, **kwargs):
        self._props = Widget._extract_props(kwargs)
        self.label = label
        self.checked = checked
        self.name = name

    def render(self):
        base = "display: flex; align-items: center; gap: 8px; color: var(--text)"
        inline = self._resolve_props(base)
        checked_attr = " checked" if self.checked else ""
        name_attr = f' name="{self.name}"' if self.name else ""
        return (
            f'<label style="{inline}">'
            f'<input type="checkbox"{checked_attr}{name_attr}>'
            f"<span>{self.label}</span></label>"
        )


class Select(Widget):
    """
    Select(options=["A","B","C"], radius=8, width="100%")
    Select(options=[("es","Español"),...], search=True, padding=10)
    """

    _id_counter = 0

    def __init__(
        self,
        options=None,
        value=None,
        search=False,
        placeholder="Seleccionar...",
        name=None,
        id=None,
        **kwargs,
    ):
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
        selected_label = next(
            (l for v, l in opts if v == selected_val), self.placeholder
        )

        if not self.search:
            base = (
                "padding: 8px 12px; border: 1px solid var(--border-input); border-radius: 6px; "
                "font-size: 14px; background: var(--input-bg); color: var(--input-color); cursor: pointer; width: 100%"
            )
            inline = f"{base}; {extra}" if extra else base
            opt_tags = "".join(
                f'<option value="{v}"{"selected" if v == selected_val else ""}>{l}</option>'
                for v, l in opts
            )
            name_attr = f' name="{self.name}"' if self.name else ""
            return f'<select id="{self.uid}" style="{inline}"{name_attr}>{opt_tags}</select>'

        wrapper_style = f"position: relative; width: 100%; font-size: 14px; {extra}"
        hidden_input = (
            f'<input type="hidden" name="{self.name}" id="{self.uid}_val" value="{selected_val}">'
            if self.name
            else f'<input type="hidden" id="{self.uid}_val" value="{selected_val}">'
        )

        uid = self.uid

        def make_opt(v, l):
            sel = "1" if v == selected_val else "0"
            weight = "600" if v == selected_val else "400"
            # Build onclick safely — no nested f-string escaping
            onclick = (
                "pwSelectPick('"
                + uid
                + "','"
                + v
                + "','"
                + l.replace("'", "\\'")
                + "')"
            )
            return (
                '<div class="pw-opt"'
                ' data-val="' + v + '"'
                ' data-label="' + l + '"'
                ' onclick="' + onclick + '"'
                ' data-sel="' + sel + '"'
                ' style="padding:10px 14px;cursor:pointer;font-size:14px;font-weight:'
                + weight
                + '">'
                + l
                + "</div>"
            )

        opt_items = "".join(make_opt(v, l) for v, l in opts)

        return (
            f"<style>"
            + f"#{uid}_list .pw-opt{{color:var(--text);background:transparent;border-radius:6px;transition:background .12s}}"
            + f"#{uid}_list .pw-opt:hover{{background:var(--surface-2)}}"
            + f'#{uid}_list .pw-opt[data-sel="1"]{{background:rgba(99,102,241,0.15);color:var(--accent);font-weight:600}}'
            + f"</style>"
            + f'<div id="{uid}_wrap" style="{wrapper_style}">'
            + f"  {hidden_input}"
            + f'  <div id="{uid}_btn" onclick="pwSelectToggle(\'{uid}\')" '
            + f'    style="display:flex;align-items:center;justify-content:space-between;'
            + f"           padding:8px 14px;border:1px solid var(--border-input);border-radius:6px;"
            + f'           background:var(--input-bg);cursor:pointer;user-select:none;gap:8px;transition:border-color .2s">'
            + f'    <span id="{uid}_label" style="color:var(--input-color);flex:1;font-size:14px">{selected_label}</span>'
            + f'    <svg id="{uid}_arrow" width="12" height="12" viewBox="0 0 12 12" '
            + f'         style="flex-shrink:0;transition:transform .2s;opacity:0.5">'
            + f'      <path d="M2 4l4 4 4-4" stroke="currentColor" stroke-width="1.5" fill="none" stroke-linecap="round"/>'
            + f"    </svg>"
            + f"  </div>"
            + f'  <div id="{uid}_drop" '
            + f'    style="display:none;position:absolute;top:calc(100% + 6px);left:0;right:0;'
            + f"           z-index:9999;border:1px solid var(--border-input);border-radius:10px;"
            + f"           box-shadow:0 12px 40px rgba(0,0,0,0.25);overflow:hidden;"
            + f'           background:var(--dropdown-bg)">'
            + f'    <div style="padding:8px 8px 6px;border-bottom:1px solid var(--border)">'
            + f'      <input id="{uid}_search" type="text" placeholder="Buscar..."'
            + f"        oninput=\"pwSelectFilter('{uid}',this.value)\""
            + f'        style="width:100%;padding:7px 10px;border:1px solid var(--border-input);'
            + f"               border-radius:6px;font-size:13px;outline:none;box-sizing:border-box;"
            + f'               background:var(--input-bg);color:var(--input-color)">'
            + f"    </div>"
            + f'    <div id="{uid}_list" style="max-height:220px;overflow-y:auto;padding:6px">'
            + f"      {opt_items}"
            + f"    </div>"
            + f"  </div>"
            + f"</div>"
            + "<script>"
            + "(function(){if(window._pwSelInit)return;window._pwSelInit=true;"
            + "window.pwSelectToggle=function(uid){"
            + '  var d=document.getElementById(uid+"_drop"),'
            + '      a=document.getElementById(uid+"_arrow"),'
            + '      b=document.getElementById(uid+"_btn"),'
            + '      o=d.style.display!=="none";'
            + '  document.querySelectorAll("[id$=_drop]").forEach(function(el){'
            + '    if(el.id!==uid+"_drop"){el.style.display="none";'
            + '      var x=document.getElementById(el.id.replace("_drop","_arrow"));'
            + '      if(x)x.style.transform="";'
            + '      var bx=document.getElementById(el.id.replace("_drop","_btn"));'
            + '      if(bx)bx.style.borderColor="";}'
            + "  });"
            + '  if(o){d.style.display="none";a.style.transform="";b.style.borderColor="";}'
            + '  else{d.style.display="block";a.style.transform="rotate(180deg)";'
            + '    b.style.borderColor="var(--accent)";'
            + '    setTimeout(function(){var s=document.getElementById(uid+"_search");'
            + '      if(s){s.value="";s.focus();pwSelectFilter(uid,"");}},30);}'
            + "};"
            + "window.pwSelectFilter=function(uid,q){"
            + '  document.querySelectorAll("#"+uid+"_list .pw-opt").forEach(function(i){'
            + '    i.style.display=i.getAttribute("data-label").toLowerCase().includes(q.toLowerCase())?"block":"none";'
            + "  });"
            + "};"
            + "window.pwSelectPick=function(uid,val,label){"
            + '  document.getElementById(uid+"_val").value=val;'
            + '  document.getElementById(uid+"_label").textContent=label;'
            + '  document.getElementById(uid+"_drop").style.display="none";'
            + '  document.getElementById(uid+"_arrow").style.transform="";'
            + '  document.getElementById(uid+"_btn").style.borderColor="";'
            + '  document.querySelectorAll("#"+uid+"_list .pw-opt").forEach(function(el){'
            + '    var s=el.getAttribute("data-val")===val;'
            + '    el.setAttribute("data-sel",s?"1":"0");'
            + '    el.style.fontWeight=s?"600":"400";'
            + "  });"
            + "};"
            + 'document.addEventListener("click",function(e){'
            + '  if(!e.target.closest("[id$=_wrap]")){'
            + '    document.querySelectorAll("[id$=_drop]").forEach(function(el){'
            + '      el.style.display="none";'
            + '      var a=document.getElementById(el.id.replace("_drop","_arrow"));'
            + '      if(a)a.style.transform="";'
            + '      var b=document.getElementById(el.id.replace("_drop","_btn"));'
            + '      if(b)b.style.borderColor="";'
            + "    });"
            + "  }"
            + "});"
            + "})();</script>"
        )


class MultiSelect(Widget):
    """
    MultiSelect(options=["A","B","C"], values=["A"], radius=8)
    MultiSelect(options=[("py","Python"),...], values=["py"], padding=10)
    """

    _id_counter = 0

    def __init__(
        self,
        options=None,
        values=None,
        placeholder="Añadir...",
        name=None,
        id=None,
        tag_color="rgba(99,102,241,0.15)",
        tag_border="rgba(99,102,241,0.35)",
        tag_text="var(--accent)",
        **kwargs,
    ):
        self._props = Widget._extract_props(kwargs)
        self.options = options or []
        self.values = values or []
        self.placeholder = placeholder
        self.name = name
        self.tag_color = tag_color
        self.tag_border = tag_border
        self.tag_text = tag_text
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

        uid = self.uid
        extra = self._resolve_props()
        opts = self._parse_options()
        selected_vals = [str(v) for v in self.values]

        opts_js = _json.dumps([{"v": v, "l": l} for v, l in opts])
        selected_js = _json.dumps(selected_vals)
        name_js = _json.dumps(self.name)
        tc_js = _json.dumps(self.tag_color)
        tb_js = _json.dumps(self.tag_border)
        tt_js = _json.dumps(self.tag_text)
        ph_js = _json.dumps(self.placeholder)

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
                ' style="display:' + display + ";padding:9px 14px;cursor:pointer;"
                'font-size:14px;color:var(--text);border-radius:6px;transition:background .1s">'
                + l
                + "</div>"
            )
        opt_rows = "".join(rows)

        # Style block for hover — avoids inline onmouseover
        hover_css = (
            "<style>"
            "#" + uid + "_list .pw-mopt:hover{background:var(--surface-2)}"
            "</style>"
        )

        return (
            hover_css + '<div id="' + uid + '_wrap" style="' + wrapper_style + '">'
            '  <div id="' + uid + '_box"'
            '    style="display:flex;flex-wrap:wrap;gap:6px;align-items:center;min-height:42px;'
            "           padding:6px 10px;border:1px solid var(--border-input);border-radius:8px;"
            '           background:var(--input-bg);cursor:text;box-sizing:border-box;transition:border-color .2s">'
            '    <div id="'
            + uid
            + '_tags" style="display:contents;flex-wrap:wrap;gap:6px"></div>'
            '    <input id="' + uid + '_input" type="text"'
            '      style="border:none;outline:none;font-size:14px;min-width:100px;flex:1;'
            '             padding:2px 0;background:transparent;color:var(--input-color)">'
            "  </div>"
            '  <div id="' + uid + '_hidden"></div>'
            '  <div id="' + uid + '_drop"'
            '    style="display:none;position:absolute;top:calc(100% + 6px);left:0;right:0;'
            "           z-index:9999;border:1px solid var(--border-input);border-radius:10px;"
            '           box-shadow:0 12px 40px rgba(0,0,0,0.25);overflow:hidden;background:var(--dropdown-bg)">'
            '    <div id="' + uid + '_list"'
            '      style="max-height:220px;overflow-y:auto;padding:6px">'
            "      " + opt_rows + "    </div>"
            '    <div style="padding:6px 12px 8px;border-top:1px solid var(--border);'
            '                display:flex;justify-content:flex-end">'
            '      <span id="' + uid + '_clear"'
            '        style="font-size:12px;color:var(--text-muted);cursor:pointer;user-select:none">'
            "        Limpiar todo"
            "      </span>"
            "    </div>"
            "  </div>"
            "</div>"
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


class Badge(Widget):
    """Badge("Nuevo", background="#3b82f6", color="#fff", radius=999, padding=8)"""

    def __init__(self, label=None, child=None, children=None, **kwargs):
        self._props = Widget._extract_props(kwargs)
        self.label = label
        self.child = child
        self.children = children
        if not self._props.get("background"):
            self._props["background"] = "#3b82f6"
        if not self._props.get("color"):
            self._props["color"] = "#ffffff"

    def render(self):
        base = "display:inline-block;padding:2px 8px;border-radius:9999px;font-size:12px;font-weight:600"
        inline = self._resolve_props(base)
        inner = self._resolve_inner(self.label, self.child, self.children)
        return f'<span style="{inline}">{inner}</span>'


class Avatar(Widget):
    """
    Avatar(src="user.jpg", width=40, height=40, radius=999)
    Avatar(initials="JD", background="#6366f1", color="white", width=40, height=40)
    """

    def __init__(self, src=None, initials=None, **kwargs):
        self._props = Widget._extract_props(kwargs)
        self.src = src
        self.initials = initials
        # defaults
        if not self._props.get("width"):
            self._props["width"] = 40
        if not self._props.get("height"):
            self._props["height"] = 40
        if self._props.get("radius") is None:
            self._props["radius"] = 999

    def render(self):
        base = "overflow:hidden;display:inline-flex;align-items:center;justify-content:center;flex-shrink:0"
        inline = self._resolve_props(base)
        w = self._props.get("width", 40)
        if self.src:
            return f'<div style="{inline}"><img src="{self.src}" style="width:100%;height:100%;object-fit:cover"></div>'
        fs = (w // 3) if isinstance(w, (int, float)) else 14
        bg = self._props.get("background", "#e5e7eb")
        color = self._props.get("color", "#374151")
        return f'<div style="{inline};background:{bg};color:{color};font-weight:600;font-size:{fs}px">{self.initials or "?"}</div>'


class Raw(Widget):
    """Inject raw HTML. Raw('<hr>')"""

    def __init__(self, html: str):
        self._props = {}
        self.html = html

    def render(self):
        return self.html


class ThemeToggle(Widget):
    """
    Botón para cambiar entre temas oscuro/claro/auto.
    Úsalo donde quieras dentro de tu layout.

    # En el navbar:
    ThemeToggle()

    # Personalizado:
    ThemeToggle(
        dark_icon="🌙",
        light_icon="☀️",
        auto_icon="🌗",
        radius=8,
        padding=8,
    )

    # Solo oscuro/claro (sin auto):
    ThemeToggle(include_auto=False)

    # Como texto:
    ThemeToggle(dark_icon="Oscuro", light_icon="Claro", auto_icon="Auto")
    """

    def __init__(
        self,
        dark_icon="🌙",
        light_icon="☀️",
        auto_icon="🌗",
        include_auto=True,
        title="Cambiar tema",
        **kwargs,
    ):
        self._props = Widget._extract_props(kwargs)
        self.dark_icon = dark_icon
        self.light_icon = light_icon
        self.auto_icon = auto_icon
        self.include_auto = include_auto
        self.title = title

    def render(self):
        base = (
            "background:var(--surface); border:1px solid var(--border); "
            "color:var(--text); cursor:pointer; font-size:16px; "
            "display:inline-flex; align-items:center; justify-content:center; "
            "border-radius:8px; padding:6px 10px; transition:all 0.2s; "
            "user-select:none"
        )
        inline = self._resolve_props(base)

        # Cycle order depends on include_auto
        if self.include_auto:
            cycle = f"{{dark:'{self.light_icon}',light:'{self.auto_icon}',auto:'{self.dark_icon}'}}"
            next_theme = "{{dark:'light',light:'auto',auto:'dark'}}"
            initial = self.auto_icon  # shown before JS runs; JS will update
        else:
            cycle = f"{{dark:'{self.light_icon}',light:'{self.dark_icon}',auto:'{self.light_icon}'}}"
            next_theme = "{{dark:'light',light:'dark',auto:'light'}}"
            initial = self.dark_icon

        uid = f"_mtt_{id(self) & 0xFFFF}"

        return (
            f'<button id="{uid}" title="{self.title}" style="{inline}" '
            f"onclick=\"_mttCycle('{uid}')\" "
            f"onmouseover=\"this.style.borderColor='var(--accent)'\" "
            f"onmouseout=\"this.style.borderColor=''\">"
            f"{initial}"
            f"</button>"
            f"<script>"
            f"(function(){{"
            f'  var ICONS={{"dark":"{self.dark_icon}","light":"{self.light_icon}","auto":"{self.auto_icon}"}};'
            f'  var NEXT={{"dark":"light","light":{"auto" if self.include_auto else "dark"},"auto":"dark"}};'
            f'  function _mttSync(id){{var t=document.documentElement.getAttribute("data-theme")||"auto";'
            f'    var btn=document.getElementById(id);if(btn)btn.textContent=ICONS[t]||"{initial}";}} '
            f"  window._mttCycle=function(id){{"
            f'    var cur=document.documentElement.getAttribute("data-theme")||"auto";'
            f'    var next=NEXT[cur]||"auto";'
            f'    document.documentElement.setAttribute("data-theme",next);'
            f'    try{{localStorage.setItem("martin-theme",next);}}catch(e){{}}'
            f"    _mttSync(id);"
            f"  }};"
            f'  _mttSync("{uid}");'
            f'  var obs=new MutationObserver(function(){{_mttSync("{uid}");}});'
            f'  obs.observe(document.documentElement,{{attributes:true,attributeFilter:["data-theme"]}});'
            f"}})();"
            f"</script>"
        )


# ══════════════════════════════════════════════════════════
# API / EVENTOS
# ══════════════════════════════════════════════════════════


class Ref:
    """
    Referencia a un input por id para usarlo en ApiCall.body.

    Ref("lang_select")          → lee el valor del Select con id="lang_select"
    Ref("areas_multi")          → lee los valores del MultiSelect con id="areas_multi"
    Ref("nombre", label=True)   → lee también el label visible (para Select)
    """

    def __init__(self, input_id, label=False):
        self.input_id = input_id
        self.label = label

    def to_js(self):
        """Genera el snippet JS que lee el valor de este input."""
        uid = self.input_id
        js = (
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

    def __init__(
        self,
        url,
        method="POST",
        body=None,
        target=None,
        loading="Enviando...",
        on_success=None,
        on_error=None,
    ):
        self.url = url
        self.method = method.upper()
        self.body = body  # dict of {key: Ref(...) or literal} | None = auto
        self.target = target
        self.loading = loading
        self.on_success = on_success
        self.on_error = on_error

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

        url = _json.dumps(self.url)
        method = _json.dumps(self.method)
        loading = _json.dumps(self.loading)
        target_js = (
            ("document.getElementById(" + _json.dumps(self.target) + ")")
            if self.target
            else "null"
        )
        body_js = self._body_js(btn_id)
        on_success = self.on_success or ""
        on_error = self.on_error or ""

        has_body = self.method not in ("GET", "DELETE")

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
            "var fetchOpts={method:"
            + method
            + ",headers:{}};"
            + (
                "var bodyData=" + body_js + ";"
                "fetchOpts.body=JSON.stringify(bodyData);"
                "fetchOpts.headers['Content-Type']='application/json';"
                if has_body
                else ""
            )
            + "var res=await fetch("
            + url
            + ",fetchOpts);"
            "var data=await res.json();"
            "if(target){"
            "  target.setAttribute('data-state',res.ok?'success':'error');"
            "  target.setAttribute('data-status',res.status);"
            "  target._martinData=data;"
            "  target.dispatchEvent(new CustomEvent('martin:result',{detail:data}));"
            "}"
            + ("(function(result){" + on_success + "})(data);" if on_success else "")
            + "}catch(e){"
            "if(target){"
            "  target.setAttribute('data-state','error');"
            "  target._martinData={error:e.message};"
            "  target.dispatchEvent(new CustomEvent('martin:result',{detail:{error:e.message}}));"
            "}"
            + ("(function(err){" + on_error + "})(e);" if on_error else "")
            + "}finally{"
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

    def __init__(
        self,
        id,
        loading="Cargando...",
        empty="",
        format="json",
        template=None,
        **kwargs,
    ):
        self._props = Widget._extract_props(kwargs)
        self.box_id = id
        self.loading = loading
        self.empty = empty
        self.format = format  # 'json' | 'message' | 'custom'
        self.template = template

    def render(self):
        import json as _json

        extra = self._resolve_props()
        box_id = self.box_id
        loading = _json.dumps(self.loading)
        empty = _json.dumps(self.empty)
        fmt = _json.dumps(self.format)
        tmpl = _json.dumps(self.template or "")

        wrapper_style = (
            "border-radius:12px;overflow:hidden;transition:all .3s;"
            "border:1px solid transparent"
        )
        if extra:
            wrapper_style += ";" + extra

        return (
            '<div id="' + box_id + '" data-state="empty"'
            ' style="' + wrapper_style + '">'
            "</div>"
            "<style>"
            "#" + box_id + "[data-state=empty]{display:none}"
            "#" + box_id + "[data-state=loading]{"
            "  display:block;padding:16px;"
            "  border-color:var(--border);background:var(--surface);"
            "  color:var(--text-muted);font-size:14px}"
            "#" + box_id + "[data-state=success]{"
            "  display:block;padding:16px;"
            "  border-color:rgba(52,211,153,0.3);background:var(--surface)}"
            "#" + box_id + "[data-state=error]{"
            "  display:block;padding:16px;"
            "  border-color:rgba(248,113,113,0.3);background:var(--surface)}"
            "</style>"
            "<script>(function(){"
            "var box=document.getElementById(" + _json.dumps(box_id) + ");"
            "if(!box)return;"
            'box.addEventListener("martin:result",function(e){'
            "  var d=e.detail;"
            "  var fmt=" + fmt + ";"
            "  var tmpl=" + tmpl + ";"
            '  var ok=box.getAttribute("data-state")==="success";'
            '  var col=ok?"#34d399":"#f87171";'
            '  var label=ok?"Respuesta del servidor":"Error";'
            "  var content;"
            '  if(fmt==="message"){'
            "    content='<p style=\"margin:0;font-size:15px;color:var(--text)\">'+( d.mensaje||d.message||d.error||JSON.stringify(d))+'</p>';"
            '  }else if(fmt==="custom"&&tmpl){'
            '    content=tmpl.replace(/\\{(\\w+)\\}/g,function(_,k){return d[k]!==undefined?d[k]:"?";});'
            "    content='<div style=\"font-size:14px;color:var(--text)\">'+content+'</div>';"
            "  }else{"
            "    content='<pre style=\"margin:0;font-family:monospace;font-size:13px;color:var(--text-muted);white-space:pre-wrap\">'+JSON.stringify(d,null,2)+'</pre>';"
            "  }"
            "  box.innerHTML="
            "    '<div style=\"display:flex;align-items:center;gap:8px;margin-bottom:12px\">'"
            "    +'<span style=\"width:8px;height:8px;border-radius:50%;background:'+col+';flex-shrink:0\"></span>'"
            "    +'<strong style=\"font-size:13px;color:var(--text)\">'+label+'</strong>'"
            "    +'</div>'+content;"
            "});"
            "})()</script>"
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

    def __init__(
        self,
        words=None,
        width=600,
        height=300,
        min_size=12,
        max_size=72,
        colors=None,
        font="inherit",
        on_click=None,
        **kwargs,
    ):
        self._props = Widget._extract_props(kwargs)
        self.words = words or []
        self.width = width
        self.height = height
        self.min_size = min_size
        self.max_size = max_size
        self.colors = colors or [
            "#818cf8",
            "#34d399",
            "#fb923c",
            "#f472b6",
            "#38bdf8",
            "#a78bfa",
            "#4ade80",
            "#fbbf24",
        ]
        self.font = font
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

        uid = self.uid
        pairs = self._parse_words()
        extra = self._resolve_props()
        w = self.width
        h = self.height

        words_js = _json.dumps(pairs)
        colors_js = _json.dumps(self.colors)
        min_s = self.min_size
        max_s = self.max_size
        font_js = _json.dumps(self.font)
        on_click = self.on_click or ""

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
            "padding:5px 10px;background:rgba(0,0,0,0.75);color:#fff;"
            "border-radius:6px;font-size:12px;white-space:nowrap;"
            'transform:translate(-50%,-100%);margin-top:-6px;z-index:99"></div>'
            "</div>"
            "<script>(function(){"
            "var canvas=document.getElementById(" + _json.dumps(uid) + ");"
            "var tip=document.getElementById(" + _json.dumps(uid + "_tip") + ");"
            "if(!canvas)return;"
            'var ctx=canvas.getContext("2d");'
            "var dpr=window.devicePixelRatio||1;"
            "var W=" + str(w) + ",H=" + str(h) + ";"
            "canvas.width=W*dpr;canvas.height=H*dpr;"
            'canvas.style.width=W+"px";canvas.style.height=H+"px";'
            "ctx.scale(dpr,dpr);"
            "var rawWords=" + words_js + ";"
            "var colors=" + colors_js + ";"
            "var minS=" + str(min_s) + ",maxS=" + str(max_s) + ";"
            "var font=" + font_js + ";"
            'if(font==="inherit")font="system-ui,sans-serif";'
            # Logarithmic scale for more visible size contrast
            "var weights=rawWords.map(function(p){return p[1];});"
            "var minW=Math.min.apply(null,weights);"
            "var maxW=Math.max.apply(null,weights);"
            "var logMin=Math.log(minW+1),logMax=Math.log(maxW+1),logRange=logMax-logMin||1;"
            "var words=rawWords.map(function(p,i){"
            "  var logNorm=(Math.log(p[1]+1)-logMin)/logRange;"
            "  var size=Math.round(minS+logNorm*(maxS-minS));"
            "  var col=colors[i%colors.length];"
            "  return {text:p[0],weight:p[1],size:size,color:col};"
            "});"
            "words.sort(function(a,b){return b.size-a.size;});"
            # Collision detection
            "var placed=[];"
            "function overlaps(r){"
            "  for(var i=0;i<placed.length;i++){"
            "    var p=placed[i];"
            "    if(r.x<p.x+p.w+4&&r.x+r.w+4>p.x&&r.y<p.y+p.h+4&&r.y+r.h+4>p.y)return true;"
            "  }"
            "  return false;"
            "}"
            "function tryPlace(word){"
            '  ctx.font="bold "+word.size+"px "+font;'
            "  var tw=ctx.measureText(word.text).width;"
            "  var th=word.size*1.1;"
            "  var cx=W/2,cy=H/2;"
            "  for(var step=0;step<400;step++){"
            "    var angle=step*0.5;"
            "    var r=step*1.1;"
            "    var x=cx+r*Math.cos(angle)-tw/2;"
            "    var y=cy+r*Math.sin(angle)*0.55+th/2;"
            "    if(x<4||y-th<4||x+tw>W-4||y>H-4)continue;"
            "    var rect={x:x,y:y-th,w:tw,h:th};"
            "    if(!overlaps(rect)){placed.push(rect);return {x:x,y:y,w:tw,h:th};}"
            "  }"
            "  return null;"
            "}"
            "var placedWords=[];"
            "words.forEach(function(word){"
            "  var pos=tryPlace(word);"
            "  if(pos)placedWords.push({word:word,pos:pos});"
            "});"
            # Draw function
            "function draw(hitItem){"
            "  ctx.clearRect(0,0,W,H);"
            "  placedWords.forEach(function(item){"
            "    var word=item.word,pos=item.pos;"
            "    var isHit=item===hitItem;"
            "    ctx.save();"
            "    ctx.globalAlpha=(hitItem&&!isHit)?0.35:1;"
            "    if(isHit){"
            "      ctx.shadowColor=word.color;"
            "      ctx.shadowBlur=14;"
            '      ctx.font="bold "+(word.size+3)+"px "+font;'
            "    }else{"
            '      ctx.font="bold "+word.size+"px "+font;'
            "    }"
            "    ctx.fillStyle=word.color;"
            "    ctx.fillText(word.text,pos.x,pos.y);"
            "    ctx.restore();"
            "  });"
            "}"
            "draw(null);"
            # Mousemove — hit detection + tooltip
            'canvas.addEventListener("mousemove",function(e){'
            "  var rect=canvas.getBoundingClientRect();"
            "  var scaleX=W/rect.width,scaleY=H/rect.height;"
            "  var mx=(e.clientX-rect.left)*scaleX;"
            "  var my=(e.clientY-rect.top)*scaleY;"
            "  var hit=null;"
            "  placedWords.forEach(function(item){"
            "    var p=item.pos;"
            "    if(mx>=p.x&&mx<=p.x+p.w&&my>=p.y-p.h&&my<=p.y)hit=item;"
            "  });"
            '  canvas.style.cursor=hit?"pointer":"default";'
            "  draw(hit);"
            "  if(hit&&tip){"
            "    var bRect=canvas.getBoundingClientRect();"
            "    var px=hit.pos.x+hit.pos.w/2;"
            "    var py=hit.pos.y-hit.pos.h;"
            "    var scX=bRect.width/W,scY=bRect.height/H;"
            '    tip.textContent=hit.word.text+" · peso: "+hit.word.weight;'
            '    tip.style.left=(px*scX)+"px";'
            '    tip.style.top=(py*scY)+"px";'
            '    tip.style.display="block";'
            "  }else if(tip){"
            '    tip.style.display="none";'
            "  }"
            "});"
            'canvas.addEventListener("mouseleave",function(){'
            "  draw(null);"
            '  if(tip)tip.style.display="none";'
            "});"
            # Click handler
            + (
                'canvas.addEventListener("click",function(e){'
                "  var rect=canvas.getBoundingClientRect();"
                "  var scaleX=W/rect.width,scaleY=H/rect.height;"
                "  var mx=(e.clientX-rect.left)*scaleX;"
                "  var my=(e.clientY-rect.top)*scaleY;"
                "  placedWords.forEach(function(item){"
                "    var p=item.pos;"
                "    if(mx>=p.x&&mx<=p.x+p.w&&my>=p.y-p.h&&my<=p.y){"
                "      var word=item.word.text;"
                "      var weight=item.word.weight;"
                "      " + on_click + "    }"
                "  });"
                "});"
                if on_click
                else ""
            )
            + "})()</script>"
        )


class Map(Widget):
    """
    Mapa interactivo basado en Leaflet + OpenStreetMap. Sin API key.

    Map(center=(40.4168, -3.7038), zoom=13, height=480)

    Parámetros:
        center          (lat, lon) — centro del mapa. Auto si hay markers.
        zoom            int        — nivel de zoom 1-19 (default 13)
        height          int        — alto en px (default 480)
        markers         list[dict] — lista de marcadores
        search          bool       — barra de búsqueda Nominatim (default True)
        geolocation     bool       — botón mi-ubicación (default True)
        route           bool       — línea entre markers en orden (default False)
        route_color     str        — color de la ruta (default "#6366f1")
        route_weight    int        — grosor de la ruta px (default 4)
        tile            str        — "osm"|"dark"|"topo"|"cycle" (default "osm")
        on_marker_click str        — JS al click en marker. Variable: `marker` dict.

    Marcador mínimo:
        {"lat": 0.0, "lon": 0.0}

    Marcador completo:
        {"lat": 0.0, "lon": 0.0, "title": "Nombre", "popup": "HTML",
         "color": "#6366f1", "icon": "🏠"}
    """

    _id_counter = 0

    _TILES = {
        "osm": (
            "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
            "&copy; OpenStreetMap contributors",
        ),
        "dark": (
            "https://tiles.stadiamaps.com/tiles/alidade_smooth_dark/{z}/{x}/{y}{r}.png",
            "&copy; Stadia Maps, OpenStreetMap contributors",
        ),
        "topo": (
            "https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png",
            "&copy; OpenTopoMap contributors",
        ),
        "cycle": (
            "https://{s}.tile-cyclosm.openstreetmap.fr/cyclosm/{z}/{x}/{y}.png",
            "&copy; CyclOSM contributors",
        ),
    }

    def __init__(
        self,
        center=None,
        zoom=13,
        height=480,
        markers=None,
        search=True,
        geolocation=True,
        route=False,
        route_color="#6366f1",
        route_weight=4,
        tile="osm",
        on_marker_click=None,
        **kwargs,
    ):
        self._props = Widget._extract_props(kwargs)
        self.center = center
        self.zoom = zoom
        self.height = height
        self.markers = markers or []
        self.search = search
        self.geolocation = geolocation
        self.route = route
        self.route_color = route_color
        self.route_weight = route_weight
        self.tile = tile
        self.on_marker_click = on_marker_click
        Map._id_counter += 1
        self.uid = "map_" + str(Map._id_counter)

    def _build_js(self):
        import json as _j

        uid = self.uid
        J = _j.dumps

        tile_url, tile_attr = self._TILES.get(self.tile, self._TILES["osm"])
        if self.tile not in self._TILES:
            tile_url, tile_attr = self.tile, "&copy; Map contributors"

        # center
        if self.center:
            center_js = J(list(self.center))
        elif self.markers:
            lats = [m["lat"] for m in self.markers if "lat" in m]
            lons = [m["lon"] for m in self.markers if "lon" in m]
            center_js = (
                J([sum(lats) / len(lats), sum(lons) / len(lons)]) if lats else "[0,0]"
            )
        else:
            center_js = "[40.4168,-3.7038]"

        # ── icon helper (builds DOM to avoid escaping hell) ──────────────────
        icon_fn = (
            "function _mkIcon(color,icon){"
            "var d=document.createElement('div');"
            "d.style.cssText='width:32px;height:32px;background:'+color+';'"
            "+'border-radius:50% 50% 50% 0;border:3px solid white;'"
            "+'box-shadow:0 2px 8px rgba(0,0,0,0.3);transform:rotate(-45deg);'"
            "+'display:flex;align-items:center;justify-content:center';"
            "var s=document.createElement('span');"
            "s.style.cssText='transform:rotate(45deg);font-size:14px';"
            "s.textContent=icon;"
            "d.appendChild(s);"
            "return d.outerHTML;"
            "}"
        )

        # ── search ───────────────────────────────────────────────────────────
        search_js = ""
        if self.search:
            search_js = (
                "var _sq=document.getElementById(" + J(uid + "_q") + ");"
                "var _sb=document.getElementById(" + J(uid + "_btn") + ");"
                "var _sm=null;"
                "function _doSearch(){"
                "var q=_sq.value.trim();if(!q)return;"
                "_sb.textContent='\u23f3';"
                "fetch('https://nominatim.openstreetmap.org/search?format=json&limit=1&q='"
                "+encodeURIComponent(q),{headers:{'Accept-Language':'es,en'}})"
                ".then(function(r){return r.json();})"
                ".then(function(data){"
                "_sb.textContent='\U0001f50d';"
                "if(!data.length){alert('No se encontr\u00f3: '+q);return;}"
                "var r=data[0];"
                "var lat=parseFloat(r.lat),lon=parseFloat(r.lon);"
                "if(_sm)_map.removeLayer(_sm);"
                "var name=r.display_name.split(',')[0];"
                "_sm=L.marker([lat,lon])"
                ".addTo(_map)"
                ".bindPopup('<b>'+name+'</b><br><small>'+r.display_name+'</small>')"
                ".openPopup();"
                "_map.flyTo([lat,lon],15,{duration:1.2});"
                "})"
                ".catch(function(){_sb.textContent='\U0001f50d';alert('Error al buscar.');});"
                "}"
                "_sb.addEventListener('click',_doSearch);"
                "_sq.addEventListener('keydown',function(e){if(e.key==='Enter')_doSearch();});"
            )

        # ── geolocation ──────────────────────────────────────────────────────
        geo_js = ""
        if self.geolocation:
            geo_js = (
                "var _gb=document.getElementById(" + J(uid + "_geo") + ");"
                "var _gm=null;"
                "_gb.addEventListener('click',function(){"
                "if(!navigator.geolocation){alert('Geolocalizaci\u00f3n no disponible.');return;}"
                "_gb.textContent='\u23f3';"
                "navigator.geolocation.getCurrentPosition(function(pos){"
                "var lat=pos.coords.latitude,lon=pos.coords.longitude;"
                "if(_gm)_map.removeLayer(_gm);"
                "_gm=L.circleMarker([lat,lon],"
                "{radius:10,fillColor:'#6366f1',color:'white',weight:3,fillOpacity:0.9})"
                ".addTo(_map).bindPopup('<b>Tu ubicaci\u00f3n</b>').openPopup();"
                "_map.flyTo([lat,lon],16,{duration:1.2});"
                "_gb.textContent='\U0001f3af';"
                "},function(){"
                "alert('No se pudo obtener la ubicaci\u00f3n.');"
                "_gb.textContent='\U0001f3af';"
                "});"
                "});"
            )

        # ── click handler ────────────────────────────────────────────────────
        click_fn = ""
        click_bind = ""
        if self.on_marker_click:
            click_fn = "function _onMk(marker){" + self.on_marker_click + "}"
            click_bind = "_mk.on('click',function(){_onMk(m);});"

        # ── route ─────────────────────────────────────────────────────────────
        route_js = ""
        if self.route:
            route_js = (
                "if(_lls.length>1){"
                "L.polyline(_lls,{"
                "color:" + J(self.route_color) + ","
                "weight:" + str(self.route_weight) + ","
                "opacity:0.85,lineJoin:'round'"
                "}).addTo(_map);"
                "}"
            )

        # ── autofit ───────────────────────────────────────────────────────────
        autofit = ""
        if not self.center and len(self.markers) > 1:
            autofit = "if(_lls.length>1){_map.fitBounds(_lls,{padding:[40,40]});}"

        return (
            "(function _im(){"
            "if(typeof L==='undefined'){setTimeout(_im,50);return;}"
            "var el=document.getElementById(" + J(uid) + ");"
            "if(!el||el._mi)return;"
            "el._mi=true;"
            "var _map=L.map(el,{zoomControl:true}).setView("
            + center_js
            + ","
            + str(self.zoom)
            + ");"
            "L.tileLayer("
            + J(tile_url)
            + ",{attribution:"
            + J(tile_attr)
            + ",maxZoom:19}).addTo(_map);"
            + icon_fn
            + click_fn
            + "var _markers="
            + J(self.markers)
            + ";"
            "var _lls=[];"
            "_markers.forEach(function(m){"
            "var color=m.color||'#6366f1';"
            "var icon=m.icon||'';"
            "var _lIcon=L.divIcon({"
            "html:_mkIcon(color,icon),"
            "className:'',iconSize:[32,32],iconAnchor:[16,32],popupAnchor:[0,-36]"
            "});"
            "var _mk=L.marker([m.lat,m.lon],{icon:_lIcon}).addTo(_map);"
            "var _ph='<b>'+(m.title||'')+'</b>';"
            "if(m.popup)_ph+='<br>'+m.popup;"
            "if(m.title||m.popup)_mk.bindPopup(_ph);"
            + click_bind
            + "_lls.push([m.lat,m.lon]);"
            "});" + route_js + autofit + search_js + geo_js + "})();"
        )

    def render(self):
        uid = self.uid
        height = str(self.height)
        extra = self._resolve_props()

        wrapper_style = (
            "position:relative;border-radius:12px;overflow:hidden;"
            "width:100%;height:" + height + "px"
        )
        if extra:
            wrapper_style += ";" + extra

        search_html = ""
        if self.search:
            search_html = (
                '<div style="position:absolute;top:10px;left:50%;'
                "transform:translateX(-50%);z-index:1000;"
                'display:flex;gap:6px;width:min(360px,80%)">'
                '<input id="' + uid + '_q" type="text"'
                ' placeholder="Buscar lugar..." style="flex:1;padding:8px 12px;'
                "border:none;border-radius:8px;font-size:14px;color:#111;"
                'box-shadow:0 2px 12px rgba(0,0,0,0.15);outline:none"/>'
                '<button id="' + uid + '_btn" style="padding:8px 14px;'
                "background:#6366f1;color:white;border:none;border-radius:8px;"
                "cursor:pointer;font-size:18px;line-height:1;"
                'box-shadow:0 2px 12px rgba(0,0,0,0.15)">&#128269;</button>'
                "</div>"
            )

        geo_html = ""
        if self.geolocation:
            geo_html = (
                '<button id="' + uid + '_geo" title="Mi ubicaci\u00f3n" style="'
                "position:absolute;bottom:80px;right:10px;z-index:1000;"
                "width:34px;height:34px;background:white;"
                "border:2px solid rgba(0,0,0,0.2);border-radius:6px;cursor:pointer;"
                "font-size:18px;line-height:1;"
                "display:flex;align-items:center;justify-content:center;"
                'box-shadow:0 1px 5px rgba(0,0,0,0.2)">&#127919;</button>'
            )

        leaflet_css = (
            '<link rel="stylesheet" '
            'href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" '
            'crossorigin=""/>'
        )
        leaflet_js_tag = (
            '<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" '
            'crossorigin=""></script>'
        )

        # data-height permite al JS fijar el alto aunque el CSS tarde en cargar
        return (
            leaflet_css
            + '<div style="'
            + wrapper_style
            + '" data-mapheight="'
            + height
            + '">'
            + '<div id="'
            + uid
            + '" style="width:100%;height:'
            + height
            + 'px"></div>'
            + search_html
            + geo_html
            + "</div>"
            + leaflet_js_tag
            + "<script>"
            + self._build_js()
            + "</script>"
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
        self._props = Widget._extract_props(kwargs)
        self.items = items or []
        self.line_color = line_color or "var(--border)"
        self.alt = alt

    def render(self):
        extra = self._resolve_props()
        line_color = self.line_color
        alt = self.alt

        # Wrapper CSS
        wrapper_style = (
            f"position:relative;display:flex;flex-direction:column;gap:0;" f"{extra}"
        )

        # Línea vertical central (o izquierda si no es alt)
        line_left = "50%" if alt else "20px"
        line_html = (
            f'<div style="position:absolute;top:0;bottom:0;left:{line_left};'
            f"width:2px;background:{line_color};transform:translateX(-50%);z-index:0;"
            f'border-radius:2px"></div>'
        )

        items_html = ""
        for i, item in enumerate(self.items):
            if not isinstance(item, TimelineItem):
                continue
            items_html += item._render(index=i, alt=alt, line_color=line_color)

        return f'<div style="{wrapper_style}">' + line_html + items_html + "</div>"


class TimelineItem:
    """Elemento individual de un Timeline. Ver Timeline para documentación."""

    def __init__(
        self,
        title,
        date=None,
        description=None,
        icon="●",
        image=None,
        color=None,
        tag=None,
    ):
        self.title = title
        self.date = date
        self.description = description
        self.icon = icon
        self.image = image
        self.color = color or "var(--accent)"
        self.tag = tag

    def _render(self, index=0, alt=False, line_color="var(--border)"):
        import json as _json

        color = self.color
        # En modo alt, los pares van a la derecha, impares a la izquierda
        go_right = (not alt) or (index % 2 == 0)

        # ── Nodo (círculo en la línea) ──────────────────────────────────────
        node_left = "50%" if alt else "20px"
        node_html = (
            f'<div style="position:absolute;left:{node_left};top:24px;'
            f"transform:translate(-50%,-0%);z-index:1;"
            f"width:36px;height:36px;border-radius:50%;"
            f"background:{color};"
            f"border:3px solid var(--bg);"
            f"box-shadow:0 0 0 2px {color},0 2px 8px rgba(0,0,0,0.15);"
            f"display:flex;align-items:center;justify-content:center;"
            f'font-size:16px;line-height:1;flex-shrink:0;">'
            f"{self.icon}</div>"
        )

        # ── Tarjeta de contenido ────────────────────────────────────────────
        if alt:
            if go_right:
                card_margin = "margin-left:calc(50% + 28px);margin-right:0;"
            else:
                card_margin = (
                    "margin-right:calc(50% + 28px);margin-left:0;text-align:right;"
                )
        else:
            card_margin = "margin-left:52px;margin-right:0;"

        # Imagen
        img_html = ""
        if self.image:
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
                f"letter-spacing:1px;text-transform:uppercase;"
                f"color:{color};background:rgba(99,102,241,0.10);"
                f'padding:2px 8px;border-radius:999px;margin-bottom:6px;">'
                f"{self.tag}</span><br>"
            )

        # Fecha
        date_html = ""
        if self.date:
            date_html = (
                f'<span style="font-size:12px;font-weight:600;'
                f'color:{color};opacity:0.9;margin-bottom:4px;display:block;">'
                f"{self.date}</span>"
            )

        # Título
        title_html = (
            f'<div style="font-size:15px;font-weight:700;'
            f'color:var(--text);margin-bottom:6px;line-height:1.3;">'
            f"{self.title}</div>"
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
            f"background:var(--surface);border:1px solid var(--border);"
            f"border-radius:12px;padding:16px;"
            f"box-shadow:0 2px 8px rgba(0,0,0,0.06);"
            f'border-left:3px solid {color};">'
            + img_html
            + tag_html
            + date_html
            + title_html
            + desc_html
            + "</div>"
        )

        # ── Fila completa ───────────────────────────────────────────────────
        return (
            f'<div style="position:relative;display:flex;'
            f'align-items:flex-start;padding-bottom:24px;min-height:64px;">'
            + node_html
            + card_html
            + "</div>"
        )
