"""
Martin — App & Dev Server
Hot reload real: recarga el módulo Python en cada cambio, no solo el HTML.
"""

import os, sys, time, threading, importlib, importlib.util
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
    """
    App(build=build, title="Mi App").run()
    App(build=build, port=3000, hot_reload=False).run()
    """

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
        self.title = title
        self.port = port
        self.hot_reload = hot_reload
        self.assets_dir = assets_dir
        self.global_styles = styles
        self._ts = str(time.time())  # cambia cuando hay reload
        self._lock = threading.Lock()
        # Guardamos referencia al módulo fuente para poder recargarlo
        self._source_module = getattr(build, "__module__", None)

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
            widget = self._build_fn()
        body = widget.render() if hasattr(widget, "render") else str(widget)
        return self._wrap(body)

    def export(self, path="index.html"):
        html = self._wrap(self._build_fn().render(), reload=False)
        Path(path).write_text(html, encoding="utf-8")
        print(f"✅ Exportado → {path}")

    # ── File watcher con reload real del módulo ───────────────────────────────

    def _start_watcher(self, watch_dir: str):
        """
        Observa cambios en .py y recarga el módulo fuente con importlib.reload.
        No necesita watchdog: usa polling puro (compatible en todos los OS).
        Si watchdog está instalado, lo usa para mayor eficiencia.
        """
        app = self

        def _reload_module():
            """Recarga el módulo donde está definida la función build."""
            mod_name = app._source_module
            if not mod_name or mod_name == "__main__":
                # Caso especial: el script se ejecutó directamente
                # Recargamos el módulo __main__ buscando su fichero
                main = sys.modules.get("__main__")
                if main and hasattr(main, "__file__") and main.__file__:
                    try:
                        spec = importlib.util.spec_from_file_location(
                            "__main__reload__", main.__file__
                        )
                        fresh = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(fresh)
                        # Actualizamos la función build al símbolo recién cargado
                        fn_name = app._build_fn.__name__
                        if hasattr(fresh, fn_name):
                            with app._lock:
                                app._build_fn = getattr(fresh, fn_name)
                    except Exception as e:
                        print(f"  ⚠️  Error recargando: {e}")
            else:
                mod = sys.modules.get(mod_name)
                if mod:
                    try:
                        importlib.reload(mod)
                        fn_name = app._build_fn.__name__
                        with app._lock:
                            app._build_fn = getattr(mod, fn_name)
                    except Exception as e:
                        print(f"  ⚠️  Error recargando: {e}")

            app._ts = str(time.time())

        # Intenta usar watchdog, si no, polling
        try:
            from watchdog.observers import Observer
            from watchdog.events import FileSystemEventHandler

            class Handler(FileSystemEventHandler):
                def on_modified(self, event):
                    if not event.is_directory and event.src_path.endswith(".py"):
                        name = os.path.basename(event.src_path)
                        print(f"  ↻  {name}")
                        _reload_module()

            observer = Observer()
            observer.schedule(Handler(), watch_dir, recursive=True)
            observer.daemon = True
            observer.start()
            print(f"  👁  watchdog activo en '{watch_dir}'")

        except ImportError:
            # Polling manual — funciona sin dependencias
            print(
                f"  👁  polling activo en '{watch_dir}' (instala watchdog para mejor rendimiento)"
            )
            mtimes: dict = {}

            def poll():
                while True:
                    changed = False
                    for root, _, files in os.walk(watch_dir):
                        for f in files:
                            if not f.endswith(".py"):
                                continue
                            fp = os.path.join(root, f)
                            try:
                                mt = os.path.getmtime(fp)
                            except OSError:
                                continue
                            if fp not in mtimes:
                                mtimes[fp] = mt
                            elif mtimes[fp] != mt:
                                mtimes[fp] = mt
                                print(f"  ↻  {f}")
                                changed = True
                    if changed:
                        _reload_module()
                    time.sleep(0.6)

            t = threading.Thread(target=poll, daemon=True)
            t.start()

    # ── HTTP server ───────────────────────────────────────────────────────────

    def run(self, open_browser=True, watch_dir="."):
        app = self

        class Handler(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                if self.path == "/__ping__":
                    self._json({"ts": app._ts})
                elif self.path.startswith("/assets/"):
                    self._static(self.path[1:])
                else:
                    try:
                        html = app._render()
                        self._html(html)
                    except Exception as e:
                        self._html(
                            f"<pre style='color:red;padding:24px'>Error:\n{e}</pre>"
                        )

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

        url = f"http://localhost:{self.port}"

        if self.hot_reload:
            self._start_watcher(watch_dir)

        server = http.server.HTTPServer(("", self.port), Handler)

        hl = "activado ↻" if self.hot_reload else "desactivado"
        print(f"\n  🌐  martin → {url}")
        print(f"  ⚡  Hot reload: {hl}")
        print(f"  ✋  Ctrl+C para parar\n")

        if open_browser:
            threading.Timer(0.6, lambda: webbrowser.open(url)).start()

        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\n👋")
            server.shutdown()
