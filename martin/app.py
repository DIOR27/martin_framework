"""
Martin — App, Router & Dev Server
"""

import os, sys, time, threading, importlib.util
import http.server, webbrowser
from pathlib import Path


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
# ROUTER — registra páginas
# ══════════════════════════════════════════════════════════


class Router:
    """
    Define las páginas de la app.

    router = Router()

    @router.page("/")
    def home():
        return Column(children=[Heading("Inicio")])

    @router.page("/about")
    def about():
        return Column(children=[Heading("Sobre nosotros")])

    App(router=router).run()
    """

    def __init__(self):
        self._routes: dict[str, callable] = {}
        self._titles: dict[str, str] = {}

    def page(self, path: str, title: str = None):
        """Decorador para registrar una página."""

        def decorator(fn):
            self._routes[path] = fn
            if title:
                self._titles[path] = title
            return fn

        return decorator

    def add(self, path: str, fn: callable, title: str = None):
        """Registra una página sin decorador."""
        self._routes[path] = fn
        if title:
            self._titles[path] = title

    def resolve(self, path: str):
        """Devuelve (fn, title) para un path, o (None, None) si no existe."""
        # Exact match
        if path in self._routes:
            return self._routes[path], self._titles.get(path)
        # Strip trailing slash
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
    Modo página única:
        App(build=build, title="Mi App").run()

    Modo multi-página con Router:
        router = Router()

        @router.page("/", title="Inicio")
        def home(): return Column(...)

        @router.page("/about", title="Acerca de")
        def about(): return Column(...)

        App(router=router, title="Mi App").run()

    Modo multi-página con ficheros separados:
        App(router=router, title="Mi App").run()
        # Cada página en su propio .py, importada en main.py
    """

    def __init__(
        self,
        build=None,
        router=None,
        title="Martin App",
        port=309,
        hot_reload=True,
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
        self.assets_dir = assets_dir
        self.global_styles = styles or global_css
        self._ts = str(time.time())
        self._lock = threading.Lock()

    # ── HTML shell ────────────────────────────────────────────────────────────

    def _nav_html(self, current_path: str) -> str:
        """Genera nav automática si hay router con varias páginas."""
        if not self._router or len(self._router.paths()) <= 1:
            return ""

        # Logo: busca assets/logo.png, logo.svg, logo.webp
        logo_html = ""
        for ext in ("png", "svg", "webp", "jpg"):
            logo_path = os.path.join(self.assets_dir, f"logo.{ext}")
            if os.path.exists(logo_path):
                logo_html = (
                    f'<a href="/" style="display:flex;align-items:center;margin-right:16px">'
                    f'<img src="/assets/logo.{ext}" style="height:32px;width:auto;display:block"></a>'
                )
                break
        # Fallback: nombre de la app como texto si no hay imagen
        if not logo_html:
            logo_html = (
                f'<a href="/" style="font-weight:800;font-size:18px;letter-spacing:-0.5px;'
                f'text-decoration:none;color:#f1f5f9;margin-right:16px">'
                f"{self.title}</a>"
            )

        links = []
        for path in self._router.paths():
            _, title = self._router.resolve(path)
            label = title or path.strip("/").capitalize() or "Inicio"
            is_active = path == current_path
            active_style = (
                "color:#a5b4fc;font-weight:600"
                if is_active
                else "color:rgba(203,213,225,0.75)"
            )
            links.append(
                f'<a href="{path}" style="text-decoration:none;font-size:14px;'
                f'font-weight:500;transition:color 0.2s;{active_style}"'
                f" onmouseover=\"if(!this.dataset.active)this.style.color='#f1f5f9'\""
                f" onmouseout=\"if(!this.dataset.active)this.style.color='rgba(203,213,225,0.75)'\""
                f'{"data-active=1" if is_active else ""}>{label}</a>'
            )
        nav_links = "\n".join(links)
        return (
            f'<nav style="display:flex;align-items:center;gap:28px;padding:0 32px;'
            f"height:56px;"
            f"background:rgba(6,8,24,0.85);"
            f"backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px);"
            f"border-bottom:1px solid rgba(255,255,255,0.08);"
            f'position:sticky;top:0;z-index:100">'
            f"{logo_html}"
            f"{nav_links}"
            f"</nav>"
        )

    def _wrap(
        self, body: str, path: str = "/", page_title: str = None, reload=True
    ) -> str:
        script = LIVE_RELOAD_SCRIPT if (reload and self.hot_reload) else ""
        title = page_title or self.title
        nav = self._nav_html(path)
        return f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    html, body {{ background: #060818; }}
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
           line-height: 1.5; color: #f1f5f9; min-height: 100vh; }}
    img {{ display: block; max-width: 100%; }}
    a {{ color: inherit; }}
    {self.global_styles}
  </style>
</head>
<body>
  {nav}
  {body}
  {script}
</body>
</html>"""

    # ── Render ────────────────────────────────────────────────────────────────

    def _render(self, path: str = "/") -> str:
        with self._lock:
            try:
                if self._router:
                    fn, page_title = self._router.resolve(path)
                    if fn is None:
                        widget = self._not_found(path)
                        page_title = "404"
                    else:
                        widget = fn()
                else:
                    widget = self._build_fn()
                    page_title = None
            except Exception:
                import traceback

                tb = traceback.format_exc()
                return self._wrap(
                    f'<pre style="color:#f87171;padding:32px;font-size:13px;'
                    f'line-height:1.6;background:#1e1e2e">⚠️  Error:\n\n{tb}</pre>',
                    path=path,
                )

        body = widget.render() if hasattr(widget, "render") else str(widget)
        return self._wrap(body, path=path, page_title=page_title)

    def _not_found(self, path: str):
        from .widgets import Column, Heading, Text, Button

        return Column(
            padding=64,
            gap=16,
            style="align-items:center;text-align:center",
            children=[
                Heading("404", level=1, style="font-size:72px;opacity:0.3"),
                Heading(f"Página '{path}' no encontrada", level=2),
                Button("← Volver al inicio", href="/", variant="ghost"),
            ],
        )

    def export(self, path="index.html", router_path="/"):
        html = self._render(router_path).replace(LIVE_RELOAD_SCRIPT, "")
        Path(path).write_text(html, encoding="utf-8")
        print(f"✅ Exportado → {path}")

    def export_all(self, out_dir="dist"):
        """Exporta todas las páginas del router a ficheros HTML."""
        out = Path(out_dir)
        out.mkdir(parents=True, exist_ok=True)
        if self._router:
            for rpath in self._router.paths():
                fname = "index.html" if rpath == "/" else rpath.strip("/") + ".html"
                self.export(str(out / fname), router_path=rpath)
        else:
            self.export(str(out / "index.html"))

    # ── Hot reload ────────────────────────────────────────────────────────────

    def _reload_from_file(self, source_file: str):
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

            self._ts = str(time.time())
            print(f"  ↻  {os.path.basename(source_file)}")
        except Exception:
            import traceback

            print(f"  ⚠️  Error al recargar:\n{traceback.format_exc()}")
            self._ts = str(time.time())

    def _start_watcher(self, watch_dir: str, source_file: str):
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
            print(f"  👁  watchdog activo en '{watch_dir}'")

        except ImportError:
            print(f"  👁  hot reload activo (polling)")
            mtimes: dict = {}

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
                path = self.path.split("?")[0]  # ignora query params
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
        elif self.hot_reload:
            print("  ⚠️  No se pudo detectar el fichero fuente para hot reload")

        url = f"http://localhost:{self.port}"
        hl = "activado ↻" if self.hot_reload else "desactivado"
        pages = (
            f"  📄  Páginas: {', '.join(self._router.paths())}\n"
            if self._router
            else ""
        )
        print(f"\n  🌐  martin → {url}")
        print(f"  ⚡  Hot reload: {hl}")
        print(f"{pages}  ✋  Ctrl+C para parar\n")

        if open_browser:
            threading.Timer(0.8, lambda: webbrowser.open(url)).start()

        server = http.server.HTTPServer(("", self.port), Handler)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\n👋")
            server.shutdown()
