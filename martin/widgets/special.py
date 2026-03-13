"""
Martin — Special Widgets

Widgets especiales y utilitarios de alto nivel.

    Raw            — inyecta HTML sin procesamiento
    ThemeToggle    — alterna tema dark/light/auto
    CookieCategory — configuración de categoría de cookies
    CookieBanner   — banner GDPR con persistencia
"""

from ..widget import Widget


# =============================================================================
# Utility / Special
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
# Cookie Banner
# =============================================================================
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

