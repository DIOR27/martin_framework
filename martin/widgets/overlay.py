"""
Martin — Overlay Widgets

Widgets de superposición sobre el contenido principal.

    Modal — ventana modal con backdrop y controles de apertura/cierre
"""

from ..widget import Widget


# =============================================================================
# Overlay
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

    def _default_a11y_attrs(self):
        if self.title is None:
            return {"aria-label": "Dialogo"}
        plain = self._to_plain_text(self.title)
        if plain:
            return {"aria-label": plain}
        return {}

    _SCRIPT_READY = False

    def render(self):
        mid        = self.modal_id
        max_w      = self.max_width
        extra      = self._resolve_props()
        title_id   = f"{mid}_title"
        panel_id   = f"{mid}_panel"

        title_html = ""
        if self.title:
            t = self.title.render() if isinstance(self.title, Widget) else self.title
            title_html = (
                f'<div style="display:flex;align-items:center;justify-content:space-between;'
                f'margin-bottom:20px">'
                f'<div id="{title_id}" style="font-size:18px;font-weight:700;color:var(--text)">{t}</div>'
                f'<button onclick="closeModal(\'{mid}\')" '
                f'aria-label="Cerrar modal"'
                f'style="background:none;border:none;cursor:pointer;font-size:20px;'
                f'color:var(--text-muted);line-height:1;padding:4px">&#x2715;</button>'
                f'</div>'
            )

        inner = self._render_children(self.children)

        backdrop_click = (f' onclick="if(event.target===this)closeModal(\'{mid}\')"'
                          if self.close_on_backdrop else "")
        box_extra = (f";{extra}" if extra else "")
        labelledby_attr = f' aria-labelledby="{title_id}"' if self.title else ""

        html = (
            f'<div id="{mid}" style="display:none;position:fixed;top:0;left:0;'
            f'width:100%;height:100%;background:rgba(0,0,0,0.55);'
            f'backdrop-filter:blur(4px);-webkit-backdrop-filter:blur(4px);'
            f'z-index:99999;align-items:center;justify-content:center"'
            f' role="dialog" aria-modal="true" aria-hidden="true"'
            f'{labelledby_attr}'
            f'{backdrop_click}>'
            f'<div id="{panel_id}" tabindex="-1" style="background:var(--surface);border:1px solid var(--border);'
            f'border-radius:16px;padding:28px 32px;max-width:{max_w}px;width:90%;'
            f'box-shadow:0 24px 64px rgba(0,0,0,0.4);max-height:85vh;overflow-y:auto{box_extra}">'
            f'{title_html}{inner}'
            f'</div></div>'
        )
        if not Modal._SCRIPT_READY:
            html += (
                f'<script>'
                f'if(!window.openModal)window.openModal=function(id){{'
                f'  var m=document.getElementById(id);'
                f'  if(m){{'
                f'    m.style.display="flex";'
                f'    m.setAttribute("aria-hidden","false");'
                f'    var p=m.querySelector("[tabindex=\'-1\']");'
                f'    if(p){{m._martinPrevFocus=document.activeElement;setTimeout(function(){{p.focus();}},0);}}'
                f'  }}'
                f'}};'
                f'if(!window.closeModal)window.closeModal=function(id){{'
                f'  var m=document.getElementById(id);'
                f'  if(m){{'
                f'    m.style.display="none";'
                f'    m.setAttribute("aria-hidden","true");'
                f'    if(m._martinPrevFocus&&m._martinPrevFocus.focus){{m._martinPrevFocus.focus();}}'
                f'  }}'
                f'}};'
                f'if(!window._martinModalEscBound){{'
                f'  window._martinModalEscBound=true;'
                f'  document.addEventListener("keydown",function(e){{'
                f'    if(e.key!=="Escape")return;'
                f'    var ms=document.querySelectorAll("[role=\'dialog\'][aria-hidden=\'false\']");'
                f'    if(ms.length){{closeModal(ms[ms.length-1].id);}}'
                f'  }});'
                f'}}'
                f'</script>'
            )
            Modal._SCRIPT_READY = True
        return html

