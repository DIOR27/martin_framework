"""
Martin — Special Widgets

Widgets especiales y utilitarios de alto nivel.

    Raw            — inyecta HTML sin procesamiento
    Script         — inyecta JavaScript inline o externo
    Stylesheet     — carga CSS externo con <link rel="stylesheet">
    StyleTag       — inyecta CSS inline con <style>
    ThemeToggle    — alterna tema dark/light/auto
    ScrollToTop    — botón flotante para volver al inicio
    WhatsAppButton — botón flotante de WhatsApp configurable
    Counter        — contador progresivo/regresivo humanizado
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


class Script(Widget):
    """
    Carga JavaScript desde Python (externo o inline).

    Ejemplos:
        Script(src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js", defer=True)
        Script(code="window.APP_READY = true;")
        Script(src="https://esm.sh/lodash-es", module=True)
    """

    def __init__(
        self,
        src=None,
        code=None,
        type="text/javascript",
        module=False,
        defer=False,
        async_load=False,
        crossorigin=None,
        integrity=None,
        referrer_policy=None,
        nonce=None,
        no_module=False,
        id=None,
        **kwargs,
    ):
        self._props = Widget._extract_props(kwargs)
        self.src = src
        self.code = code or ""
        self.type = type
        self.module = module
        self.defer = defer
        self.async_load = async_load
        self.crossorigin = crossorigin
        self.integrity = integrity
        self.referrer_policy = referrer_policy
        self.nonce = nonce
        self.no_module = no_module
        self.id = id

    def render(self):
        script_type = "module" if self.module else self.type
        attrs = self._attrs(
            src=self.src,
            type=script_type,
            defer=self.defer,
            **{"async": self.async_load},
            crossorigin=self.crossorigin,
            integrity=self.integrity,
            referrerpolicy=self.referrer_policy,
            nonce=self.nonce,
            nomodule=self.no_module,
            id=self.id,
        )
        if self.src:
            return f"<script{attrs}></script>"
        return f"<script{attrs}>{self.code}</script>"


class Stylesheet(Widget):
    """
    Carga CSS externo con <link>.

    Ejemplos:
        Stylesheet("https://unpkg.com/leaflet@1.9.4/dist/leaflet.css")
        Stylesheet("/assets/custom.css", media="print")
    """

    def __init__(
        self,
        href,
        rel="stylesheet",
        media=None,
        crossorigin=None,
        integrity=None,
        referrer_policy=None,
        id=None,
        **kwargs,
    ):
        self._props = Widget._extract_props(kwargs)
        self.href = href
        self.rel = rel
        self.media = media
        self.crossorigin = crossorigin
        self.integrity = integrity
        self.referrer_policy = referrer_policy
        self.id = id

    def render(self):
        attrs = self._attrs(
            rel=self.rel,
            href=self.href,
            media=self.media,
            crossorigin=self.crossorigin,
            integrity=self.integrity,
            referrerpolicy=self.referrer_policy,
            id=self.id,
        )
        return f"<link{attrs}>"


class StyleTag(Widget):
    """
    Inyecta CSS inline desde Python.

    Ejemplo:
        StyleTag(".hero { text-wrap: balance; }")
    """

    def __init__(self, css, id=None, media=None, **kwargs):
        self._props = Widget._extract_props(kwargs)
        self.css = css
        self.id = id
        self.media = media

    def render(self):
        attrs = self._attrs(id=self.id, media=self.media)
        return f"<style{attrs}>{self.css}</style>"


class ThemeToggle(Widget):
    """
    Boton para cambiar entre temas oscuro/claro/auto.

        ThemeToggle()                            # con emojis por defecto
        ThemeToggle(dark_icon="Oscuro", light_icon="Claro")
        ThemeToggle(include_auto=False)          # solo dark/light
        ThemeToggle(radius=8, padding=8)
        ThemeToggle(floating=True, float_position="bottom-right")

    Por defecto es inline, asi que puede colocarse en un NavBar o donde
    necesites. Si activas ``floating=True``, usa el sistema flotante
    universal de MARTIN y se apila automaticamente con otros botones
    flotantes de la misma esquina sin superponerse.
    """
    def __init__(
        self,
        dark_icon="🌙",
        light_icon="☀️",
        auto_icon="🌗",
        include_auto=True,
        title="Cambiar tema",
        shape="circle",
        size=48,
        **kwargs,
    ):
        self._props       = Widget._extract_props(kwargs)
        self.dark_icon    = dark_icon
        self.light_icon   = light_icon
        self.auto_icon    = auto_icon
        self.include_auto = include_auto
        self.title        = title
        self.shape        = str(shape or "circle").lower()
        self.size         = max(28, int(size))

    def render(self):
        if self.shape == "pill":
            base = (
                "background:var(--dropdown-bg,var(--bg-secondary,var(--surface))); border:1px solid var(--border); "
                "color:var(--text); cursor:pointer; font-size:16px; "
                "display:inline-flex; align-items:center; justify-content:center; "
                "border-radius:999px; padding:6px 12px; min-height:40px; "
                "transition:all 0.2s; user-select:none"
            )
        elif self.shape == "square":
            base = (
                "background:var(--dropdown-bg,var(--bg-secondary,var(--surface))); border:1px solid var(--border); "
                "color:var(--text); cursor:pointer; font-size:16px; "
                "display:inline-flex; align-items:center; justify-content:center; "
                f"width:{self.size}px; height:{self.size}px; border-radius:12px; "
                "padding:0; transition:all 0.2s; user-select:none"
            )
        else:
            base = (
                "background:var(--dropdown-bg,var(--bg-secondary,var(--surface))); border:1px solid var(--border); "
                "color:var(--text); cursor:pointer; font-size:16px; "
                "display:inline-flex; align-items:center; justify-content:center; "
                f"width:{self.size}px; height:{self.size}px; border-radius:999px; "
                "padding:0; transition:all 0.2s; user-select:none"
            )
        inline  = self._resolve_props(base)
        initial = self.auto_icon if self.include_auto else self.dark_icon
        uid     = f"_mtt_{id(self) & 0xFFFF}"
        next_light = "auto" if self.include_auto else "dark"

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
            f'  var NEXT={{"dark":"light","light":"{next_light}","auto":"dark"}};'
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


class ScrollToTop(Widget):
    """
    Boton flotante para volver al inicio con scroll suave.

        ScrollToTop()
        ScrollToTop(icon="↑", show_after=320)
        ScrollToTop(icon=Icon(name="arrow-up", provider="fa", variant="solid"), background="#6366f1", color="#fff")
    """

    _id_counter = 0

    def __init__(
        self,
        icon="↑",
        content=None,
        title="Volver arriba",
        show_after=240,
        behavior="smooth",
        size=48,
        bottom=20,
        right=20,
        left=None,
        top=None,
        z_index=999,
        target="window",
        **kwargs,
    ):
        self._props = Widget._extract_props(kwargs)
        if self._props.get("floating") is None:
            self._props["floating"] = True
        if not self._props.get("float_position"):
            if top is not None and left is not None:
                self._props["float_position"] = "top-left"
            elif top is not None:
                self._props["float_position"] = "top-right"
            elif left is not None:
                self._props["float_position"] = "bottom-left"
            else:
                self._props["float_position"] = "bottom-right"
        if self._props.get("float_offset") is None:
            inferred_offset = top if top is not None else bottom
            if left is not None and top is None:
                inferred_offset = left
            elif right is not None and top is None and left is None:
                inferred_offset = right
            self._props["float_offset"] = inferred_offset
        if self._props.get("float_z_index") is None:
            self._props["float_z_index"] = z_index
        self.icon = icon
        self.content = content
        self.title = title
        self.show_after = max(0, int(show_after))
        self.behavior = str(behavior or "smooth")
        self.size = max(40, int(size))
        self.bottom = bottom
        self.right = right
        self.left = left
        self.top = top
        self.z_index = int(z_index)
        self.target = str(target or "window")
        ScrollToTop._id_counter += 1
        self.uid = f"scroll_top_{ScrollToTop._id_counter}"

    def _render_content(self):
        content = self.content if self.content is not None else self.icon
        if isinstance(content, Widget):
            return content.render()
        return str(content)

    @staticmethod
    def _css_size(value):
        if value is None:
            return None
        if isinstance(value, (int, float)):
            return f"{value}px"
        return str(value)

    def render(self):
        uid = self.uid
        content_html = self._render_content()
        extra = self._resolve_props()

        button_parts = [
            "display:inline-flex",
            "align-items:center",
            "justify-content:center",
            "gap:8px",
            f"width:{self.size}px",
            f"height:{self.size}px",
            "padding:0",
            "border-radius:999px",
            "border:1px solid var(--border)",
            "background:var(--surface)",
            "color:var(--text)",
            "box-shadow:var(--shadow)",
            "cursor:pointer",
            "user-select:none",
            "line-height:1",
            "opacity:0",
            "visibility:hidden",
            "transform:translateY(10px)",
            "transition:opacity .2s ease, transform .2s ease, visibility .2s ease, border-color .2s ease",
        ]
        inline = ";".join(button_parts) + ";" + extra

        return (
            f'<button id="{uid}" type="button" title="{self.title}" aria-label="{self.title}" style="{inline}">'
            f"{content_html}"
            f"</button>"
            f"<script>(function(){{"
            f"var btn=document.getElementById('{uid}');"
            f"if(!btn||btn.dataset.martinScrollTopBound)return;"
            f"btn.dataset.martinScrollTopBound='1';"
            f"var threshold={self.show_after};"
            f"var behavior={self.behavior!r};"
            f"var target={self.target!r};"
            f"function getContainer(){{"
            f"  if(!target||target==='window')return window;"
            f"  return document.getElementById(target)||document.querySelector(target)||window;"
            f"}}"
            f"function scrollTopValue(node){{"
            f"  if(node===window)return window.pageYOffset||document.documentElement.scrollTop||document.body.scrollTop||0;"
            f"  return node&&typeof node.scrollTop==='number'?node.scrollTop:0;"
            f"}}"
            f"function setVisible(show){{"
            f"  btn.style.opacity=show?'1':'0';"
            f"  btn.style.visibility=show?'visible':'hidden';"
            f"  btn.style.transform=show?'translateY(0)':'translateY(10px)';"
            f"}}"
            f"function update(){{"
            f"  var container=getContainer();"
            f"  setVisible(scrollTopValue(container)>threshold);"
            f"}}"
            f"function goTop(){{"
            f"  var container=getContainer();"
            f"  if(container===window)window.scrollTo({{top:0,behavior:behavior}});"
            f"  else if(container&&typeof container.scrollTo==='function')container.scrollTo({{top:0,behavior:behavior}});"
            f"  else if(container)container.scrollTop=0;"
            f"}}"
            f"btn.addEventListener('click',goTop);"
            f"btn.addEventListener('mouseenter',function(){{btn.style.borderColor='var(--accent)';}});"
            f"btn.addEventListener('mouseleave',function(){{btn.style.borderColor='';}});"
            f"window.addEventListener('scroll',update,{{passive:true}});"
            f"document.addEventListener('scroll',update,{{passive:true,capture:true}});"
            f"update();"
            f"}})();</script>"
        )


class WhatsAppButton(Widget):
    """
    Boton flotante reutilizable para abrir WhatsApp.

        WhatsAppButton(phone="593999999999")
        WhatsAppButton(phone="593999999999", message="Hola Martin")
        WhatsAppButton(icon=Icon(name="whatsapp", provider="fa", variant="brands"), url="https://wa.me/593999999999")
    """

    _id_counter = 0

    def __init__(
        self,
        phone=None,
        message="",
        icon="✆",
        content=None,
        label="WhatsApp",
        title="Abrir WhatsApp",
        url=None,
        action=None,
        target="_blank",
        shape="circle",
        size=48,
        show_label=False,
        **kwargs,
    ):
        self._props = Widget._extract_props(kwargs)
        if self._props.get("floating") is None:
            self._props["floating"] = True
        if not self._props.get("float_position"):
            self._props["float_position"] = "bottom-right"
        if self._props.get("float_offset") is None:
            self._props["float_offset"] = 20
        if self._props.get("float_gap") is None:
            self._props["float_gap"] = 12
        if self._props.get("float_z_index") is None:
            self._props["float_z_index"] = 999
        self.phone = "".join(ch for ch in str(phone or "") if ch.isdigit())
        self.message = str(message or "")
        self.icon = icon
        self.content = content
        self.label = label
        self.title = title
        self.url = url
        self.action = action
        self.target = target
        self.shape = str(shape or "circle").lower()
        self.size = max(40, int(size))
        self.show_label = bool(show_label)
        WhatsAppButton._id_counter += 1
        self.uid = f"wa_btn_{WhatsAppButton._id_counter}"

    def _render_content(self):
        content = self.content if self.content is not None else self.icon
        if isinstance(content, Widget):
            return content.render()
        return str(content)

    def _resolved_url(self):
        if self.url:
            return str(self.url)
        if not self.phone:
            return ""
        base = f"https://wa.me/{self.phone}"
        if self.message:
            from urllib.parse import quote

            return f"{base}?text={quote(self.message)}"
        return base

    def render(self):
        content_html = self._render_content()
        extra = self._resolve_props()
        if self.shape == "pill" or self.show_label:
            base = (
                "display:inline-flex;align-items:center;justify-content:center;gap:10px;"
                f"min-height:{self.size}px;padding:0 16px;border-radius:999px;"
                "background:#25D366;color:#fff;border:1px solid rgba(0,0,0,.06);"
                "box-shadow:0 18px 32px rgba(37,211,102,.28);font-weight:700;"
                "font-size:14px;cursor:pointer;text-decoration:none;user-select:none"
            )
        elif self.shape == "square":
            base = (
                f"display:inline-flex;align-items:center;justify-content:center;width:{self.size}px;height:{self.size}px;"
                "border-radius:14px;background:#25D366;color:#fff;border:1px solid rgba(0,0,0,.06);"
                "box-shadow:0 18px 32px rgba(37,211,102,.28);font-size:22px;cursor:pointer;text-decoration:none;user-select:none"
            )
        else:
            base = (
                f"display:inline-flex;align-items:center;justify-content:center;width:{self.size}px;height:{self.size}px;"
                "border-radius:999px;background:#25D366;color:#fff;border:1px solid rgba(0,0,0,.06);"
                "box-shadow:0 18px 32px rgba(37,211,102,.28);font-size:22px;cursor:pointer;text-decoration:none;user-select:none"
            )
        inline = base + ";" + extra
        label_html = (
            f'<span style="white-space:nowrap;font-size:14px;font-weight:700">{self.label}</span>'
            if (self.show_label or self.shape == "pill")
            else ""
        )
        attrs = [
            f'id="{self.uid}"',
            f'title="{self.title}"',
            f'aria-label="{self.title}"',
            f'style="{inline}"',
        ]
        href = self._resolved_url()
        tag = "a" if href else "button"
        if tag == "a":
            attrs.append(f'href="{href}"')
            attrs.append(f'target="{self.target}"')
            if self.target == "_blank":
                attrs.append('rel="noopener noreferrer"')
        else:
            attrs.append('type="button"')
        action_js = self.action or ""
        return (
            f'<{tag} {" ".join(attrs)}'
            + (f' onclick="{action_js}"' if action_js else "")
            + ' onmouseover="this.style.transform=\'translateY(-2px)\';this.style.filter=\'brightness(1.03)\'"'
            + ' onmouseout="this.style.transform=\'\';this.style.filter=\'\'">'
            + f'<span aria-hidden="true" style="display:inline-flex;align-items:center;justify-content:center;line-height:1">{content_html}</span>'
            + label_html
            + f"</{tag}>"
        )


class Counter(Widget):
    """
    Contador progresivo o regresivo basado en fecha/hora.

        Counter(to="2026-12-31 23:59:59", mode="countdown")
        Counter(from_="2026-03-01 09:00:00", mode="countup", format="clock")
        Counter(to="2026-04-01", mode="remaining", format="human")
    """

    _id_counter = 0

    def __init__(
        self,
        to=None,
        from_=None,
        mode="countdown",
        format="full",
        prefix="",
        suffix="",
        completed_text="Ahora",
        tick=1000,
        labels=None,
        **kwargs,
    ):
        self._props = Widget._extract_props(kwargs)
        self.to = to
        self.from_ = from_
        self.mode = str(mode or "countdown").lower()
        self.format = str(format or "full").lower()
        self.prefix = str(prefix or "")
        self.suffix = str(suffix or "")
        self.completed_text = str(completed_text or "Ahora")
        self.tick = max(250, int(tick or 1000))
        self.labels = labels or {
            "day": "día",
            "days": "días",
            "hour": "hora",
            "hours": "horas",
            "minute": "minuto",
            "minutes": "minutos",
            "second": "segundo",
            "seconds": "segundos",
            "remaining": "Faltan",
            "elapsed": "Han pasado",
        }
        Counter._id_counter += 1
        self.uid = f"martin_counter_{Counter._id_counter}"

    def render(self):
        import json as _json

        base = (
            "display:inline-flex;align-items:center;gap:8px;"
            "font-variant-numeric:tabular-nums;"
            "color:var(--text);font-weight:700"
        )
        inline = self._resolve_props(base)
        payload = {
            "mode": self.mode,
            "format": self.format,
            "to": self.to,
            "from": self.from_,
            "prefix": self.prefix,
            "suffix": self.suffix,
            "completed_text": self.completed_text,
            "tick": self.tick,
            "labels": self.labels,
        }
        return (
            f'<span id="{self.uid}" data-martin-counter="1" style="{inline}">'
            f'{self.prefix}{self.completed_text}{self.suffix}'
            f"</span>"
            f"<script>(function(){{"
            f"var el=document.getElementById({_json.dumps(self.uid)});"
            f"if(!el||el.dataset.counterBound)return;"
            f"el.dataset.counterBound='1';"
            f"var cfg={_json.dumps(payload, ensure_ascii=False)};"
            f"function parseDate(value){{"
            f"  if(!value)return null;"
            f"  var parsed=new Date(value);"
            f"  return isNaN(parsed.getTime())?null:parsed;"
            f"}}"
            f"function pad(n){{n=Math.max(0,Math.floor(n||0));return n<10?'0'+n:String(n);}}"
            f"function splitParts(totalMs){{"
            f"  var total=Math.max(0,Math.floor(totalMs/1000));"
            f"  var days=Math.floor(total/86400);"
            f"  var hours=Math.floor((total%86400)/3600);"
            f"  var minutes=Math.floor((total%3600)/60);"
            f"  var seconds=total%60;"
            f"  return {{days:days,hours:hours,minutes:minutes,seconds:seconds}};"
            f"}}"
            f"function human(parts,labels,prefix){{"
            f"  var units=[];"
            f"  if(parts.days)units.push(parts.days+' '+(parts.days===1?labels.day:labels.days));"
            f"  if(parts.hours)units.push(parts.hours+' '+(parts.hours===1?labels.hour:labels.hours));"
            f"  if(parts.minutes)units.push(parts.minutes+' '+(parts.minutes===1?labels.minute:labels.minutes));"
            f"  if(parts.seconds||!units.length)units.push(parts.seconds+' '+(parts.seconds===1?labels.second:labels.seconds));"
            f"  return (prefix?prefix+' ':'')+units.slice(0,2).join(' ');"
            f"}}"
            f"function formatText(diffMs){{"
            f"  var parts=splitParts(diffMs);"
            f"  if(cfg.format==='clock')return pad(parts.hours+(parts.days*24))+':'+pad(parts.minutes)+':'+pad(parts.seconds);"
            f"  if(cfg.format==='human'){{"
            f"    var marker=(cfg.mode==='countup')?cfg.labels.elapsed:cfg.labels.remaining;"
            f"    return human(parts,cfg.labels,marker);"
            f"  }}"
            f"  return parts.days+'d '+pad(parts.hours)+'h '+pad(parts.minutes)+'m '+pad(parts.seconds)+'s';"
            f"}}"
            f"function render(){{"
            f"  var now=new Date();"
            f"  var target=parseDate(cfg.to);"
            f"  var source=parseDate(cfg.from)||now;"
            f"  var diff=0;"
            f"  if(cfg.mode==='countup')diff=Math.max(0,now.getTime()-source.getTime());"
            f"  else if(target)diff=target.getTime()-now.getTime();"
            f"  else diff=0;"
            f"  if(diff<=0&&(cfg.mode==='countdown'||cfg.mode==='remaining')){{"
            f"    el.textContent=(cfg.prefix||'')+(cfg.completed_text||'Ahora')+(cfg.suffix||'');"
            f"    return;"
            f"  }}"
            f"  el.textContent=(cfg.prefix||'')+formatText(diff)+(cfg.suffix||'');"
            f"}}"
            f"render();"
            f"var timer=window.setInterval(render,Math.max(250,parseInt(cfg.tick||1000,10)||1000));"
            f"window.addEventListener('beforeunload',function(){{clearInterval(timer);}});"
            f"}})();</script>"
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

"""
Martin — SafeArea Widget

Replica el comportamiento de SafeArea de Flutter:
detecta el dispositivo, notch/Dynamic Island, barras del sistema
y aplica padding automático usando CSS env(safe-area-inset-*).
"""

from ..widget import Widget


class SafeArea(Widget):
    """
    Envuelve contenido respetando las zonas no seguras del dispositivo:
    notch, Dynamic Island, barra de estado, barra de navegación inferior,
    esquinas redondeadas, etc.

    Requiere que el viewport tenga ``viewport-fit=cover`` — Martin lo
    añade automáticamente al meta viewport cuando detecta un SafeArea
    en la página (ver app.py).

    Uso básico — proteger todo el contenido:
        SafeArea(
            children=[MiContenido()],
        )

    Solo lados específicos:
        SafeArea(top=True, bottom=True, left=False, right=False,
                 children=[NavBar(...)])

    Con padding adicional encima del safe-area:
        SafeArea(top=True, extra_top=16, children=[...])

    Como wrapper de página completa:
        SafeArea(
            full=True,
            children=[Column([...])]
        )

    Obtener las medidas desde JS (para animaciones, etc.):
        SafeArea(on_ready="miCallback(insets)")
        # insets = { top, bottom, left, right, hasNotch,
        #            deviceType, viewportWidth, viewportHeight }

    Parámetros:
        top           bool    aplica inset superior (default: True)
        bottom        bool    aplica inset inferior (default: True)
        left          bool    aplica inset izquierdo (default: True)
        right         bool    aplica inset derecho (default: True)
        extra_top     int     padding extra sobre el inset top (px)
        extra_bottom  int     padding extra sobre el inset bottom (px)
        extra_left    int     padding extra sobre el inset left (px)
        extra_right   int     padding extra sobre el inset right (px)
        min_top       int     padding mínimo top aunque no haya notch (px)
        min_bottom    int     padding mínimo bottom (px)
        full          bool    ocupa 100vw × 100dvh (útil como root)
        tag           str     elemento HTML (default: "div")
        on_ready      str     JS llamado con el objeto insets cuando se calcula
        debug         bool    muestra overlay con las medidas (dev only)
        child         Widget  hijo único
        children      list    lista de hijos
        id            str     id del elemento
        class_name    str     clase CSS adicional
    """

    _id_counter = 0

    def __init__(
        self,
        top=True,
        bottom=True,
        left=True,
        right=True,
        extra_top=0,
        extra_bottom=0,
        extra_left=0,
        extra_right=0,
        min_top=0,
        min_bottom=0,
        full=False,
        tag="div",
        on_ready=None,
        debug=False,
        child=None,
        children=None,
        id=None,
        class_name=None,
        **kwargs,
    ):
        self._props = Widget._extract_props(kwargs)
        self.top = top
        self.bottom = bottom
        self.left = left
        self.right = right
        self.extra_top = extra_top
        self.extra_bottom = extra_bottom
        self.extra_left = extra_left
        self.extra_right = extra_right
        self.min_top = min_top
        self.min_bottom = min_bottom
        self.full = full
        self.tag = tag
        self.on_ready = on_ready
        self.debug = debug
        self.class_name = class_name
        if child is not None and children is None:
            children = [child]
        self.children = children or []
        SafeArea._id_counter += 1
        self.uid = id or f"sa_{SafeArea._id_counter}"

    # ── CSS env() helpers ────────────────────────────────────────────────────

    def _inset_css(self):
        """
        Construye el padding CSS usando env(safe-area-inset-*) con fallback a 0px.
        El extra padding se suma usando calc().
        El min_* garantiza un mínimo aunque el dispositivo no tenga notch.
        """

        def _side(use, inset_name, extra, minimum):
            if not use:
                return f"{extra}px" if extra else "0px"
            base = f"env({inset_name}, 0px)"
            parts = [base]
            if extra:
                parts.append(f"{extra}px")
            css = f"calc({' + '.join(parts)})" if len(parts) > 1 else base
            if minimum:
                css = f"max({minimum}px, {css})"
            return css

        pt = _side(self.top, "safe-area-inset-top", self.extra_top, self.min_top)
        pb = _side(
            self.bottom, "safe-area-inset-bottom", self.extra_bottom, self.min_bottom
        )
        pl = _side(self.left, "safe-area-inset-left", self.extra_left, 0)
        pr = _side(self.right, "safe-area-inset-right", self.extra_right, 0)

        return (
            f"padding-top:{pt};padding-bottom:{pb};padding-left:{pl};padding-right:{pr}"
        )

    # ── JavaScript de detección ──────────────────────────────────────────────

    def _build_js(self):
        uid = self.uid
        on_ready_call = f"({self.on_ready})(insets);" if self.on_ready else ""
        debug_js = (
            f"""
            var dbg = document.getElementById('{uid}_debug');
            if (dbg) {{
                dbg.innerHTML =
                    '<b>SafeArea</b><br>' +
                    'top: ' + insets.top + 'px<br>' +
                    'bottom: ' + insets.bottom + 'px<br>' +
                    'left: ' + insets.left + 'px<br>' +
                    'right: ' + insets.right + 'px<br>' +
                    'notch: ' + insets.hasNotch + '<br>' +
                    'device: ' + insets.deviceType + '<br>' +
                    (insets.dynamicIsland ? 'Dynamic Island<br>' : '') +
                    insets.viewportWidth + '×' + insets.viewportHeight;
            }}
            """
            if self.debug
            else ""
        )

        return f"""
<script>
(function() {{
    var uid = '{uid}';
    var el  = document.getElementById(uid);
    if (!el) return;

    function getInsets() {{
        // Leer las CSS env() variables reales usando un elemento temporal
        var probe = document.createElement('div');
        probe.style.cssText = [
            'position:fixed',
            'top:env(safe-area-inset-top,0px)',
            'bottom:env(safe-area-inset-bottom,0px)',
            'left:env(safe-area-inset-left,0px)',
            'right:env(safe-area-inset-right,0px)',
            'pointer-events:none',
            'visibility:hidden',
            'z-index:-1'
        ].join(';');
        document.body.appendChild(probe);
        var cs  = window.getComputedStyle(probe);
        var top    = parseFloat(cs.top)    || 0;
        var bottom = parseFloat(cs.bottom) || 0;
        var left   = parseFloat(cs.left)   || 0;
        var right  = parseFloat(cs.right)  || 0;
        document.body.removeChild(probe);

        // Detección de dispositivo
        var ua = navigator.userAgent || '';
        var isIOS     = /iPad|iPhone|iPod/.test(ua) || (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1);
        var isAndroid = /Android/.test(ua);
        var isMobile  = isIOS || isAndroid || window.innerWidth < 768;
        var isTablet  = isMobile && window.innerWidth >= 600;

        var deviceType = 'desktop';
        if (isTablet)       deviceType = 'tablet';
        else if (isMobile)  deviceType = 'mobile';

        // Detección de notch / Dynamic Island
        var hasNotch      = top > 20;
        var dynamicIsland = isIOS && top >= 54;  // DI comienza en ~54px

        // Dimensiones de viewport (dvh si disponible)
        var vw = window.innerWidth;
        var vh = window.innerHeight;

        // Orientación
        var orientation = (screen.orientation && screen.orientation.type)
            || (window.innerWidth > window.innerHeight ? 'landscape' : 'portrait');

        return {{
            top:           top,
            bottom:        bottom,
            left:          left,
            right:         right,
            hasNotch:      hasNotch,
            dynamicIsland: dynamicIsland,
            deviceType:    deviceType,
            isIOS:         isIOS,
            isAndroid:     isAndroid,
            isMobile:      isMobile,
            isTablet:      isTablet,
            orientation:   orientation,
            viewportWidth: vw,
            viewportHeight: vh,
            pixelRatio:    window.devicePixelRatio || 1,
        }};
    }}

    function apply() {{
        var insets = getInsets();

        // Exponer globalmente como martin.safeArea para JS del usuario
        if (!window.martin) window.martin = {{}};
        window.martin.safeArea = insets;
        window.martin.safeArea.elementId = uid;

        // Aplicar como CSS custom properties en el elemento
        el.style.setProperty('--sa-top',    insets.top    + 'px');
        el.style.setProperty('--sa-bottom', insets.bottom + 'px');
        el.style.setProperty('--sa-left',   insets.left   + 'px');
        el.style.setProperty('--sa-right',  insets.right  + 'px');

        // También en :root para acceso global
        document.documentElement.style.setProperty('--sa-top',    insets.top    + 'px');
        document.documentElement.style.setProperty('--sa-bottom', insets.bottom + 'px');
        document.documentElement.style.setProperty('--sa-left',   insets.left   + 'px');
        document.documentElement.style.setProperty('--sa-right',  insets.right  + 'px');

        // data-* para CSS attribute selectors
        el.dataset.deviceType  = insets.deviceType;
        el.dataset.hasNotch    = insets.hasNotch;
        el.dataset.orientation = insets.orientation;

        // Callback del usuario
        {on_ready_call}

        // Debug overlay
        {debug_js}
    }}

    // Ejecutar al cargar y al cambiar orientación / resize
    if (document.readyState === 'loading') {{
        document.addEventListener('DOMContentLoaded', apply);
    }} else {{
        apply();
    }}

    // Recalcular en resize y orientationchange (el notch puede variar en landscape)
    var _saTimer;
    function _saDebounce() {{
        clearTimeout(_saTimer);
        _saTimer = setTimeout(apply, 150);
    }}
    window.addEventListener('resize',            _saDebounce);
    window.addEventListener('orientationchange', _saDebounce);
}})();
</script>
"""

    # ── Debug overlay ─────────────────────────────────────────────────────────

    def _debug_overlay(self):
        if not self.debug:
            return ""
        return (
            f'<div id="{self.uid}_debug" style="'
            "position:fixed;bottom:80px;right:12px;z-index:99999;"
            "background:rgba(0,0,0,0.82);color:#fff;font-size:11px;"
            "font-family:monospace;padding:10px 14px;border-radius:10px;"
            "line-height:1.7;pointer-events:none;backdrop-filter:blur(8px);"
            'border:1px solid rgba(255,255,255,0.15)">'
            "calculando..."
            "</div>"
        )

    # ── render ───────────────────────────────────────────────────────────────

    def render(self):
        uid = self.uid
        inset_css = self._inset_css()

        base_css = inset_css + ";box-sizing:border-box"
        if self.full:
            base_css += ";width:100%;min-height:100dvh"

        inline = self._resolve_props(base_css)
        inner = self._render_children(self.children)

        attrs = self._attrs(
            style=inline,
            id=uid,
            **{"class": self.class_name},
        )

        html = (
            f"<{self.tag}{attrs}>"
            + inner
            + f"</{self.tag}>"
            + self._debug_overlay()
            + self._build_js()
        )
        return html
