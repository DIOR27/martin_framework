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
