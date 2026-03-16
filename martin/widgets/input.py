"""
Martin — Input Widgets

Widgets de interacción: botones, campos de texto y selectores.

    Button      — botón interactivo, el widget de acción principal
    TextField   — campo de texto de una línea
    TextArea    — campo de texto multilínea con auto-resize y contador
    Checkbox    — casilla de verificación con etiqueta
    Select      — selector desplegable, nativo o con búsqueda
    MultiSelect — selector múltiple con tags y búsqueda
"""

import json as _json
import uuid as _uuid

from ..widget import Widget


# =============================================================================
# Button
# =============================================================================


class Button(Widget):
    """
    Botón interactivo. El widget de acción principal.

        Button("Guardar")
        Button("Cancelar", variant="ghost")
        Button("Eliminar", variant="danger", radius=8)

        # Con enlace:
        Button("Ver docs", href="/docs")

        # Con acción JS directa:
        Button("Click", on_click="alert('hola')")

        # Con llamada a API:
        Button("Enviar", on_click=ApiCall("/api/datos", body={"key": Ref("campo")}))

    Variantes: "primary" | "secondary" | "danger" | "ghost" | "link"
    """

    VARIANTS = {
        "primary": "background:var(--accent); color:#fff; border:none",
        "secondary": "background:var(--surface-2); color:var(--text); border:1px solid var(--border)",
        "danger": "background:var(--danger,#ef4444); color:#fff; border:none",
        "ghost": "background:transparent; color:var(--text); border:1px solid var(--border)",
        "link": "background:transparent; color:var(--accent); border:none; text-decoration:underline",
        "success": "background:var(--success,#22c55e); color:#fff; border:none",
    }

    def __init__(
        self,
        label="",
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
        self.on_click = on_click  # str JS | ApiCall

    def render(self):
        base = (
            self.VARIANTS.get(self.variant, self.VARIANTS["primary"])
            + "; padding:8px 16px; border-radius:6px; cursor:pointer; "
            "font-size:14px; font-weight:500; display:inline-flex; "
            "align-items:center; gap:6px; text-decoration:none; "
            "transition:opacity .2s"
        )
        inline = self._resolve_props(base)
        inner = self.label.render() if isinstance(self.label, Widget) else self.label

        btn_id = self.id or ("btn_" + _uuid.uuid4().hex[:8] if self.on_click else None)

        if self.href:
            attrs = self._attrs(
                href=self.href,
                style=inline,
                id=btn_id,
                **{"class": self.class_name},
            )
            return self._wrap_url(f"<a{attrs}>{inner}</a>")

        attrs = self._attrs(
            style=inline,
            disabled=self.disabled,
            id=btn_id,
            **{"class": self.class_name},
        )
        html = f"<button{attrs}>{inner}</button>"

        if self.on_click and btn_id:
            if isinstance(self.on_click, str):
                js_body = self.on_click
            else:
                js_body = self.on_click.to_js(btn_id)
            html += (
                "<script>"
                "document.getElementById("
                + repr(btn_id)
                + ").addEventListener('click',function(){"
                + js_body
                + "});"
                "</script>"
            )

        return self._wrap_url(html)


# =============================================================================
# TextField
# =============================================================================


class TextField(Widget):
    """
    Campo de texto de una línea.

        TextField(placeholder="Tu nombre")
        TextField(placeholder="Email", type="email", name="email", width="100%")
        TextField(placeholder="Buscar", id="search_input", radius=999)
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
            "padding:8px 12px; border:1px solid var(--border); border-radius:6px; "
            "font-size:14px; outline:none; width:100%; box-sizing:border-box; "
            "background:var(--input-bg,var(--surface)); color:var(--text); "
            "transition:border-color .2s"
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


# =============================================================================
# TextArea
# =============================================================================


class TextArea(Widget):
    """
    Campo de texto multilínea.

    Básico:
        TextArea(placeholder="Escribe tu mensaje...")

    Con opciones:
        TextArea(
            value="Hola mundo",
            rows=6,
            placeholder="Descripción...",
            id="desc_field",
            name="descripcion",
            max_length=500,
        )

    Auto-resize:
        TextArea(placeholder="...", auto_resize=True)

    Monoespaciado:
        TextArea(placeholder="Pega tu JSON aquí...", monospace=True)

    Parámetros:
        placeholder  str   texto de ayuda
        value        str   valor inicial
        rows         int   filas visibles (default: 4)
        name         str   nombre para formularios
        id           str   id del elemento
        disabled     bool  desactiva el campo
        readonly     bool  solo lectura
        resize       bool  permite redimensionar (default True)
        auto_resize  bool  crece con el contenido (default False)
        max_length   int   máx de caracteres — activa contador
        show_count   bool  muestra contador aunque no haya max_length
        monospace    bool  fuente monoespaciada (default False)
    """

    _id_counter = 0

    def __init__(
        self,
        placeholder="",
        value="",
        rows=4,
        name=None,
        id=None,
        disabled=False,
        readonly=False,
        resize=True,
        auto_resize=False,
        max_length=None,
        show_count=False,
        monospace=False,
        **kwargs,
    ):
        self._props = Widget._extract_props(kwargs)
        self.placeholder = placeholder
        self.value = value
        self.rows = rows
        self.name = name
        self.disabled = disabled
        self.readonly = readonly
        self.resize = resize
        self.auto_resize = auto_resize
        self.max_length = max_length
        self.show_count = show_count or (max_length is not None)
        self.monospace = monospace
        TextArea._id_counter += 1
        self.uid = id or f"ta_{TextArea._id_counter}"

    def render(self):
        uid = self.uid
        extra = self._resolve_props()

        resize_val = "none" if (not self.resize or self.auto_resize) else "vertical"
        font_extra = (
            "font-family:'Fira Code','Cascadia Code',monospace;"
            if self.monospace
            else ""
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
            p = self.placeholder.replace('"', "&quot;")
            parts.append(f'placeholder="{p}"')
        if self.max_length:
            parts.append(f'maxlength="{self.max_length}"')
        if self.disabled:
            parts.append("disabled")
        if self.readonly:
            parts.append("readonly")
        parts.append('spellcheck="false"')

        escaped_val = (
            str(self.value)
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            if self.value
            else ""
        )
        ta_html = f'<textarea {" ".join(parts)}>{escaped_val}</textarea>'

        # Auto-resize JS
        auto_js = ""
        if self.auto_resize:
            auto_js = (
                f"<script>(function(){{"
                f"var el=document.getElementById({_json.dumps(uid)});"
                f"if(!el)return;"
                f'function _fit(){{el.style.height="auto";el.style.height=(el.scrollHeight+2)+"px";}}'
                f'el.addEventListener("input",_fit);_fit();'
                f"}})();</script>"
            )

        # Character counter
        counter_html = ""
        if self.show_count:
            lim_js = _json.dumps(self.max_length)
            init_len = len(str(self.value)) if self.value else 0
            init_txt = (
                f"{init_len}"
                + (f"/{self.max_length}" if self.max_length else "")
                + " car."
            )
            counter_html = (
                f'<div id="{uid}_ct" style="text-align:right;font-size:11px;'
                f'color:var(--text-muted);margin-top:3px">{init_txt}</div>'
                f"<script>(function(){{"
                f"var el=document.getElementById({_json.dumps(uid)});"
                f'var ct=document.getElementById({_json.dumps(uid + "_ct")});'
                f"var lim={lim_js};"
                f"if(!el||!ct)return;"
                f'el.addEventListener("input",function(){{'
                f"  var n=el.value.length;"
                f'  ct.textContent=n+(lim?"/"+lim:"")+" car.";'
                f'  ct.style.color=(lim&&n>=lim)?"var(--danger,#ef4444)":'
                f'                 (lim&&n>lim*0.85)?"#f59e0b":'
                f'                 "var(--text-muted)";'
                f"}});"
                f"}})();</script>"
            )

        wrapper_style = "width:100%"
        if extra:
            wrapper_style += ";" + extra

        return (
            f'<div style="{wrapper_style}">'
            + ta_html
            + counter_html
            + auto_js
            + "</div>"
        )


# =============================================================================
# Checkbox
# =============================================================================


class Checkbox(Widget):
    """
    Casilla de verificación con etiqueta.

        Checkbox("Aceptar términos")
        Checkbox("Activo", checked=True, name="active")
    """

    def __init__(self, label="", checked=False, name=None, id=None, **kwargs):
        self._props = Widget._extract_props(kwargs)
        self.label = label
        self.checked = checked
        self.name = name
        self.id = id

    def render(self):
        base = "display:flex; align-items:center; gap:8px; color:var(--text); cursor:pointer"
        inline = self._resolve_props(base)
        checked = " checked" if self.checked else ""
        name_a = f' name="{self.name}"' if self.name else ""
        id_a = f' id="{self.id}"' if self.id else ""
        return (
            f'<label style="{inline}">'
            f'<input type="checkbox"{checked}{name_a}{id_a}>'
            f"<span>{self.label}</span></label>"
        )


# =============================================================================
# Select
# =============================================================================


class Select(Widget):
    """
    Selector desplegable, nativo o con búsqueda.

        Select(options=["A", "B", "C"], radius=8, width="100%")
        Select(options=[("es", "Español"), ("en", "English")], search=True)
        Select(options=[...], placeholder="Elige uno...", name="lang")
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
        selected_lbl = next((l for v, l in opts if v == selected_val), self.placeholder)

        # ── Native <select> (no search) ───────────────────────────────────
        if not self.search:
            base = (
                "padding: 8px 12px; border: 1px solid var(--border-input,var(--border)); border-radius: 6px; "
                "font-size: 14px; background: var(--input-bg,var(--surface)); color: var(--input-color,var(--text)); "
                "cursor: pointer; width: 100%"
            )
            inline = f"{base}; {extra}" if extra else base
            opt_tags = "".join(
                f'<option value="{v}"{"selected" if v == selected_val else ""}>{l}</option>'
                for v, l in opts
            )
            name_attr = f' name="{self.name}"' if self.name else ""
            return f'<select id="{self.uid}" style="{inline}"{name_attr}>{opt_tags}</select>'

        # ── Custom select with search ─────────────────────────────────────
        uid = self.uid
        wrapper_style = f"position: relative; width: 100%; font-size: 14px; {extra}"
        hidden_input = (
            f'<input type="hidden" name="{self.name}" id="{uid}_val" value="{selected_val}">'
            if self.name
            else f'<input type="hidden" id="{uid}_val" value="{selected_val}">'
        )

        def make_opt(v, l):
            sel = "1" if v == selected_val else "0"
            weight = "600" if v == selected_val else "400"
            onclick = (
                f"pwSelectPick('{uid}','{v}','{l.replace(chr(39), chr(92)+chr(39))}')"
            )
            return (
                f'<div class="pw-opt"'
                f' data-val="{v}" data-label="{l}" data-sel="{sel}"'
                f' onclick="{onclick}"'
                f' style="padding:10px 14px;cursor:pointer;font-size:14px;font-weight:{weight}">'
                f"{l}</div>"
            )

        opt_items = "".join(make_opt(v, l) for v, l in opts)

        return (
            f"<style>"
            f"#{uid}_list .pw-opt{{color:var(--text);background:transparent;border-radius:6px;transition:background .12s}}"
            f"#{uid}_list .pw-opt:hover{{background:var(--surface-2)}}"
            f'#{uid}_list .pw-opt[data-sel="1"]{{background:rgba(99,102,241,0.15);color:var(--accent);font-weight:600}}'
            f"</style>"
            f'<div id="{uid}_wrap" style="{wrapper_style}">'
            f"  {hidden_input}"
            f'  <div id="{uid}_btn" onclick="pwSelectToggle(\'{uid}\')"'
            f'    style="display:flex;align-items:center;justify-content:space-between;'
            f"           padding:8px 14px;border:1px solid var(--border-input,var(--border));border-radius:6px;"
            f'           background:var(--input-bg);cursor:pointer;user-select:none;gap:8px;transition:border-color .2s">'
            f'    <span id="{uid}_label" style="color:var(--input-color,var(--text));flex:1;font-size:14px">{selected_lbl}</span>'
            f'    <svg id="{uid}_arrow" width="12" height="12" viewBox="0 0 12 12"'
            f'         style="flex-shrink:0;transition:transform .2s;opacity:0.5">'
            f'      <path d="M2 4l4 4 4-4" stroke="currentColor" stroke-width="1.5" fill="none" stroke-linecap="round"/>'
            f"    </svg>"
            f"  </div>"
            f'  <div id="{uid}_drop"'
            f'    style="display:none;position:absolute;top:calc(100% + 6px);left:0;right:0;'
            f"           z-index:10020;border:1px solid var(--border-input,var(--border));border-radius:10px;"
            f'           box-shadow:0 12px 40px rgba(0,0,0,0.25);overflow:hidden;background:var(--dropdown-bg,var(--surface))">'
            f'    <div style="padding:8px 8px 6px;border-bottom:1px solid var(--border)">'
            f'      <input id="{uid}_search" type="text" placeholder="Buscar..."'
            f"        oninput=\"pwSelectFilter('{uid}',this.value)\""
            f'        style="width:100%;padding:7px 10px;border:1px solid var(--border-input,var(--border));'
            f"               border-radius:6px;font-size:13px;outline:none;box-sizing:border-box;"
            f'               background:var(--input-bg,var(--surface));color:var(--input-color,var(--text))">'
            f"    </div>"
            f'    <div id="{uid}_list" style="max-height:220px;overflow-y:auto;padding:6px">'
            f"      {opt_items}"
            f"    </div>"
            f"  </div>"
            f"</div>"
            "<script>"
            "(function(){if(window._pwSelInit)return;window._pwSelInit=true;"
            "window.pwSelectToggle=function(uid){"
            '  var d=document.getElementById(uid+"_drop"),'
            '      a=document.getElementById(uid+"_arrow"),'
            '      b=document.getElementById(uid+"_btn"),'
            '      o=d.style.display!=="none";'
            '  document.querySelectorAll("[id$=_drop]").forEach(function(el){'
            '    if(el.id!==uid+"_drop"){el.style.display="none";'
            '      var x=document.getElementById(el.id.replace("_drop","_arrow"));'
            '      if(x)x.style.transform="";'
            '      var bx=document.getElementById(el.id.replace("_drop","_btn"));'
            '      if(bx)bx.style.borderColor="";}'
            "  });"
            '  if(o){d.style.display="none";a.style.transform="";b.style.borderColor="";}'
            '  else{d.style.display="block";a.style.transform="rotate(180deg)";'
            '    b.style.borderColor="var(--accent)";'
            '    setTimeout(function(){var s=document.getElementById(uid+"_search");'
            '      if(s){s.value="";s.focus();pwSelectFilter(uid,"");}},30);}'
            "};"
            "window.pwSelectFilter=function(uid,q){"
            '  document.querySelectorAll("#"+uid+"_list .pw-opt").forEach(function(i){'
            '    i.style.display=i.getAttribute("data-label").toLowerCase().includes(q.toLowerCase())?"block":"none";'
            "  });"
            "};"
            "window.pwSelectPick=function(uid,val,label){"
            '  document.getElementById(uid+"_val").value=val;'
            '  document.getElementById(uid+"_label").textContent=label;'
            '  document.getElementById(uid+"_drop").style.display="none";'
            '  document.getElementById(uid+"_arrow").style.transform="";'
            '  document.getElementById(uid+"_btn").style.borderColor="";'
            '  document.querySelectorAll("#"+uid+"_list .pw-opt").forEach(function(el){'
            '    var s=el.getAttribute("data-val")===val;'
            '    el.setAttribute("data-sel",s?"1":"0");'
            '    el.style.fontWeight=s?"600":"400";'
            "  });"
            "};"
            'document.addEventListener("click",function(e){'
            '  if(!e.target.closest("[id$=_wrap]")){'
            '    document.querySelectorAll("[id$=_drop]").forEach(function(el){'
            '      el.style.display="none";'
            '      var a=document.getElementById(el.id.replace("_drop","_arrow"));'
            '      if(a)a.style.transform="";'
            '      var b=document.getElementById(el.id.replace("_drop","_btn"));'
            '      if(b)b.style.borderColor="";'
            "    });"
            "  }"
            "});"
            "})();</script>"
        )


# =============================================================================
# MultiSelect
# =============================================================================


class MultiSelect(Widget):
    """
    Selector múltiple con tags visuales y búsqueda.

        MultiSelect(options=["A", "B", "C"], values=["A"], radius=8)
        MultiSelect(options=[("py", "Python"), ("js", "JavaScript")], values=["py"])
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
        uid = self.uid
        extra = self._resolve_props()
        opts = self._parse_options()
        selected_vals = [str(v) for v in self.values]

        opts_js = _json.dumps([{"v": v, "l": l} for v, l in opts])
        name_js = _json.dumps(self.name or "")
        tc_js = _json.dumps(self.tag_color)
        tb_js = _json.dumps(self.tag_border)
        tt_js = _json.dumps(self.tag_text)
        ph_js = _json.dumps(self.placeholder)
        sel_js = _json.dumps(selected_vals)

        opt_rows = "".join(
            f'<div class="pw-mopt" data-val="{v}" data-label="{l}"'
            f' style="padding:10px 14px;cursor:pointer;font-size:14px;'
            f'display:{"none" if v in selected_vals else "block"}">{l}</div>'
            for v, l in opts
        )

        wrapper_style = f"position:relative;width:100%;font-size:14px;{extra}"

        return (
            f'<div id="{uid}_wrap" style="{wrapper_style}">'
            f'  <div id="{uid}_box"'
            f'    style="display:flex;flex-wrap:wrap;align-items:center;gap:6px;'
            f"           min-height:42px;padding:6px 10px;"
            f"           border:1px solid var(--border-input,var(--border));border-radius:8px;"
            f'           background:var(--input-bg,var(--surface));cursor:text;transition:border-color .2s"'
            f"    onclick=\"document.getElementById('{uid}_input').focus()\">"
            f'    <input id="{uid}_input" type="text" placeholder="{self.placeholder}"'
            f'      style="border:none;outline:none;background:transparent;'
            f'             color:var(--text);font-size:14px;flex:1;min-width:80px;">'
            f"  </div>"
            f'  <div id="{uid}_hidden"></div>'
            f'  <div id="{uid}_drop"'
            f'    style="display:none;position:absolute;top:calc(100% + 6px);left:0;right:0;'
            f"           z-index:10020;border:1px solid var(--border-input,var(--border));border-radius:10px;"
            f'           box-shadow:0 12px 40px rgba(0,0,0,0.25);overflow:hidden;background:var(--dropdown-bg,var(--surface))">'
            f'    <div id="{uid}_list"'
            f'      style="max-height:220px;overflow-y:auto;padding:6px">'
            f"      {opt_rows}"
            f"    </div>"
            f'    <div style="padding:6px 12px 8px;border-top:1px solid var(--border);'
            f'                display:flex;justify-content:flex-end">'
            f'      <span id="{uid}_clear"'
            f'        style="font-size:12px;color:var(--text-muted);cursor:pointer;user-select:none">'
            f"        Limpiar todo"
            f"      </span>"
            f"    </div>"
            f"  </div>"
            f"</div>"
            f"<script>(function(){{"
            f"var uid={_json.dumps(uid)};"
            f"var opts={opts_js};"
            f"var name={name_js};"
            f"var tc={tc_js};"
            f"var tb={tb_js};"
            f"var tt={tt_js};"
            f"var ph={ph_js};"
            f"var sel=new Set({sel_js});"
            f"if(!window._pwMultiState)window._pwMultiState={{}};"
            f"window._pwMultiState[uid]=sel;"
            f"var box=document.getElementById(uid+'_box');"
            f"var input=document.getElementById(uid+'_input');"
            f"var drop=document.getElementById(uid+'_drop');"
            f"var list=document.getElementById(uid+'_list');"
            f"var hidden=document.getElementById(uid+'_hidden');"
            f"var clearBtn=document.getElementById(uid+'_clear');"
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
            f"}})();</script>"
        )


# =============================================================================
# Slider
# =============================================================================


class Slider(Widget):
    """
    Control deslizante simple o de rango doble.

        Slider(label="Volumen", min=0, max=100, value=70, format="{v}%")

        Slider(label="Precio", min=0, max=1000, value=200, value_max=800,
               range=True, format="${v}", step=10)

    Parámetros:
        label       str     etiqueta encima del slider
        min         int     valor mínimo (default: 0)
        max         int     valor máximo (default: 100)
        value       int     valor inicial (o extremo inferior en range=True)
        value_max   int     extremo superior en modo range
        step        int|float  incremento (default: 1)
        range       bool    modo doble cursor
        show_value  bool    muestra el valor actual (default: True)
        show_ticks  bool    muestra mín/máx debajo del slider
        format      str     formato de display — usar {v} como placeholder
        name        str     nombre para formularios
        id          str     id del elemento
        disabled    bool    deshabilita el control
        color       str     color del rango activo (default: var(--accent))
    """

    _id_counter = 0

    def __init__(
        self,
        label=None,
        min=0,
        max=100,
        value=None,
        value_max=None,
        step=1,
        range=False,
        show_value=True,
        show_ticks=False,
        format="{v}",
        name=None,
        id=None,
        disabled=False,
        color="var(--accent)",
        **kwargs,
    ):
        self._props = Widget._extract_props(kwargs)
        self.label = label
        self.min = min
        self.max = max
        self.value = value if value is not None else min
        self.value_max = value_max if value_max is not None else max
        self.step = step
        self.is_range = range
        self.show_value = show_value
        self.show_ticks = show_ticks
        self.format = format
        self.name = name
        self.disabled = disabled
        self.color = color
        Slider._id_counter += 1
        self.uid = id or f"sl_{Slider._id_counter}"

    def _fmt(self, v):
        return self.format.replace("{v}", str(v))

    def render(self):
        uid = self.uid
        mn, mx, st = self.min, self.max, self.step
        v1, v2 = self.value, self.value_max
        color = self.color
        dis = " disabled" if self.disabled else ""
        extra = self._resolve_props()
        w_extra = f";{extra}" if extra else ""

        # ── CSS del thumb (webkit + moz) ──────────────────────────────────
        css = (
            f"<style>"
            f"#{uid}_w input[type=range]{{-webkit-appearance:none;appearance:none;"
            f"width:100%;height:6px;border-radius:3px;outline:none;cursor:pointer;"
            f"background:transparent}}"
            f"#{uid}_w input[type=range]::-webkit-slider-thumb{{"
            f"-webkit-appearance:none;appearance:none;"
            f"width:20px;height:20px;border-radius:50%;background:{color};"
            f"cursor:pointer;border:2.5px solid var(--surface);"
            f"box-shadow:0 1px 6px rgba(0,0,0,.3);transition:transform .12s}}"
            f"#{uid}_w input[type=range]::-moz-range-thumb{{"
            f"width:20px;height:20px;border-radius:50%;background:{color};"
            f"cursor:pointer;border:2.5px solid var(--surface);"
            f"box-shadow:0 1px 6px rgba(0,0,0,.3)}}"
            f"#{uid}_w input[type=range]:hover::-webkit-slider-thumb{{transform:scale(1.18)}}"
            f"#{uid}_w input[type=range]:disabled{{opacity:.4;cursor:not-allowed}}"
            f"</style>"
        )

        # ── Etiqueta + display de valor ───────────────────────────────────
        disp_init = (
            f"{self._fmt(v1)} \u2014 {self._fmt(v2)}"
            if self.is_range
            else self._fmt(v1)
        )
        hdr = ""
        if self.label or self.show_value:
            left_html = (
                f'<span style="font-size:13px;font-weight:600;color:var(--text)">'
                f"{self.label}</span>"
                if self.label
                else "<span></span>"
            )
            right_html = (
                f'<span id="{uid}_disp" style="font-size:13px;font-weight:600;'
                f'color:{color}">{disp_init}</span>'
                if self.show_value
                else ""
            )
            hdr = (
                f'<div style="display:flex;justify-content:space-between;'
                f'align-items:center;margin-bottom:10px">'
                f"{left_html}{right_html}</div>"
            )

        # ── Ticks ─────────────────────────────────────────────────────────
        ticks = ""
        if self.show_ticks:
            ticks = (
                f'<div style="display:flex;justify-content:space-between;'
                f'margin-top:5px;font-size:11px;color:var(--text-muted)">'
                f"<span>{self._fmt(mn)}</span><span>{self._fmt(mx)}</span></div>"
            )

        if not self.is_range:
            # ── Slider simple ─────────────────────────────────────────────
            pct = (v1 - mn) / (mx - mn) * 100 if mx != mn else 0
            # Track con color via CSS gradient (actualizado en JS)
            track_bg = (
                f"linear-gradient(to right,{color} {pct:.1f}%,"
                f"var(--border,#334155) {pct:.1f}%)"
            )
            name_attr = f' name="{self.name}"' if self.name else ""
            # JS: actualiza track + display sin comillas conflictivas
            js_update = (
                f"var p=(this.value-{mn})/({mx}-{mn})*100;"
                f"this.style.background="
                f"'linear-gradient(to right,{color} '+p+'%,var(--border,#334155) '+p+'%)';"
            )
            if self.show_value:
                js_update += (
                    f"var d=document.getElementById('{uid}_disp');"
                    f"if(d)d.textContent='{self.format}'.replace('{{v}}',this.value);"
                )
            track_html = (
                f'<input type="range" id="{uid}" min="{mn}" max="{mx}" '
                f'step="{st}" value="{v1}"{name_attr}{dis} '
                f'style="width:100%;background:{track_bg}" '
                f'oninput="{js_update}">'
            )
            body = hdr + track_html + ticks

        else:
            # ── Slider de rango doble ─────────────────────────────────────
            # Arquitectura: track visual separado (div), dos inputs transparentes encima.
            # El z-index del thumb activo se gestiona en JS según cuál está siendo movido.
            p1 = (v1 - mn) / (mx - mn) * 100 if mx != mn else 0
            p2 = (v2 - mn) / (mx - mn) * 100 if mx != mn else 100
            n1 = f' name="{self.name}_min"' if self.name else ""
            n2 = f' name="{self.name}_max"' if self.name else ""

            track_html = (
                # Track container
                f'<div style="position:relative;height:28px;display:flex;align-items:center">'
                # Track visual (fondo gris + relleno de color)
                f'<div style="position:absolute;left:0;right:0;height:6px;'
                f'border-radius:3px;background:var(--border,#334155);overflow:visible">'
                f'<div id="{uid}_fill" style="position:absolute;height:100%;'
                f"background:{color};border-radius:3px;"
                f'left:{p1:.1f}%;right:{100-p2:.1f}%"></div>'
                f"</div>"
                # Input MIN — encima del track, transparente
                f'<input type="range" id="{uid}_a" min="{mn}" max="{mx}" '
                f'step="{st}" value="{v1}"{n1}{dis} '
                f'style="position:absolute;left:0;right:0;width:100%;'
                f'margin:0;background:transparent;z-index:3;pointer-events:none">'
                # Input MAX
                f'<input type="range" id="{uid}_b" min="{mn}" max="{mx}" '
                f'step="{st}" value="{v2}"{n2}{dis} '
                f'style="position:absolute;left:0;right:0;width:100%;'
                f'margin:0;background:transparent;z-index:4;pointer-events:none">'
                f"</div>"
            )

            # JS limpio — sin usar 'this' dentro de funciones nombradas
            js = f"""<script>(function(){{
  var uid='{uid}',mn={mn},mx={mx};
  var fmt='{self.format}';
  var show={str(self.show_value).lower()};

  function pct(v){{return (v-mn)/(mx-mn)*100;}}
  function fmtV(v){{return fmt.replace('{{v}}',v);}}

  function sync(){{
    var a=document.getElementById(uid+'_a');
    var b=document.getElementById(uid+'_b');
    var fill=document.getElementById(uid+'_fill');
    var disp=document.getElementById(uid+'_disp');
    if(!a||!b)return;

    var va=parseFloat(a.value), vb=parseFloat(b.value);

    // Cruce: empujar el otro thumb
    if(va>vb){{ b.value=va; vb=va; }}

    var pa=pct(va), pb=pct(vb);
    if(fill){{
      fill.style.left=pa+'%';
      fill.style.right=(100-pb)+'%';
    }}
    if(show&&disp){{
      disp.textContent=fmtV(va)+' \u2014 '+fmtV(vb);
    }}

    // El thumb que está más a la derecha necesita z-index mayor
    // para ser clickeable cuando ambos están en el extremo derecho
    a.style.zIndex=(va>=mx)?'5':'3';
    b.style.zIndex=(vb>=mx)?'4':'4';
  }}

  function enableThumb(el){{
    el.style.pointerEvents='all';
  }}
  function disableThumb(el){{
    el.style.pointerEvents='none';
  }}

  var a=document.getElementById(uid+'_a');
  var b=document.getElementById(uid+'_b');
  if(!a||!b)return;

  // Habilitar pointer-events al mousedown/touch, deshabilitar al soltar
  [a,b].forEach(function(el){{
    el.addEventListener('mousedown', function(){{ enableThumb(el); }});
    el.addEventListener('touchstart',function(){{ enableThumb(el); }},{{passive:true}});
    el.addEventListener('input',     sync);
    el.addEventListener('change',    sync);
    el.addEventListener('mouseup',   function(){{ disableThumb(el); sync(); }});
    el.addEventListener('touchend',  function(){{ disableThumb(el); sync(); }});
  }});

  // Al hover sobre la zona del track, activar el thumb más cercano al cursor
  var wrap=document.getElementById('{uid}_w');
  if(wrap){{
    wrap.addEventListener('mousemove',function(e){{
      var rect=wrap.getBoundingClientRect();
      var relX=(e.clientX-rect.left)/rect.width;
      var va=parseFloat(a.value), vb=parseFloat(b.value);
      var pa=(va-mn)/(mx-mn), pb=(vb-mn)/(mx-mn);
      var distA=Math.abs(relX-pa), distB=Math.abs(relX-pb);
      if(distA<=distB){{
        enableThumb(a); disableThumb(b);
        a.style.zIndex='5'; b.style.zIndex='3';
      }}else{{
        enableThumb(b); disableThumb(a);
        b.style.zIndex='5'; a.style.zIndex='3';
      }}
    }});
    wrap.addEventListener('mouseleave',function(){{
      disableThumb(a); disableThumb(b);
    }});
  }}

  // Render inicial
  sync();
}})();</script>"""

            body = hdr + track_html + ticks + js

        return (
            css
            + f'<div id="{uid}_w" style="width:100%;user-select:none{w_extra}">'
            + body
            + "</div>"
        )


# =============================================================================
# RadioGroup
# =============================================================================


class RadioGroup(Widget):
    """
    Grupo de botones de opción (radio buttons).

        RadioGroup(
            label="Género",
            name="genero",
            options=["Masculino", "Femenino", "Otro"],
            value="Otro",
        )

        RadioGroup(
            name="plan",
            options=[("free", "Gratis"), ("pro", "Pro $9/mes"), ("biz", "Business $29/mes")],
            value="pro",
            direction="column",
        )

    Parámetros:
        label       str     etiqueta del grupo
        name        str     nombre del input (requerido para formularios)
        options     list    strings o tuplas (value, label)
        value       str     opción seleccionada inicialmente
        direction   str     "row" | "column" (default: "row")
        id          str     id base del grupo
        disabled    bool    deshabilita todas las opciones
        on_change   str     JS ejecutado al cambiar (recibe el valor como string)
    """

    _id_counter = 0

    def __init__(
        self,
        options=None,
        value=None,
        name=None,
        label=None,
        direction="row",
        id=None,
        disabled=False,
        on_change=None,
        **kwargs,
    ):
        self._props = Widget._extract_props(kwargs)
        self.options = options or []
        self.value = value
        self.name = name
        self.label = label
        self.direction = direction
        self.disabled = disabled
        self.on_change = on_change
        RadioGroup._id_counter += 1
        self.uid = id or f"rg_{RadioGroup._id_counter}"

    def _parse(self):
        out = []
        for opt in self.options:
            if isinstance(opt, (tuple, list)):
                out.append((str(opt[0]), str(opt[1]) if len(opt) > 1 else str(opt[0])))
            else:
                out.append((str(opt), str(opt)))
        return out

    def render(self):
        uid = self.uid
        opts = self._parse()
        extra = self._resolve_props()
        gap = "12px" if self.direction == "row" else "8px"
        flex_dir = "row" if self.direction == "row" else "column"

        css = (
            f"<style>"
            f"#{uid}_wrap label{{display:inline-flex;align-items:center;gap:8px;"
            f"cursor:pointer;font-size:14px;color:var(--text);user-select:none}}"
            f"#{uid}_wrap input[type=radio]{{-webkit-appearance:none;appearance:none;"
            f"width:18px;height:18px;border-radius:50%;flex-shrink:0;"
            f"border:2px solid var(--border-input,var(--border));"
            f"background:var(--input-bg,var(--surface));transition:all .15s;cursor:pointer}}"
            f"#{uid}_wrap input[type=radio]:checked{{border-color:var(--accent);"
            f"background:var(--accent);"
            f"box-shadow:inset 0 0 0 3px var(--surface)}}"
            f"#{uid}_wrap input[type=radio]:hover:not(:disabled){{border-color:var(--accent)}}"
            f"#{uid}_wrap input[type=radio]:disabled{{opacity:.4;cursor:not-allowed}}"
            f"#{uid}_wrap label:has(input:disabled){{opacity:.5;cursor:not-allowed}}"
            f"</style>"
        )

        label_html = ""
        if self.label:
            label_html = (
                f'<div style="font-size:13px;font-weight:600;color:var(--text);'
                f'margin-bottom:8px">{self.label}</div>'
            )

        on_change_js = ""
        if self.on_change:
            on_change_js = f' onchange="({self.on_change})(this.value)"'

        items = ""
        for i, (val, lbl) in enumerate(opts):
            rid = f"{uid}_{i}"
            checked = " checked" if str(val) == str(self.value) else ""
            dis = " disabled" if self.disabled else ""
            items += (
                f'<label for="{rid}">'
                f'<input type="radio" id="{rid}" name="{self.name or uid}" '
                f'value="{val}"{checked}{dis}{on_change_js}>'
                f"<span>{lbl}</span>"
                f"</label>"
            )

        wrap_style = (
            f"display:flex;flex-direction:{flex_dir};gap:{gap};flex-wrap:wrap"
            + (f";{extra}" if extra else "")
        )

        return (
            css
            + f'<div id="{uid}_wrap" style="display:flex;flex-direction:column">'
            + label_html
            + f'<div style="{wrap_style}">{items}</div>'
            + "</div>"
        )


# =============================================================================
# NumberInput
# =============================================================================


class NumberInput(Widget):
    """
    Campo numérico con botones +/− integrados.

        NumberInput(value=5, min=1, max=100)
        NumberInput(label="Cantidad", value=1, min=1, max=99, step=1)
        NumberInput(label="Precio", value=9.99, step=0.01, format="$ {v}")

    Parámetros:
        label       str     etiqueta encima del input
        value       int|float  valor inicial
        min         int|float  valor mínimo
        max         int|float  valor máximo
        step        int|float  incremento de +/- (default: 1)
        format      str     formato de display — usar {v} como placeholder
        name        str     nombre para formularios
        id          str     id del elemento
        disabled    bool    deshabilita el control
        on_change   str     JS ejecutado al cambiar (recibe el valor numérico)
    """

    _id_counter = 0

    def __init__(
        self,
        label=None,
        value=0,
        min=None,
        max=None,
        step=1,
        format="{v}",
        name=None,
        id=None,
        disabled=False,
        on_change=None,
        **kwargs,
    ):
        self._props = Widget._extract_props(kwargs)
        self.label = label
        self.value = value
        self.min = min
        self.max = max
        self.step = step
        self.format = format
        self.name = name
        self.disabled = disabled
        self.on_change = on_change
        NumberInput._id_counter += 1
        self.uid = id or f"ni_{NumberInput._id_counter}"

    def render(self):
        uid = self.uid
        extra = self._resolve_props()
        dis = " disabled" if self.disabled else ""
        mn_js = str(self.min) if self.min is not None else "null"
        mx_js = str(self.max) if self.max is not None else "null"
        on_change_js = f";({self.on_change})(v);" if self.on_change else ""

        label_html = ""
        if self.label:
            label_html = (
                f'<div style="font-size:13px;font-weight:600;color:var(--text);'
                f'margin-bottom:6px">{self.label}</div>'
            )

        btn_style = (
            "background:var(--surface-2,var(--surface));border:1px solid var(--border);"
            "color:var(--text);cursor:pointer;font-size:16px;font-weight:500;"
            "width:36px;height:36px;display:flex;align-items:center;justify-content:center;"
            "flex-shrink:0;transition:background .12s;user-select:none"
        )

        fmt_escaped = self.format.replace("'", "\\'")

        js = f"""<script>(function(){{
  var uid='{uid}',step={self.step},mn={mn_js},mx={mx_js};
  var fmt='{fmt_escaped}';
  function get(){{
    var el=document.getElementById(uid+'_in');
    return el?parseFloat(el.dataset.value)||0:0;
  }}
  function set(v){{
    if(mn!==null&&v<mn)v=mn;
    if(mx!==null&&v>mx)v=mx;
    // round to step precision
    var dec=(step.toString().split('.')[1]||'').length;
    v=parseFloat(v.toFixed(dec));
    var el=document.getElementById(uid+'_in');
    if(!el)return;
    el.dataset.value=v;
    el.textContent=fmt.replace('{{v}}',v);
    var hi=document.getElementById(uid+'_hid');
    if(hi)hi.value=v;
    {on_change_js}
  }}
  window[uid+'_inc']=function(){{set(get()+step);}};
  window[uid+'_dec']=function(){{set(get()-step);}};
  // init
  set({self.value});
}})();</script>"""

        wrapper_style = "display:inline-flex;flex-direction:column" + (
            f";{extra}" if extra else ""
        )

        return (
            f'<div style="{wrapper_style}">'
            + label_html
            + f'<div style="display:inline-flex;align-items:center;'
            f"border:1px solid var(--border-input,var(--border));border-radius:8px;"
            f'overflow:hidden;background:var(--input-bg,var(--surface))">'
            f'<button type="button" onclick="{uid}_dec()" style="{btn_style};'
            f'border-right:1px solid var(--border)"'
            + (" disabled" if self.disabled else "")
            + f">−</button>"
            f'<div id="{uid}_in" data-value="{self.value}" '
            f'style="min-width:64px;text-align:center;font-size:14px;'
            f"font-weight:600;color:var(--text);padding:0 12px;"
            f'height:36px;display:flex;align-items:center;justify-content:center">'
            f"{self.value}</div>"
            f'<button type="button" onclick="{uid}_inc()" style="{btn_style};'
            f'border-left:1px solid var(--border)"'
            + (" disabled" if self.disabled else "")
            + f">+</button>"
            + (
                f'<input type="hidden" id="{uid}_hid" name="{self.name}" value="{self.value}">'
                if self.name
                else ""
            )
            + "</div>"
            + js
            + "</div>"
        )


# =============================================================================
# TimePicker
# =============================================================================


class TimePicker(Widget):
    """
    Selector de hora con ruedas de scroll o inputs numéricos.

        TimePicker(label="Hora de inicio", value="09:00")
        TimePicker(value="14:30", seconds=True)
        TimePicker(value="08:00", format_12h=True)

    Parámetros:
        label       str     etiqueta encima
        value       str     hora inicial "HH:MM" o "HH:MM:SS"
        seconds     bool    incluye selector de segundos
        format_12h  bool    modo 12h con AM/PM
        name        str     nombre para formularios
        id          str     id del elemento
        disabled    bool    deshabilita el control
        step        int     incremento de minutos (default: 1)
        on_change   str     JS ejecutado al cambiar (recibe "HH:MM" o "HH:MM:SS")
    """

    _id_counter = 0

    def __init__(
        self,
        label=None,
        value="00:00",
        seconds=False,
        format_12h=False,
        name=None,
        id=None,
        disabled=False,
        step=1,
        on_change=None,
        **kwargs,
    ):
        self._props = Widget._extract_props(kwargs)
        self.label = label
        self.value = value or "00:00"
        self.seconds = seconds
        self.format_12h = format_12h
        self.name = name
        self.disabled = disabled
        self.step = step
        self.on_change = on_change
        TimePicker._id_counter += 1
        self.uid = id or f"tp_{TimePicker._id_counter}"

    def _parse(self):
        parts = (self.value or "00:00").split(":")
        h = int(parts[0]) if parts else 0
        m = int(parts[1]) if len(parts) > 1 else 0
        s = int(parts[2]) if len(parts) > 2 else 0
        return h, m, s

    def render(self):
        uid = self.uid
        h, m, s = self._parse()
        extra = self._resolve_props()
        dis = " disabled" if self.disabled else ""
        on_change_js = f";({self.on_change})(v);" if self.on_change else ""

        # Convertir a 12h si aplica
        ampm = "AM"
        h12 = h
        if self.format_12h:
            ampm = "PM" if h >= 12 else "AM"
            h12 = h % 12
            if h12 == 0:
                h12 = 12

        label_html = ""
        if self.label:
            label_html = (
                f'<div style="font-size:13px;font-weight:600;color:var(--text);'
                f'margin-bottom:6px">{self.label}</div>'
            )

        input_style = (
            "width:52px;text-align:center;font-size:20px;font-weight:700;"
            "border:none;outline:none;background:transparent;color:var(--text);"
            "padding:4px 0"
        )
        sep_style = (
            "font-size:20px;font-weight:700;color:var(--text-muted);line-height:1"
        )

        h_init = h12 if self.format_12h else h
        h_max = 11 if self.format_12h else 23

        js = f"""<script>(function(){{
  var uid='{uid}';
  var use12={str(self.format_12h).lower()};
  var useS={str(self.seconds).lower()};
  {on_change_js and f"var cb=function(v){{{on_change_js}}};"}

  function pad(n){{return n<10?'0'+n:String(n);}}

  function getVal(id){{
    var el=document.getElementById(uid+'_'+id);
    return el?parseInt(el.value)||0:0;
  }}

  function update(){{
    var h=getVal('h'),m=getVal('m'),s=useS?getVal('s'):0;
    if(use12){{
      var ap=document.getElementById(uid+'_ap');
      var ispm=ap&&ap.value==='PM';
      h=h%12+(ispm?12:0);
    }}
    var v=pad(h)+':'+pad(m)+(useS?':'+pad(s):'');
    var hi=document.getElementById(uid+'_hid');
    if(hi)hi.value=v;
    {'var cb=function(v){'+on_change_js+'};cb(v);' if self.on_change else ''}
  }}

  // Bind all inputs
  ['h','m','s','ap'].forEach(function(k){{
    var el=document.getElementById(uid+'_'+k);
    if(el)el.addEventListener('change',update);
    if(el)el.addEventListener('input',update);
  }});
}})();</script>"""

        ampm_select = ""
        if self.format_12h:
            ampm_select = (
                f'<select id="{uid}_ap"{dis} style="'
                f"margin-left:8px;font-size:14px;font-weight:600;"
                f'background:var(--input-bg,var(--surface));color:var(--text);">'
                f'<option value="AM"{"selected" if ampm=="AM" else ""}>AM</option>'
                f'<option value="PM"{"selected" if ampm=="PM" else ""}>PM</option>'
                f"</select>"
            )

        secs_html = ""
        if self.seconds:
            secs_html = (
                f'<span style="{sep_style}">:</span>'
                f'<input type="number" id="{uid}_s" min="0" max="59" '
                f'value="{s:02d}"{dis} style="{input_style}">'
            )

        hidden = (
            f'<input type="hidden" id="{uid}_hid" name="{self.name}" value="{self.value}">'
            if self.name
            else ""
        )

        wrapper_style = "display:inline-flex;flex-direction:column" + (
            f";{extra}" if extra else ""
        )
        field_style = (
            "display:inline-flex;align-items:center;gap:4px;"
            "padding:8px 16px;"
            "border:1px solid var(--border-input,var(--border));"
            "border-radius:10px;background:var(--input-bg,var(--surface))"
        )

        return (
            f'<div style="{wrapper_style}">'
            + label_html
            + f'<div style="{field_style}">'
            + f'<input type="number" id="{uid}_h" min="0" max="{h_max}" '
            + f'value="{h_init:02d}"{dis} style="{input_style}">'
            + f'<span style="{sep_style}">:</span>'
            + f'<input type="number" id="{uid}_m" min="0" max="59" step="{self.step}" '
            + f'value="{m:02d}"{dis} style="{input_style}">'
            + secs_html
            + ampm_select
            + "</div>"
            + hidden
            + js
            + "</div>"
        )


# =============================================================================
# ProgressBar
# =============================================================================


class ProgressBar(Widget):
    """
    Barra de progreso determinada o indeterminada.

        ProgressBar(value=65)
        ProgressBar(value=30, label="Cargando...", color="#22c55e")
        ProgressBar(indeterminate=True, label="Procesando...")
        ProgressBar(value=80, show_value=True, striped=True, animated=True)

    Parámetros:
        value           int     porcentaje de progreso (0-100)
        label           str     texto encima de la barra
        show_value      bool    muestra el porcentaje dentro/fuera de la barra
        color           str     color de la barra (default: var(--accent))
        height          int     altura en px (default: 8)
        radius          int     border-radius (default: 999 = píldora)
        striped         bool    efecto de rayas
        animated        bool    anima las rayas (requiere striped=True)
        indeterminate   bool    modo indeterminado (barra que oscila)
        id              str     id del elemento (para actualizar dinámicamente)
    """

    _id_counter = 0

    def __init__(
        self,
        value=0,
        label=None,
        show_value=False,
        color="var(--accent)",
        height=8,
        radius=999,
        striped=False,
        animated=False,
        indeterminate=False,
        id=None,
        **kwargs,
    ):
        self._props = Widget._extract_props(kwargs)
        self.value = max(0, min(100, value))
        self.label = label
        self.show_value = show_value
        self.color = color
        self.height = height
        self.radius = radius
        self.striped = striped
        self.animated = animated
        self.indeterminate = indeterminate
        ProgressBar._id_counter += 1
        self.uid = id or f"pb_{ProgressBar._id_counter}"

    def render(self):
        uid = self.uid
        extra = self._resolve_props()
        wrapper_extra = f";{extra}" if extra else ""

        # Animación CSS
        css = ""
        if self.indeterminate:
            css = (
                f"<style>"
                f"@keyframes {uid}_ind{{"
                f"0%{{left:-40%;width:40%}}"
                f"60%{{left:60%;width:40%}}"
                f"100%{{left:100%;width:0}}"
                f"}}"
                f"#{uid}_bar{{animation:{uid}_ind 1.5s ease-in-out infinite}}"
                f"</style>"
            )
        elif self.striped:
            stripe_anim = (
                f"@keyframes {uid}_str{{from{{background-position:0 0}}to{{background-position:40px 0}}}}"
                if self.animated
                else ""
            )
            anim_css = (
                f"animation:{uid}_str 1s linear infinite;" if self.animated else ""
            )
            css = (
                f"<style>" + stripe_anim + f"#{uid}_bar{{"
                f"background-image:linear-gradient(45deg,"
                f"rgba(255,255,255,.2) 25%,transparent 25%,"
                f"transparent 50%,rgba(255,255,255,.2) 50%,"
                f"rgba(255,255,255,.2) 75%,transparent 75%);"
                f"background-size:40px 40px;{anim_css}}}"
                f"</style>"
            )

        label_html = ""
        if self.label:
            label_html = (
                f'<div style="display:flex;justify-content:space-between;'
                f'align-items:center;margin-bottom:6px">'
                f'<span style="font-size:13px;font-weight:600;color:var(--text)">'
                f"{self.label}</span>"
                + (
                    f'<span style="font-size:13px;font-weight:600;color:{self.color}">'
                    f"{self.value}%</span>"
                    if self.show_value
                    else ""
                )
                + "</div>"
            )
        elif self.show_value:
            label_html = (
                f'<div style="text-align:right;margin-bottom:4px;'
                f'font-size:13px;font-weight:600;color:{self.color}">'
                f"{self.value}%</div>"
            )

        if self.indeterminate:
            bar_inner = (
                f'<div id="{uid}_bar" style="position:absolute;height:100%;'
                f'background:{self.color};border-radius:{self.radius}px"></div>'
            )
            track_style = (
                f"position:relative;overflow:hidden;width:100%;"
                f"height:{self.height}px;border-radius:{self.radius}px;"
                f"background:var(--border,rgba(99,102,241,.15))"
            )
        else:
            bar_inner = (
                f'<div id="{uid}_bar" style="width:{self.value}%;height:100%;'
                f"background:{self.color};border-radius:{self.radius}px;"
                f'transition:width .4s ease">'
                f"</div>"
            )
            track_style = (
                f"width:100%;height:{self.height}px;border-radius:{self.radius}px;"
                f"background:var(--border,rgba(99,102,241,.15));overflow:hidden"
            )

        return (
            css
            + f'<div id="{uid}" style="width:100%{wrapper_extra}">'
            + label_html
            + f'<div style="{track_style}">{bar_inner}</div>'
            + "</div>"
        )


# =============================================================================
# Rating
# =============================================================================


class Rating(Widget):
    """
    Widget de calificación con estrellas (o cualquier símbolo).

        Rating(value=4)
        Rating(label="Calidad", value=3, max=5, on_change="console.log")
        Rating(value=4.5, readonly=True, half=True)
        Rating(symbol="❤", value=3, color="#ef4444")

    Parámetros:
        value       int|float  valor inicial
        max         int     número de estrellas (default: 5)
        label       str     etiqueta encima
        readonly    bool    solo muestra, no permite cambiar
        half        bool    permite medias estrellas
        symbol      str     carácter o emoji (default: "★")
        color       str     color activo (default: "#f59e0b")
        size        int     tamaño en px (default: 28)
        name        str     nombre para formularios
        id          str     id del elemento
        on_change   str     JS ejecutado al cambiar (recibe el valor)
    """

    _id_counter = 0

    def __init__(
        self,
        value=0,
        max=5,
        label=None,
        readonly=False,
        half=False,
        symbol="★",
        color="#f59e0b",
        size=28,
        name=None,
        id=None,
        on_change=None,
        **kwargs,
    ):
        self._props = Widget._extract_props(kwargs)
        self.value = value
        self.max = max
        self.label = label
        self.readonly = readonly
        self.half = half
        self.symbol = symbol
        self.color = color
        self.size = size
        self.name = name
        self.on_change = on_change
        Rating._id_counter += 1
        self.uid = id or f"rt_{Rating._id_counter}"

    def render(self):
        uid = self.uid
        extra = self._resolve_props()

        label_html = ""
        if self.label:
            label_html = (
                f'<div style="font-size:13px;font-weight:600;color:var(--text);'
                f'margin-bottom:6px">{self.label}</div>'
            )

        on_change_js = f"({self.on_change})(v);" if self.on_change else ""

        if self.readonly:
            # Modo solo lectura — renderiza estrellas en SVG/texto con clip
            stars = ""
            for i in range(1, self.max + 1):
                if self.value >= i:
                    fill = self.color
                elif self.half and self.value >= i - 0.5:
                    # media estrella via gradient
                    fill = f"url(#{uid}_hg{i})"
                else:
                    fill = "var(--border)"
                stars += (
                    f'<span style="font-size:{self.size}px;color:{fill};'
                    f'line-height:1;transition:color .1s">{self.symbol}</span>'
                )
            half_defs = ""
            if self.half:
                for i in range(1, self.max + 1):
                    if self.half and self.value >= i - 0.5 and self.value < i:
                        half_defs += (
                            f'<svg width="0" height="0"><defs>'
                            f'<linearGradient id="{uid}_hg{i}">'
                            f'<stop offset="50%" stop-color="{self.color}"/>'
                            f'<stop offset="50%" stop-color="var(--border)"/>'
                            f"</linearGradient></defs></svg>"
                        )

            wrapper_extra = f";{extra}" if extra else ""
            return (
                f'<div style="display:inline-flex;flex-direction:column{wrapper_extra}">'
                + label_html
                + half_defs
                + f'<div style="display:flex;gap:2px">{stars}</div>'
                + "</div>"
            )

        # Modo interactivo
        css = (
            f"<style>"
            f"#{uid}_stars span{{font-size:{self.size}px;cursor:pointer;line-height:1;"
            f"transition:transform .1s,color .1s;color:var(--border)}}"
            f"#{uid}_stars span:hover{{transform:scale(1.2)}}"
            f"</style>"
        )

        stars_html = "".join(
            f'<span data-v="{i}" onmouseover="{uid}_hover({i})" '
            f'onmouseout="{uid}_reset()" onclick="{uid}_set({i})">'
            f"{self.symbol}</span>"
            for i in range(1, self.max + 1)
        )

        js = f"""<script>(function(){{
  var uid='{uid}',cur={self.value},color='{self.color}';
  function paint(v){{
    var stars=document.querySelectorAll('#{uid}_stars span');
    stars.forEach(function(s){{
      s.style.color=parseFloat(s.dataset.v)<=v?color:'var(--border)';
    }});
  }}
  window[uid+'_hover']=function(v){{paint(v);}};
  window[uid+'_reset']=function(){{paint(cur);}};
  window[uid+'_set']=function(v){{
    cur=v;paint(v);
    var hi=document.getElementById(uid+'_hid');
    if(hi)hi.value=v;
    {on_change_js}
  }};
  paint(cur);
}})();</script>"""

        hidden = (
            f'<input type="hidden" id="{uid}_hid" name="{self.name}" value="{self.value}">'
            if self.name
            else ""
        )
        wrapper_extra = f";{extra}" if extra else ""

        return (
            css
            + f'<div style="display:inline-flex;flex-direction:column{wrapper_extra}">'
            + label_html
            + f'<div id="{uid}_stars" style="display:flex;gap:2px">{stars_html}</div>'
            + hidden
            + js
            + "</div>"
        )


# =============================================================================
# FileInput
# =============================================================================


class FileInput(Widget):
    """
    Input de archivo con zona de drag & drop estilizada.

        FileInput(name="avatar")
        FileInput(label="Subir imagen", accept="image/*", name="foto")
        FileInput(multiple=True, accept=".pdf,.docx", label="Documentos")
        FileInput(drag_drop=True, label="Arrastra o haz clic")

    Parámetros:
        label       str     etiqueta encima
        name        str     nombre para formularios
        accept      str     tipos aceptados (MIME o extensión, ej: "image/*", ".pdf")
        multiple    bool    permite seleccionar varios archivos
        drag_drop   bool    zona de drag & drop (default: True)
        id          str     id del elemento
        disabled    bool    deshabilita el control
        on_change   str     JS ejecutado al seleccionar (recibe FileList)
        max_size_mb float   tamaño máximo en MB (solo validación visual)
    """

    _id_counter = 0

    def __init__(
        self,
        label=None,
        name=None,
        accept="*",
        multiple=False,
        drag_drop=True,
        id=None,
        disabled=False,
        on_change=None,
        max_size_mb=None,
        **kwargs,
    ):
        self._props = Widget._extract_props(kwargs)
        self.label = label
        self.name = name
        self.accept = accept
        self.multiple = multiple
        self.drag_drop = drag_drop
        self.disabled = disabled
        self.on_change = on_change
        self.max_size_mb = max_size_mb
        FileInput._id_counter += 1
        self.uid = id or f"fi_{FileInput._id_counter}"

    def render(self):
        uid = self.uid
        extra = self._resolve_props()
        dis = " disabled" if self.disabled else ""
        mult = " multiple" if self.multiple else ""
        on_change_js = f"({self.on_change})(files);" if self.on_change else ""
        max_bytes = int(self.max_size_mb * 1024 * 1024) if self.max_size_mb else "null"

        label_html = ""
        if self.label:
            label_html = (
                f'<div style="font-size:13px;font-weight:600;color:var(--text);'
                f'margin-bottom:6px">{self.label}</div>'
            )

        icon = (
            '<svg width="32" height="32" viewBox="0 0 24 24" fill="none" '
            'stroke="currentColor" stroke-width="1.5" stroke-linecap="round" '
            'stroke-linejoin="round" style="color:var(--text-muted)">'
            '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>'
            '<polyline points="17 8 12 3 7 8"/>'
            '<line x1="12" y1="3" x2="12" y2="15"/>'
            "</svg>"
        )

        drop_hint = "Arrastra archivos aquí o " if self.drag_drop else ""
        mult_hint = "varios archivos" if self.multiple else "un archivo"

        zone_style = (
            "display:flex;flex-direction:column;align-items:center;justify-content:center;"
            "gap:10px;padding:32px 24px;"
            "border:2px dashed var(--border-input,var(--border));"
            "border-radius:12px;"
            "background:var(--input-bg,var(--surface));"
            "cursor:pointer;transition:border-color .2s,background .2s;"
            "text-align:center"
        )

        js = f"""<script>(function(){{
  var uid='{uid}';
  var zone=document.getElementById(uid+'_zone');
  var inp=document.getElementById(uid+'_inp');
  var info=document.getElementById(uid+'_info');
  var maxB={max_bytes};

  function showFiles(files){{
    if(!info)return;
    var names=Array.from(files).map(function(f){{
      var ok=maxB===null||f.size<=maxB;
      return '<span style="color:'+(ok?'var(--accent)':'var(--danger,#ef4444)')+'">'+f.name+'</span>';
    }});
    info.innerHTML=names.join(', ');
    {on_change_js}
  }}

  if(inp){{
    inp.addEventListener('change',function(){{
      if(this.files.length)showFiles(this.files);
    }});
  }}

  if(zone){{
    zone.addEventListener('click',function(){{if(inp)inp.click();}});
    zone.addEventListener('dragover',function(e){{
      e.preventDefault();
      zone.style.borderColor='var(--accent)';
      zone.style.background='color-mix(in srgb,var(--accent) 6%,var(--surface))';
    }});
    zone.addEventListener('dragleave',function(){{
      zone.style.borderColor='';zone.style.background='';
    }});
    zone.addEventListener('drop',function(e){{
      e.preventDefault();
      zone.style.borderColor='';zone.style.background='';
      var files=e.dataTransfer.files;
      if(inp)inp.files=files;
      if(files.length)showFiles(files);
    }});
  }}
}})();</script>"""

        wrapper_extra = f";{extra}" if extra else ""

        return (
            f'<div style="display:flex;flex-direction:column{wrapper_extra}">'
            + label_html
            + f'<div id="{uid}_zone" style="{zone_style}">'
            + icon
            + f'<div style="font-size:14px;color:var(--text-muted)">'
            + drop_hint
            + f'<span style="color:var(--accent);font-weight:600;text-decoration:underline">'
            + f"elige {mult_hint}</span>"
            + (
                f'<div style="font-size:11px;margin-top:2px">'
                f"Máx. {self.max_size_mb} MB</div>"
                if self.max_size_mb
                else ""
            )
            + "</div>"
            + f'<div id="{uid}_info" style="font-size:12px;margin-top:4px"></div>'
            + "</div>"
            + f'<input type="file" id="{uid}_inp" name="{self.name or uid}" '
            + f'accept="{self.accept}"{mult}{dis} style="display:none">'
            + js
            + "</div>"
        )


# =============================================================================
# FormGroup
# =============================================================================


class FormGroup(Widget):
    """
    Agrupa inputs bajo un título con borde (equivale a <fieldset>/<legend>).

        FormGroup(
            title="Datos personales",
            children=[
                TextField(placeholder="Nombre"),
                TextField(placeholder="Email", type="email"),
            ],
        )

        FormGroup(
            title="Preferencias",
            description="Personaliza tu experiencia.",
            collapsible=True,
            children=[...],
        )

    Parámetros:
        title           str     título del grupo
        description     str     texto de ayuda debajo del título
        children        list    lista de widgets
        child           Widget  hijo único
        collapsible     bool    permite colapsar el grupo (default: False)
        collapsed       bool    estado inicial colapsado (default: False)
        id              str     id del elemento
        gap             int     espacio entre hijos (default: 16)
    """

    _id_counter = 0

    def __init__(
        self,
        title=None,
        description=None,
        children=None,
        child=None,
        collapsible=False,
        collapsed=False,
        id=None,
        gap=16,
        **kwargs,
    ):
        self._props = Widget._extract_props(kwargs)
        self.title = title
        self.description = description
        self.collapsible = collapsible
        self.collapsed = collapsed
        self.gap = gap
        if child is not None and children is None:
            children = [child]
        self.children = children or []
        FormGroup._id_counter += 1
        self.uid = id or f"fg_{FormGroup._id_counter}"

    def render(self):
        uid = self.uid
        extra = self._resolve_props()
        inner = self._render_children(self.children)

        legend_html = ""
        if self.title:
            toggle_btn = ""
            if self.collapsible:
                arrow = "▸" if self.collapsed else "▾"
                toggle_btn = (
                    f'<button type="button" id="{uid}_btn" onclick="{uid}_toggle()" '
                    f'style="background:none;border:none;cursor:pointer;font-size:14px;'
                    f'color:var(--text-muted);padding:0;margin-left:8px;line-height:1">'
                    f"{arrow}</button>"
                )
            legend_html = (
                f'<legend style="padding:0 10px;font-size:13px;font-weight:700;'
                f'color:var(--text);display:flex;align-items:center;gap:4px">'
                f"{self.title}{toggle_btn}</legend>"
            )

        desc_html = ""
        if self.description:
            desc_html = (
                f'<p style="font-size:13px;color:var(--text-muted);'
                f'margin-bottom:16px;line-height:1.5">{self.description}</p>'
            )

        body_style = (
            f"display:{'none' if self.collapsed else 'flex'};"
            f"flex-direction:column;gap:{self.gap}px"
        )

        js = ""
        if self.collapsible:
            js = (
                f"<script>(function(){{"
                f"window.{uid}_toggle=function(){{"
                f"var b=document.getElementById('{uid}_body');"
                f"var btn=document.getElementById('{uid}_btn');"
                f"var open=b.style.display==='none';"
                f"b.style.display=open?'flex':'none';"
                f"if(btn)btn.textContent=open?'\u25be':'\u25b8';"
                f"}};}})();</script>"
            )

        fs_style = (
            "border:1px solid var(--border);border-radius:12px;padding:20px;"
            "background:var(--surface)" + (f";{extra}" if extra else "")
        )

        return (
            f'<fieldset id="{uid}" style="{fs_style}">'
            + legend_html
            + f'<div id="{uid}_body" style="{body_style}">'
            + desc_html
            + inner
            + "</div>"
            + js
            + "</fieldset>"
        )


# =============================================================================
# ColorPicker
# =============================================================================


class ColorPicker(Widget):
    """
    Selector de color con swatch visual, input hex editable y presets.

        ColorPicker(value="#6366f1")

        ColorPicker(
            label="Color de marca",
            value="#6366f1",
            presets=["#6366f1","#f59e0b","#ef4444","#22c55e","#0ea5e9"],
        )

    Parámetros:
        label       str     etiqueta encima del picker
        value       str     color inicial en hex (default: "#6366f1")
        presets     list    lista de colores hex para selección rápida
        show_hex    bool    muestra campo de texto hex editable (default: True)
        name        str     nombre del input para formularios
        id          str     id del elemento
        disabled    bool    deshabilita el control
    """

    _id_counter = 0

    def __init__(
        self,
        label=None,
        value="#6366f1",
        presets=None,
        show_hex=True,
        name=None,
        id=None,
        disabled=False,
        **kwargs,
    ):
        self._props = Widget._extract_props(kwargs)
        self.label = label
        self.value = value
        self.presets = presets or []
        self.show_hex = show_hex
        self.name = name
        self.disabled = disabled
        ColorPicker._id_counter += 1
        self.uid = id or f"cp_{ColorPicker._id_counter}"

    def render(self):
        uid = self.uid
        val = self.value
        dis = " disabled" if self.disabled else ""
        extra = self._resolve_props()
        w_extra = f";{extra}" if extra else ""

        label_html = ""
        if self.label:
            label_html = (
                f'<div style="font-size:13px;font-weight:600;color:var(--text);'
                f'margin-bottom:8px">{self.label}</div>'
            )

        hex_input = ""
        if self.show_hex:
            hex_input = (
                f'<input type="text" id="{uid}_hex" value="{val}" maxlength="7"'
                f' placeholder="#000000"{dis}'
                f' style="width:90px;padding:7px 10px;border:1px solid var(--border-input,var(--border));'
                f"border-radius:6px;font-size:13px;font-family:monospace;outline:none;"
                f'background:var(--input-bg,var(--surface));color:var(--text);transition:border-color .2s"'
                f' oninput="{uid}_hexInput(this.value)"'
                f' onblur="{uid}_hexBlur(this)">'
            )

        hidden = (
            f'<input type="hidden" id="{uid}_val" name="{self.name}" value="{val}">'
            if self.name
            else ""
        )

        presets_html = ""
        if self.presets:
            dots = "".join(
                f"<div onclick=\"{uid}_update('{c}')\" "
                f'title="{c}" '
                f'style="width:26px;height:26px;border-radius:6px;background:{c};'
                f"cursor:pointer;border:2px solid transparent;"
                f"transition:transform .15s,border-color .15s;"
                f'box-shadow:0 1px 4px rgba(0,0,0,.2)"'
                f" onmouseover=\"this.style.transform='scale(1.2)'\""
                f" onmouseout=\"this.style.transform='scale(1)'\"></div>"
                for c in self.presets
            )
            presets_html = (
                f'<div style="display:flex;gap:6px;flex-wrap:wrap;margin-top:10px">'
                f"{dots}</div>"
            )

        js = (
            f"<script>(function(){{"
            f"window.{uid}_update=function(hex){{"
            f"var sw=document.getElementById('{uid}_swatch');"
            f"var ni=document.getElementById('{uid}_native');"
            f"var hx=document.getElementById('{uid}_hex');"
            f"var hv=document.getElementById('{uid}_val');"
            f"if(sw)sw.style.background=hex;"
            f"if(ni)ni.value=hex;"
            f"if(hx)hx.value=hex;"
            f"if(hv)hv.value=hex;"
            f"}};"
            f"window.{uid}_hexInput=function(v){{"
            f"if(/^#[0-9a-fA-F]{{6}}$/.test(v)){{{uid}_update(v);}}"
            f"}};"
            f"window.{uid}_hexBlur=function(el){{"
            f"if(!/^#[0-9a-fA-F]{{6}}$/.test(el.value)){{"
            f"var cur=document.getElementById('{uid}_native').value;"
            f"el.value=cur;}}"
            f"}};"
            f"}})();</script>"
        )

        return (
            f'<div id="{uid}_wrap" style="display:inline-flex;flex-direction:column{w_extra}">'
            + label_html
            + f'<div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap">'
            + f'<label for="{uid}_native" style="cursor:pointer;display:flex;align-items:center;gap:8px">'
            + f'<div id="{uid}_swatch" style="width:38px;height:38px;border-radius:8px;'
            + f"background:{val};border:2px solid var(--border);"
            + f'box-shadow:0 2px 8px rgba(0,0,0,.15);flex-shrink:0;transition:background .1s"></div>'
            + f'<input type="color" id="{uid}_native" value="{val}"{dis} '
            + f'style="position:absolute;opacity:0;width:38px;height:38px;cursor:pointer;border:none;padding:0"'
            + f' oninput="{uid}_update(this.value)">'
            + hex_input
            + hidden
            + f"</label>"
            + f"</div>"
            + presets_html
            + js
            + "</div>"
        )


# =============================================================================
# DatePicker
# =============================================================================


class DatePicker(Widget):
    """
    Selector de fecha simple o rango al estilo reservas de hotel/vuelo.

        DatePicker(label="Fecha de nacimiento", value="2000-01-15")

        DatePicker(
            label="Estancia",
            range=True,
            value="2026-06-10",
            value_end="2026-06-17",
            label_start="Check-in",
            label_end="Check-out",
        )

    Parámetros:
        label           str     etiqueta general
        value           str     fecha inicial (ISO: YYYY-MM-DD)
        value_end       str     fecha final en modo rango
        range           bool    habilita selección de rango (default: False)
        label_start     str     etiqueta del campo inicio
        label_end       str     etiqueta del campo fin
        placeholder     str     texto de ayuda campo simple
        placeholder_start str   texto de ayuda campo inicio
        placeholder_end str     texto de ayuda campo fin
        min_date        str     fecha mínima seleccionable (ISO)
        max_date        str     fecha máxima seleccionable (ISO)
        locale          str     "es" | "en" (default: "es")
        name            str     nombre del input (simple)
        name_start      str     nombre del campo inicio
        name_end        str     nombre del campo fin
        id              str     id base del elemento
        disabled        bool    deshabilita el control
        format          str     "DD/MM/YYYY" | "MM/DD/YYYY" | "YYYY-MM-DD"
    """

    _id_counter = 0

    _MONTHS = {
        "es": [
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
        ],
        "en": [
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
        ],
    }
    _DAYS = {
        "es": ["Lu", "Ma", "Mi", "Ju", "Vi", "S\u00e1", "Do"],
        "en": ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"],
    }

    def __init__(
        self,
        label=None,
        value=None,
        value_end=None,
        range=False,
        label_start="Inicio",
        label_end="Fin",
        placeholder="Seleccionar fecha",
        placeholder_start="Fecha inicio",
        placeholder_end="Fecha fin",
        min_date=None,
        max_date=None,
        locale="es",
        name=None,
        name_start=None,
        name_end=None,
        id=None,
        disabled=False,
        format="DD/MM/YYYY",
        **kwargs,
    ):
        self._props = Widget._extract_props(kwargs)
        self.label = label
        self.value = value or ""
        self.value_end = value_end or ""
        self.is_range = range
        self.label_start = label_start
        self.label_end = label_end
        self.placeholder = placeholder
        self.placeholder_start = placeholder_start
        self.placeholder_end = placeholder_end
        self.min_date = min_date or ""
        self.max_date = max_date or ""
        self.locale = locale if locale in self._MONTHS else "es"
        self.name = name
        self.name_start = name_start or (f"{name}_start" if name else "")
        self.name_end = name_end or (f"{name}_end" if name else "")
        self.disabled = disabled
        self.fmt = format
        DatePicker._id_counter += 1
        self.uid = id or f"dp_{DatePicker._id_counter}"

    def _display(self, iso):
        if not iso or len(iso) < 10:
            return ""
        y, m, d = iso[:4], iso[5:7], iso[8:10]
        return self.fmt.replace("YYYY", y).replace("MM", m).replace("DD", d)

    def render(self):
        uid = self.uid
        extra = self._resolve_props()
        w_extra = f";{extra}" if extra else ""

        months_js = _json.dumps(self._MONTHS[self.locale])
        days_js = _json.dumps(self._DAYS[self.locale])
        min_js = _json.dumps(self.min_date)
        max_js = _json.dumps(self.max_date)
        fmt_js = _json.dumps(self.fmt)
        is_range_js = "true" if self.is_range else "false"

        ph_start = _json.dumps(self.placeholder_start)
        ph_end = _json.dumps(self.placeholder_end)
        ph_simple = _json.dumps(self.placeholder)

        disp1 = self._display(self.value)
        disp2 = self._display(self.value_end)

        css = (
            f"<style>"
            f"#{uid}_cal{{position:absolute;z-index:10050;"
            f"background:var(--dropdown-bg,var(--surface));"
            f"border:1px solid var(--border-input,var(--border));"
            f"border-radius:14px;box-shadow:0 16px 48px rgba(0,0,0,.25);"
            f"padding:16px;min-width:300px;user-select:none;display:none}}"
            f"#{uid}_cal .dp-day{{width:36px;height:36px;display:flex;"
            f"align-items:center;justify-content:center;border-radius:8px;"
            f"cursor:pointer;font-size:13px;transition:background .12s,color .12s}}"
            f"#{uid}_cal .dp-day:hover:not(.dp-disabled){{background:var(--accent);color:#fff}}"
            f"#{uid}_cal .dp-sel{{background:var(--accent);color:#fff;font-weight:700}}"
            f"#{uid}_cal .dp-in{{background:color-mix(in srgb,var(--accent) 18%,transparent);border-radius:0}}"
            f"#{uid}_cal .dp-rs{{border-radius:8px 0 0 8px}}"
            f"#{uid}_cal .dp-re{{border-radius:0 8px 8px 0}}"
            f"#{uid}_cal .dp-disabled{{opacity:.35;cursor:not-allowed;pointer-events:none}}"
            f"#{uid}_cal .dp-today{{box-shadow:inset 0 0 0 2px var(--accent)}}"
            f"#{uid}_cal .dp-om{{opacity:.35}}"
            f"</style>"
        )

        label_html = ""
        if self.label:
            label_html = (
                f'<div style="font-size:13px;font-weight:600;color:var(--text);'
                f'margin-bottom:8px">{self.label}</div>'
            )

        cal_icon = (
            '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" '
            'stroke="currentColor" stroke-width="2" stroke-linecap="round" '
            'stroke-linejoin="round" style="flex-shrink:0;opacity:.5">'
            '<rect x="3" y="4" width="18" height="18" rx="2"/>'
            '<line x1="16" y1="2" x2="16" y2="6"/>'
            '<line x1="8" y1="2" x2="8" y2="6"/>'
            '<line x1="3" y1="10" x2="21" y2="10"/>'
            "</svg>"
        )
        arrow_icon = (
            '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" '
            'stroke="currentColor" stroke-width="2" stroke-linecap="round" '
            'style="opacity:.4;flex-shrink:0">'
            '<path d="M5 12h14M12 5l7 7-7 7"/></svg>'
        )

        if not self.is_range:
            trigger_html = (
                f'<div id="{uid}_trigger" onclick="{uid}_open()"'
                f' style="display:flex;align-items:center;gap:8px;padding:9px 12px;'
                f"border:1px solid var(--border-input,var(--border));border-radius:8px;"
                f"background:var(--input-bg,var(--surface));cursor:pointer;"
                f'transition:border-color .2s;color:var(--text);font-size:14px">'
                f"{cal_icon}"
                f'<span id="{uid}_disp" style="flex:1;color:{"var(--text)" if disp1 else "var(--text-muted)"}">'
                f"{disp1 or self.placeholder}</span>"
                f"</div>"
                + (
                    f'<input type="hidden" id="{uid}_val" name="{self.name}" value="{self.value}">'
                    if self.name
                    else f'<input type="hidden" id="{uid}_val" value="{self.value}">'
                )
            )
        else:
            trigger_html = (
                f'<div style="display:flex;align-items:stretch;'
                f"border:1px solid var(--border-input,var(--border));border-radius:10px;"
                f'overflow:hidden;background:var(--input-bg,var(--surface))">'
                f'<div id="{uid}_t1" onclick="{uid}_open(\'start\')"'
                f' style="display:flex;align-items:center;gap:8px;padding:10px 14px;'
                f'flex:1;cursor:pointer;transition:background .15s">'
                f'<div style="display:flex;flex-direction:column;gap:2px">'
                f'<span style="font-size:10px;font-weight:700;letter-spacing:.06em;'
                f'text-transform:uppercase;color:var(--text-muted)">{self.label_start}</span>'
                f'<span id="{uid}_d1" style="font-size:14px;'
                f'color:{"var(--text)" if disp1 else "var(--text-muted)"}">'
                f"{disp1 or self.placeholder_start}</span>"
                f"</div></div>"
                f'<div style="display:flex;align-items:center;padding:0 4px;color:var(--text-muted)">'
                f"{arrow_icon}</div>"
                f'<div id="{uid}_t2" onclick="{uid}_open(\'end\')"'
                f' style="display:flex;align-items:center;gap:8px;padding:10px 14px;'
                f'flex:1;cursor:pointer;border-left:1px solid var(--border);transition:background .15s">'
                f'<div style="display:flex;flex-direction:column;gap:2px">'
                f'<span style="font-size:10px;font-weight:700;letter-spacing:.06em;'
                f'text-transform:uppercase;color:var(--text-muted)">{self.label_end}</span>'
                f'<span id="{uid}_d2" style="font-size:14px;'
                f'color:{"var(--text)" if disp2 else "var(--text-muted)"}">'
                f"{disp2 or self.placeholder_end}</span>"
                f"</div></div>"
                f"</div>"
                + (
                    f'<input type="hidden" id="{uid}_v1" name="{self.name_start}" value="{self.value}">'
                    if self.name_start
                    else f'<input type="hidden" id="{uid}_v1" value="{self.value}">'
                )
                + (
                    f'<input type="hidden" id="{uid}_v2" name="{self.name_end}" value="{self.value_end}">'
                    if self.name_end
                    else f'<input type="hidden" id="{uid}_v2" value="{self.value_end}">'
                )
            )

        calendar_html = (
            f'<div id="{uid}_cal" role="dialog">'
            f'<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px">'
            f'<button type="button" onclick="{uid}_prev()" style="background:none;border:none;'
            f'cursor:pointer;padding:4px 8px;border-radius:6px;color:var(--text);font-size:18px">&lsaquo;</button>'
            f'<span id="{uid}_lbl" style="font-size:14px;font-weight:700;color:var(--text)"></span>'
            f'<button type="button" onclick="{uid}_next()" style="background:none;border:none;'
            f'cursor:pointer;padding:4px 8px;border-radius:6px;color:var(--text);font-size:18px">&rsaquo;</button>'
            f"</div>"
            f'<div id="{uid}_grid" style="display:grid;grid-template-columns:repeat(7,1fr);gap:2px"></div>'
            f'<div style="display:flex;justify-content:space-between;margin-top:12px;'
            f'border-top:1px solid var(--border);padding-top:10px">'
            f'<button type="button" onclick="{uid}_clear()" style="font-size:12px;'
            f'color:var(--text-muted);background:none;border:none;cursor:pointer">Limpiar</button>'
            f'<button type="button" onclick="{uid}_close()" style="font-size:13px;font-weight:600;'
            f'color:var(--accent);background:none;border:none;cursor:pointer">Aceptar</button>'
            f"</div></div>"
        )

        js = f"""<script>(function(){{
var U='{uid}',MONTHS={months_js},DAYS={days_js};
var isR={is_range_js},minD={min_js},maxD={max_js},fmt={fmt_js};
var s1='{self.value}',s2='{self.value_end}';
var cy=new Date().getFullYear(),cm=new Date().getMonth();
var af='start';

function toISO(y,m,d){{return y+'-'+(m<9?'0':'')+(m+1)+'-'+(d<10?'0':'')+d;}}
function fmtD(iso){{if(!iso)return '';var p=iso.split('-');
  return fmt.replace('DD',p[2]).replace('MM',p[1]).replace('YYYY',p[0]);}}

function render(){{
  var lbl=document.getElementById(U+'_lbl');
  if(lbl)lbl.textContent=MONTHS[cm]+' '+cy;
  var grid=document.getElementById(U+'_grid');
  if(!grid)return;
  var html='';
  DAYS.forEach(function(d){{html+='<div style="font-size:11px;font-weight:700;'
    +'color:var(--text-muted);text-align:center;padding:4px 0">'+d+'</div>';}});
  var first=(new Date(cy,cm,1).getDay()+6)%7;
  var days=new Date(cy,cm+1,0).getDate();
  var prev=new Date(cy,cm,0).getDate();
  var today=toISO(new Date().getFullYear(),new Date().getMonth(),new Date().getDate());
  for(var i=first-1;i>=0;i--)html+='<div class="dp-day dp-om">'+( prev-i)+'</div>';
  for(var d=1;d<=days;d++){{
    var iso=toISO(cy,cm,d);
    var cls='dp-day';
    if(minD&&iso<minD||maxD&&iso>maxD)cls+=' dp-disabled';
    if(iso===today)cls+=' dp-today';
    var lo=s1&&s2?(s1<s2?s1:s2):null;
    var hi=s1&&s2?(s1<s2?s2:s1):null;
    if(isR&&lo&&hi&&iso>lo&&iso<hi)cls+=' dp-in';
    if(isR&&lo&&iso===lo)cls+=' dp-sel dp-rs';
    else if(isR&&hi&&iso===hi)cls+=' dp-sel dp-re';
    else if(!isR&&iso===s1)cls+=' dp-sel';
    html+='<div class="'+cls+'" onclick="{uid}_pick(\\''+iso+'\\')">'+d+'</div>';
  }}
  var tot=first+days,rem=(7-tot%7)%7;
  for(var d=1;d<=rem;d++)html+='<div class="dp-day dp-om">'+d+'</div>';
  grid.innerHTML=html;
}}

function updDisp(){{
  if(isR){{
    var d1=document.getElementById(U+'_d1'),d2=document.getElementById(U+'_d2');
    var v1=document.getElementById(U+'_v1'),v2=document.getElementById(U+'_v2');
    if(d1){{d1.textContent=fmtD(s1)||{ph_start};d1.style.color=s1?'var(--text)':'var(--text-muted)';}}
    if(d2){{d2.textContent=fmtD(s2)||{ph_end};d2.style.color=s2?'var(--text)':'var(--text-muted)';}}
    if(v1)v1.value=s1;if(v2)v2.value=s2;
  }}else{{
    var d=document.getElementById(U+'_disp'),v=document.getElementById(U+'_val');
    if(d){{d.textContent=fmtD(s1)||{ph_simple};d.style.color=s1?'var(--text)':'var(--text-muted)';}}
    if(v)v.value=s1;
  }}
}}

window[U+'_open']=function(field){{
  af=field||'start';
  var cal=document.getElementById(U+'_cal');
  if(!cal)return;
  var wrap=document.getElementById(U+'_wrap');
  var trig=document.getElementById(U+(isR?(af==='start'?'_t1':'_t2'):'_trigger'));
  if(trig&&wrap){{
    var tr=trig.getBoundingClientRect(),wr=wrap.getBoundingClientRect();
    cal.style.top=(tr.bottom-wr.top+6)+'px';
    var l=tr.left-wr.left;
    if(l+310>wrap.offsetWidth)l=Math.max(0,wrap.offsetWidth-310);
    cal.style.left=l+'px';
  }}
  var ref=isR&&af==='end'&&s2?s2:s1;
  if(ref){{var p=ref.split('-');cy=+p[0];cm=+p[1]-1;}}
  render();cal.style.display='block';
}};

window[U+'_close']=function(){{var c=document.getElementById(U+'_cal');if(c)c.style.display='none';}};
window[U+'_clear']=function(){{s1='';s2='';updDisp();render();}};

window[U+'_pick']=function(iso){{
  if(isR){{
    if(af==='start'||(!s1&&!s2)){{s1=iso;s2='';af='end';render();}}
    else{{if(iso<s1){{s2=s1;s1=iso;}}else{{s2=iso;}}updDisp();render();{uid}_close();}}
  }}else{{s1=iso;updDisp();render();{uid}_close();}}
}};

window[U+'_prev']=function(){{cm--;if(cm<0){{cm=11;cy--;}}render();}};
window[U+'_next']=function(){{cm++;if(cm>11){{cm=0;cy++;}}render();}};

document.addEventListener('click',function(e){{
  var cal=document.getElementById(U+'_cal'),wrap=document.getElementById(U+'_wrap');
  if(cal&&wrap&&!wrap.contains(e.target))cal.style.display='none';
}});

updDisp();
}})();</script>""".replace(
            "{uid}", uid
        )

        return (
            css + f'<div id="{uid}_wrap" style="position:relative;display:inline-flex;'
            f'flex-direction:column;width:100%{w_extra}">'
            + label_html
            + trigger_html
            + calendar_html
            + js
            + "</div>"
        )
