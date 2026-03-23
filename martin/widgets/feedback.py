"""
Martin — Feedback Widgets

Widgets para comunicar estado al usuario.

    Badge       — etiqueta de estado o categoría, pequeña y llamativa
    Alert       — mensaje de alerta o notificación inline
    Toast       — notificación flotante y temporal
    ToastCenter — runtime global para disparar toasts manualmente
"""

import html as _html

from ..widget import Widget


# =============================================================================
# Badge
# =============================================================================


class Badge(Widget):
    """
    Etiqueta de estado o categoría. Pequeña y llamativa.

        Badge("Nuevo")
        Badge("Pro", background="var(--accent)", color="#fff")
        Badge("Beta", background="#f59e0b", radius=4)
        Badge("v2.0", background="var(--surface-2)", color="var(--text)", radius=4)

    Por defecto usa el color de acento del tema con texto blanco.
    """

    def __init__(self, label=None, child=None, children=None, **kwargs):
        self._props = Widget._extract_props(kwargs)
        self.label = label
        self.child = child
        self.children = children
        # Defaults de color si no se proporcionaron
        if not self._props.get("background"):
            self._props["background"] = "var(--accent)"
        if not self._props.get("color"):
            self._props["color"] = "#ffffff"

    def render(self):
        base = (
            "display:inline-block; padding:2px 10px; border-radius:9999px; "
            "font-size:12px; font-weight:600; white-space:nowrap"
        )
        inline = self._resolve_props(base)
        inner = self._resolve_inner(self.label, self.child, self.children)
        return self._wrap_url(f'<span style="{inline}">{inner}</span>')


# =============================================================================
# Alert
# =============================================================================


class Alert(Widget):
    """
    Mensaje de alerta o notificación inline.

        Alert("Guardado correctamente.", variant="success")
        Alert("Email inválido.", variant="error")
        Alert("Recuerda completar todos los campos.", variant="warning")
        Alert("Tienes 3 mensajes nuevos.", variant="info")

    Variantes: "info" | "success" | "warning" | "error"

    Acepta title para mayor claridad:
        Alert("El archivo fue eliminado.", variant="error", title="Error")

    Acepta icon personalizado:
        Alert("Proceso completado.", variant="success", icon="🎉")
    """

    VARIANTS = {
        "info": {
            "bg": "rgba(59,130,246,0.1)",
            "border": "rgba(59,130,246,0.3)",
            "icon": "ℹ️",
            "color": "#3b82f6",
        },
        "success": {
            "bg": "rgba(34,197,94,0.1)",
            "border": "rgba(34,197,94,0.3)",
            "icon": "✅",
            "color": "#22c55e",
        },
        "warning": {
            "bg": "rgba(234,179,8,0.1)",
            "border": "rgba(234,179,8,0.3)",
            "icon": "⚠️",
            "color": "#eab308",
        },
        "error": {
            "bg": "rgba(239,68,68,0.1)",
            "border": "rgba(239,68,68,0.3)",
            "icon": "❌",
            "color": "#ef4444",
        },
    }

    def __init__(self, message="", variant="info", title=None, icon=None, **kwargs):
        self._props = Widget._extract_props(kwargs)
        self.message = message
        self.variant = variant
        self.title = title
        self.icon = icon

    def render(self):
        v = self.VARIANTS.get(self.variant, self.VARIANTS["info"])
        ico = self.icon if self.icon is not None else v["icon"]
        base = (
            f"display:flex; align-items:flex-start; gap:12px; "
            f"padding:14px 16px; border-radius:10px; "
            f"background:{v['bg']}; border:1px solid {v['border']}"
        )
        inline = self._resolve_props(base)

        title_html = (
            f'<div style="font-weight:700;font-size:14px;color:{v["color"]};'
            f'margin-bottom:4px;">{self.title}</div>'
            if self.title
            else ""
        )

        return (
            f'<div style="{inline}">'
            f'<span style="font-size:18px;flex-shrink:0;margin-top:1px">{ico}</span>'
            f'<div style="font-size:14px;color:var(--text);line-height:1.5">'
            f"{title_html}{self.message}</div>"
            f"</div>"
        )


class Toast(Widget):
    """
    Notificación flotante que aparece en una esquina y puede cerrarse sola.

        Toast("Cambios guardados", variant="success")
        Toast("Correo enviado", title="Listo", variant="info", duration=2500)

    Compatible con stacking por posición, para que varios toasts no se superpongan.
    """

    VARIANTS = {
        "info": {
            "bg": "rgba(59,130,246,0.14)",
            "border": "rgba(59,130,246,0.28)",
            "icon": "ℹ️",
            "color": "#60a5fa",
        },
        "success": {
            "bg": "rgba(34,197,94,0.14)",
            "border": "rgba(34,197,94,0.28)",
            "icon": "✅",
            "color": "#4ade80",
        },
        "warning": {
            "bg": "rgba(234,179,8,0.14)",
            "border": "rgba(234,179,8,0.28)",
            "icon": "⚠️",
            "color": "#facc15",
        },
        "error": {
            "bg": "rgba(239,68,68,0.14)",
            "border": "rgba(239,68,68,0.28)",
            "icon": "❌",
            "color": "#f87171",
        },
    }

    POSITIONS = {
        "bottom-right": {"bottom": "20px", "right": "20px", "axis": "y", "direction": -1},
        "bottom-left": {"bottom": "20px", "left": "20px", "axis": "y", "direction": -1},
        "top-right": {"top": "20px", "right": "20px", "axis": "y", "direction": 1},
        "top-left": {"top": "20px", "left": "20px", "axis": "y", "direction": 1},
    }

    _counter = 0

    def __init__(
        self,
        message="",
        title=None,
        variant="info",
        icon=None,
        duration=4000,
        closable=True,
        position="bottom-right",
        max_width=360,
        **kwargs,
    ):
        self._props = Widget._extract_props(kwargs)
        self.message = message
        self.title = title
        self.variant = variant
        self.icon = icon
        self.duration = max(0, int(duration or 0))
        self.closable = bool(closable)
        self.position = position if position in self.POSITIONS else "bottom-right"
        self.max_width = max(220, int(max_width or 360))
        Toast._counter += 1
        self.uid = f"martin_toast_{Toast._counter}"

    def _render_icon(self, fallback_icon):
        icon = self.icon if self.icon is not None else fallback_icon
        if isinstance(icon, Widget):
            return icon.render()
        return _html.escape(str(icon), quote=False)

    def render(self):
        variant = self.VARIANTS.get(self.variant, self.VARIANTS["info"])
        pos = self.POSITIONS[self.position]
        inline = self._resolve_props(
            "position:fixed;"
            f"max-width:{self.max_width}px;width:min(calc(100vw - 32px), {self.max_width}px);"
            "display:flex;align-items:flex-start;gap:12px;"
            "padding:14px 16px;border-radius:16px;"
            f"background:{variant['bg']};border:1px solid {variant['border']};"
            "backdrop-filter:blur(18px);-webkit-backdrop-filter:blur(18px);"
            "box-shadow:0 16px 48px rgba(0,0,0,0.24);"
            "z-index:1200;opacity:0;transform:translateY(12px) scale(.96);"
            "transition:opacity .22s ease,transform .22s ease;"
        )
        title_html = (
            f'<div style="font-weight:700;font-size:14px;color:{variant["color"]};margin-bottom:4px;">'
            f"{_html.escape(str(self.title), quote=False)}</div>"
            if self.title
            else ""
        )
        close_html = (
            f'<button type="button" aria-label="Dismiss toast" onclick="window.__martinToastHide&&window.__martinToastHide(\'{self.uid}\')" '
            'style="margin-left:auto;flex-shrink:0;border:none;background:transparent;color:var(--text-muted);'
            'font-size:16px;cursor:pointer;line-height:1;padding:2px 0 0 6px">×</button>'
            if self.closable
            else ""
        )
        script = (
            "<script>(function(){"
            "if(!window.__martinToastLayout){"
            "window.__martinToastHide=function(id){var el=document.getElementById(id);if(!el)return;"
            "el.setAttribute('data-open','0');el.style.opacity='0';el.style.transform='translateY(10px) scale(.96)';"
            "setTimeout(function(){if(el&&el.parentNode){el.parentNode.removeChild(el);window.__martinToastLayout&&window.__martinToastLayout();}},220);};"
            "window.__martinToastLayout=function(){"
            "var groups={};document.querySelectorAll('[data-martin-toast=\"1\"]').forEach(function(el){"
            "var pos=el.getAttribute('data-toast-position')||'bottom-right';(groups[pos]=groups[pos]||[]).push(el);});"
            "Object.keys(groups).forEach(function(pos){var items=groups[pos];var offset=20;"
            "items.forEach(function(el){var dir=(el.getAttribute('data-toast-direction')||'-1')==='1'?1:-1;"
            "var anchor=el.getAttribute('data-toast-anchor')||'bottom';"
            "el.style[anchor]=offset+'px';el.style.top=anchor==='top'?offset+'px':'';el.style.bottom=anchor==='bottom'?offset+'px':'';"
            "offset += el.offsetHeight + 12; el.style.transform='translateY(0) scale(1)'; el.style.opacity='1';});});};"
            "window.addEventListener('resize',window.__martinToastLayout);"
            "}"
            f"var el=document.getElementById('{self.uid}');if(!el)return;"
            f"el.setAttribute('data-toast-anchor','{'top' if 'top' in self.position else 'bottom'}');"
            f"el.setAttribute('data-toast-direction','{pos['direction']}');"
            "requestAnimationFrame(function(){window.__martinToastLayout&&window.__martinToastLayout();});"
            + (f"setTimeout(function(){{window.__martinToastHide&&window.__martinToastHide('{self.uid}');}},{self.duration});" if self.duration > 0 else "")
            + "})();</script>"
        )

        return (
            f'<div id="{self.uid}" data-martin-toast="1" data-toast-position="{self.position}" '
            f'style="{inline};{"top:20px;" if "top" in self.position else "bottom:20px;"}'
            f'{"left:20px;" if "left" in self.position else "right:20px;"}">'
            f'<span style="font-size:18px;flex-shrink:0;margin-top:1px;color:{variant["color"]}">{self._render_icon(variant["icon"])}</span>'
            f'<div style="min-width:0;flex:1 1 auto;font-size:14px;color:var(--text);line-height:1.5">'
            f"{title_html}{_html.escape(str(self.message), quote=False)}</div>"
            f"{close_html}"
            f"</div>{script}"
        )


class ToastCenter(Widget):
    """
    Runtime global para disparar toasts desde cualquier widget o script.

        ToastCenter()
        Button("Avisar", on_click="window.martinNotify({message:'Hola',variant:'success'})")
    """

    def __init__(self, items=None, **kwargs):
        self._props = Widget._extract_props(kwargs)
        self.items = list(items or [])

    def render(self):
        payload_js = _html.escape(str(self._props.get("id") or ""))
        items_js = __import__("json").dumps(self.items, ensure_ascii=False)
        return (
            f'<div data-martin-toast-center="1" style="display:none" aria-hidden="true">{payload_js}</div>'
            "<script>(function(){"
            "if(!window.__martinToastFromPayload){"
            "window.__martinToastHide=function(id){var el=document.getElementById(id);if(!el)return;"
            "el.style.opacity='0';el.style.transform='translateY(10px) scale(.96)';"
            "setTimeout(function(){if(el&&el.parentNode){el.parentNode.removeChild(el);window.__martinToastLayout&&window.__martinToastLayout();}},220);};"
            "window.__martinToastLayout=function(){var groups={};"
            "document.querySelectorAll('[data-martin-toast=\"1\"]').forEach(function(el){var pos=el.getAttribute('data-toast-position')||'bottom-right';(groups[pos]=groups[pos]||[]).push(el);});"
            "Object.keys(groups).forEach(function(pos){var items=groups[pos];var offset=20;items.forEach(function(el){var anchor=el.getAttribute('data-toast-anchor')||'bottom';"
            "if(anchor==='top'){el.style.top=offset+'px';el.style.bottom='';}else{el.style.bottom=offset+'px';el.style.top='';}"
            "offset+=el.offsetHeight+12;el.style.opacity='1';el.style.transform='translateY(0) scale(1)';});});};"
            "window.__martinToastFromPayload=function(payload){if(!payload||typeof payload!=='object')return;"
            "var variant=payload.variant||'info';var map={info:{bg:'rgba(59,130,246,0.14)',border:'rgba(59,130,246,0.28)',icon:'ℹ️',color:'#60a5fa'},success:{bg:'rgba(34,197,94,0.14)',border:'rgba(34,197,94,0.28)',icon:'✅',color:'#4ade80'},warning:{bg:'rgba(234,179,8,0.14)',border:'rgba(234,179,8,0.28)',icon:'⚠️',color:'#facc15'},error:{bg:'rgba(239,68,68,0.14)',border:'rgba(239,68,68,0.28)',icon:'❌',color:'#f87171'}};"
            "var cfg=map[variant]||map.info;var pos=payload.position||'bottom-right';var anchor=pos.indexOf('top')===0?'top':'bottom';"
            "var wrap=document.createElement('div');var id='martin_toast_runtime_'+Math.random().toString(36).slice(2);"
            "wrap.id=id;wrap.setAttribute('data-martin-toast','1');wrap.setAttribute('data-toast-position',pos);wrap.setAttribute('data-toast-anchor',anchor);"
            "wrap.style.cssText='position:fixed;left:'+(pos.indexOf('left')>=0?'20px':'')+';right:'+(pos.indexOf('right')>=0?'20px':'')+';max-width:360px;width:min(calc(100vw - 32px),360px);display:flex;align-items:flex-start;gap:12px;padding:14px 16px;border-radius:16px;background:'+cfg.bg+';border:1px solid '+cfg.border+';backdrop-filter:blur(18px);-webkit-backdrop-filter:blur(18px);box-shadow:0 16px 48px rgba(0,0,0,0.24);z-index:1200;opacity:0;transform:translateY(12px) scale(.96);transition:opacity .22s ease,transform .22s ease;';"
            "var title=payload.title?'<div style=\"font-weight:700;font-size:14px;color:'+cfg.color+';margin-bottom:4px;\">'+payload.title+'</div>':'';var closable=payload.closable!==false;"
            "wrap.innerHTML='<div style=\"font-size:18px;line-height:1.1\">'+(payload.icon||cfg.icon)+'</div><div style=\"flex:1;min-width:0;font-size:14px;color:var(--text);line-height:1.5\">'+title+(payload.message||'')+'</div>'+(closable?'<button type=\"button\" style=\"margin-left:auto;border:none;background:transparent;color:var(--text-muted);font-size:16px;cursor:pointer;line-height:1;padding:2px 0 0 6px\">×</button>':'');"
            "document.body.appendChild(wrap);if(closable){var btn=wrap.querySelector('button');if(btn)btn.addEventListener('click',function(){window.__martinToastHide(id);});}"
            "requestAnimationFrame(function(){window.__martinToastLayout&&window.__martinToastLayout();});var duration=Number(payload.duration||0);if(duration>0){setTimeout(function(){window.__martinToastHide&&window.__martinToastHide(id);},duration);}"
            "};window.martinNotify=window.__martinToastFromPayload;window.addEventListener('resize',window.__martinToastLayout);}"
            "var initial=" + items_js + ";if(Array.isArray(initial)){initial.forEach(function(item){window.martinNotify&&window.martinNotify(item);});}"
            "})();</script>"
        )
