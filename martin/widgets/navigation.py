"""
Martin — Navigation Widgets

Widgets que estructuran la navegación de la página.

    NavBar           — barra de navegación superior sticky
    SideMenu         — menú lateral para documentación o paneles
    Footer           — pie de página con zonas left / center / right
    LanguageSelector — selector de idioma para navbar/footer con banderas
    Breadcrumb       — ruta de navegación jerárquica
    Tabs             — navegación por pestañas con contenido intercambiable
"""

import json as _json

from ..i18n import describe_locale, discover_locale_codes, normalize_locale
from ..widget import Widget
from .._context import get_current_path
from .._routing import paths_match


# =============================================================================
# NavBar
# =============================================================================


class NavBar(Widget):
    """
    Barra de navegación superior. Un pilar de cualquier sitio.

        NavBar(
            brand=Heading("MiSitio", level=3),
            links=[
                Link("Inicio",    href="/"),
                Link("Productos", href="/productos"),
                Link("Contacto",  href="/contacto"),
            ],
            actions=[
                Button("Login",    href="/login",    variant="ghost"),
                Button("Registro", href="/registro"),
            ],
        )

    Parámetros:
        brand      Widget   logo o nombre del sitio (izquierda)
        links      list     lista de Link o cualquier widget (centro)
        actions    list     botones o widgets (derecha)
        sticky     bool     fija el header al scroll (default: True)
        bordered   bool     borde inferior (default: True)
    """

    _id_counter = 0

    def __init__(
        self, brand=None, links=None, actions=None, sticky=True, bordered=True, **kwargs
    ):
        self._props = Widget._extract_props(kwargs)
        self.brand = brand
        self.links = links or []
        self.actions = actions or []
        self.sticky = sticky
        self.bordered = bordered
        NavBar._id_counter += 1
        self.uid = f"nav_{NavBar._id_counter}"

    def _default_a11y_attrs(self):
        return {"aria-label": "Barra de navegacion"}

    def render(self):
        uid = self.uid
        sticky_css = "position:sticky; top:0; z-index:100; " if self.sticky else ""
        border_css = "border-bottom:1px solid var(--border); " if self.bordered else ""
        base = (
            f"{sticky_css}{border_css}"
            f"background:var(--surface); "
            f"display:flex; align-items:center; "
            f"justify-content:space-between; position:relative; "
            f"padding:0 32px; height:64px; gap:32px; "
            f"max-width:100%; box-sizing:border-box; "
            f"backdrop-filter:blur(12px); "
            f"-webkit-backdrop-filter:blur(12px)"
        )
        inline = self._resolve_props(base)

        # Brand (left)
        brand_html = ""
        if self.brand:
            b = self.brand.render() if isinstance(self.brand, Widget) else self.brand
            brand_html = (
                '<a href="/" aria-label="Inicio" style="flex-shrink:0;text-decoration:none;color:inherit">'
                + b
                + "</a>"
            )

        links_items = "".join(
            (lk.render() if isinstance(lk, Widget) else str(lk))
            for lk in self.links
        )
        actions_items = "".join(
            (a.render() if isinstance(a, Widget) else str(a)) for a in self.actions
        )
        has_menu = bool(links_items or actions_items)

        links_html = ""
        if links_items:
            links_html = (
                f'<nav id="{uid}_links" aria-label="Principal" style="display:flex;align-items:center;gap:24px;'
                f"min-width:0;overflow-x:auto;overflow-y:hidden;white-space:nowrap;justify-content:center\">"
                f"{links_items}</nav>"
            )

        actions_html = ""
        if actions_items:
            actions_html = (
                f'<div id="{uid}_actions" style="display:flex;align-items:center;'
                f'gap:8px;flex-shrink:0">{actions_items}</div>'
            )

        menu_html = ""
        burger_html = ""
        if has_menu:
            burger_html = (
                f'<button id="{uid}_burger" type="button" aria-label="Abrir menu" '
                f'aria-controls="{uid}_menu" aria-expanded="false" '
                f'style="display:none;align-items:center;justify-content:center;'
                f'width:38px;height:38px;border:1px solid var(--border);border-radius:10px;'
                f'background:var(--surface);color:var(--text);cursor:pointer;flex-shrink:0;font-size:18px">☰</button>'
            )
            menu_html = (
                f'<div id="{uid}_menu" style="display:flex;align-items:center;gap:18px;'
                f'position:absolute;left:32px;right:32px;top:0;height:100%;min-width:0;pointer-events:none">{links_html}{actions_html}</div>'
            )

        css = (
            f"<style>"
            f"#{uid}{{overflow-x:clip}}"
            f"#{uid}_links::-webkit-scrollbar{{display:none}}"
            f"#{uid}_menu{{box-sizing:border-box}}"
            f"#{uid}_links{{position:absolute;left:50%;transform:translateX(-50%);pointer-events:auto}}"
            f"#{uid}_actions{{margin-left:auto;pointer-events:auto}}"
            f"@media(max-width:840px){{"
            f"#{uid}{{height:64px!important;min-height:64px;padding:0 14px!important;gap:10px!important;"
            f"justify-content:space-between;position:relative;z-index:120}}"
            f"#{uid}_burger{{display:inline-flex!important}}"
            f"#{uid}_menu{{display:none!important;position:absolute;top:calc(100% + 8px);left:10px;right:10px;"
            f"background:color-mix(in srgb,var(--bg,#0b1020) 88%, var(--surface,#111827) 12%);"
            f"backdrop-filter:none!important;-webkit-backdrop-filter:none!important;"
            f"border:1px solid color-mix(in srgb,var(--border,#334155) 85%, #000 15%);"
            f"border-radius:12px;box-shadow:0 14px 36px rgba(0,0,0,.42);"
            f"padding:12px;flex-direction:column;align-items:stretch;gap:12px;z-index:140}}"
            f"#{uid}[data-mobile-open='1'] #{uid}_menu{{display:flex!important}}"
            f"#{uid}_links{{display:flex!important;flex-direction:column;align-items:stretch;flex:none!important;"
            f"justify-content:flex-start!important;white-space:normal!important;overflow:visible!important;gap:6px!important;"
            f"position:static!important;left:auto!important;transform:none!important}}"
            f"#{uid}_links > *{{display:block;width:100%}}"
            f"#{uid}_menu a{{display:block;color:var(--text)!important;padding:10px 10px;border-radius:8px}}"
            f"#{uid}_actions{{display:flex;flex-direction:column;align-items:stretch;justify-content:flex-start;gap:8px}}"
            f"#{uid}_actions > *{{width:100%}}"
            f"}}"
            f"</style>"
        )

        js = ""
        if has_menu:
            js = (
                f"<script>(function(){{"
                f'var root=document.getElementById("{uid}");'
                f'var btn=document.getElementById("{uid}_burger");'
                f"if(!root||!btn||root.dataset.martinNavBound)return;"
                f'root.dataset.martinNavBound="1";'
                f"function isMobile(){{return window.matchMedia&&window.matchMedia('(max-width:840px)').matches;}}"
                f"function closeMenu(){{root.setAttribute('data-mobile-open','0');btn.setAttribute('aria-expanded','false');}}"
                f"function toggleMenu(){{"
                f"  if(!isMobile())return;"
                f"  var open=root.getAttribute('data-mobile-open')==='1';"
                f"  if(open)closeMenu();"
                f"  else{{root.setAttribute('data-mobile-open','1');btn.setAttribute('aria-expanded','true');}}"
                f"}}"
                f"btn.addEventListener('click',function(e){{e.stopPropagation();toggleMenu();}});"
                f"document.addEventListener('click',function(e){{if(!isMobile())return;if(!root.contains(e.target))closeMenu();}});"
                f"document.addEventListener('keydown',function(e){{if(e.key==='Escape')closeMenu();}});"
                f"window.addEventListener('resize',function(){{if(!isMobile())closeMenu();}});"
                f"}})();</script>"
            )

        return f'{css}<header id="{uid}" data-mobile-open="0" role="banner" style="{inline}">{brand_html}{menu_html}{burger_html}</header>{js}'


# =============================================================================
# Footer
# =============================================================================


class Footer(Widget):
    """
    Pie de página. Cierre natural de cualquier página.

        Footer(
            left=Text("© 2025 MiEmpresa"),
            right=Row([
                Link("Privacidad", href="/privacidad"),
                Link("Términos",   href="/terminos"),
            ], gap=16),
        )

        # Solo texto centrado:
        Footer(center=Text("Hecho con Martin Framework"))

    Parámetros:
        left     Widget   contenido izquierdo
        center   Widget   contenido central
        right    Widget   contenido derecho
        bordered bool     borde superior (default: True)
    """

    def __init__(self, left=None, center=None, right=None, bordered=True, **kwargs):
        self._props = Widget._extract_props(kwargs)
        self.left = left
        self.center = center
        self.right = right
        self.bordered = bordered

    def render(self):
        border_css = "border-top:1px solid var(--border); " if self.bordered else ""
        base = (
            f"{border_css}padding:24px 32px; "
            f"display:flex; align-items:center; justify-content:space-between; "
            f"background:var(--surface); gap:16px; flex-wrap:wrap"
        )
        inline = self._resolve_props(base)

        def _r(w):
            return (w.render() if isinstance(w, Widget) else str(w)) if w else ""

        left_html = f"<div>{_r(self.left)}</div>" if self.left else "<div></div>"
        center_html = (
            f'<div style="text-align:center">{_r(self.center)}</div>'
            if self.center
            else ""
        )
        right_html = f"<div>{_r(self.right)}</div>" if self.right else "<div></div>"

        return f'<footer style="{inline}">{left_html}{center_html}{right_html}</footer>'


# =============================================================================
# LanguageSelector
# =============================================================================


class LanguageSelector(Widget):
    """
    Selector de idioma con búsqueda, banderas y persistencia en cliente.

        LanguageSelector(locales=["es_ES", "en_US"], value="es_ES")
        LanguageSelector(path="locales", translations=load_locale_catalogs("locales"))

    Puede colocarse directamente en NavBar, Footer o cualquier layout.
    """

    _id_counter = 0

    def __init__(
        self,
        locales=None,
        value=None,
        path=None,
        translations=None,
        default_locale=None,
        fallback_locale=None,
        storage_key="martin.locale",
        query_param="lang",
        update_url=True,
        persist=True,
        search=True,
        name=None,
        id=None,
        placeholder="Idioma",
        on_change=None,
        **kwargs,
    ):
        self._props = Widget._extract_props(kwargs)
        self.locales = locales or []
        self.value = normalize_locale(value)
        self.path = path
        self.translations = translations or {}
        self.default_locale = normalize_locale(default_locale or self.value)
        self.fallback_locale = normalize_locale(fallback_locale or "")
        self.storage_key = storage_key
        self.query_param = query_param
        self.update_url = update_url
        self.persist = persist
        self.search = search
        self.name = name
        self.placeholder = placeholder
        self.on_change = on_change or ""
        LanguageSelector._id_counter += 1
        self.uid = id or f"lang_select_{LanguageSelector._id_counter}"

    def _resolved_locales(self):
        locales = discover_locale_codes(
            path=self.path,
            locales=self.locales,
            messages=self.translations,
        )
        if not locales and self.value:
            locales = [self.value]
        if not locales:
            locales = ["es_ES", "en_US"]
        return locales

    def _default_a11y_attrs(self):
        return {"aria-label": self.placeholder or "Selector de idioma"}

    def render(self):
        uid = self.uid
        extra = self._resolve_props()
        locales = self._resolved_locales()
        option_meta = [describe_locale(code) for code in locales]
        selected = next(
            (
                item
                for item in option_meta
                if item["code"] == (self.value or self.default_locale)
            ),
            option_meta[0],
        )

        translations_js = _json.dumps(self.translations, ensure_ascii=False)
        meta_js = _json.dumps({item["code"]: item for item in option_meta}, ensure_ascii=False)
        default_locale_js = _json.dumps(self.default_locale or selected["code"])
        fallback_locale_js = _json.dumps(self.fallback_locale or "")
        storage_key_js = _json.dumps(self.storage_key)
        query_param_js = _json.dumps(self.query_param)
        update_url_js = "true" if self.update_url else "false"
        persist_js = "true" if self.persist else "false"
        on_change_js = _json.dumps(self.on_change)
        search_display = "block" if self.search else "none"
        name_attr = f' name="{self.name}"' if self.name else ""
        hidden_input = f'<input type="hidden" id="{uid}_val" value="{selected["code"]}"{name_attr}>'

        options_html = "".join(
            (
                f'<div class="mls-opt" '
                f'data-locale="{item["code"]}" '
                f'data-label="{item["label"]}" '
                f'data-flag="{item["flag"]}" '
                f'data-flag-url="{item.get("flag_url", "")}" '
                f'data-country="{item.get("country", "")}" '
                f'data-dir="{item["dir"]}" '
                f'role="option" '
                f'aria-selected="{"true" if item["code"] == selected["code"] else "false"}" '
                f'style="display:flex;align-items:center;gap:10px;padding:10px 14px;'
                f'cursor:pointer;border-radius:8px;transition:background .12s">'
                f'<span class="mls-flagbox" aria-hidden="true" style="display:inline-flex;align-items:center;justify-content:center;'
                f'width:20px;height:15px;flex:0 0 20px;border-radius:3px;overflow:hidden;'
                f'border:1px solid color-mix(in srgb,var(--border,#334155) 80%, transparent);background:var(--surface-2,#1f2937)">'
                f'<img src="{item.get("flag_url", "")}" alt="" loading="lazy" referrerpolicy="no-referrer" '
                f'onerror="this.style.display=\'none\';this.nextElementSibling.style.display=\'inline-flex\'" '
                f'style="width:100%;height:100%;object-fit:cover;display:block">'
                f'<span class="mls-flag-fallback" style="display:none;align-items:center;justify-content:center;'
                f'width:100%;height:100%;font-size:9px;font-weight:700;letter-spacing:.04em;color:var(--text-muted,var(--text))">'
                f'{item.get("country", "") or item["flag"]}</span></span>'
                f'<span style="color:var(--text);font-size:14px">{item["label"]}</span>'
                f"</div>"
            )
            for item in option_meta
        )

        wrapper_style = f"position:relative;width:100%;min-width:220px;font-size:14px;{extra}"

        return (
            f"<style>"
            f"#{uid}_list .mls-opt:hover{{background:var(--surface-2)}}"
            f'#{uid}_list .mls-opt[aria-selected="true"]{{background:rgba(99,102,241,0.15);}}'
            f"#{uid}_btn .mls-flagbox{{display:inline-flex;align-items:center;justify-content:center;width:20px;height:15px;flex:0 0 20px;"
            f"border-radius:3px;overflow:hidden;border:1px solid color-mix(in srgb,var(--border,#334155) 80%, transparent);"
            f"background:var(--surface-2,#1f2937)}}"
            f"#{uid}_btn .mls-flagbox img{{width:100%;height:100%;object-fit:cover;display:block}}"
            f"#{uid}_btn .mls-flag-fallback{{display:none;align-items:center;justify-content:center;width:100%;height:100%;"
            f"font-size:9px;font-weight:700;letter-spacing:.04em;color:var(--text-muted,var(--text))}}"
            f"</style>"
            f'<div id="{uid}_wrap" style="{wrapper_style}">'
            f"{hidden_input}"
            f'<div id="{uid}_btn" role="combobox" aria-haspopup="listbox" aria-expanded="false" '
            f'aria-controls="{uid}_list" tabindex="0" '
            f'style="display:flex;align-items:center;justify-content:space-between;gap:10px;'
            f'padding:8px 14px;border:1px solid var(--border-input,var(--border));border-radius:8px;'
            f'background:var(--input-bg,var(--surface));cursor:pointer;user-select:none;transition:border-color .2s">'
            f'<span id="{uid}_label" style="display:flex;align-items:center;gap:10px;min-width:0">'
            f'<span id="{uid}_flagbox" class="mls-flagbox" aria-hidden="true">'
            f'<img id="{uid}_flag_img" src="{selected.get("flag_url", "")}" alt="" loading="lazy" referrerpolicy="no-referrer" '
            f'onerror="this.style.display=\'none\';document.getElementById(\'{uid}_flag_fallback\').style.display=\'inline-flex\'">'
            f'<span id="{uid}_flag_fallback" class="mls-flag-fallback">{selected.get("country", "") or selected["flag"]}</span>'
            f"</span>"
            f'<span id="{uid}_text" style="color:var(--input-color,var(--text));font-size:14px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">{selected["label"]}</span>'
            f"</span>"
            f'<svg id="{uid}_arrow" width="12" height="12" viewBox="0 0 12 12" '
            f'style="flex-shrink:0;transition:transform .2s;opacity:0.55">'
            f'<path d="M2 4l4 4 4-4" stroke="currentColor" stroke-width="1.5" fill="none" stroke-linecap="round"/>'
            f"</svg>"
            f"</div>"
            f'<div id="{uid}_drop" style="display:none;position:absolute;top:calc(100% + 6px);left:0;right:0;'
            f'z-index:10030;border:1px solid var(--border-input,var(--border));border-radius:10px;'
            f'box-shadow:0 12px 40px rgba(0,0,0,0.25);overflow:hidden;background:var(--dropdown-bg,var(--surface))">'
            f'<div style="display:{search_display};padding:8px 8px 6px;border-bottom:1px solid var(--border)">'
            f'<input id="{uid}_search" type="text" placeholder="Buscar idioma..." '
            f'style="width:100%;padding:7px 10px;border:1px solid var(--border-input,var(--border));'
            f'border-radius:6px;font-size:13px;outline:none;box-sizing:border-box;'
            f'background:var(--input-bg,var(--surface));color:var(--input-color,var(--text))">'
            f"</div>"
            f'<div id="{uid}_list" role="listbox" aria-label="Idiomas disponibles" style="max-height:260px;overflow-y:auto;padding:6px">'
            f"{options_html}"
            f"</div>"
            f"</div>"
            f"</div>"
            f"<script>(function(){{"
            f"var uid={_json.dumps(uid)};"
            f"var meta={meta_js};"
            f"var translations={translations_js};"
            f"var defaultLocale={default_locale_js};"
            f"var fallbackLocale={fallback_locale_js};"
            f"var storageKey={storage_key_js};"
            f"var queryParam={query_param_js};"
            f"var updateUrl={update_url_js};"
            f"var persist={persist_js};"
            f"var onChange={on_change_js};"
            f"var root=document.getElementById(uid+'_wrap');"
            f"var btn=document.getElementById(uid+'_btn');"
            f"var drop=document.getElementById(uid+'_drop');"
            f"var list=document.getElementById(uid+'_list');"
            f"var search=document.getElementById(uid+'_search');"
            f"var input=document.getElementById(uid+'_val');"
            f"var text=document.getElementById(uid+'_text');"
            f"var flagImg=document.getElementById(uid+'_flag_img');"
            f"var flagFallback=document.getElementById(uid+'_flag_fallback');"
            f"var arrow=document.getElementById(uid+'_arrow');"
            f"if(!root||!btn||!drop||!list||root.dataset.martinLangBound)return;"
            f"root.dataset.martinLangBound='1';"
            f"window.MartinI18n=window.MartinI18n||{{}};"
            f"if(!window.MartinI18n.messages)window.MartinI18n.messages={{}};"
            f"Object.keys(translations||{{}}).forEach(function(loc){{window.MartinI18n.messages[loc]=translations[loc];}});"
            f"window.MartinI18n.defaultLocale=window.MartinI18n.defaultLocale||defaultLocale;"
            f"window.MartinI18n.fallbackLocale=window.MartinI18n.fallbackLocale||fallbackLocale;"
            f"window.MartinI18n._deepGet=function(obj,key){{"
            f"  var cur=obj||{{}};"
            f"  String(key||'').split('.').forEach(function(part){{cur=(cur&&typeof cur==='object'&&part in cur)?cur[part]:undefined;}});"
            f"  return cur;"
            f"}};"
            f"window.MartinI18n._candidates=function(locale){{"
            f"  var raw=String(locale||'').trim().replace(/-/g,'_');"
            f"  if(!raw)return[];"
            f"  var out=[raw];"
            f"  var base=raw.split('_')[0];"
            f"  if(base&&out.indexOf(base)===-1)out.push(base);"
            f"  return out;"
            f"}};"
            f"window.MartinI18n.t=function(key,locale,fallback){{"
            f"  var candidates=[];"
            f"  window.MartinI18n._candidates(locale).forEach(function(loc){{if(candidates.indexOf(loc)===-1)candidates.push(loc);}});"
            f"  window.MartinI18n._candidates(window.MartinI18n.fallbackLocale).forEach(function(loc){{if(candidates.indexOf(loc)===-1)candidates.push(loc);}});"
            f"  window.MartinI18n._candidates(window.MartinI18n.defaultLocale).forEach(function(loc){{if(candidates.indexOf(loc)===-1)candidates.push(loc);}});"
            f"  for(var i=0;i<candidates.length;i++){{"
            f"    var hit=window.MartinI18n._deepGet(window.MartinI18n.messages[candidates[i]], key);"
            f"    if(hit!==undefined&&hit!==null)return String(hit);"
            f"  }}"
            f"  return fallback!==undefined?String(fallback):String(key||'');"
            f"}};"
            f"window.MartinI18n.decorateInternalLinks=function(locale){{"
            f"  var normalized=String(locale||'').replace(/-/g,'_');"
            f"  document.querySelectorAll('a[href]').forEach(function(el){{"
            f"    var raw=String(el.getAttribute('href')||'').trim();"
            f"    if(!raw)return;"
            f"    if(raw[0]==='#')return;"
            f"    if(/^mailto:|^tel:|^javascript:/i.test(raw))return;"
            f"    if(/^https?:\\/\\//i.test(raw))return;"
            f"    if(/^\\/assets\\//i.test(raw))return;"
            f"    if(/\\.(png|jpe?g|svg|webp|gif|ico|css|js|pdf|zip)(\\?|#|$)/i.test(raw))return;"
            f"    try{{"
            f"      var url=new URL(raw, window.location.origin);"
            f"      if(url.origin!==window.location.origin)return;"
            f"      url.searchParams.set(queryParam, normalized);"
            f"      var finalHref=url.pathname + (url.search||'') + (url.hash||'');"
            f"      el.setAttribute('href', finalHref);"
            f"    }}catch(_linkErr){{}}"
            f"  }});"
            f"}};"
            f"window.MartinI18n.applyLocale=function(locale){{"
            f"  var normalized=String(locale||window.MartinI18n.defaultLocale||'').replace(/-/g,'_');"
            f"  var info=meta[normalized]||{{dir:(/^ar|^he|^fa|^ur|^ps|^dv/.test(normalized)?'rtl':'ltr')}};"
            f"  document.documentElement.lang=normalized.replace(/_/g,'-');"
            f"  document.documentElement.setAttribute('dir', info.dir||'ltr');"
            f"  document.querySelectorAll('[data-i18n]').forEach(function(el){{"
            f"    el.textContent=window.MartinI18n.t(el.getAttribute('data-i18n'), normalized, el.textContent);"
            f"  }});"
            f"  document.querySelectorAll('[data-i18n-placeholder]').forEach(function(el){{"
            f"    el.setAttribute('placeholder', window.MartinI18n.t(el.getAttribute('data-i18n-placeholder'), normalized, el.getAttribute('placeholder')||''));"
            f"  }});"
            f"  document.querySelectorAll('[data-i18n-title]').forEach(function(el){{"
            f"    el.setAttribute('title', window.MartinI18n.t(el.getAttribute('data-i18n-title'), normalized, el.getAttribute('title')||''));"
            f"  }});"
            f"  document.querySelectorAll('[data-i18n-aria-label]').forEach(function(el){{"
            f"    el.setAttribute('aria-label', window.MartinI18n.t(el.getAttribute('data-i18n-aria-label'), normalized, el.getAttribute('aria-label')||''));"
            f"  }});"
            f"  if(typeof window.MartinI18n.decorateInternalLinks==='function')window.MartinI18n.decorateInternalLinks(normalized);"
            f"  window.dispatchEvent(new CustomEvent('martin:locale-change',{{detail:{{locale:normalized,dir:info.dir||'ltr'}}}}));"
            f"}};"
            f"function closeDrop(){{drop.style.display='none';arrow.style.transform='';btn.style.borderColor='';btn.setAttribute('aria-expanded','false');}}"
            f"function openDrop(){{drop.style.display='block';arrow.style.transform='rotate(180deg)';btn.style.borderColor='var(--accent)';btn.setAttribute('aria-expanded','true');if(search){{search.value='';filterOptions('');setTimeout(function(){{search.focus();}},30);}}}}"
            f"function toggleDrop(){{if(drop.style.display==='none'||!drop.style.display)openDrop();else closeDrop();}}"
            f"function filterOptions(query){{"
            f"  var q=String(query||'').toLowerCase();"
            f"  list.querySelectorAll('.mls-opt').forEach(function(opt){{"
            f"    var label=String(opt.getAttribute('data-label')||'').toLowerCase();"
            f"    opt.style.display=label.indexOf(q)!==-1?'flex':'none';"
            f"  }});"
            f"}}"
            f"function applySelection(locale, runI18n){{"
            f"  var info=meta[locale]||meta[defaultLocale]||{{}};"
            f"  input.value=locale;"
            f"  text.textContent=info.label||locale;"
            f"  if(flagImg){{"
            f"    flagImg.style.display='block';"
            f"    flagImg.src=info.flag_url||'';"
            f"  }}"
            f"  if(flagFallback){{"
            f"    flagFallback.textContent=info.country||info.flag||'GL';"
            f"    flagFallback.style.display=(info.flag_url?'none':'inline-flex');"
            f"  }}"
            f"  list.querySelectorAll('.mls-opt').forEach(function(opt){{"
            f"    var active=opt.getAttribute('data-locale')===locale;"
            f"    opt.setAttribute('aria-selected', active?'true':'false');"
            f"  }});"
            f"  if(persist&&window.localStorage){{try{{localStorage.setItem(storageKey, locale);}}catch(_e){{}}}}"
            f"  if(updateUrl&&window.history&&window.location){{"
            f"    var url=new URL(window.location.href);"
            f"    url.searchParams.set(queryParam, locale);"
            f"    window.history.replaceState(null,'',url.toString());"
            f"  }}"
            f"  if(runI18n&&window.MartinI18n&&typeof window.MartinI18n.applyLocale==='function')window.MartinI18n.applyLocale(locale);"
            f"  if(onChange){{try{{new Function('locale', onChange)(locale);}}catch(_err){{}}}}"
            f"  closeDrop();"
            f"}}"
            f"btn.addEventListener('click',function(e){{e.stopPropagation();toggleDrop();}});"
            f"btn.addEventListener('keydown',function(e){{if(e.key==='Enter'||e.key===' '||e.key==='ArrowDown'){{e.preventDefault();openDrop();}}if(e.key==='Escape')closeDrop();}});"
            f"if(search)search.addEventListener('input',function(){{filterOptions(this.value);}});"
            f"list.querySelectorAll('.mls-opt').forEach(function(opt){{"
            f"  opt.addEventListener('click',function(){{applySelection(opt.getAttribute('data-locale'), true);}});"
            f"}});"
            f"document.addEventListener('click',function(e){{if(!root.contains(e.target))closeDrop();}});"
            f"document.addEventListener('keydown',function(e){{if(e.key==='Escape')closeDrop();}});"
            f"var initial=input.value||defaultLocale;"
            f"if(window.location){{"
            f"  var urlLocale=new URL(window.location.href).searchParams.get(queryParam);"
            f"  if(urlLocale&&meta[String(urlLocale).replace(/-/g,'_')])initial=String(urlLocale).replace(/-/g,'_');"
            f"}}"
            f"if(persist&&window.localStorage){{"
            f"  try{{var stored=localStorage.getItem(storageKey);if(stored&&meta[String(stored).replace(/-/g,'_')])initial=String(stored).replace(/-/g,'_');}}catch(_e){{}}"
            f"}}"
            f"function _initLS(){{applySelection(initial, true);}}"
            f"if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',_initLS);else _initLS();"
            f"}})();</script>"
        )


# =============================================================================
# Breadcrumb
# =============================================================================


class Breadcrumb(Widget):
    """
    Ruta de navegación. Muestra dónde está el usuario en la jerarquía.

        Breadcrumb([
            ("Inicio",    "/"),
            ("Productos", "/productos"),
            ("Zapatillas", None),    # último ítem sin link
        ])

        # O con widgets directos:
        Breadcrumb([Link("Inicio", "/"), Text(" / "), Text("Actual")])

    Separador por defecto: "/"
    """

    def __init__(self, items=None, separator="/", **kwargs):
        self._props = Widget._extract_props(kwargs)
        self.items = items or []
        self.separator = separator

    def render(self):
        base = "display:flex; align-items:center; gap:8px; flex-wrap:wrap"
        inline = self._resolve_props(base)
        sep = (
            f'<span style="color:var(--text-muted);font-size:13px">'
            f"{self.separator}</span>"
        )
        parts = []
        for i, item in enumerate(self.items):
            if isinstance(item, Widget):
                parts.append(item.render())
            elif isinstance(item, (tuple, list)):
                label = item[0]
                href = item[1] if len(item) > 1 else None
                is_last = i == len(self.items) - 1
                if href and not is_last:
                    parts.append(
                        f'<a href="{href}" style="color:var(--accent);'
                        f'font-size:13px;text-decoration:none;">{label}</a>'
                    )
                else:
                    weight = "600" if is_last else "400"
                    parts.append(
                        f'<span style="color:var(--text);font-size:13px;'
                        f'font-weight:{weight}">{label}</span>'
                    )
            else:
                parts.append(
                    f'<span style="font-size:13px;color:var(--text)">{item}</span>'
                )

        html = sep.join(parts)
        return f'<nav aria-label="breadcrumb" style="{inline}">{html}</nav>'


# =============================================================================
# Tabs
# =============================================================================


class Tabs(Widget):
    """
    Navegación por pestañas. Muestra un contenido a la vez.

        Tabs([
            ("General",  Column([Text("Contenido general...")])),
            ("Avanzado", Column([Text("Opciones avanzadas...")])),
            ("Sobre mí", Column([Avatar(initials="JD"), Text("Juan Díaz")])),
        ])

    Cada ítem es una tupla (label, widget_contenido).
    El primer tab está activo por defecto; puedes cambiarlo con `default`.

    Parámetros:
        tabs     list   lista de tuplas (label, contenido)
        default  int    índice del tab activo inicial (default: 0)
    """

    _id_counter = 0

    def __init__(self, tabs=None, default=0, **kwargs):
        self._props = Widget._extract_props(kwargs)
        self.tabs = tabs or []
        self.default = default
        Tabs._id_counter += 1
        self.uid = f"tabs_{Tabs._id_counter}"

    def _default_a11y_attrs(self):
        return {"aria-label": "Pestanas"}

    def render(self):
        uid = self.uid
        extra = self._resolve_props()
        n = len(self.tabs)

        btn_base = (
            "padding:8px 20px; border:none; cursor:pointer; font-size:14px; "
            "font-weight:500; border-radius:8px 8px 0 0; transition:all .2s"
        )
        active_style = (
            "background:var(--surface); color:var(--text); "
            "border-bottom:2px solid var(--accent)"
        )
        inactive_style = (
            "background:transparent; color:var(--text-muted); "
            "border-bottom:2px solid transparent"
        )

        btns = ""
        panels = ""

        for i, (label, content) in enumerate(self.tabs):
            tid = f"{uid}_t{i}"
            pid = f"{uid}_p{i}"
            active = i == self.default

            lbl_html = label.render() if isinstance(label, Widget) else label
            content_html = (
                content.render() if isinstance(content, Widget) else str(content)
            )
            display = "block" if active else "none"

            btns += (
                f'<button id="{tid}" onclick="{uid}_go({i})" '
                f'role="tab" aria-selected="{"true" if active else "false"}" '
                f'aria-controls="{pid}" tabindex="{"0" if active else "-1"}" '
                f'style="{btn_base};{active_style if active else inactive_style}">'
                f"{lbl_html}</button>"
            )
            panels += (
                f'<div id="{pid}" role="tabpanel" aria-labelledby="{tid}" '
                f'aria-hidden="{"false" if active else "true"}" style="display:{display};padding-top:16px">'
                f"{content_html}</div>"
            )

        wrapper_style = extra or "width:100%"
        tablist_label = self._get_universal_attrs().get("aria-label") or "Pestanas"
        tabs_bar = (
            f'<div id="{uid}_tablist" role="tablist" aria-label="{tablist_label}" style="display:flex;border-bottom:1px solid var(--border);gap:4px">'
            f"{btns}</div>"
        )

        js = (
            f"<script>(function(){{"
            f"window.{uid}_go=function(i){{"
            f"  for(var j=0;j<{n};j++){{"
                f'    var b=document.getElementById("{uid}_t"+j);'
                f'    var p=document.getElementById("{uid}_p"+j);'
                f"    var active=j===i;"
                f"    if(b){{"
                f'      b.style.color=active?"var(--text)":"var(--text-muted)";'
                f'      b.style.background=active?"var(--surface)":"transparent";'
                f'      b.style.borderBottom=active?"2px solid var(--accent)":"2px solid transparent";'
                f'      b.setAttribute("aria-selected",active?"true":"false");'
                f'      b.tabIndex=active?0:-1;'
                f"    }}"
                f'    if(p){{p.style.display=active?"block":"none";p.setAttribute("aria-hidden",active?"false":"true");}}'
                f"  }}"
                f'  var ab=document.getElementById("{uid}_t"+i);if(ab)ab.focus();'
            f"}};"
            f'var list=document.getElementById("{uid}_tablist");'
            f'if(list&&!list.dataset.martinTabsBound){{'
            f'  list.dataset.martinTabsBound="1";'
            f'  list.addEventListener("keydown",function(e){{'
            f'    if(e.key!=="ArrowRight"&&e.key!=="ArrowLeft")return;'
            f'    var i=0;for(var j=0;j<{n};j++){{var b=document.getElementById("{uid}_t"+j);if(b&&b.getAttribute("aria-selected")==="true"){{i=j;break;}}}}'
            f'    var next=e.key==="ArrowRight"?(i+1)%{n}:(i-1+{n})%{n};'
            f'    window.{uid}_go(next);'
            f'    e.preventDefault();'
            f'  }});'
            f'}}'
            f"}})();</script>"
        )

        return f'<div style="{wrapper_style}">' + tabs_bar + panels + js + "</div>"


# =============================================================================
# SideMenu
# =============================================================================


class SideMenu(Widget):
    """
    Menú lateral vertical con links.

        SideMenu(
            title="Widgets",
            items=[
                ("Text", "#widget-text"),
                ("Button", "#widget-button"),
                ("Form", "/forms"),
            ],
        )

    Parámetros:
        title       str       título opcional del menú
        items       list      lista de (label, href) o dict {"label","href"}
        sticky      bool      fija el menú durante scroll (default: True)
        top         int       offset superior en px para sticky
        width       int|str   ancho del menú
        bordered    bool      borde del contenedor (default: True)
    """

    def __init__(
        self,
        title=None,
        items=None,
        position="content-left",
        sticky=True,
        top=84,
        width=260,
        bordered=True,
        id=None,
        class_name=None,
        **kwargs,
    ):
        self._props = Widget._extract_props(kwargs)
        self.title = title
        self.items = items or []
        self.position = position
        self.sticky = sticky
        self.top = top
        self.width = width
        self.bordered = bordered
        self.id = id
        self.class_name = class_name

    @staticmethod
    def _item_parts(item):
        if isinstance(item, (tuple, list)):
            if not item:
                return None, None
            label = item[0]
            href = item[1] if len(item) > 1 else "#"
            return label, href
        if isinstance(item, dict):
            return item.get("label"), item.get("href", "#")
        return str(item), "#"

    def render(self):
        is_page = "page" in self.position
        is_right = "right" in self.position
        
        pos_css = ""
        order_css = ""
        if is_page:
            edge = "right:0;" if is_right else "left:0;"
            pos_css = f"position:fixed;{edge}top:{self.top}px;z-index:40;"
            order_css = "order:999;" if is_right else "order:-999;"
        else:
            edge = "right:0;" if is_right else "left:0;"
            pos_css = f"position:sticky;{edge}top:{self.top}px;align-self:flex-start;" if self.sticky else ""
            if is_right: order_css = "order:999;"
            else: order_css = "order:-999;"

        width_css = f"width:{self.width}px;" if isinstance(self.width, (int, float)) else f"width:{self.width};"
        
        border_css = ""
        if self.bordered:
            border_css = "border-left:1px solid var(--border);" if is_right else "border-right:1px solid var(--border);"
            
        base = (
            f"{pos_css}{width_css}{border_css}{order_css}"
            f"background:var(--surface);border-radius:0;padding:14px;margin:0;height:calc(100vh - {self.top}px);overflow-y:auto;"
            "display:flex;flex-direction:column;gap:10px"
        )
        inline = self._resolve_props(base)
        attrs = self._attrs(style=inline, id=self.id, **{"class": self.class_name})

        title_html = ""
        if self.title:
            title_html = (
                f'<div style="font-size:13px;font-weight:700;color:var(--text);'
                f'letter-spacing:.02em;text-transform:uppercase">{self.title}</div>'
            )

        current_path = get_current_path()
        links = []
        for item in self.items:
            label, href = self._item_parts(item)
            if label is None:
                continue

            is_active = paths_match(current_path, href)
            label_html = label.render() if isinstance(label, Widget) else str(label)
            active_css = "color:var(--accent);font-weight:600;background:rgba(99,102,241,.10);" if is_active else ""
            aria_current = ' aria-current="page"' if is_active else ""
            links.append(
                f'<a href="{href}"{aria_current} style="display:block;padding:8px 10px;'
                f'border-radius:8px;text-decoration:none;color:var(--text-muted);'
                f'font-size:14px;line-height:1.35;transition:all .18s;{active_css}">{label_html}</a>'
            )

        links_html = "".join(links)
        aside_html = f"<aside{attrs}>{title_html}<nav>{links_html}</nav></aside>"
        if is_page:
            spacer_order = "order:999;" if is_right else "order:-999;"
            spacer = f'<div style="{width_css}flex-shrink:0;{spacer_order}"></div>'
            return spacer + aside_html
        return aside_html
