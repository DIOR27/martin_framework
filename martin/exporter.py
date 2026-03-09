"""
Martin — Exporter
Genera archivos estáticos que funcionan tanto en servidor web
como abiertos directamente desde el sistema de archivos (file://).
"""

import re, os, shutil
from pathlib import Path


# ══════════════════════════════════════════════════════════
# ARCHIVOS ESTÁTICOS BASE
# ══════════════════════════════════════════════════════════

BASE_CSS = """\
/* Martin — base.css */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
:root {
  --font-sans: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  --font-mono: 'JetBrains Mono', 'Fira Code', monospace;
  --color-bg: #060818; --color-text: #f1f5f9;
  --color-muted: rgba(148,163,184,0.8); --color-border: rgba(255,255,255,0.08);
  --color-accent: #818cf8; --color-accent2: #34d399;
}
html, body { background: var(--color-bg); min-height: 100vh; }
body { font-family: var(--font-sans); line-height: 1.5; color: var(--color-text); }
img { display: block; max-width: 100%; }
a   { color: inherit; }
@keyframes pulse  { 0%,100%{opacity:1;transform:scale(1)} 50%{opacity:.5;transform:scale(.8)} }
@keyframes fadeUp { from{opacity:0;transform:translateY(20px)} to{opacity:1;transform:translateY(0)} }
@keyframes float  { 0%,100%{transform:translate(0,0) scale(1)} 33%{transform:translate(30px,-20px) scale(1.05)} 66%{transform:translate(-20px,15px) scale(.97)} }
::-webkit-scrollbar { width:6px } ::-webkit-scrollbar-track { background:transparent }
::-webkit-scrollbar-thumb { background:rgba(129,140,248,.3); border-radius:3px }
"""

NAV_CSS = """\
/* Martin — nav.css */
nav.martin-nav {
  display:flex; align-items:center; gap:28px; padding:0 32px; height:56px;
  background:rgba(6,8,24,.85); backdrop-filter:blur(20px);
  -webkit-backdrop-filter:blur(20px);
  border-bottom:1px solid rgba(255,255,255,.08);
  position:sticky; top:0; z-index:100;
}
nav.martin-nav a { text-decoration:none; font-size:14px; font-weight:500; color:rgba(203,213,225,.75); transition:color .2s; }
nav.martin-nav a:hover  { color:#f1f5f9; }
nav.martin-nav a.active { color:#a5b4fc; font-weight:600; }
nav.martin-nav .nav-logo { font-weight:800; font-size:18px; letter-spacing:-.5px; color:#f1f5f9; margin-right:8px; text-decoration:none; }
nav.martin-nav .nav-logo img { height:32px; width:auto; }
"""

# NAV_JS — usa el nombre del archivo para marcar el link activo (funciona en file://)
NAV_JS = """\
/* Martin — nav.js */
(function () {
  var file = window.location.pathname.split('/').pop() || 'index.html';
  if (!file.endsWith('.html')) file = 'index.html';
  document.querySelectorAll('nav.martin-nav a').forEach(function (a) {
    var href = (a.getAttribute('href') || '').split('/').pop() || 'index.html';
    if (href === file) a.classList.add('active');
  });
})();
"""

SELECT_JS = """\
/* Martin — select.js */
(function () {
  if (!window._pwSelectInit) {
    window._pwSelectInit = true;
    window.pwSelectToggle = function (uid) {
      var drop=document.getElementById(uid+'_drop'), arrow=document.getElementById(uid+'_arrow');
      var isOpen=drop.style.display!=='none';
      document.querySelectorAll('[id$="_drop"]').forEach(function(el){
        if(el.id!==uid+'_drop'){el.style.display='none';
          var a=document.getElementById(el.id.replace('_drop','_arrow'));if(a)a.style.transform='';}
      });
      if(isOpen){drop.style.display='none';arrow.style.transform='';}
      else{drop.style.display='block';arrow.style.transform='rotate(180deg)';
        setTimeout(function(){var s=document.getElementById(uid+'_search');
          if(s){s.value='';s.focus();pwSelectFilter(uid,'');}},50);}
    };
    window.pwSelectFilter = function(uid,q){
      document.querySelectorAll('#'+uid+'_list .pw-opt').forEach(function(i){
        i.style.display=i.getAttribute('data-label').toLowerCase().includes(q.toLowerCase())?'block':'none';});
    };
    window.pwSelectPick = function(uid,val,label){
      document.getElementById(uid+'_val').value=val;
      document.getElementById(uid+'_label').textContent=label;
      document.getElementById(uid+'_drop').style.display='none';
      document.getElementById(uid+'_arrow').style.transform='';
      document.querySelectorAll('#'+uid+'_list .pw-opt').forEach(function(el){
        var s=el.getAttribute('data-val')===val;
        el.style.background=s?'#eff6ff':'#fff';el.style.fontWeight=s?'600':'400';});
    };
    document.addEventListener('click',function(e){
      if(!e.target.closest('[id$="_wrap"]'))
        document.querySelectorAll('[id$="_drop"]').forEach(function(el){
          el.style.display='none';
          var a=document.getElementById(el.id.replace('_drop','_arrow'));if(a)a.style.transform='';});
    });
  }
  if(!window._pwMultiState) window._pwMultiState={};
  window.pwMultiIsSelected=function(uid,val){return window._pwMultiState[uid]&&window._pwMultiState[uid].has(val);};
  window.pwMultiOpen=function(uid){document.getElementById(uid+'_drop').style.display='block';};
  window.pwMultiFocus=function(uid){document.getElementById(uid+'_input').focus();};
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
    s = path.strip("/")
    return s.replace("/", "-") or "index"


def _route_to_file(route: str) -> str:
    return "index.html" if route == "/" else f"{_slugify(route)}.html"


def _extract_head_style(html: str):
    m = re.search(r"<style>(.*?)</style>", html, re.DOTALL)
    if not m:
        return html, ""
    return html[: m.start()] + html[m.end() :], m.group(1).strip()


def _extract_inline_scripts(html: str):
    scripts = []

    def rep(m):
        if "src=" in m.group(1):
            return m.group(0)
        body = m.group(2)
        if "__ping__" in body or "__reload__" in body:
            return ""
        scripts.append(body.strip())
        return ""

    clean = re.sub(r"<script([^>]*)>(.*?)</script>", rep, html, flags=re.DOTALL)
    return clean, "\n\n".join(scripts)


def _extract_external_scripts(html: str):
    tags = []

    def rep(m):
        tags.append(m.group(0))
        return ""

    clean = re.sub(r"<script\s[^>]*src=[^>]*>\s*</script>", rep, html)
    return clean, tags


def _extract_external_links(html: str):
    tags = []

    def rep(m):
        if 'href="http' in m.group(0) or "href='http" in m.group(0):
            tags.append(m.group(0))
            return ""
        return m.group(0)

    clean = re.sub(r"<link\b[^>]*/?>", rep, html)
    return clean, tags


def _extract_inline_styles(html: str):
    rules = []
    n = [0]

    def rep(m):
        cls = f"m-{n[0]}"
        n[0] += 1
        rules.append(f".{cls} {{ {m.group(1)} }}")
        return f'class="{cls}"'

    clean = re.sub(r'\bstyle="([^"]*)"', rep, html)
    return clean, "\n".join(rules)


def _rewrite_paths(html: str, routes: list) -> str:
    """
    Convierte TODAS las rutas absolutas en relativas.
    Crítico para que funcione con file:// (abrir HTML directo).
    """
    # 1. Rutas del router → nombre de archivo .html
    for route in routes:
        html = html.replace(f'href="{route}"', f'href="{_route_to_file(route)}"')

    # 2. Cualquier href="/..." restante
    def fix_href(m):
        val = m.group(1)
        if val.startswith(("http", "#", "data:", "mailto:", "tel:")):
            return m.group(0)
        if val.startswith("/assets/"):
            return f'href="{val.lstrip("/")}"'
        if val.startswith("/"):
            slug = _slugify(val)
            return f'href="{slug or "index"}.html"'
        return m.group(0)

    html = re.sub(r'href="([^"]*)"', fix_href, html)

    # 3. src="/assets/..." → src="assets/..."
    html = re.sub(r'src="/assets/', 'src="assets/', html)

    # 4. url() en CSS inline
    html = re.sub(r"url\('/assets/", "url('assets/", html)
    html = re.sub(r'url\("/assets/', 'url("assets/', html)

    return html


# ══════════════════════════════════════════════════════════
# EXPORT PRINCIPAL
# ══════════════════════════════════════════════════════════


def export_split(app, out_dir: str = "dist", assets_src: str = "assets"):
    """
    Exporta el sitio Martin a HTML estático en out_dir/.
    Los archivos generados funcionan:
      - Servidos desde cualquier servidor web estático
      - Abiertos directamente desde el sistema de archivos (file://)
    """
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

    if os.path.exists(assets_src):
        dst = out / "assets"
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(assets_src, dst)
        print(f"  📁  assets/ copiado")

    routes = app._router.paths() if app._router else ["/"]

    for route in routes:
        slug = _slugify(route)
        out_file = _route_to_file(route)
        html = app._render(route)

        # 1. Quitar live reload
        html = re.sub(
            r"<script[^>]*>.*?/__ping__.*?</script>", "", html, flags=re.DOTALL
        )

        # 2. Extraer <style> del head
        html, css_global = _extract_head_style(html)

        # 3. Extraer JS inline del body
        html, js_inline = _extract_inline_scripts(html)

        # 4. Extraer <script src=...> externos del body → subirlos al head
        html, ext_scripts = _extract_external_scripts(html)

        # 5. Extraer <link href="http..."> externos del body → subirlos al head
        html, ext_links = _extract_external_links(html)

        # 6. Convertir style="..." → class="m-N"
        html, css_inline = _extract_inline_styles(html)

        # 7. Marcar <nav> con martin-nav (tiene class="m-N" del paso anterior)
        html = re.sub(
            r'<nav\s+class="([^"]*)"',
            lambda m: f'<nav class="martin-nav {m.group(1)}"',
            html,
            count=1,
        )
        if '<nav class="martin-nav' not in html:
            html = html.replace("<nav ", '<nav class="martin-nav" ', 1)

        # 8. Reescribir TODAS las rutas a relativas (fix file://)
        html = _rewrite_paths(html, routes)

        # 9. CSS de la página
        page_css = f"/* {slug}.css */\n\n"
        if css_global:
            page_css += f"/* global */\n{css_global}\n\n"
        if css_inline:
            page_css += f"/* inline */\n{css_inline}\n"

        # 10. JS de la página
        page_js = ""
        if js_inline:
            js_clean = re.sub(
                r"\(function\(\)\{.*?window\._pwSelectInit.*?\}\)\(\);",
                "",
                js_inline,
                flags=re.DOTALL,
            )
            js_clean = re.sub(
                r"\(function\(\)\{.*?window\._pwMultiState.*?\}\)\(\);",
                "",
                js_clean,
                flags=re.DOTALL,
            ).strip()
            if js_clean:
                page_js = f"/* {slug}.js */\n{js_clean}"

        # 11. Inyectar en <head>:
        #     CSS propio → CSS externo → JS externo (sin defer) → JS diferido
        head_inject = (
            f'  <link rel="stylesheet" href="css/base.css">\n'
            f'  <link rel="stylesheet" href="css/nav.css">\n'
            f'  <link rel="stylesheet" href="css/{slug}.css">\n'
            + "".join(f"  {t}\n" for t in ext_links)
            + "".join(f"  {t}\n" for t in ext_scripts)
            + f'  <script src="js/select.js" defer></script>\n'
            + f'  <script src="js/nav.js" defer></script>\n'
            + (f'  <script src="js/{slug}.js" defer></script>\n' if page_js else "")
        )
        html = html.replace("</head>", head_inject + "</head>", 1)

        # 12. Escribir
        (out / out_file).write_text(html, encoding="utf-8")
        (css_dir / f"{slug}.css").write_text(page_css, encoding="utf-8")
        if page_js:
            (js_dir / f"{slug}.js").write_text(page_js, encoding="utf-8")

        note = f" + js/{slug}.js" if page_js else ""
        print(f"  📄  {out_file}  →  css/{slug}.css{note}")

    print(f"\n  ✅  Exportado en '{out_dir}/'")
    print(f"      {len(routes)} página(s) · base.css · nav.css · select.js · nav.js")
