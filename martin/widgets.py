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

    def __init__(self, content, id=None, **kwargs):
        self._props = Widget._extract_props(kwargs)
        self.content = content
        self.id = id

    def render(self):
        inline = self._resolve_props()
        attrs = self._attrs(style=inline or None, id=self.id)
        return f"<span{attrs}>{self.content}</span>"


class Heading(Widget):
    """
    Heading("Título", level=1, color="#111", margin=16)
    """

    def __init__(self, content, level=1, id=None, **kwargs):
        self._props = Widget._extract_props(kwargs)
        self.content = content
        self.level = max(1, min(6, level))
        self.id = id

    def render(self):
        inline = self._resolve_props()
        attrs = self._attrs(style=inline or None, id=self.id)
        tag = f"h{self.level}"
        return f"<{tag}{attrs}>{self.content}</{tag}>"


class Paragraph(Widget):
    def __init__(self, content, id=None, **kwargs):
        self._props = Widget._extract_props(kwargs)
        self.content = content
        self.id = id

    def render(self):
        inline = self._resolve_props()
        attrs = self._attrs(style=inline or None, id=self.id)
        return f"<p{attrs}>{self.content}</p>"


class Link(Widget):
    """
    Link("Click", href="/page", color="#3b82f6")
    """

    def __init__(self, content, href="#", target=None, **kwargs):
        self._props = Widget._extract_props(kwargs)
        self.content = content
        self.href = href
        self.target = target

    def render(self):
        inline = self._resolve_props()
        attrs = self._attrs(href=self.href, target=self.target, style=inline or None)
        inner = (
            self.content.render() if isinstance(self.content, Widget) else self.content
        )
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

    def __init__(self, icon, size=20, **kwargs):
        self._props = Widget._extract_props(kwargs)
        self.icon = icon
        self.size = size

    def render(self):
        base = f"font-size: {self.size}px; line-height: 1"
        inline = self._resolve_props(base)
        return f'<span style="{inline}" aria-hidden="true">{self.icon}</span>'


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
        **kwargs,
    ):
        self._props = Widget._extract_props(kwargs)
        self.label = label
        self.variant = variant
        self.href = href
        self.disabled = disabled
        self.id = id
        self.class_name = class_name

    def render(self):
        base = (
            self.VARIANTS.get(self.variant, self.VARIANTS["primary"])
            + "; padding: 8px 16px; border-radius: 6px; cursor: pointer; "
            "font-size: 14px; font-weight: 500; display: inline-flex; "
            "align-items: center; gap: 6px; text-decoration: none"
        )
        inline = self._resolve_props(base)
        inner = self.label.render() if isinstance(self.label, Widget) else self.label
        if self.href:
            attrs = self._attrs(
                href=self.href, style=inline, id=self.id, **{"class": self.class_name}
            )
            return f"<a{attrs}>{inner}</a>"
        attrs = self._attrs(
            style=inline,
            disabled=self.disabled,
            id=self.id,
            **{"class": self.class_name},
        )
        return f"<button{attrs}>{inner}</button>"


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

        return f"""
<div id="{self.uid}_wrap" style="{wrapper_style}">
  {hidden_input}
  <div id="{self.uid}_btn" onclick="pwSelectToggle('{self.uid}')"
    style="display:flex;align-items:center;justify-content:space-between;padding:8px 12px;border:1px solid var(--border-input);border-radius:6px;background:var(--input-bg);cursor:pointer;user-select:none;gap:8px">
    <span id="{self.uid}_label" style="color:var(--input-color);flex:1">{selected_label}</span>
    <svg width="12" height="12" viewBox="0 0 12 12" style="flex-shrink:0;transition:transform 0.2s" id="{self.uid}_arrow">
      <path d="M2 4l4 4 4-4" stroke="#9ca3af" stroke-width="1.5" fill="none" stroke-linecap="round"/>
    </svg>
  </div>
  <div id="{self.uid}_drop" style="display:none;position:absolute;top:calc(100% + 4px);left:0;right:0;z-index:9999;background:var(--surface,#fff);border:1px solid var(--border-input);border-radius:8px;box-shadow:var(--shadow,0 8px 24px rgba(0,0,0,0.12));overflow:hidden;backdrop-filter:blur(12px)">
    <div style="padding:8px;border-bottom:1px solid var(--border)">
      <input type="text" placeholder="Buscar..." oninput="pwSelectFilter('{self.uid}',this.value)"
        style="width:100%;padding:6px 10px;border:1px solid var(--border-input);border-radius:6px;font-size:13px;outline:none;box-sizing:border-box;background:var(--input-bg);color:var(--input-color)"
        id="{self.uid}_search">
    </div>
    <div id="{self.uid}_list" style="max-height:200px;overflow-y:auto">
      {"".join(
        f'<div class="pw-opt" data-val="{v}" data-label="{l}"'
        f' onclick="pwSelectPick(\'{self.uid}\',\'{v}\',\'{l}\')"'
        f' style="padding:8px 12px;cursor:pointer;color:var(--text);background:{"rgba(99,102,241,0.12)" if v==selected_val else "transparent"};font-weight:{"600" if v==selected_val else "400"}"'
        f' onmouseover="this.style.background=\'var(--surface-2,#f9fafb)\'"'
        f' onmouseout="this.style.background=\'{"rgba(99,102,241,0.12)" if v==selected_val else "transparent"}\'">{l}</div>'
        for v, l in opts)}
    </div>
  </div>
</div>
<script>
(function(){{
  if(window._pwSelectInit)return; window._pwSelectInit=true;
  window.pwSelectToggle=function(uid){{var d=document.getElementById(uid+'_drop'),a=document.getElementById(uid+'_arrow'),o=d.style.display!=='none';document.querySelectorAll('[id$="_drop"]').forEach(function(el){{if(el.id!==uid+'_drop'){{el.style.display='none';var x=document.getElementById(el.id.replace('_drop','_arrow'));if(x)x.style.transform='';}}}}); if(o){{d.style.display='none';a.style.transform='';}}else{{d.style.display='block';a.style.transform='rotate(180deg)';setTimeout(function(){{var s=document.getElementById(uid+'_search');if(s){{s.value='';s.focus();pwSelectFilter(uid,'');}}}},50);}}}};
  window.pwSelectFilter=function(uid,q){{document.querySelectorAll('#'+uid+'_list .pw-opt').forEach(function(i){{i.style.display=i.getAttribute('data-label').toLowerCase().includes(q.toLowerCase())?'block':'none';}});}};
  window.pwSelectPick=function(uid,val,label){{document.getElementById(uid+'_val').value=val;document.getElementById(uid+'_label').textContent=label;document.getElementById(uid+'_drop').style.display='none';document.getElementById(uid+'_arrow').style.transform='';document.querySelectorAll('#'+uid+'_list .pw-opt').forEach(function(el){{var s=el.getAttribute('data-val')===val;el.style.background=s?'#eff6ff':'#fff';el.style.fontWeight=s?'600':'400';}});}};
  document.addEventListener('click',function(e){{if(!e.target.closest('[id$="_wrap"]')){{document.querySelectorAll('[id$="_drop"]').forEach(function(el){{el.style.display='none';var a=document.getElementById(el.id.replace('_drop','_arrow'));if(a)a.style.transform='';}})}}}});
}})();
</script>"""


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
        placeholder="Buscar...",
        name=None,
        id=None,
        tag_color="#eff6ff",
        tag_border="#bfdbfe",
        tag_text="#1d4ed8",
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
        extra = self._resolve_props()
        opts = self._parse_options()
        opts_json = "[" + ",".join(f'{{"v":"{v}","l":"{l}"}}' for v, l in opts) + "]"
        selected_vals = [str(v) for v in self.values]
        selected_json = "[" + ",".join(f'"{v}"' for v in selected_vals) + "]"
        wrapper_extra = f"; {extra}" if extra else ""

        return f"""
<div id="{self.uid}_wrap" style="position:relative;width:100%;font-size:14px{wrapper_extra}">
  <div id="{self.uid}_box" onclick="pwMultiFocus('{self.uid}')"
    style="display:flex;flex-wrap:wrap;gap:6px;align-items:center;min-height:40px;padding:6px 10px;border:1px solid #d1d5db;border-radius:8px;background:#fff;cursor:text;box-sizing:border-box">
    <div id="{self.uid}_tags" style="display:contents"></div>
    <input type="text" id="{self.uid}_input" placeholder="{self.placeholder}"
      oninput="pwMultiFilter('{self.uid}',this.value)" onfocus="pwMultiOpen('{self.uid}')"
      style="border:none;outline:none;font-size:14px;min-width:120px;flex:1;padding:2px 0;background:transparent">
  </div>
  <div id="{self.uid}_hidden"></div>
  <div id="{self.uid}_drop" style="display:none;position:absolute;top:calc(100% + 4px);left:0;right:0;z-index:9999;background:#fff;border:1px solid #d1d5db;border-radius:8px;box-shadow:0 8px 24px rgba(0,0,0,0.12);overflow:hidden">
    <div id="{self.uid}_list" style="max-height:200px;overflow-y:auto">
      {"".join(
        f'<div class="pw-mopt" data-val="{v}" data-label="{l}"'
        f' onclick="pwMultiToggle(\'{self.uid}\',\'{v}\',\'{l}\')"'
        f' style="padding:8px 12px;cursor:pointer;display:flex;align-items:center;gap:8px;background:{"#eff6ff" if v in selected_vals else "#fff"}"'
        f' onmouseover="this.style.background=\'#f9fafb\'"'
        f' onmouseout="this.style.background=pwMultiIsSelected(\'{self.uid}\',\'{v}\')?\'#eff6ff\':\'#fff\'">'
        f'<span id="{self.uid}_check_{v}" style="width:16px;height:16px;border-radius:4px;display:inline-flex;align-items:center;justify-content:center;flex-shrink:0;border:2px solid {"#3b82f6" if v in selected_vals else "#d1d5db"};background:{"#3b82f6" if v in selected_vals else "#fff"}">'
        f'{"<svg width=10 height=10 viewBox=\'0 0 10 10\'><path d=\'M1.5 5l2.5 2.5 4.5-4.5\' stroke=\'#fff\' stroke-width=\'1.5\' fill=\'none\' stroke-linecap=\'round\'/></svg>" if v in selected_vals else ""}'
        f'</span>{l}</div>'
        for v, l in opts)}
    </div>
    <div style="padding:8px 12px;border-top:1px solid #f3f4f6;display:flex;justify-content:flex-end">
      <span onclick="pwMultiClear('{self.uid}')" style="font-size:12px;color:#6b7280;cursor:pointer;user-select:none"
        onmouseover="this.style.color='#374151'" onmouseout="this.style.color='#6b7280'">Limpiar todo</span>
    </div>
  </div>
</div>
<script>
(function(){{
  if(!window._pwMultiState)window._pwMultiState={{}};
  var uid='{self.uid}',opts={opts_json},name={f'"{self.name}"' if self.name else 'null'};
  var tc='{self.tag_color}',tb='{self.tag_border}',tt='{self.tag_text}';
  window._pwMultiState[uid]=new Set({selected_json});
  _pwMultiRender(uid,opts,name,tc,tb,tt);
  function _pwMultiRender(uid,opts,name,tc,tb,tt){{
    var tagsEl=document.getElementById(uid+'_tags'),hiddenEl=document.getElementById(uid+'_hidden'),selected=window._pwMultiState[uid];
    if(!tagsEl)return;
    tagsEl.innerHTML='';
    selected.forEach(function(val){{
      var label=(opts.find(function(o){{return o.v===val;}})||{{}}).l||val;
      var tag=document.createElement('span');
      tag.style.cssText='display:inline-flex;align-items:center;gap:4px;padding:2px 8px;border-radius:9999px;font-size:12px;font-weight:500;flex-shrink:0;background:'+tc+';color:'+tt+';border:1px solid '+tb;
      tag.innerHTML=label+'<span onclick="pwMultiToggle(\''+uid+'\',\''+val+'\',\''+label+'\')" style="cursor:pointer;font-size:14px;line-height:1;opacity:0.6;margin-left:2px" onmouseover="this.style.opacity=1" onmouseout="this.style.opacity=0.6">×</span>';
      tagsEl.appendChild(tag);
    }});
    if(name){{hiddenEl.innerHTML='';selected.forEach(function(val){{var i=document.createElement('input');i.type='hidden';i.name=name;i.value=val;hiddenEl.appendChild(i);}});}}
    opts.forEach(function(opt){{
      var el=document.getElementById(uid+'_check_'+opt.v);if(!el)return;
      var s=selected.has(opt.v);
      el.style.background=s?'#3b82f6':'#fff';el.style.borderColor=s?'#3b82f6':'#d1d5db';
      el.innerHTML=s?'<svg width=10 height=10 viewBox="0 0 10 10"><path d="M1.5 5l2.5 2.5 4.5-4.5" stroke="#fff" stroke-width="1.5" fill="none" stroke-linecap="round"/></svg>':'';
      var row=el.parentElement;if(row)row.style.background=s?'#eff6ff':'#fff';
    }});
  }}
  window.pwMultiIsSelected=function(uid,val){{return window._pwMultiState[uid]&&window._pwMultiState[uid].has(val);}};
  window.pwMultiToggle=function(uid,val,label){{var s=window._pwMultiState[uid];if(s.has(val))s.delete(val);else s.add(val);_pwMultiRender(uid,opts,name,tc,tb,tt);}};
  window.pwMultiClear=function(uid){{window._pwMultiState[uid].clear();_pwMultiRender(uid,opts,name,tc,tb,tt);}};
  window.pwMultiOpen=function(uid){{document.getElementById(uid+'_drop').style.display='block';}};
  window.pwMultiFocus=function(uid){{document.getElementById(uid+'_input').focus();}};
  window.pwMultiFilter=function(uid,q){{document.querySelectorAll('#'+uid+'_list .pw-mopt').forEach(function(el){{el.style.display=el.getAttribute('data-label').toLowerCase().includes(q.toLowerCase())?'flex':'none';}});}};
  document.addEventListener('click',function(e){{if(!e.target.closest('#'+uid+'_wrap')){{var d=document.getElementById(uid+'_drop'),i=document.getElementById(uid+'_input');if(d)d.style.display='none';if(i){{i.value='';pwMultiFilter(uid,'');}}}}}});
}})();
</script>"""


# ══════════════════════════════════════════════════════════
# UTILITY
# ══════════════════════════════════════════════════════════


class Badge(Widget):
    """Badge("Nuevo", background="#3b82f6", color="#fff", radius=999, padding=8)"""

    def __init__(self, label, **kwargs):
        self._props = Widget._extract_props(kwargs)
        self.label = label
        # defaults si no se pasan
        if not self._props.get("background"):
            self._props["background"] = "#3b82f6"
        if not self._props.get("color"):
            self._props["color"] = "#ffffff"

    def render(self):
        base = "display:inline-block;padding:2px 8px;border-radius:9999px;font-size:12px;font-weight:600"
        inline = self._resolve_props(base)
        return f'<span style="{inline}">{self.label}</span>'


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
