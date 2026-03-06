"""
Martin — App, Router & Dev Server
"""

import os, sys, time, threading, importlib.util
import http.server, webbrowser
from pathlib import Path
from .theme import THEME_CSS, THEME_TOGGLE_JS, THEME_TOGGLE_BTN


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

    def __init__(self, header=None, footer=None, title=None, theme=None):
        self.header = header  # False = sin header | Widget = header custom
        self.footer = footer  # False = sin footer | Widget = footer custom
        self.title = title  # str = título custom para esta página
        self.theme = theme  # "dark"|"light"|"auto" override para esta página


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
        # header=MyHeader(),      # header global (Widget)
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
        self._ts = str(time.time())
        self._lock = threading.Lock()

    # ── Nav ───────────────────────────────────────────────────────────────────

    def _nav_html(self, current_path):
        if not self._router or len(self._router.paths()) <= 1:
            return ""

        logo_html = ""
        for ext in ("png", "svg", "webp", "jpg"):
            if os.path.exists(os.path.join(self.assets_dir, f"logo.{ext}")):
                logo_html = (
                    f'<a href="/" style="display:flex;align-items:center;margin-right:16px">'
                    f'<img src="/assets/logo.{ext}" style="height:32px;width:auto"></a>'
                )
                break
        if not logo_html:
            logo_html = (
                f'<a href="/" style="font-weight:800;font-size:18px;letter-spacing:-0.5px;'
                f'text-decoration:none;color:var(--text);margin-right:16px">'
                f"{self.title}</a>"
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
                f'<a href="{path}" style="text-decoration:none;font-size:14px;'
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
        toggle = THEME_TOGGLE_BTN if self.theme_toggle else ""

        # Inyectar theme en el JS
        toggle_js = THEME_TOGGLE_JS.replace("'INITIAL_THEME'", f"'{theme}'")

        return f"""<!DOCTYPE html>
<html lang="es" data-theme="{theme}">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
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

        return self._wrap(
            body,
            path=path,
            page_title=p_title,
            page_header=p_header,
            page_footer=p_footer,
            page_theme=p_theme,
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
            if self._router and hasattr(fresh, "router"):
                with self._lock:
                    self._router = fresh.router
            elif self._build_fn and hasattr(fresh, self._build_fn.__name__):
                with self._lock:
                    self._build_fn = getattr(fresh, self._build_fn.__name__)
            # Recargar header/footer si son callables en el módulo
            if hasattr(fresh, "header"):
                self.header = fresh.header
            if hasattr(fresh, "footer"):
                self.footer = fresh.footer
            self._ts = str(time.time())
            print(f"  ↻  {os.path.basename(source_file)}")
        except Exception:
            import traceback

            print(f"  Error al recargar:\n{traceback.format_exc()}")
            self._ts = str(time.time())

    def _start_watcher(self, watch_dir, source_file):
        app = self

        def on_change(fp):
            app._reload_from_file(fp if fp.endswith("main.py") else source_file)

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
                path = self.path.split("?")[0]
                if path == "/__ping__":
                    self._json({"ts": app._ts})
                elif path.startswith("/assets/"):
                    self._static(path[1:])
                else:
                    self._html(app._render(path))

            def _html(self, content):
                data = content.encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)

            def _json(self, obj):
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
