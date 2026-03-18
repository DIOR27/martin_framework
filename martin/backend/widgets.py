"""Backend-oriented widgets for martin.backend."""

from martin.widget import Widget

__all__ = ["Ref", "ApiCall", "MethodCall", "ResultBox"]


class Ref:
    """Referencia a un input por id para usarlo en `ApiCall.body`."""

    def __init__(self, input_id, label=False):
        self.input_id = input_id
        self.label = label

    def to_js(self):
        uid = self.input_id
        return (
            "(function(){"
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
            "var sv=document.getElementById('" + uid + "_val');"
            "if(sv){"
            "  var sl=document.getElementById('" + uid + "_label');"
            "  return {valor:sv.value,etiqueta:sl?sl.textContent.trim():sv.value};"
            "}"
            "var el=document.getElementById('" + uid + "');"
            "if(el)return el.value;"
            "return null;"
            "})()"
        )


class ApiCall:
    """Accion JS para usar con `Button(on_click=...)`."""

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
        self.body = body
        self.target = target
        self.loading = loading
        self.on_success = on_success
        self.on_error = on_error

    def _encode_value_js(self, value):
        import json as _json

        if isinstance(value, Ref):
            return value.to_js()
        if isinstance(value, dict):
            parts = []
            for key, val in value.items():
                parts.append(_json.dumps(str(key)) + ":" + self._encode_value_js(val))
            return "{" + ",".join(parts) + "}"
        if isinstance(value, (list, tuple)):
            return "[" + ",".join(self._encode_value_js(v) for v in value) + "]"
        return _json.dumps(value)

    def _body_js(self, btn_id):
        if self.body is None:
            return (
                "(function(){"
                "var btn=document.getElementById('" + btn_id + "');"
                "var form=btn?btn.closest('form,[data-martin-form]'):null;"
                "var scope=form||document;"
                "var data={};"
                "scope.querySelectorAll('input[name],textarea[name]').forEach(function(el){"
                "  if(el.type==='hidden'&&el.closest('[id$=_hidden]'))return;"
                "  data[el.name]=el.value;"
                "});"
                "scope.querySelectorAll('select').forEach(function(el){data[el.name]=el.value;});"
                "scope.querySelectorAll('[id$=_val]').forEach(function(el){"
                "  var uid=el.id.replace('_val','');"
                "  var lbl=document.getElementById(uid+'_label');"
                "  var key=el.name||uid;"
                "  data[key]={valor:el.value,etiqueta:lbl?lbl.textContent.trim():el.value};"
                "});"
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
        return self._encode_value_js(self.body)

    def to_js(self, btn_id):
        import json as _json

        url = _json.dumps(self.url)
        method = _json.dumps(self.method)
        loading = _json.dumps(self.loading)
        target_js = (
            "document.getElementById(" + _json.dumps(self.target) + ")"
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
            "var fetchOpts={method:" + method + ",headers:{}};"
            + (
                "var bodyData=" + body_js + ";"
                "fetchOpts.body=JSON.stringify(bodyData);"
                "fetchOpts.headers['Content-Type']='application/json';"
                if has_body else ""
            )
            + "var res=await fetch(" + url + ",fetchOpts);"
            + "var data=await res.json();"
            + "if(target){"
            + "  target.setAttribute('data-state',res.ok?'success':'error');"
            + "  target.setAttribute('data-status',res.status);"
            + "  target._martinData=data;"
            + "  target.dispatchEvent(new CustomEvent('martin:result',{detail:data}));"
            + "}"
            + ("(function(result){" + on_success + "})(data);" if on_success else "")
            + "}catch(e){"
            + "if(target){"
            + "  target.setAttribute('data-state','error');"
            + "  target._martinData={error:e.message};"
            + "  target.dispatchEvent(new CustomEvent('martin:result',{detail:{error:e.message}}));"
            + "}"
            + ("(function(err){" + on_error + "})(e);" if on_error else "")
            + "}finally{"
            + "btn.textContent=orig;"
            + "btn.disabled=false;"
            + "btn.style.opacity='1';"
            + "}"
            + "})()"
        )


class ResultBox(Widget):
    """Widget para mostrar la respuesta de un `ApiCall`."""

    def __init__(self, id, loading="Cargando...", empty="", format="json", template=None, **kwargs):
        self._props = Widget._extract_props(kwargs)
        self.box_id = id
        self.loading = loading
        self.empty = empty
        self.format = format
        self.template = template

    def render(self):
        import json as _json

        extra = self._resolve_props()
        box_id = self.box_id
        fmt = _json.dumps(self.format)
        tmpl = _json.dumps(self.template or "")

        wrapper_style = (
            "border-radius:12px;overflow:hidden;transition:all .3s;"
            "border:1px solid transparent"
        )
        if extra:
            wrapper_style += ";" + extra

        return (
            '<div id="' + box_id + '" data-state="empty" style="' + wrapper_style + '"></div>'
            '<style>'
            '#' + box_id + '[data-state=empty]{display:none}'
            '#' + box_id + '[data-state=loading]{display:block;padding:16px;border-color:var(--border);background:var(--surface);color:var(--text-muted);font-size:14px}'
            '#' + box_id + '[data-state=success]{display:block;padding:16px;border-color:rgba(52,211,153,0.3);background:var(--surface)}'
            '#' + box_id + '[data-state=error]{display:block;padding:16px;border-color:rgba(248,113,113,0.3);background:var(--surface)}'
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


class MethodCall(ApiCall):
    """
    Llamada RPC por nombre de método backend.

    Ejemplo:
        Button(
            "Guardar",
            on_click=MethodCall(
                "contact.create",
                params={"name": Ref("name_input")},
                endpoint="/api/_method",
                target="result_box",
            ),
        )
    """

    def __init__(
        self,
        method,
        params=None,
        args=None,
        kwargs=None,
        endpoint="/api/_method",
        target=None,
        loading="Procesando...",
        on_success=None,
        on_error=None,
    ):
        payload = {"method": method}
        if params is not None:
            payload["params"] = params
        if args is not None:
            payload["args"] = args
        if kwargs is not None:
            payload["kwargs"] = kwargs
        super().__init__(
            url=endpoint,
            method="POST",
            body=payload,
            target=target,
            loading=loading,
            on_success=on_success,
            on_error=on_error,
        )
