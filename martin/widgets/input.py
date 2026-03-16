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
    Control deslizante (range input) con valor visible y tick marks opcionales.

    Uso básico:
        Slider(min=0, max=100, value=40)

    Con etiqueta y paso:
        Slider(label="Volumen", min=0, max=100, value=75, step=5)

    Doble rango (valor mínimo y máximo):
        Slider(label="Rango de precio", min=0, max=1000, value=200, value_max=800, range=True)

    Con ticks y formato:
        Slider(min=0, max=100, value=50, show_ticks=True,
               format="{v}%", suffix="%")

    Parámetros:
        label       str     etiqueta encima del slider
        min         int     valor mínimo (default: 0)
        max         int     valor máximo (default: 100)
        value       int     valor inicial (o valor inferior en range=True)
        value_max   int     valor superior en modo range
        step        int     incremento (default: 1)
        range       bool    modo doble cursor para seleccionar un rango
        show_value  bool    muestra el valor actual (default: True)
        show_ticks  bool    dibuja marcas en los extremos y valor
        format      str     formato del valor, usar {v} como placeholder. Ej: "{v}%"
        name        str     nombre del input para formularios
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
        self.uid = id or f"slider_{Slider._id_counter}"

    def _fmt(self, v):
        return self.format.replace("{v}", str(v))

    def render(self):
        uid = self.uid
        mn, mx, st = self.min, self.max, self.step
        v1 = self.value
        v2 = self.value_max
        color = self.color
        disabled_attr = " disabled" if self.disabled else ""
        extra = self._resolve_props()
        wrapper_extra = f";{extra}" if extra else ""

        # ── CSS compartido ────────────────────────────────────────────────
        css = (
            f"<style>"
            f"#{uid}_wrap input[type=range]{{-webkit-appearance:none;appearance:none;"
            f"height:6px;border-radius:3px;outline:none;cursor:pointer;"
            f"background:transparent;width:100%}}"
            f"#{uid}_wrap input[type=range]::-webkit-slider-thumb{{-webkit-appearance:none;"
            f"appearance:none;width:18px;height:18px;border-radius:50%;"
            f"background:{color};cursor:pointer;border:2px solid var(--surface);"
            f"box-shadow:0 1px 4px rgba(0,0,0,0.25);transition:transform .15s}}"
            f"#{uid}_wrap input[type=range]::-moz-range-thumb{{width:18px;height:18px;"
            f"border-radius:50%;background:{color};cursor:pointer;"
            f"border:2px solid var(--surface);box-shadow:0 1px 4px rgba(0,0,0,0.25)}}"
            f"#{uid}_wrap input[type=range]:hover::-webkit-slider-thumb{{transform:scale(1.15)}}"
            f"#{uid}_wrap input[type=range]:disabled{{opacity:0.45;cursor:not-allowed}}"
            f"</style>"
        )

        label_html = ""
        if self.label:
            label_html = (
                f'<div style="display:flex;justify-content:space-between;'
                f'align-items:center;margin-bottom:8px">'
                f'<span style="font-size:13px;font-weight:600;color:var(--text)">{self.label}</span>'
                + (
                    f'<span id="{uid}_disp" style="font-size:13px;font-weight:600;'
                    f'color:{color}">{self._fmt(v1)}'
                    + (f" — {self._fmt(v2)}" if self.is_range else "")
                    + "</span>"
                    if self.show_value
                    else ""
                )
                + "</div>"
            )
        elif self.show_value:
            label_html = (
                f'<div style="text-align:right;margin-bottom:6px">'
                f'<span id="{uid}_disp" style="font-size:13px;font-weight:600;color:{color}">'
                f"{self._fmt(v1)}"
                + (f" — {self._fmt(v2)}" if self.is_range else "")
                + "</span></div>"
            )

        ticks_html = ""
        if self.show_ticks:
            ticks_html = (
                f'<div style="display:flex;justify-content:space-between;'
                f'margin-top:4px;font-size:11px;color:var(--text-muted)">'
                f"<span>{self._fmt(mn)}</span><span>{self._fmt(mx)}</span></div>"
            )

        if not self.is_range:
            # ── Slider simple ─────────────────────────────────────────────
            pct = (v1 - mn) / (mx - mn) * 100 if mx != mn else 0
            track_style = (
                f"background:linear-gradient(to right,{color} {pct:.1f}%,"
                f"var(--border) {pct:.1f}%)"
            )
            name_attr = f' name="{self.name}"' if self.name else ""
            _grad = f"linear-gradient(to right,{color} '+p+'%,var(--border) '+p+'%)"
            _disp_js = (
                f"var d=document.getElementById('{uid}_disp');"
                f"if(d)d.textContent='{self.format}'.replace('{{v}}',el.value);"
                if self.show_value
                else ""
            )
            _oninput = (
                f"(function(el){{"
                f"var p=(el.value-{mn})/({mx}-{mn})*100;"
                f"el.style.background='{_grad}';" + _disp_js + f"}})(this)"
            )
            range_html = (
                f'<input type="range" id="{uid}" min="{mn}" max="{mx}" step="{st}" '
                f'value="{v1}"{name_attr}{disabled_attr} '
                f'style="{track_style}" '
                f'oninput="{_oninput}">'
            )
            hidden = (
                f'<input type="hidden" name="{self.name}_val" id="{uid}_val" value="{v1}">'
                if self.name
                else ""
            )
            body = label_html + range_html + ticks_html + hidden

        else:
            # ── Slider de rango doble ─────────────────────────────────────
            # Se superponen dos inputs con position:absolute + JS que sincroniza
            p1 = (v1 - mn) / (mx - mn) * 100 if mx != mn else 0
            p2 = (v2 - mn) / (mx - mn) * 100 if mx != mn else 100
            name1 = f' name="{self.name}_min"' if self.name else ""
            name2 = f' name="{self.name}_max"' if self.name else ""
            range_html = (
                f'<div style="position:relative;height:24px;margin:4px 0">'
                f'<div id="{uid}_track" style="position:absolute;top:50%;left:0;right:0;'
                f'height:6px;border-radius:3px;transform:translateY(-50%);">'
                f'<div style="position:absolute;left:0;right:0;height:100%;'
                f'background:var(--border);border-radius:3px"></div>'
                f'<div id="{uid}_fill" style="position:absolute;'
                f"left:{p1:.1f}%;right:{100-p2:.1f}%;height:100%;"
                f'background:{color};border-radius:3px"></div>'
                f"</div>"
                f'<input type="range" id="{uid}_min" min="{mn}" max="{mx}" step="{st}" '
                f'value="{v1}"{name1}{disabled_attr} '
                f'style="position:absolute;width:100%;pointer-events:none;'
                f'background:transparent;top:50%;transform:translateY(-50%)" '
                f'oninput="{uid}_sync()">'
                f'<input type="range" id="{uid}_max" min="{mn}" max="{mx}" step="{st}" '
                f'value="{v2}"{name2}{disabled_attr} '
                f'style="position:absolute;width:100%;pointer-events:none;'
                f'background:transparent;top:50%;transform:translateY(-50%)" '
                f'oninput="{uid}_sync()">'
                f"</div>"
            )
            js = (
                f"<script>(function(){{"
                f"window.{uid}_sync=function(){{"
                f"var a=document.getElementById('{uid}_min');"
                f"var b=document.getElementById('{uid}_max');"
                f"var f=document.getElementById('{uid}_fill');"
                f"var d=document.getElementById('{uid}_disp');"
                f"var mn={mn},mx={mx};"
                f"var v1=parseFloat(a.value),v2=parseFloat(b.value);"
                # mantener v1 <= v2
                f"if(v1>v2){{if(this===a)a.value=v2;else b.value=v1;v1=parseFloat(a.value);v2=parseFloat(b.value);}}"
                f"var p1=(v1-mn)/(mx-mn)*100,p2=(v2-mn)/(mx-mn)*100;"
                # habilitar pointer-events solo en el thumb relevante (truco CSS)
                f"a.style.zIndex=v1>mx-10?'5':'3';"
                f"if(f){{f.style.left=p1+'%';f.style.right=(100-p2)+'%';}}"
                f"if(d){{var fmt='{self.format}';"
                f"d.textContent=fmt.replace('{{v}}',v1)+' \u2014 '+fmt.replace('{{v}}',v2);}}"
                f"}};"
                # habilitar pointer events solo en el thumb
                f"var ra=document.getElementById('{uid}_min');"
                f"var rb=document.getElementById('{uid}_max');"
                f"[ra,rb].forEach(function(el){{"
                f"el.style.pointerEvents='none';"
                f"el.addEventListener('mousedown',function(){{el.style.pointerEvents='all';}});"
                f"el.addEventListener('touchstart',function(){{el.style.pointerEvents='all';}});"
                f"el.addEventListener('mouseup',function(){{el.style.pointerEvents='none';{uid}_sync();}});"
                f"el.addEventListener('touchend',function(){{el.style.pointerEvents='none';{uid}_sync();}});"
                f"}});"
                # thumb siempre visible
                f"ra.style.pointerEvents='all';"
                f"rb.style.pointerEvents='all';"
                f"{uid}_sync();"
                f"}})();</script>"
            )
            body = label_html + range_html + ticks_html + js

        return (
            css
            + f'<div id="{uid}_wrap" style="width:100%;user-select:none{wrapper_extra}">'
            + body
            + "</div>"
        )


# =============================================================================
# ColorPicker
# =============================================================================


class ColorPicker(Widget):
    """
    Selector de color con swatch visual y input hex editable.

    Uso básico:
        ColorPicker(value="#6366f1")

    Con etiqueta y colores predefinidos:
        ColorPicker(
            label="Color de marca",
            value="#6366f1",
            presets=["#6366f1","#f59e0b","#ef4444","#22c55e","#0ea5e9"],
        )

    Solo swatch sin hex:
        ColorPicker(value="#ff0000", show_hex=False)

    Parámetros:
        label       str     etiqueta encima del picker
        value       str     color inicial en hex (default: "#6366f1")
        presets     list    lista de colores hex para selección rápida
        show_hex    bool    muestra campo de texto hex editable (default: True)
        show_alpha  bool    muestra slider de opacidad (experimental)
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
        disabled_attr = " disabled" if self.disabled else ""
        extra = self._resolve_props()
        wrapper_extra = f";{extra}" if extra else ""

        label_html = ""
        if self.label:
            label_html = (
                f'<div style="font-size:13px;font-weight:600;color:var(--text);margin-bottom:8px">'
                f"{self.label}</div>"
            )

        # Swatch + native color input (oculto, abre el picker del SO)
        swatch = (
            f'<div style="position:relative;display:inline-flex;align-items:center;'
            f'gap:10px;flex-wrap:wrap">'
            f'<label for="{uid}_native" style="cursor:pointer;display:flex;align-items:center;gap:8px">'
            f'<div id="{uid}_swatch" style="width:36px;height:36px;border-radius:8px;'
            f"background:{val};border:2px solid var(--border);"
            f'box-shadow:0 2px 8px rgba(0,0,0,0.15);transition:background .1s;flex-shrink:0"></div>'
            f'<input type="color" id="{uid}_native" value="{val}"{disabled_attr} '
            f'style="position:absolute;opacity:0;width:36px;height:36px;cursor:pointer;border:none;padding:0"'
            f' oninput="{uid}_update(this.value)">'
            + (
                f'<input type="text" id="{uid}_hex" value="{val}" maxlength="7"'
                f' placeholder="#000000"{disabled_attr}'
                f' style="width:90px;padding:7px 10px;border:1px solid var(--border-input,var(--border));'
                f"border-radius:6px;font-size:13px;font-family:monospace;outline:none;"
                f'background:var(--input-bg,var(--surface));color:var(--text);transition:border-color .2s"'
                f' oninput="{uid}_hexInput(this.value)"'
                f' onblur="{uid}_hexBlur(this)">'
                if self.show_hex
                else ""
            )
            + (
                f'<input type="hidden" id="{uid}_val" name="{self.name}" value="{val}">'
                if self.name
                else ""
            )
            + "</label></div>"
        )

        # Presets
        presets_html = ""
        if self.presets:
            dots = "".join(
                f"<div onclick=\"{uid}_update('{c}')\" "
                f'style="width:24px;height:24px;border-radius:6px;background:{c};'
                f"cursor:pointer;border:2px solid transparent;transition:transform .15s,border-color .15s;"
                f'box-shadow:0 1px 4px rgba(0,0,0,.2)"'
                f" onmouseover=\"this.style.transform='scale(1.2)'\""
                f" onmouseout=\"this.style.transform='scale(1)'\"></div>"
                for c in self.presets
            )
            presets_html = f'<div style="display:flex;gap:6px;flex-wrap:wrap;margin-top:10px">{dots}</div>'

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
            f'<div id="{uid}_wrap" style="display:inline-flex;flex-direction:column{wrapper_extra}">'
            + label_html
            + swatch
            + presets_html
            + js
            + "</div>"
        )


# =============================================================================
# DatePicker
# =============================================================================


class DatePicker(Widget):
    """
    Selector de fecha o rango de fechas con calendario desplegable,
    al estilo de las páginas de reservas de hoteles o vuelos.

    Fecha simple:
        DatePicker(label="Fecha de nacimiento", value="2000-01-15")

    Rango de fechas (check-in / check-out):
        DatePicker(
            label="Fechas de estancia",
            range=True,
            value="2026-06-01",
            value_end="2026-06-07",
            label_start="Check-in",
            label_end="Check-out",
        )

    Con fecha mínima y máxima:
        DatePicker(range=True, min_date="2026-01-01", max_date="2027-12-31")

    Parámetros:
        label           str     etiqueta general encima del picker
        value           str     fecha inicial seleccionada (ISO: YYYY-MM-DD)
        value_end       str     fecha final en modo rango
        range           bool    habilita selección de rango (default: False)
        label_start     str     etiqueta del campo de inicio (default: "Inicio")
        label_end       str     etiqueta del campo de fin (default: "Fin")
        placeholder     str     texto de ayuda en campo simple
        placeholder_start str   texto de ayuda en campo inicio
        placeholder_end str     texto de ayuda en campo fin
        min_date        str     fecha mínima seleccionable (ISO)
        max_date        str     fecha máxima seleccionable (ISO)
        locale          str     código de idioma para nombres de meses/días (default: "es")
        name            str     nombre del input para formularios (simple)
        name_start      str     nombre del campo inicio en formularios
        name_end        str     nombre del campo fin en formularios
        id              str     id base del elemento
        disabled        bool    deshabilita el control
        format          str     formato de visualización: "DD/MM/YYYY" | "MM/DD/YYYY" | "YYYY-MM-DD"
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
        "es": ["Lu", "Ma", "Mi", "Ju", "Vi", "Sá", "Do"],
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
        """Convierte YYYY-MM-DD al formato de display."""
        if not iso or len(iso) < 10:
            return ""
        y, m, d = iso[:4], iso[5:7], iso[8:10]
        f = self.fmt
        return f.replace("YYYY", y).replace("MM", m).replace("DD", d)

    def render(self):
        uid = self.uid
        extra = self._resolve_props()
        wrapper_extra = f";{extra}" if extra else ""
        disabled_attr = " disabled" if self.disabled else ""

        months_js = _json.dumps(self._MONTHS[self.locale])
        days_js = _json.dumps(self._DAYS[self.locale])
        min_js = _json.dumps(self.min_date)
        max_js = _json.dumps(self.max_date)
        fmt_js = _json.dumps(self.fmt)
        is_range_js = "true" if self.is_range else "false"
        val1_js = _json.dumps(self.value)
        val2_js = _json.dumps(self.value_end)

        # ── CSS ────────────────────────────────────────────────────────────
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
            f"#{uid}_cal .dp-day:hover:not(.dp-disabled){{background:var(--accent);"
            f"color:#fff}}"
            f"#{uid}_cal .dp-selected{{background:var(--accent);color:#fff;font-weight:700}}"
            f"#{uid}_cal .dp-in-range{{background:color-mix(in srgb,var(--accent) 18%,transparent);"
            f"border-radius:0}}"
            f"#{uid}_cal .dp-range-end{{border-radius:0 8px 8px 0}}"
            f"#{uid}_cal .dp-range-start{{border-radius:8px 0 0 8px}}"
            f"#{uid}_cal .dp-disabled{{opacity:.35;cursor:not-allowed;pointer-events:none}}"
            f"#{uid}_cal .dp-today{{box-shadow:inset 0 0 0 2px var(--accent)}}"
            f"#{uid}_cal .dp-other-month{{opacity:.4}}"
            f"</style>"
        )

        # ── Label principal ────────────────────────────────────────────────
        label_html = ""
        if self.label:
            label_html = (
                f'<div style="font-size:13px;font-weight:600;color:var(--text);'
                f'margin-bottom:8px">{self.label}</div>'
            )

        # ── Campos de entrada ──────────────────────────────────────────────
        field_style = (
            "display:flex;align-items:center;gap:8px;"
            "padding:9px 12px;border:1px solid var(--border-input,var(--border));"
            "border-radius:8px;background:var(--input-bg,var(--surface));"
            "cursor:pointer;transition:border-color .2s;min-width:140px;"
            "color:var(--text);font-size:14px"
        )
        cal_icon = (
            '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" '
            'stroke="currentColor" stroke-width="2" stroke-linecap="round" '
            'stroke-linejoin="round" style="flex-shrink:0;opacity:.5">'
            '<rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>'
            '<line x1="16" y1="2" x2="16" y2="6"/>'
            '<line x1="8" y1="2" x2="8" y2="6"/>'
            '<line x1="3" y1="10" x2="21" y2="10"/>'
            "</svg>"
        )
        arrow_icon = (
            '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" '
            'stroke="currentColor" stroke-width="2" stroke-linecap="round" '
            'style="opacity:.4;flex-shrink:0">'
            '<path d="M5 12h14M12 5l7 7-7 7"/></svg>'
        )

        disp1 = self._display(self.value)
        disp2 = self._display(self.value_end)

        if not self.is_range:
            ph = self.placeholder if not disp1 else ""
            trigger_html = (
                f'<div id="{uid}_trigger" onclick="{uid}_open(\'start\')" '
                f'style="{field_style}"{disabled_attr}>'
                f"{cal_icon}"
                f'<span id="{uid}_disp" style="flex:1;color:{"var(--text)" if disp1 else "var(--text-muted)"}">'
                f"{disp1 or self.placeholder}</span>"
                f"</div>"
                f'<input type="hidden" id="{uid}_val" '
                + (f'name="{self.name}" ' if self.name else "")
                + f'value="{self.value}">'
            )
        else:
            # Dos campos estilo hoteles conectados
            trigger_html = (
                f'<div style="display:flex;align-items:stretch;gap:0;'
                f"border:1px solid var(--border-input,var(--border));border-radius:10px;"
                f'overflow:hidden;background:var(--input-bg,var(--surface))">'
                # campo inicio
                f'<div id="{uid}_t1" onclick="{uid}_open(\'start\')" '
                f'style="display:flex;align-items:center;gap:8px;padding:10px 14px;'
                f'flex:1;cursor:pointer;transition:background .15s">'
                f'<div style="display:flex;flex-direction:column;gap:2px">'
                f'<span style="font-size:10px;font-weight:700;letter-spacing:.06em;'
                f'text-transform:uppercase;color:var(--text-muted)">{self.label_start}</span>'
                f'<span id="{uid}_d1" style="font-size:14px;color:{"var(--text)" if disp1 else "var(--text-muted)"}">'
                f"{disp1 or self.placeholder_start}</span>"
                f"</div></div>"
                # separador
                f'<div style="display:flex;align-items:center;padding:0 4px;'
                f'color:var(--text-muted)">{arrow_icon}</div>'
                # campo fin
                f'<div id="{uid}_t2" onclick="{uid}_open(\'end\')" '
                f'style="display:flex;align-items:center;gap:8px;padding:10px 14px;'
                f'flex:1;cursor:pointer;border-left:1px solid var(--border);transition:background .15s">'
                f'<div style="display:flex;flex-direction:column;gap:2px">'
                f'<span style="font-size:10px;font-weight:700;letter-spacing:.06em;'
                f'text-transform:uppercase;color:var(--text-muted)">{self.label_end}</span>'
                f'<span id="{uid}_d2" style="font-size:14px;color:{"var(--text)" if disp2 else "var(--text-muted)"}">'
                f"{disp2 or self.placeholder_end}</span>"
                f"</div></div>"
                f"</div>"
                f'<input type="hidden" id="{uid}_val1" '
                + (f'name="{self.name_start}" ' if self.name_start else "")
                + f'value="{self.value}">'
                f'<input type="hidden" id="{uid}_val2" '
                + (f'name="{self.name_end}" ' if self.name_end else "")
                + f'value="{self.value_end}">'
            )

        # ── Calendario (se renderiza con JS) ───────────────────────────────
        calendar_html = (
            f'<div id="{uid}_cal" role="dialog" aria-modal="true">'
            f'<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px">'
            f'<button onclick="{uid}_prevMonth()" style="background:none;border:none;cursor:pointer;'
            f'padding:4px 8px;border-radius:6px;color:var(--text);font-size:16px">&lsaquo;</button>'
            f'<span id="{uid}_month_lbl" style="font-size:14px;font-weight:700;color:var(--text)"></span>'
            f'<button onclick="{uid}_nextMonth()" style="background:none;border:none;cursor:pointer;'
            f'padding:4px 8px;border-radius:6px;color:var(--text);font-size:16px">&rsaquo;</button>'
            f"</div>"
            f'<div id="{uid}_grid" style="display:grid;grid-template-columns:repeat(7,1fr);gap:2px"></div>'
            + (
                f'<div style="display:flex;justify-content:space-between;margin-top:12px;'
                f'border-top:1px solid var(--border);padding-top:10px">'
                f'<button onclick="{uid}_clear()" style="font-size:12px;color:var(--text-muted);'
                f'background:none;border:none;cursor:pointer">Limpiar</button>'
                f'<button onclick="{uid}_close()" style="font-size:13px;font-weight:600;'
                f'color:var(--accent);background:none;border:none;cursor:pointer">Aceptar</button>'
                f"</div>"
            )
            + f"</div>"
        )

        # ── JavaScript ─────────────────────────────────────────────────────
        js = (
            f"<script>(function(){{"
            f"var U='{uid}',MONTHS={months_js},DAYS={days_js};"
            f"var isRange={is_range_js};"
            f"var sel1={val1_js},sel2={val2_js};"
            f"var minD={min_js},maxD={max_js};"
            f"var fmt={fmt_js};"
            f"var curYear=new Date().getFullYear();"
            f"var curMonth=new Date().getMonth();"
            f"var activeField='start';"  # qué campo se está editando
            f"var hoverDate=null;"
            # parse ISO
            f"function parseISO(s){{if(!s)return null;"
            f"var p=s.split('-');if(p.length<3)return null;"
            f"return new Date(+p[0],+p[1]-1,+p[2]);}}"
            # format to display
            f"function fmtDisp(iso){{"
            f"if(!iso)return '';"
            f"var p=iso.split('-');if(p.length<3)return iso;"
            f"return fmt.replace('DD',p[2]).replace('MM',p[1]).replace('YYYY',p[0]);}}"
            # format to ISO
            f"function toISO(y,m,d){{"
            f"return y+'-'+(m<9?'0':'')+(m+1)+'-'+(d<10?'0':'')+d;}}"
            # compare ISO strings
            f"function cmp(a,b){{return a<b?-1:a>b?1:0;}}"
            # render grid
            f"function render(){{"
            f"var lbl=document.getElementById(U+'_month_lbl');"
            f"if(lbl)lbl.textContent=MONTHS[curMonth]+' '+curYear;"
            f"var grid=document.getElementById(U+'_grid');"
            f"if(!grid)return;"
            f"var html='';"
            # day headers
            f"DAYS.forEach(function(d){{html+='<div style=\"font-size:11px;font-weight:700;"
            f"color:var(--text-muted);text-align:center;padding:4px 0\">'+d+'</div>';}});"
            # first day of month (Mon=0)
            f"var first=new Date(curYear,curMonth,1).getDay();"
            f"first=(first+6)%7;"  # lunes primero
            f"var days=new Date(curYear,curMonth+1,0).getDate();"
            f"var prevDays=new Date(curYear,curMonth,0).getDate();"
            f"var today=toISO(new Date().getFullYear(),new Date().getMonth(),new Date().getDate());"
            # prev month padding
            f"for(var i=first-1;i>=0;i--){{"
            f"html+='<div class=\"dp-day dp-other-month\" style=\"pointer-events:none\">'+(prevDays-i)+'</div>';}}"
            # days of month
            f"for(var d=1;d<=days;d++){{"
            f"var iso=toISO(curYear,curMonth,d);"
            f"var cls='dp-day';"
            f"if(minD&&iso<minD)cls+=' dp-disabled';"
            f"if(maxD&&iso>maxD)cls+=' dp-disabled';"
            f"if(iso===today)cls+=' dp-today';"
            # range highlighting
            f"var lo=sel1&&sel2?Math.min(cmp(sel1,sel2)===1?1:0,0)>=0?sel1:sel2:null;"  # menor
            f"var lo=sel1&&sel2?(sel1<sel2?sel1:sel2):null;"
            f"var hi=sel1&&sel2?(sel1<sel2?sel2:sel1):null;"
            f"if(isRange&&lo&&hi&&iso>lo&&iso<hi)cls+=' dp-in-range';"
            f"if(isRange&&lo&&iso===lo)cls+=' dp-selected dp-range-start';"
            f"if(isRange&&hi&&iso===hi)cls+=' dp-selected dp-range-end';"
            f"if(!isRange&&iso===sel1)cls+=' dp-selected';"
            f"html+='<div class=\"'+cls+'\" data-iso=\"'+iso+'\" onclick=\"'+U+'_pick(\\''+iso+'\\')\">';"
            f"html+=d+'</div>';}}"
            # fill remaining cells
            f"var total=first+days;"
            f"var rem=(7-total%7)%7;"
            f"for(var d=1;d<=rem;d++){{"
            f"html+='<div class=\"dp-day dp-other-month\" style=\"pointer-events:none\">'+d+'</div>';}}"
            f"grid.innerHTML=html;}}"
            # open calendar
            f"window.{uid}_open=function(field){{"
            f"activeField=field;"
            f"var cal=document.getElementById(U+'_cal');"
            f"if(!cal)return;"
            # posicionar debajo del trigger
            f"var trigger=document.getElementById(U+(isRange?(field==='start'?'_t1':'_t2'):'_trigger'));"
            f"var wrap=document.getElementById(U+'_wrap');"
            f"if(trigger&&wrap){{"
            f"var tr=trigger.getBoundingClientRect(),wr=wrap.getBoundingClientRect();"
            f"cal.style.top=(tr.bottom-wr.top+6)+'px';"
            f"var left=tr.left-wr.left;"
            f"var calW=310;var wrapW=wrap.offsetWidth;"
            f"if(left+calW>wrapW)left=Math.max(0,wrapW-calW);"
            f"cal.style.left=left+'px';}}"
            # ir al mes del valor seleccionado
            f"var refDate=parseISO(field==='end'&&sel2?sel2:sel1);"
            f"if(refDate){{curYear=refDate.getFullYear();curMonth=refDate.getMonth();}}"
            f"render();"
            f"cal.style.display='block';"
            f"}};"
            # close
            f"window.{uid}_close=function(){{"
            f"var cal=document.getElementById(U+'_cal');"
            f"if(cal)cal.style.display='none';"
            f"}};"
            # clear
            f"window.{uid}_clear=function(){{"
            f"sel1='';sel2='';"
            f"_updateDisplay();"
            f"render();"
            f"}};"
            # pick date
            f"window.{uid}_pick=function(iso){{"
            f"if(isRange){{"
            f"if(activeField==='start'||(!sel1&&!sel2)){{"
            f"sel1=iso;sel2='';"
            f"activeField='end';"  # auto-avanzar al campo fin
            f"render();"
            # reabrir para seleccionar fin
            f"}}else{{"
            f"if(iso<sel1){{sel2=sel1;sel1=iso;}}else{{sel2=iso;}}"
            f"_updateDisplay();"
            f"render();"
            f"{uid}_close();}}"
            f"}}else{{"
            f"sel1=iso;"
            f"_updateDisplay();"
            f"render();"
            f"{uid}_close();}}"
            f"}};"
            # update display fields
            f"function _updateDisplay(){{"
            f"if(isRange){{"
            f"var d1=document.getElementById(U+'_d1');"
            f"var d2=document.getElementById(U+'_d2');"
            f"var v1=document.getElementById(U+'_val1');"
            f"var v2=document.getElementById(U+'_val2');"
            f"if(d1){{d1.textContent=fmtDisp(sel1)||'{self.placeholder_start}';"
            f"d1.style.color=sel1?'var(--text)':'var(--text-muted)';}}"
            f"if(d2){{d2.textContent=fmtDisp(sel2)||'{self.placeholder_end}';"
            f"d2.style.color=sel2?'var(--text)':'var(--text-muted)';}}"
            f"if(v1)v1.value=sel1;"
            f"if(v2)v2.value=sel2;"
            f"}}else{{"
            f"var d=document.getElementById(U+'_disp');"
            f"var v=document.getElementById(U+'_val');"
            f"if(d){{d.textContent=fmtDisp(sel1)||'{self.placeholder}';"
            f"d.style.color=sel1?'var(--text)':'var(--text-muted)';}}"
            f"if(v)v.value=sel1;}}"
            f"}}"
            # prev/next month
            f"window.{uid}_prevMonth=function(){{"
            f"curMonth--;if(curMonth<0){{curMonth=11;curYear--;}}render();}};"
            f"window.{uid}_nextMonth=function(){{"
            f"curMonth++;if(curMonth>11){{curMonth=0;curYear++;}}render();}};"
            # cerrar al hacer clic fuera
            f"document.addEventListener('click',function(e){{"
            f"var cal=document.getElementById(U+'_cal');"
            f"var wrap=document.getElementById(U+'_wrap');"
            f"if(cal&&wrap&&!wrap.contains(e.target))cal.style.display='none';"
            f"}});"
            # inicializar display
            f"_updateDisplay();"
            f"}})();</script>"
        )

        return (
            css + f'<div id="{uid}_wrap" style="position:relative;display:inline-flex;'
            f'flex-direction:column;width:100%{wrapper_extra}">'
            + label_html
            + trigger_html
            + calendar_html
            + js
            + "</div>"
        )
