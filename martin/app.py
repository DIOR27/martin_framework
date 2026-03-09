"""
Martin — App, Router & Dev Server
"""

import os, sys, time, threading, importlib.util
import http.server, webbrowser
from pathlib import Path
from .theme import THEME_CSS, THEME_TOGGLE_JS
from .response import Response, Request


LIVE_RELOAD_SCRIPT = """
<script>
(function() {
  let _ts = null;
  setInterval(() => {
    fetch('/__ping__')
      .then(r => r.json())
      .then(d => { if (_ts !== null && d.ts !== _ts) location.reload(); _ts = d.ts; })
      .catch(() => {});
  }, 500);
})();
</script>"""


# ══════════════════════════════════════════════════════════
# PAGE CONFIG — override por página
# ══════════════════════════════════════════════════════════


class PageConfig:
    """
    Configura opciones específicas de una página.
    Úsalo retornando (widget, config) desde tu función de página.

    Ejemplo:
        def home():
            return Column(...), PageConfig(
                header=False,           # sin header en esta página
                footer=MyFooter(),      # footer personalizado
                title="Inicio — Mi App",
            )
    """

    def __init__(
        self,
        header=None,
        footer=None,
        title=None,
        theme=None,
        description=None,
        keywords=None,
        og_image=None,
        canonical=None,
        noindex=False,
        schema=None,
        og_type="website",
    ):
        self.header = header  # False = sin header | Widget = header custom
        self.footer = footer  # False = sin footer | Widget = footer custom
        self.title = title  # str = título custom para esta página
        self.theme = theme  # "dark"|"light"|"auto" override
        self.description = description  # meta description (160 chars ideal)
        self.keywords = keywords  # str o list de keywords
        self.og_image = og_image  # URL imagen Open Graph
        self.canonical = canonical  # URL canónica absoluta
        self.noindex = noindex  # True = noindex,nofollow
        self.schema = schema  # dict → JSON-LD structured data
        self.og_type = og_type  # "website"|"article"|"product"


# ══════════════════════════════════════════════════════════
# ROUTER
# ══════════════════════════════════════════════════════════


class Router:
    """
    router = Router()

    @router.page("/")
    def home():
        return Column(...)

    # Con PageConfig:
    @router.page("/landing")
    def landing():
        return Column(...), PageConfig(header=False, footer=False)

    App(router=router).run()
    """

    def __init__(self):
        self._routes = {}
        self._titles = {}
        self._app = None  # set by App after creation

    def page(self, path, title=None):
        def decorator(fn):
            self._routes[path] = fn
            if title:
                self._titles[path] = title
            return fn

        return decorator

    def add(self, path, fn, title=None):
        self._routes[path] = fn
        if title:
            self._titles[path] = title
        # Auto-registrar endpoints si la función tiene un módulo con register_routes
        if self._app is not None:
            mod = getattr(fn, "__module__", None)
            if mod and mod in sys.modules:
                m = sys.modules[mod]
                if hasattr(m, "register_routes") and callable(m.register_routes):
                    try:
                        m.register_routes(self._app)
                    except Exception as e:
                        print(f"  ⚠️  register_routes en '{mod}': {e}")

    def resolve(self, path):
        if path in self._routes:
            return self._routes[path], self._titles.get(path)
        stripped = path.rstrip("/") or "/"
        if stripped in self._routes:
            return self._routes[stripped], self._titles.get(stripped)
        return None, None

    def paths(self):
        return list(self._routes.keys())


# ══════════════════════════════════════════════════════════
# APP
# ══════════════════════════════════════════════════════════


class App:
    """
    App(build=build, title="Mi App").run()

    App(
        router=router,
        title="Mi App",
        theme="dark",           # "dark" | "light" | "auto" (default)
        theme_toggle=True,      # botón flotante para cambiar tema
        header=MyHeader(),      # header global (Widget)
        footer=MyFooter(),      # footer global (Widget)
    ).run()

    Las páginas pueden sobreescribir header/footer retornando (widget, PageConfig(...)).
    """

    def __init__(
        self,
        build=None,
        router=None,
        title="Martin App",
        port=309,
        hot_reload=True,
        theme="auto",
        theme_toggle=True,
        header=None,
        footer=None,
        # SEO global
        site_url=None,
        description=None,
        keywords=None,
        og_image=None,
        twitter_handle=None,
        lang="es",
        favicon=None,
        assets_dir="assets",
        styles="",
        global_css="",
    ):
        if build is None and router is None:
            raise ValueError("Debes pasar 'build' o 'router'")

        self._build_fn = build
        self._router = router
        self._source_file = None
        self.title = title
        self.port = port
        self.hot_reload = hot_reload
        self.theme = theme
        self.theme_toggle = theme_toggle
        self.header = header
        self.footer = footer
        self.assets_dir = assets_dir
        self.global_styles = styles or global_css
        self._export_mode = False  # set True by exporter
        self._ts = str(time.time())
        self._lock = threading.Lock()
        self._api_routes = {}
        # SEO
        self.site_url = (site_url or "").rstrip("/")
        self.description = description or ""
        self.keywords = keywords or ""
        self.og_image = og_image or ""
        self.twitter_handle = twitter_handle or ""
        self.lang = lang
        self.favicon = favicon or ""

        # Link router back to app so router.add() can auto-register routes
        if self._router:
            self._router._app = self
            # Scan already-added pages for register_routes
            self._scan_router_routes()

    # ── API routes ───────────────────────────────────────────────────────────

    def route(self, path, methods=None):
        """
        Registra un endpoint de API.

            @app.route("/api/datos")
            def datos(req):
                return {"clave": "valor"}          # dict -> JSON 200

            @app.route("/api/guardar", methods=["POST"])
            def guardar(req):
                body = req.json()
                return Response({"ok": True, "data": body})
        """
        if methods is None:
            methods = ["GET", "POST"]

        def decorator(fn):
            for m in methods:
                self._api_routes[(m.upper(), path)] = fn
            return fn

        return decorator

    def _scan_router_routes(self):
        """Llama register_routes(app) en todos los módulos de páginas ya registradas."""
        if not self._router:
            return
        seen = set()
        for fn in self._router._routes.values():
            mod_name = getattr(fn, "__module__", None)
            if not mod_name or mod_name in seen:
                continue
            seen.add(mod_name)
            mod = sys.modules.get(mod_name)
            if (
                mod
                and hasattr(mod, "register_routes")
                and callable(mod.register_routes)
            ):
                try:
                    mod.register_routes(self)
                except Exception as e:
                    print(f"  ⚠️  register_routes en '{mod_name}': {e}")

    def _handle_api(self, method, path, qs, body, headers):
        import json as _json, traceback

        handler = self._api_routes.get((method, path))
        if handler is None:
            has_path = any(p == path for _, p in self._api_routes)
            if has_path:
                return Response({"error": f"Metodo {method} no permitido"}, status=405)
            return Response({"error": f"Ruta '{path}' no encontrada"}, status=404)
        req = Request(method, path, qs, body, headers)
        try:
            result = handler(req)
            if isinstance(result, (dict, list)):
                return Response(result)
            elif isinstance(result, Response):
                return result
            else:
                return Response(str(result), content_type="text/plain")
        except Exception:
            tb = traceback.format_exc()
            print(f"  Error en {method} {path}:\n{tb}")
            return Response({"error": "Error interno", "detail": tb}, status=500)

    # ── Nav ───────────────────────────────────────────────────────────────────

    def _nav_html(self, current_path):
        if not self._router or len(self._router.paths()) <= 1:
            return ""

        # Buscar icono en assets/ — icon.* tiene prioridad, luego logo.*
        icon_html = ""
        for name_ext in (
            "icon.png",
            "icon.svg",
            "icon.webp",
            "logo.png",
            "logo.svg",
            "logo.webp",
            "logo.jpg",
        ):
            if os.path.exists(os.path.join(self.assets_dir, name_ext)):
                _pfx = "assets/" if self._export_mode else "/assets/"
                icon_html = (
                    f'<img src="{_pfx}{name_ext}" '
                    f'style="height:28px;width:28px;object-fit:contain;border-radius:6px;flex-shrink:0">'
                )
                break

        # Siempre muestra título; con icono a la izquierda si existe
        inner = icon_html
        inner += (
            f'<span style="font-weight:800;font-size:17px;letter-spacing:-0.3px;'
            f'color:var(--text)">{self.title}</span>'
        )
        _home_href = "index.html" if self._export_mode else "/"
        logo_html = (
            f'<a href="{_home_href}" style="display:flex;align-items:center;gap:8px;'
            f'text-decoration:none;margin-right:16px;flex-shrink:0">{inner}</a>'
        )

        links = []
        for path in self._router.paths():
            _, title = self._router.resolve(path)
            label = title or path.strip("/").capitalize() or "Inicio"
            is_active = path == current_path
            color = (
                "color:var(--accent);font-weight:600"
                if is_active
                else "color:var(--nav-text)"
            )
            links.append(
                f'<a href="{(path.lstrip("/") + ".html").replace("//","/") if self._export_mode and path != "/" else ("index.html" if self._export_mode else path)}"'
                f' style="text-decoration:none;font-size:14px;'
                f'font-weight:500;transition:color 0.2s;{color}"'
                f" onmouseover=\"this.style.color='var(--text)'\""
                f' onmouseout="this.style.color=\'{("var(--accent)" if is_active else "var(--nav-text)")}\'">{ label}</a>'
            )

        return (
            f'<nav style="display:flex;align-items:center;gap:28px;padding:0 32px;'
            f"height:56px;background:var(--nav-bg);"
            f"backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px);"
            f"border-bottom:1px solid var(--nav-border);"
            f'position:sticky;top:0;z-index:100">'
            f'{logo_html}{"".join(links)}</nav>'
        )

    # ── Render header/footer ──────────────────────────────────────────────────

    def _render_widget(self, widget):
        if widget is None or widget is False:
            return ""
        return widget.render() if hasattr(widget, "render") else str(widget)

    # ── HTML shell ────────────────────────────────────────────────────────────

    def _wrap(
        self,
        body,
        path="/",
        page_title=None,
        reload=True,
        page_header=None,
        page_footer=None,
        page_theme=None,
        page_desc=None,
        page_keywords=None,
        page_og_image=None,
        page_canonical=None,
        page_noindex=False,
        page_schema=None,
        page_og_type="website",
    ):

        # Resolver header y footer para esta página
        # False = desactivado | None = usar global | Widget = override
        use_header = page_header if page_header is not None else self.header
        use_footer = page_footer if page_footer is not None else self.footer

        header_html = self._render_widget(use_header)
        footer_html = self._render_widget(use_footer)
        nav_html = self._nav_html(path)
        script = LIVE_RELOAD_SCRIPT if (reload and self.hot_reload) else ""
        title = page_title or self.title
        theme = page_theme or self.theme
        if self.theme_toggle:
            toggle = (
                '<button id="_martin_theme_btn"'
                + ' onclick="window._martinCycleTheme()"'
                + ' title="Cambiar tema"'
                + ' style="position:fixed;bottom:20px;right:20px;z-index:9999;'
                + "        width:40px;height:40px;border-radius:50%;font-size:18px;"
                + "        border:1px solid var(--border);background:var(--surface);"
                + '        cursor:pointer;box-shadow:var(--shadow);backdrop-filter:blur(12px);transition:all .2s"'
                + " onmouseover=\"this.style.borderColor='var(--accent)'\""
                + " onmouseout=\"this.style.borderColor=''\">&#127763;</button>"
            )
        else:
            toggle = ""

        # Inyectar theme en el JS
        toggle_js = THEME_TOGGLE_JS.replace("'INITIAL_THEME'", f"'{theme}'")

        # ── SEO meta tags ─────────────────────────────────────────────
        import json as _json

        desc = page_desc or self.description
        kw = page_keywords or self.keywords
        og_img = page_og_image or self.og_image
        canonical = page_canonical
        noindex = page_noindex
        schema = page_schema
        og_type = page_og_type
        tw = self.twitter_handle
        full_url = (self.site_url + path) if self.site_url else ""
        canonical = canonical or full_url

        if isinstance(kw, list):
            kw = ", ".join(kw)

        # robots
        robots_content = (
            "noindex,nofollow"
            if noindex
            else "index,follow,max-snippet:-1,max-image-preview:large"
        )

        # Build meta tags string
        seo_tags = []

        # Basic
        if desc:
            seo_tags.append(f'  <meta name="description" content="{desc}">')
        if kw:
            seo_tags.append(f'  <meta name="keywords" content="{kw}">')
        seo_tags.append(f'  <meta name="robots" content="{robots_content}">')

        # Canonical
        if canonical:
            seo_tags.append(f'  <link rel="canonical" href="{canonical}">')

        # Open Graph
        seo_tags.append(f'  <meta property="og:type" content="{og_type}">')
        seo_tags.append(f'  <meta property="og:title" content="{title}">')
        if desc:
            seo_tags.append(f'  <meta property="og:description" content="{desc}">')
        if canonical:
            seo_tags.append(f'  <meta property="og:url" content="{canonical}">')
        if og_img:
            seo_tags.append(f'  <meta property="og:image" content="{og_img}">')
            seo_tags.append(f'  <meta property="og:image:width" content="1200">')
            seo_tags.append(f'  <meta property="og:image:height" content="630">')
        seo_tags.append(f'  <meta property="og:site_name" content="{self.title}">')
        seo_tags.append(f'  <meta property="og:locale" content="{self.lang}">')

        # Twitter Card
        tw_card = "summary_large_image" if og_img else "summary"
        seo_tags.append(f'  <meta name="twitter:card" content="{tw_card}">')
        seo_tags.append(f'  <meta name="twitter:title" content="{title}">')
        if desc:
            seo_tags.append(f'  <meta name="twitter:description" content="{desc}">')
        if og_img:
            seo_tags.append(f'  <meta name="twitter:image" content="{og_img}">')
        if tw:
            handle = tw if tw.startswith("@") else f"@{tw}"
            seo_tags.append(f'  <meta name="twitter:site" content="{handle}">')

        # Favicon
        # Auto-detect favicon: explicit > assets/icon.* > assets/favicon.* > assets/logo.*
        favicon = self.favicon
        if not favicon:
            for _fn in (
                "icon.png",
                "icon.svg",
                "icon.webp",
                "favicon.png",
                "favicon.ico",
                "logo.png",
            ):
                if os.path.exists(os.path.join(self.assets_dir, _fn)):
                    favicon = f"/assets/{_fn}"
                    break
        if favicon:
            ext = favicon.rsplit(".", 1)[-1].lower()
            mime = {
                "png": "image/png",
                "jpg": "image/jpeg",
                "jpeg": "image/jpeg",
                "svg": "image/svg+xml",
                "ico": "image/x-icon",
                "webp": "image/webp",
            }.get(ext, "image/x-icon")
            seo_tags.append(f'  <link rel="icon" type="{mime}" href="{favicon}">')
        else:
            seo_tags.append(
                "  <link rel=\"icon\" href=\"data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'><text y='26' font-size='28'>🅜</text></svg>\">"
            )

        # Performance hints
        seo_tags.append('  <meta http-equiv="X-UA-Compatible" content="IE=edge">')
        seo_tags.append('  <meta name="theme-color" content="#6366f1">')
        if self.site_url:
            seo_tags.append(f'  <link rel="preconnect" href="{self.site_url}">')

        # JSON-LD structured data
        schema_tag = ""
        if schema:
            schema_str = _json.dumps(schema, ensure_ascii=False)
            schema_tag = f'  <script type="application/ld+json">{schema_str}</script>'

        seo_html = "\n".join(seo_tags)
        if schema_tag:
            seo_html += "\n" + schema_tag

        return f"""<!DOCTYPE html>
<html lang="{self.lang}" data-theme="{theme}">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
{seo_html}
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
           line-height: 1.5; min-height: 100vh; }}
    img {{ display: block; max-width: 100%; }}
    a {{ color: inherit; }}
    {THEME_CSS}
    {self.global_styles}
  </style>
  {toggle_js}
</head>
<body>
  {nav_html}
  {header_html}
  {body}
  {footer_html}
  {toggle}
  {script}
</body>
</html>"""

    # ── Render ────────────────────────────────────────────────────────────────

    def _render(self, path="/"):
        with self._lock:
            try:
                page_cfg = None
                if self._router:
                    fn, page_title = self._router.resolve(path)
                    if fn is None:
                        widget = self._not_found(path)
                        page_title = "404"
                    else:
                        result = fn()
                        # Soporte para (widget, PageConfig) tuple
                        if isinstance(result, tuple):
                            widget, page_cfg = result
                        else:
                            widget = result
                else:
                    result = self._build_fn()
                    if isinstance(result, tuple):
                        widget, page_cfg = result
                    else:
                        widget = result
                    page_title = None

            except Exception:
                import traceback

                tb = traceback.format_exc()
                return self._wrap(
                    f'<pre style="color:#f87171;padding:32px;font-size:13px;'
                    f'line-height:1.6">Error:\n\n{tb}</pre>',
                    path=path,
                )

        body = widget.render() if hasattr(widget, "render") else str(widget)

        # Extraer overrides de PageConfig si existe
        p_header = page_cfg.header if page_cfg else None
        p_footer = page_cfg.footer if page_cfg else None
        p_title = (
            page_cfg.title if page_cfg and page_cfg.title else None
        ) or page_title
        p_theme = page_cfg.theme if page_cfg and page_cfg.theme else None

        p_desc = page_cfg.description if page_cfg and page_cfg.description else None
        p_keywords = page_cfg.keywords if page_cfg and page_cfg.keywords else None
        p_og_image = page_cfg.og_image if page_cfg and page_cfg.og_image else None
        p_canonical = page_cfg.canonical if page_cfg and page_cfg.canonical else None
        p_noindex = page_cfg.noindex if page_cfg else False
        p_schema = page_cfg.schema if page_cfg and page_cfg.schema else None
        p_og_type = page_cfg.og_type if page_cfg and page_cfg.og_type else "website"
        return self._wrap(
            body,
            path=path,
            page_title=p_title,
            page_header=p_header,
            page_footer=p_footer,
            page_theme=p_theme,
            page_desc=p_desc,
            page_keywords=p_keywords,
            page_og_image=p_og_image,
            page_canonical=p_canonical,
            page_noindex=p_noindex,
            page_schema=p_schema,
            page_og_type=p_og_type,
        )

    def _not_found(self, path):
        from .widgets import Column, Heading, Text, Button

        return Column(
            padding=64,
            gap=16,
            style="align-items:center;text-align:center",
            children=[
                Heading("404", level=1, style="font-size:72px;opacity:0.3"),
                Heading(f"'{path}' no encontrada", level=2),
                Button("← Inicio", href="/", variant="ghost"),
            ],
        )

    def export(self, path="index.html", router_path="/"):
        html = self._render(router_path)
        html = html.replace(LIVE_RELOAD_SCRIPT, "")
        Path(path).write_text(html, encoding="utf-8")
        print(f"  OK  {path}")

    def export_all(self, out_dir="dist"):
        out = Path(out_dir)
        out.mkdir(parents=True, exist_ok=True)
        routes = self._router.paths() if self._router else ["/"]
        for rpath in routes:
            fname = "index.html" if rpath == "/" else rpath.strip("/") + ".html"
            self.export(str(out / fname), router_path=rpath)

    # ── Hot reload ────────────────────────────────────────────────────────────

    def _reload_from_file(self, source_file):
        try:
            spec = importlib.util.spec_from_file_location("_martin_hot_", source_file)
            fresh = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(fresh)

            with self._lock:
                # Router: reemplazar y re-vincular
                if self._router and hasattr(fresh, "router"):
                    self._router = fresh.router
                    self._router._app = self
                elif self._build_fn and hasattr(fresh, self._build_fn.__name__):
                    self._build_fn = getattr(fresh, self._build_fn.__name__)

                # Si fresh tiene app (instancia App), tomar su router y rutas
                from martin import App as _App

                if hasattr(fresh, "app") and isinstance(fresh.app, _App):
                    if fresh.app._router:
                        self._router = fresh.app._router
                        self._router._app = self
                    # Copiar rutas de API registradas en el app fresco
                    self._api_routes = dict(fresh.app._api_routes)

                # Header / footer
                if hasattr(fresh, "header"):
                    self.header = fresh.header
                if hasattr(fresh, "footer"):
                    self.footer = fresh.footer

            # Re-escanear register_routes de todas las páginas
            (
                self._api_routes.clear()
                if not (hasattr(fresh, "app") and hasattr(fresh.app, "_api_routes"))
                else None
            )
            self._scan_router_routes()

            self._ts = str(time.time())
            print(f"  ↻  recargado")
        except Exception:
            import traceback

            print(f"  Error al recargar:\n{traceback.format_exc()}")
            self._ts = str(time.time())

    def _start_watcher(self, watch_dir, source_file):
        app = self

        def on_change(fp):
            # Eliminar de sys.modules el archivo cambiado y todos los del proyecto
            # para que main.py los reimporte frescos al recargar
            changed = os.path.abspath(fp)
            to_remove = []
            for mod_name, mod in list(sys.modules.items()):
                mod_file = getattr(mod, "__file__", None)
                if mod_file and os.path.abspath(mod_file).startswith(
                    os.path.abspath(watch_dir)
                ):
                    to_remove.append(mod_name)
            for mod_name in to_remove:
                sys.modules.pop(mod_name, None)
            app._reload_from_file(source_file)

        try:
            from watchdog.observers import Observer
            from watchdog.events import FileSystemEventHandler

            class Handler(FileSystemEventHandler):
                def on_modified(self, event):
                    if not event.is_directory and event.src_path.endswith(".py"):
                        on_change(event.src_path)

            observer = Observer()
            observer.schedule(Handler(), watch_dir, recursive=True)
            observer.daemon = True
            observer.start()
            print(f"  👁  watchdog activo")
        except ImportError:
            print(f"  👁  hot reload activo (polling)")
            mtimes = {}

            def poll():
                while True:
                    for root, _, files in os.walk(watch_dir):
                        for f in files:
                            if not f.endswith(".py"):
                                continue
                            fp = os.path.join(root, f)
                            try:
                                mt = os.path.getmtime(fp)
                            except OSError:
                                continue
                            if fp in mtimes and mtimes[fp] != mt:
                                mtimes[fp] = mt
                                on_change(fp)
                            else:
                                mtimes[fp] = mt
                    time.sleep(0.6)

            threading.Thread(target=poll, daemon=True).start()

    # ── HTTP server ───────────────────────────────────────────────────────────

    def run(self, open_browser=True, watch_dir=".", source_file=None):
        if source_file is None:
            source_file = self._source_file
        if source_file is None:
            main = sys.modules.get("__main__")
            if main and hasattr(main, "__file__") and main.__file__:
                source_file = os.path.abspath(main.__file__)

        app = self

        class Handler(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                parts = self.path.split("?", 1)
                path = parts[0]
                qs = parts[1] if len(parts) > 1 else ""
                if path == "/__ping__":
                    self._send_json({"ts": app._ts})
                elif path.startswith("/assets/"):
                    self._static(path[1:])
                elif ("GET", path) in app._api_routes:
                    self._api("GET", path, qs, b"")
                else:
                    self._html(app._render(path))

            def do_POST(self):
                parts = self.path.split("?", 1)
                path = parts[0]
                qs = parts[1] if len(parts) > 1 else ""
                length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(length) if length else b""
                self._api("POST", path, qs, body)

            def do_PUT(self):
                parts = self.path.split("?", 1)
                path = parts[0]
                qs = parts[1] if len(parts) > 1 else ""
                length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(length) if length else b""
                self._api("PUT", path, qs, body)

            def do_DELETE(self):
                parts = self.path.split("?", 1)
                path = parts[0]
                qs = parts[1] if len(parts) > 1 else ""
                self._api("DELETE", path, qs, b"")

            def _api(self, method, path, qs, body):
                resp = app._handle_api(method, path, qs, body, dict(self.headers))
                data, ct = resp.to_bytes()
                self.send_response(resp.status)
                self.send_header("Content-Type", ct)
                self.send_header("Content-Length", str(len(data)))
                self.send_header("Access-Control-Allow-Origin", "*")
                for k, v in resp.headers.items():
                    self.send_header(k, v)
                self.end_headers()
                self.wfile.write(data)

            def _html(self, content):
                data = content.encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)

            def _send_json(self, obj):
                import json

                data = json.dumps(obj).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)

            def _static(self, path):
                if os.path.exists(path):
                    with open(path, "rb") as f:
                        data = f.read()
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(data)
                else:
                    self.send_response(404)
                    self.end_headers()

            def log_message(self, *a):
                pass

        if self.hot_reload and source_file:
            self._start_watcher(watch_dir, source_file)

        url = f"http://localhost:{self.port}"
        hl = "activado" if self.hot_reload else "desactivado"
        pages = ""
        if self._router:
            pages = "  📄  " + ", ".join(self._router.paths()) + "\n"
        print(f"\n  🌐  martin -> {url}")
        print(f"  ⚡  Hot reload: {hl}  |  Tema: {self.theme}")
        print(f"{pages}  Ctrl+C para parar\n")

        if open_browser:
            threading.Timer(0.8, lambda: webbrowser.open(url)).start()

        server = http.server.HTTPServer(("", self.port), Handler)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\n👋")
            server.shutdown()
