"""
Martin — App & Dev Server
Hot reload: recarga el fichero desde disco en cada cambio.
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
      .then(d => {
        if (_ts !== null && d.ts !== _ts) location.reload();
        _ts = d.ts;
      })
      .catch(() => {});
  }, 500);
})();
</script>"""


class App:
    def __init__(
        self,
        build,
        title="Martin App",
        port=309,
        hot_reload=True,
        assets_dir="assets",
        styles="",
    ):
        self._build_fn = build
        self._source_file = None  # lo rellena el CLI o _detect_source
        self.title = title
        self.port = port
        self.hot_reload = hot_reload
        self.assets_dir = assets_dir
        self.global_styles = styles
        self._ts = str(time.time())
        self._lock = threading.Lock()

    # ── HTML ─────────────────────────────────────────────────────────────────

    def _wrap(self, body: str, reload=True) -> str:
        script = LIVE_RELOAD_SCRIPT if (reload and self.hot_reload) else ""
        return f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{self.title}</title>
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
           line-height: 1.5; color: #1a1a1a; background: #f9fafb; }}
    img {{ display: block; max-width: 100%; }}
    {self.global_styles}
  </style>
</head>
<body>
  {body}
  {script}
</body>
</html>"""

    def _render(self) -> str:
        with self._lock:
            try:
                widget = self._build_fn()
            except Exception as e:
                import traceback

                tb = traceback.format_exc()
                return self._wrap(
                    f'<pre style="color:red;padding:32px;font-size:13px;line-height:1.6">'
                    f"⚠️  Error en build():\n\n{tb}</pre>"
                )
        body = widget.render() if hasattr(widget, "render") else str(widget)
        return self._wrap(body)

    def export(self, path="index.html"):
        html = self._wrap(self._build_fn().render(), reload=False)
        Path(path).write_text(html, encoding="utf-8")
        print(f"✅ Exportado → {path}")

    # ── Hot reload ────────────────────────────────────────────────────────────

    def _reload_from_file(self, source_file: str):
        """Carga el fichero desde disco, sin tocar importlib.reload."""
        try:
            fn_name = self._build_fn.__name__
            spec = importlib.util.spec_from_file_location("_martin_hot_", source_file)
            fresh = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(fresh)
            if hasattr(fresh, fn_name):
                with self._lock:
                    self._build_fn = getattr(fresh, fn_name)
                self._ts = str(time.time())
                print(f"  ↻  {os.path.basename(source_file)}")
            else:
                print(f"  ⚠️  '{fn_name}' no encontrado en {source_file}")
                self._ts = str(time.time())  # recarga igual para mostrar el error
        except Exception as e:
            import traceback

            print(f"  ⚠️  Error al recargar:\n{traceback.format_exc()}")
            self._ts = str(time.time())

    def _start_watcher(self, watch_dir: str, source_file: str):
        app = self

        def on_change():
            app._reload_from_file(source_file)

        try:
            from watchdog.observers import Observer
            from watchdog.events import FileSystemEventHandler

            class Handler(FileSystemEventHandler):
                def on_modified(self, event):
                    if not event.is_directory and event.src_path.endswith(".py"):
                        on_change()

            observer = Observer()
            observer.schedule(Handler(), watch_dir, recursive=True)
            observer.daemon = True
            observer.start()
            print(f"  👁  watchdog activo en '{watch_dir}'")

        except ImportError:
            print(f"  👁  hot reload activo (polling cada 600ms)")
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
                                on_change()
                            else:
                                mtimes[fp] = mt
                    time.sleep(0.6)

            threading.Thread(target=poll, daemon=True).start()

    # ── HTTP server ───────────────────────────────────────────────────────────

    def run(self, open_browser=True, watch_dir=".", source_file=None):
        # source_file lo pasa el CLI; si se ejecuta directo (python main.py)
        # intentamos detectarlo desde __main__
        if source_file is None:
            source_file = self._source_file
        if source_file is None:
            main = sys.modules.get("__main__")
            if main and hasattr(main, "__file__") and main.__file__:
                source_file = os.path.abspath(main.__file__)

        app = self

        class Handler(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                if self.path == "/__ping__":
                    self._json({"ts": app._ts})
                elif self.path.startswith("/assets/"):
                    self._static(self.path[1:])
                else:
                    self._html(app._render())

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
        print(f"\n  🌐  martin → {url}")
        print(f"  ⚡  Hot reload: {hl}")
        print(f"  ✋  Ctrl+C para parar\n")

        if open_browser:
            threading.Timer(0.8, lambda: webbrowser.open(url)).start()

        server = http.server.HTTPServer(("", self.port), Handler)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\n👋")
            server.shutdown()
