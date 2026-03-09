"""
Martin — Exporter
Genera archivos estáticos (HTML + CSS + JS separados) que funcionan:
  - Servidos desde cualquier servidor web estático
  - Abiertos directamente desde el sistema de archivos (file://)
"""

import re, os, shutil
from pathlib import Path


# ══════════════════════════════════════════════════════════
# CSS / JS ESTÁTICOS
# ══════════════════════════════════════════════════════════

BASE_CSS = """\
/* Martin — base.css */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html, body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  line-height: 1.5; min-height: 100vh;
  background: var(--bg); color: var(--text);
}
img { display: block; max-width: 100%; }
a   { color: inherit; }
@keyframes pulse  { 0%,100%{opacity:1;transform:scale(1)} 50%{opacity:.5;transform:scale(.8)} }
@keyframes fadeUp { from{opacity:0;transform:translateY(20px)} to{opacity:1;transform:translateY(0)} }
@keyframes float  { 0%,100%{transform:translate(0,0) scale(1)} 33%{transform:translate(30px,-20px) scale(1.05)} 66%{transform:translate(-20px,15px) scale(.97)} }
::-webkit-scrollbar { width:6px }
::-webkit-scrollbar-track { background:transparent }
::-webkit-scrollbar-thumb { background:rgba(129,140,248,.3); border-radius:3px }

/* Temas */
[data-theme="light"], .theme-light {
  --bg:#f8fafc; --bg-secondary:#f1f5f9; --surface:#ffffff; --surface-2:#f3f4f6;
  --border:rgba(0,0,0,0.10); --border-input:#d1d5db;
  --text:#0f172a; --text-muted:#64748b; --text-placeholder:#94a3b8;
  --input-bg:#ffffff; --input-color:#0f172a;
  --accent:#6366f1; --accent-hover:#4f46e5;
  --shadow:0 2px 12px rgba(0,0,0,0.08);
  --nav-bg:rgba(248,250,252,0.92); --nav-border:rgba(0,0,0,0.07); --nav-text:rgba(15,23,42,0.70);
  --dropdown-bg:#ffffff;
}
[data-theme="dark"], .theme-dark {
  --bg:#060818; --bg-secondary:#0d1117; --surface:rgba(255,255,255,0.05); --surface-2:rgba(255,255,255,0.03);
  --border:rgba(255,255,255,0.08); --border-input:rgba(255,255,255,0.15);
  --text:#f1f5f9; --text-muted:rgba(148,163,184,0.8); --text-placeholder:rgba(148,163,184,0.45);
  --input-bg:rgba(255,255,255,0.06); --input-color:#f1f5f9;
  --accent:#818cf8; --accent-hover:#6366f1;
  --shadow:0 4px 24px rgba(0,0,0,0.35);
  --nav-bg:rgba(6,8,24,0.88); --nav-border:rgba(255,255,255,0.08); --nav-text:rgba(203,213,225,0.75);
  --dropdown-bg:#1a1d2e;
}
@media (prefers-color-scheme: dark) {
  [data-theme="auto"] {
    --bg:#060818; --bg-secondary:#0d1117; --surface:rgba(255,255,255,0.05); --surface-2:rgba(255,255,255,0.03);
    --border:rgba(255,255,255,0.08); --border-input:rgba(255,255,255,0.15);
    --text:#f1f5f9; --text-muted:rgba(148,163,184,0.8); --text-placeholder:rgba(148,163,184,0.45);
    --input-bg:rgba(255,255,255,0.06); --input-color:#f1f5f9;
    --accent:#818cf8; --accent-hover:#6366f1; --shadow:0 4px 24px rgba(0,0,0,0.35);
    --nav-bg:rgba(6,8,24,0.88); --nav-border:rgba(255,255,255,0.08); --nav-text:rgba(203,213,225,0.75);
    --dropdown-bg:#1a1d2e;
  }
}
@media (prefers-color-scheme: light) {
  [data-theme="auto"] {
    --bg:#f8fafc; --bg-secondary:#f1f5f9; --surface:#ffffff; --surface-2:#f3f4f6;
    --border:rgba(0,0,0,0.10); --border-input:#d1d5db;
    --text:#0f172a; --text-muted:#64748b; --text-placeholder:#94a3b8;
    --input-bg:#ffffff; --input-color:#0f172a;
    --accent:#6366f1; --accent-hover:#4f46e5; --shadow:0 2px 12px rgba(0,0,0,0.08);
    --nav-bg:rgba(248,250,252,0.92); --nav-border:rgba(0,0,0,0.07); --nav-text:rgba(15,23,42,0.70);
    --dropdown-bg:#ffffff;
  }
}

/* Inputs themed */
input:not([type="checkbox"]):not([type="radio"]), select, textarea {
  background: var(--input-bg) !important; color: var(--input-color) !important;
  border-color: var(--border-input) !important;
}
input::placeholder, textarea::placeholder { color: var(--text-placeholder) !important; }
input:focus:not([type="checkbox"]), select:focus, textarea:focus {
  border-color: var(--accent) !important;
  box-shadow: 0 0 0 3px rgba(99,102,241,0.15) !important;
  outline: none !important;
}
.pw-opt, .pw-mopt { color: var(--text) !important; }
.pw-opt:hover, .pw-mopt:hover { background: var(--surface-2) !important; }
"""

NAV_CSS = """\
/* Martin — nav.css */
nav.martin-nav {
  display: flex; align-items: center; padding: 0 24px; height: 56px;
  background: var(--nav-bg); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);
  border-bottom: 1px solid var(--nav-border);
  position: sticky; top: 0; z-index: 200; gap: 0;
}
nav.martin-nav .mn-logo {
  display: flex; align-items: center; gap: 8px;
  text-decoration: none; font-weight: 800; font-size: 17px;
  letter-spacing: -0.3px; color: var(--text); flex-shrink: 0; margin-right: auto;
}
nav.martin-nav .mn-logo img { height: 28px; width: 28px; object-fit: contain; border-radius: 6px; }
nav.martin-nav .mn-links { display: flex; align-items: center; gap: 4px; }
nav.martin-nav .mn-links a {
  text-decoration: none; font-size: 14px; font-weight: 500; color: var(--nav-text);
  padding: 6px 12px; border-radius: 8px; transition: color .2s, background .2s;
}
nav.martin-nav .mn-links a:hover { color: var(--text); background: rgba(128,128,128,0.08); }
nav.martin-nav .mn-links a.active { color: var(--accent); font-weight: 600; background: rgba(99,102,241,0.10); }
nav.martin-nav .mn-burger {
  display: none; flex-direction: column; justify-content: center; align-items: center;
  gap: 5px; width: 40px; height: 40px; background: none; border: none;
  cursor: pointer; padding: 4px; border-radius: 8px; transition: background .2s; flex-shrink: 0;
}
nav.martin-nav .mn-burger:hover { background: rgba(128,128,128,0.1); }
nav.martin-nav .mn-burger span {
  display: block; width: 22px; height: 2px; background: var(--text);
  border-radius: 2px; transition: transform .25s, opacity .25s;
}
nav.martin-nav.mn-open .mn-burger span:nth-child(1) { transform: translateY(7px) rotate(45deg); }
nav.martin-nav.mn-open .mn-burger span:nth-child(2) { opacity: 0; transform: scaleX(0); }
nav.martin-nav.mn-open .mn-burger span:nth-child(3) { transform: translateY(-7px) rotate(-45deg); }
nav.martin-nav .mn-drawer {
  display: none; position: fixed; top: 56px; left: 0; right: 0;
  background: var(--nav-bg); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);
  border-bottom: 1px solid var(--nav-border);
  padding: 12px 16px 16px; flex-direction: column; gap: 4px;
  z-index: 199; box-shadow: 0 8px 32px rgba(0,0,0,0.15);
}
nav.martin-nav.mn-open .mn-drawer { display: flex; }
nav.martin-nav .mn-drawer a {
  text-decoration: none; font-size: 15px; font-weight: 500; color: var(--nav-text);
  padding: 10px 14px; border-radius: 10px; transition: color .15s, background .15s;
}
nav.martin-nav .mn-drawer a:hover { color: var(--text); background: rgba(128,128,128,0.08); }
nav.martin-nav .mn-drawer a.active { color: var(--accent); font-weight: 600; background: rgba(99,102,241,0.10); }
@media (max-width: 640px) {
  nav.martin-nav .mn-links { display: none; }
  nav.martin-nav .mn-burger { display: flex; }
}
"""

NAV_JS = """\
/* Martin — nav.js */
document.addEventListener('DOMContentLoaded', function () {
  var file = window.location.pathname.split('/').pop() || 'index.html';
  if (!file.endsWith('.html')) file = 'index.html';
  document.querySelectorAll('nav.martin-nav a').forEach(function (a) {
    var href = (a.getAttribute('href') || '').split('/').pop() || 'index.html';
    if (href === file) a.classList.add('active');
  });
  var nav    = document.querySelector('nav.martin-nav');
  var burger = nav && nav.querySelector('.mn-burger');
  if (burger) {
    burger.addEventListener('click', function (e) {
      e.stopPropagation();
      nav.classList.toggle('mn-open');
    });
    var drawer = nav.querySelector('.mn-drawer');
    if (drawer) {
      drawer.querySelectorAll('a').forEach(function (a) {
        a.addEventListener('click', function () { nav.classList.remove('mn-open'); });
      });
    }
    document.addEventListener('click', function (e) {
      if (!nav.contains(e.target)) nav.classList.remove('mn-open');
    });
  }
});
"""

SELECT_JS = """\
/* Martin — select.js */
(function () {
  if (!window._pwSelectInit) {
    window._pwSelectInit = true;
    window.pwSelectToggle = function (uid) {
      var drop=document.getElementById(uid+'_drop'),arrow=document.getElementById(uid+'_arrow'),btn=document.getElementById(uid+'_btn');
      var isOpen=drop&&drop.style.display!=='none';
      document.querySelectorAll('[id$="_drop"]').forEach(function(el){
        if(el.id!==uid+'_drop'){el.style.display='none';
          var a=document.getElementById(el.id.replace('_drop','_arrow'));if(a)a.style.transform='';
          var b=document.getElementById(el.id.replace('_drop','_btn'));if(b)b.style.borderColor='';}
      });
      if(isOpen){drop.style.display='none';if(arrow)arrow.style.transform='';if(btn)btn.style.borderColor='';}
      else{drop.style.display='block';if(arrow)arrow.style.transform='rotate(180deg)';if(btn)btn.style.borderColor='var(--accent)';
        setTimeout(function(){var s=document.getElementById(uid+'_search');if(s){s.value='';s.focus();pwSelectFilter(uid,'');}},50);}
    };
    window.pwSelectFilter=function(uid,q){
      document.querySelectorAll('#'+uid+'_list .pw-opt').forEach(function(i){
        i.style.display=i.getAttribute('data-label').toLowerCase().includes(q.toLowerCase())?'block':'none';});
    };
    window.pwSelectPick=function(uid,val,label){
      document.getElementById(uid+'_val').value=val;
      document.getElementById(uid+'_label').textContent=label;
      document.getElementById(uid+'_drop').style.display='none';
      var arrow=document.getElementById(uid+'_arrow');if(arrow)arrow.style.transform='';
      var btn=document.getElementById(uid+'_btn');if(btn)btn.style.borderColor='';
      document.querySelectorAll('#'+uid+'_list .pw-opt').forEach(function(el){
        var s=el.getAttribute('data-val')===val;
        el.style.background=s?'rgba(99,102,241,0.15)':'';el.style.color=s?'var(--accent)':'';el.style.fontWeight=s?'600':'400';});
    };
    document.addEventListener('click',function(e){
      if(!e.target.closest('[id$="_wrap"]'))
        document.querySelectorAll('[id$="_drop"]').forEach(function(el){
          el.style.display='none';
          var a=document.getElementById(el.id.replace('_drop','_arrow'));if(a)a.style.transform='';
          var b=document.getElementById(el.id.replace('_drop','_btn'));if(b)b.style.borderColor='';});
    });
  }
  if(!window._pwMultiState)window._pwMultiState={};
  window.pwMultiIsSelected=function(uid,val){return window._pwMultiState[uid]&&window._pwMultiState[uid].has(val);};
  window.pwMultiOpen=function(uid){var d=document.getElementById(uid+'_drop');if(d)d.style.display='block';};
  window.pwMultiFocus=function(uid){var i=document.getElementById(uid+'_input');if(i)i.focus();};
  window.pwMultiFilter=function(uid,q){
    document.querySelectorAll('#'+uid+'_list .pw-mopt').forEach(function(el){
      el.style.display=el.getAttribute('data-label').toLowerCase().includes(q.toLowerCase())?'flex':'none';});
  };
})();
"""


# ══════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════


def _slugify(path: str) -> str:
    return (path.strip("/").replace("/", "-")) or "index"


def _route_to_file(route: str) -> str:
    return "index.html" if route == "/" else f"{_slugify(route)}.html"


def _reset_widget_counters():
    """Resetea contadores de UID antes de cada render para que HTML y JS coincidan."""
    try:
        from martin.widgets import Select, MultiSelect, WordCloud, Map

        Select._id_counter = MultiSelect._id_counter = WordCloud._id_counter = (
            Map._id_counter
        ) = 0
    except Exception:
        pass


def _extract_head_style(html):
    m = re.search(r"<style[^>]*>(.*?)</style>", html, re.DOTALL)
    if not m:
        return html, ""
    return html[: m.start()] + html[m.end() :], m.group(1).strip()


def _collect_inline_scripts(html):
    chunks = []

    def rep(m):
        attrs, body = m.group(1), m.group(2).strip()
        if "src=" in attrs:
            return m.group(0)
        if not body or "__ping__" in body or "__reload__" in body:
            return ""
        chunks.append(body)
        return ""

    clean = re.sub(r"<script([^>]*)>(.*?)</script>", rep, html, flags=re.DOTALL)
    return clean, ";\n\n".join(chunks)


def _collect_external_scripts(html):
    tags = []

    def rep(m):
        tags.append(m.group(0).strip())
        return ""

    clean = re.sub(r"<script\s[^>]*src=[^>]*>\s*</script>", rep, html)
    return clean, tags


def _collect_external_links(html):
    tags = []

    def rep(m):
        if 'href="http' in m.group(0) or "href='http" in m.group(0):
            tags.append(m.group(0).strip())
            return ""
        return m.group(0)

    clean = re.sub(r"<link\b[^>]*/?>", rep, html)
    return clean, tags


def _extract_inline_styles(html):
    rules, n = [], [0]

    def rep(m):
        cls = f"m-{n[0]}"
        n[0] += 1
        rules.append(f".{cls} {{ {m.group(1)} }}")
        return f'class="{cls}"'

    clean = re.sub(r'\bstyle="([^"]*)"', rep, html)
    return clean, "\n".join(rules)


def _rewrite_paths(html, route_map):
    def fix_href(m):
        val = m.group(1)
        if val.startswith(("http", "//", "#", "data:", "mailto:", "tel:")):
            return m.group(0)
        if val.endswith(".html") or val.startswith(("css/", "js/", "assets/")):
            return m.group(0)
        if val in route_map:
            return f'href="{route_map[val]}"'
        if val.startswith("/"):
            slug = _slugify(val)
            return f'href="{slug or "index"}.html"'
        return m.group(0)

    html = re.sub(r'href="([^"]*)"', fix_href, html)
    html = re.sub(r'src="/assets/', 'src="assets/', html)
    html = re.sub(r"url\('/assets/", "url('assets/", html)
    html = re.sub(r'url\("/assets/', 'url("assets/', html)
    return html


def _build_nav(app, current_route, route_map):
    """Nav HTML responsivo puro usando clases mn-* del nav.css estático."""
    if not app._router or len(app._router.paths()) <= 1:
        return ""

    icon_html = ""
    for ext in (
        "icon.png",
        "icon.svg",
        "icon.webp",
        "logo.png",
        "logo.svg",
        "logo.webp",
        "logo.jpg",
    ):
        if os.path.exists(os.path.join(app.assets_dir, ext)):
            icon_html = f'<img src="assets/{ext}" alt="">'
            break

    home = route_map.get("/", "index.html")
    logo = f'<a href="{home}" class="mn-logo">{icon_html}<span>{app.title}</span></a>'

    links_html = ""
    for path in app._router.paths():
        _, title = app._router.resolve(path)
        label = title or path.strip("/").capitalize() or "Inicio"
        href = route_map.get(path, _route_to_file(path))
        act = ' class="active"' if path == current_route else ""
        links_html += f'<a href="{href}"{act}>{label}</a>'

    burger = '<button class="mn-burger" aria-label="Menú"><span></span><span></span><span></span></button>'
    drawer = f'<div class="mn-drawer">{links_html}</div>'

    return (
        f'<nav class="martin-nav">'
        f'{logo}<div class="mn-links">{links_html}</div>{burger}{drawer}'
        f"</nav>"
    )


def _assemble_page(raw_html, app, current_route, route_map, slug):
    """
    Procesa el HTML crudo → (html_final, page_css, page_js).
    Pipeline garantizado:
      1. Quitar live-reload
      2. Sustituir nav inline por nav responsivo de clases
      3. Extraer <style> global
      4. Extraer <script> inline → page_js
      5. Subir CDN <script src> al head (sin defer = bloquea = Leaflet listo antes que widgets)
      6. Subir CDN <link> al head
      7. Convertir style="…" → class="m-N" → page_css
      8. Reescribir rutas absolutas → relativas
      9. Inyectar assets en <head>
     10. Page JS al final del <body> sin defer
    """
    html = re.sub(
        r"<script[^>]*>.*?/__ping__.*?</script>", "", raw_html, flags=re.DOTALL
    )

    # Quitar el <style>+<script> inline del nav (app.py los inyecta para dev/html);
    # en split mode el nav.css estático los sustituye.
    html = re.sub(r'<style id="_martin_nav_css">.*?</style>', "", html, flags=re.DOTALL)

    nav = _build_nav(app, current_route, route_map)
    if nav:
        html = re.sub(r"<nav\b[^>]*>.*?</nav>", nav, html, count=1, flags=re.DOTALL)

    html, css_global = _extract_head_style(html)
    html, js_inline = _collect_inline_scripts(html)
    html, ext_scripts = _collect_external_scripts(html)
    html, ext_links = _collect_external_links(html)
    html, css_inline = _extract_inline_styles(html)
    html = _rewrite_paths(html, route_map)

    # Head: base → nav → page → CDN CSS → CDN JS (blocking) → select defer → nav defer
    head = (
        f'  <link rel="stylesheet" href="css/base.css">\n'
        f'  <link rel="stylesheet" href="css/nav.css">\n'
        f'  <link rel="stylesheet" href="css/{slug}.css">\n'
        + "".join(f"  {t}\n" for t in ext_links)
        + "".join(f"  {t}\n" for t in ext_scripts)
        + f'  <script src="js/select.js" defer></script>\n'
        + f'  <script src="js/nav.js" defer></script>\n'
    )
    html = html.replace("</head>", head + "</head>", 1)

    page_js = ""
    if js_inline.strip():
        page_js = f"/* {slug}.js */\n{js_inline.strip()}"
        html = html.replace(
            "</body>", f'  <script src="js/{slug}.js"></script>\n</body>', 1
        )

    page_css = f"/* {slug}.css */\n\n"
    if css_global:
        page_css += f"/* global */\n{css_global}\n\n"
    if css_inline:
        page_css += f"/* inline */\n{css_inline}\n"

    return html, page_css, page_js


# ══════════════════════════════════════════════════════════
# ENTRY POINT
# ══════════════════════════════════════════════════════════


def export_split(app, out_dir: str = "dist", assets_src: str = "assets"):
    """Exporta el sitio Martin a HTML estático con CSS/JS separados."""
    out = Path(out_dir)
    css_dir = out / "css"
    js_dir = out / "js"
    out.mkdir(parents=True, exist_ok=True)
    css_dir.mkdir(exist_ok=True)
    js_dir.mkdir(exist_ok=True)

    (css_dir / "base.css").write_text(BASE_CSS, encoding="utf-8")
    (css_dir / "nav.css").write_text(NAV_CSS, encoding="utf-8")
    (js_dir / "nav.js").write_text(NAV_JS, encoding="utf-8")
    (js_dir / "select.js").write_text(SELECT_JS, encoding="utf-8")

    # Assets: paquete primero, proyecto encima
    dst = out / "assets"
    dst.mkdir(exist_ok=True)
    pkg_assets = Path(__file__).parent / "assets"
    if pkg_assets.exists():
        for f in pkg_assets.iterdir():
            if f.is_file() and not (dst / f.name).exists():
                shutil.copy2(f, dst / f.name)
    if os.path.exists(assets_src):
        for item in Path(assets_src).iterdir():
            if item.is_file():
                shutil.copy2(item, dst / item.name)
            elif item.is_dir():
                sub = dst / item.name
                if sub.exists():
                    shutil.rmtree(sub)
                shutil.copytree(item, sub)
        print(f"  📁  assets/ copiado")
    elif pkg_assets.exists():
        print(f"  📁  assets/ (paquete) copiado")

    routes = app._router.paths() if app._router else ["/"]
    route_map = {r: _route_to_file(r) for r in routes}
    app._export_mode = True

    print()
    for route in routes:
        slug = _slugify(route)
        _reset_widget_counters()  # IDs siempre desde 1
        raw_html = app._render(route)
        html, page_css, page_js = _assemble_page(raw_html, app, route, route_map, slug)
        (out / route_map[route]).write_text(html, encoding="utf-8")
        (css_dir / f"{slug}.css").write_text(page_css, encoding="utf-8")
        if page_js:
            (js_dir / f"{slug}.js").write_text(page_js, encoding="utf-8")
        note = f" + js/{slug}.js" if page_js else ""
        print(f"  📄  {route_map[route]}  →  css/{slug}.css{note}")

    print(f"\n  ✅  Exportado en '{out_dir}/'")
    print(
        f"      {len(routes)} página(s)  ·  base.css  ·  nav.css  ·  select.js  ·  nav.js"
    )


def export_html(app, out_dir: str = "dist"):
    """
    Exporta el sitio como HTML autocontenido (un archivo por página).
    Aplica reescritura de rutas para que los hrefs sean relativos (.html).
    """
    import re
    from pathlib import Path

    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    routes = app._router.paths() if app._router else ["/"]
    route_map = {r: _route_to_file(r) for r in routes}
    app._export_mode = True

    print()
    for route in routes:
        slug = _slugify(route)
        _reset_widget_counters()
        raw = app._render(route)
        # Quitar live-reload
        raw = re.sub(r"<script[^>]*>.*?/__ping__.*?</script>", "", raw, flags=re.DOTALL)
        # Reescribir rutas absolutas → relativas
        raw = _rewrite_paths(raw, route_map)
        fname = route_map[route]
        (out / fname).write_text(raw, encoding="utf-8")
        print(f"  📄  {fname}")

    print(f"\n  ✅  Exportado en '{out_dir}/'")
    print(f"      {len(routes)} página(s)")
