"""
Martin — Exporter
Convierte el HTML generado en archivos HTML + CSS + JS separados.

Estructura de salida:
    dist/
    ├── index.html
    ├── about.html
    ├── components.html
    ├── assets/          ← copiado del proyecto
    ├── css/
    │   ├── base.css     ← reset + estilos globales
    │   ├── nav.css      ← estilos del navbar
    │   ├── index.css    ← estilos inline extraídos de cada página
    │   ├── about.css
    │   └── components.css
    └── js/
        ├── nav.js       ← hover del navbar
        ├── reload.js    ← NO incluido en export
        ├── select.js    ← lógica de Select/MultiSelect
        └── index.js     ← JS inline extraído de cada página
"""

import re, os, shutil
from pathlib import Path


# ══════════════════════════════════════════════════════════
# CSS BASE — reset + variables globales
# ══════════════════════════════════════════════════════════

BASE_CSS = """\
/* Martin — base.css */
*, *::before, *::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

:root {
  --font-sans: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  --font-mono: 'JetBrains Mono', 'Fira Code', monospace;
  --color-bg:  #060818;
  --color-text: #f1f5f9;
  --color-muted: rgba(148, 163, 184, 0.8);
  --color-border: rgba(255, 255, 255, 0.08);
  --color-accent: #818cf8;
  --color-accent2: #34d399;
  --radius-sm: 6px;
  --radius-md: 12px;
  --radius-lg: 16px;
  --radius-xl: 24px;
}

html, body {
  background: var(--color-bg);
  min-height: 100vh;
}

body {
  font-family: var(--font-sans);
  line-height: 1.5;
  color: var(--color-text);
}

img { display: block; max-width: 100%; }
a   { color: inherit; }

/* Keyframes globales usados por los widgets */
@keyframes pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50%       { opacity: 0.5; transform: scale(0.8); }
}

@keyframes fadeUp {
  from { opacity: 0; transform: translateY(20px); }
  to   { opacity: 1; transform: translateY(0); }
}

@keyframes float {
  0%, 100% { transform: translate(0, 0) scale(1); }
  33%       { transform: translate(30px, -20px) scale(1.05); }
  66%       { transform: translate(-20px, 15px) scale(0.97); }
}

/* Scrollbar */
::-webkit-scrollbar       { width: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(129,140,248,0.3); border-radius: 3px; }
"""

NAV_CSS = """\
/* Martin — nav.css */
nav.martin-nav {
  display: flex;
  align-items: center;
  gap: 28px;
  padding: 0 32px;
  height: 56px;
  background: rgba(6, 8, 24, 0.85);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  position: sticky;
  top: 0;
  z-index: 100;
}

nav.martin-nav a {
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
  color: rgba(203, 213, 225, 0.75);
  transition: color 0.2s;
}

nav.martin-nav a:hover    { color: #f1f5f9; }
nav.martin-nav a.active   { color: #a5b4fc; font-weight: 600; }

nav.martin-nav .nav-logo {
  font-weight: 800;
  font-size: 18px;
  letter-spacing: -0.5px;
  color: #f1f5f9;
  margin-right: 8px;
  text-decoration: none;
}

nav.martin-nav .nav-logo img {
  height: 32px;
  width: auto;
}
"""

NAV_JS = """\
/* Martin — nav.js */
(function () {
  const path = window.location.pathname;
  document.querySelectorAll('nav.martin-nav a').forEach(function (a) {
    const href = a.getAttribute('href');
    if (href === path || (path === '/' && href === '/index.html')) {
      a.classList.add('active');
    }
  });
})();
"""

SELECT_JS = """\
/* Martin — select.js — Select y MultiSelect widgets */
(function () {
  /* ── Select ── */
  if (!window._pwSelectInit) {
    window._pwSelectInit = true;

    window.pwSelectToggle = function (uid) {
      var drop  = document.getElementById(uid + '_drop');
      var arrow = document.getElementById(uid + '_arrow');
      var isOpen = drop.style.display !== 'none';
      document.querySelectorAll('[id$="_drop"]').forEach(function (el) {
        if (el.id !== uid + '_drop') {
          el.style.display = 'none';
          var a = document.getElementById(el.id.replace('_drop', '_arrow'));
          if (a) a.style.transform = '';
        }
      });
      if (isOpen) {
        drop.style.display = 'none';
        arrow.style.transform = '';
      } else {
        drop.style.display = 'block';
        arrow.style.transform = 'rotate(180deg)';
        setTimeout(function () {
          var s = document.getElementById(uid + '_search');
          if (s) { s.value = ''; s.focus(); pwSelectFilter(uid, ''); }
        }, 50);
      }
    };

    window.pwSelectFilter = function (uid, q) {
      document.querySelectorAll('#' + uid + '_list .pw-opt').forEach(function (i) {
        i.style.display = i.getAttribute('data-label').toLowerCase().includes(q.toLowerCase())
          ? 'block' : 'none';
      });
    };

    window.pwSelectPick = function (uid, val, label) {
      document.getElementById(uid + '_val').value = val;
      document.getElementById(uid + '_label').textContent = label;
      document.getElementById(uid + '_drop').style.display = 'none';
      document.getElementById(uid + '_arrow').style.transform = '';
      document.querySelectorAll('#' + uid + '_list .pw-opt').forEach(function (el) {
        var s = el.getAttribute('data-val') === val;
        el.style.background = s ? '#eff6ff' : '#fff';
        el.style.fontWeight  = s ? '600' : '400';
      });
    };

    document.addEventListener('click', function (e) {
      if (!e.target.closest('[id$="_wrap"]')) {
        document.querySelectorAll('[id$="_drop"]').forEach(function (el) {
          el.style.display = 'none';
          var a = document.getElementById(el.id.replace('_drop', '_arrow'));
          if (a) a.style.transform = '';
        });
      }
    });
  }

  /* ── MultiSelect ── */
  if (!window._pwMultiState) window._pwMultiState = {};

  window.pwMultiIsSelected = function (uid, val) {
    return window._pwMultiState[uid] && window._pwMultiState[uid].has(val);
  };
  window.pwMultiOpen  = function (uid) {
    document.getElementById(uid + '_drop').style.display = 'block';
  };
  window.pwMultiFocus = function (uid) {
    document.getElementById(uid + '_input').focus();
  };
  window.pwMultiFilter = function (uid, q) {
    document.querySelectorAll('#' + uid + '_list .pw-mopt').forEach(function (el) {
      el.style.display = el.getAttribute('data-label').toLowerCase().includes(q.toLowerCase())
        ? 'flex' : 'none';
    });
  };
})();
"""


# ══════════════════════════════════════════════════════════
# EXTRACTOR
# ══════════════════════════════════════════════════════════


def _extract_inline_styles(html: str) -> tuple[str, str]:
    """
    Extrae todos los style="..." del HTML.
    Devuelve (html_limpio_con_clases, css_extraido).
    """
    css_rules = []
    counter = [0]

    def replacer(m):
        inline = m.group(1)
        # No extraer estilos de <style> tags ni del nav (ya tienen clases)
        cls = f"m-{counter[0]}"
        counter[0] += 1
        css_rules.append(f".{cls} {{ {inline} }}")
        return f'class="{cls}"'

    clean_html = re.sub(r'\bstyle="([^"]*)"', replacer, html)
    return clean_html, "\n".join(css_rules)


def _extract_scripts(html: str) -> tuple[str, str]:
    """
    Extrae bloques <script>...</script> del body (no los externos con src=).
    Devuelve (html_sin_scripts_inline, js_extraido).
    """
    scripts = []

    def replacer(m):
        # Saltar scripts con src=
        if "src=" in m.group(0):
            return m.group(0)
        # Saltar el live reload
        if "__ping__" in m.group(1) or "__reload__" in m.group(1):
            return ""
        scripts.append(m.group(1).strip())
        return ""

    clean = re.sub(r"<script[^>]*>(.*?)</script>", replacer, html, flags=re.DOTALL)
    return clean, "\n\n".join(scripts)


def _extract_global_style(html: str) -> tuple[str, str]:
    """Extrae el bloque <style> del <head>."""
    m = re.search(r"<style>(.*?)</style>", html, re.DOTALL)
    if not m:
        return html, ""
    css = m.group(1).strip()
    clean = html[: m.start()] + html[m.end() :]
    return clean, css


def _slugify(router_path: str) -> str:
    """/ → index,  /about → about,  /my/page → my-page"""
    s = router_path.strip("/")
    return s.replace("/", "-") or "index"


# ══════════════════════════════════════════════════════════
# EXPORT PRINCIPAL
# ══════════════════════════════════════════════════════════


def export_split(app, out_dir: str = "dist", assets_src: str = "assets"):
    """
    Exporta el proyecto a HTML + CSS + JS separados.

    dist/
    ├── index.html
    ├── about.html
    ├── assets/
    ├── css/
    │   ├── base.css
    │   ├── nav.css
    │   ├── index.css
    │   └── about.css
    └── js/
        ├── nav.js
        ├── select.js
        ├── index.js
        └── about.js
    """
    out = Path(out_dir)
    css_dir = out / "css"
    js_dir = out / "js"

    out.mkdir(parents=True, exist_ok=True)
    css_dir.mkdir(exist_ok=True)
    js_dir.mkdir(exist_ok=True)

    # ── Archivos estáticos base ───────────────────────────────────────────────
    (css_dir / "base.css").write_text(BASE_CSS, encoding="utf-8")
    (css_dir / "nav.css").write_text(NAV_CSS, encoding="utf-8")
    (js_dir / "nav.js").write_text(NAV_JS, encoding="utf-8")
    (js_dir / "select.js").write_text(SELECT_JS, encoding="utf-8")

    # ── Copiar assets ─────────────────────────────────────────────────────────
    if os.path.exists(assets_src):
        assets_dst = out / "assets"
        if assets_dst.exists():
            shutil.rmtree(assets_dst)
        shutil.copytree(assets_src, assets_dst)
        print(f"  📁  assets/ → {assets_dst}")

    # ── Páginas ───────────────────────────────────────────────────────────────
    routes = app._router.paths() if app._router else ["/"]

    for route in routes:
        slug = _slugify(route)
        html_raw = app._render(route)

        # 1. Quitar live reload
        html_raw = html_raw.replace(app.hot_reload and "true" or "", "")
        html_raw = re.sub(
            r"<script[^>]*>.*?/__ping__.*?</script>", "", html_raw, flags=re.DOTALL
        )

        # 2. Extraer <style> global del head
        html_raw, page_css_global = _extract_global_style(html_raw)

        # 3. Extraer scripts inline del body
        html_raw, page_js = _extract_scripts(html_raw)

        # 4. Extraer estilos inline → clases CSS
        html_clean, page_css_inline = _extract_inline_styles(html_raw)

        # 5. Añadir clase martin-nav al <nav>
        html_clean = html_clean.replace("<nav ", '<nav class="martin-nav" ', 1)

        # 6. Unir CSS de la página
        page_css = f"/* {slug}.css — estilos extraídos de {route} */\n\n"
        if page_css_global:
            page_css += (
                f"/* — estilos globales de la página — */\n{page_css_global}\n\n"
            )
        if page_css_inline:
            page_css += f"/* — estilos inline extraídos — */\n{page_css_inline}\n"

        # 7. JS de la página (widgets + lógica propia)
        page_js_full = ""
        if page_js:
            # Quitar duplicados de pwSelect/pwMulti (ya están en select.js)
            page_js_clean = re.sub(
                r"\(function\(\)\{.*?window\._pwSelectInit.*?\}\)\(\);",
                "",
                page_js,
                flags=re.DOTALL,
            )
            page_js_clean = re.sub(
                r"\(function\(\)\{.*?window\._pwMultiState.*?\}\)\(\);",
                "",
                page_js_clean,
                flags=re.DOTALL,
            ).strip()
            if page_js_clean:
                page_js_full = f"/* {slug}.js */\n{page_js_clean}"

        # 8. Reescribir <head> limpio con links a CSS y JS externos
        css_links = (
            f'  <link rel="stylesheet" href="css/base.css">\n'
            f'  <link rel="stylesheet" href="css/nav.css">\n'
            f'  <link rel="stylesheet" href="css/{slug}.css">\n'
        )
        js_scripts = (
            f'  <script src="js/select.js" defer></script>\n'
            f'  <script src="js/nav.js" defer></script>\n'
        )
        if page_js_full:
            js_scripts += f'  <script src="js/{slug}.js" defer></script>\n'

        # Insertar links en el <head>
        html_final = re.sub(r"(</head>)", css_links + js_scripts + r"\1", html_clean)

        # Arreglar rutas relativas de assets
        html_final = html_final.replace('src="/assets/', 'src="assets/')
        html_final = html_final.replace('href="/assets/', 'href="assets/')

        # Arreglar hrefs de navegación entre páginas
        for other_route in routes:
            other_slug = _slugify(other_route)
            other_file = "index.html" if other_route == "/" else f"{other_slug}.html"
            html_final = re.sub(
                rf'href="{re.escape(other_route)}"', f'href="{other_file}"', html_final
            )

        # 9. Escribir archivos
        out_html = slug + ".html"
        (out / out_html).write_text(html_final, encoding="utf-8")
        (css_dir / f"{slug}.css").write_text(page_css, encoding="utf-8")
        if page_js_full:
            (js_dir / f"{slug}.js").write_text(page_js_full, encoding="utf-8")

        js_note = f" + js/{slug}.js" if page_js_full else ""
        print(f"  📄  {out_html}  →  css/{slug}.css{js_note}")

    print(f"\n  ✅  Exportado en '{out_dir}/'")
    print(
        f"      {len(routes)} página(s) · css/base.css · css/nav.css · js/select.js · js/nav.js"
    )
