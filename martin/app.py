"""
MARTIN - App & Dev Server
"""

import os
import threading
import time
import http.server
import webbrowser
from pathlib import Path


LIVE_RELOAD_SCRIPT = """
<script>
(function() {
    let lastModified = null;
    setInterval(() => {
        fetch('/__reload__')
            .then(r => r.json())
            .then(data => {
                if (lastModified && data.modified !== lastModified) {
                    location.reload();
                }
                lastModified = data.modified;
            }).catch(() => {});
    }, 800);
})();
</script>
"""


class App:
    """
    Entry point for a MARTIN app.

    Usage:
        from pyweave import App
        from .widgets import *

        def build():
            return Card(children=[
                Heading("Hello world"),
                Text("Welcome to MARTIN"),
            ])

        App(build=build, title="My App").run()
    """

    def __init__(
        self, build, title="Martin App", port=309, assets_dir="assets", styles=""
    ):
        self.build = build  # callable → Widget
        self.title = title
        self.port = port
        self.assets_dir = assets_dir
        self.global_styles = styles
        self._last_modified = str(time.time())

    # ── HTML generation ──────────────────────────────────────────────────────

    def _wrap_html(self, body_html: str, live_reload=True) -> str:
        reload_script = LIVE_RELOAD_SCRIPT if live_reload else ""
        return f"""<!DOCTYPE html>
<html lang="en">
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
  {body_html}
  {reload_script}
</body>
</html>"""

    def build_html(self, live_reload=True) -> str:
        widget = self.build()
        body = widget.render() if hasattr(widget, "render") else str(widget)
        return self._wrap_html(body, live_reload=live_reload)

    def export(self, path="index.html"):
        """Export static HTML file (no live reload)."""
        html = self.build_html(live_reload=False)
        Path(path).write_text(html, encoding="utf-8")
        print(f"✅ Exported → {path}")

    # ── Dev server ────────────────────────────────────────────────────────────

    def run(self, open_browser=True):
        app_ref = self

        class Handler(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                if self.path == "/__reload__":
                    self._json({"modified": app_ref._last_modified})
                elif self.path == "/" or self.path == "/index.html":
                    self._html(app_ref.build_html())
                elif self.path.startswith("/assets/"):
                    self._static(self.path[1:])
                else:
                    self._html(app_ref.build_html())

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

            def log_message(self, format, *args):
                pass  # Silence request logs

        server = http.server.HTTPServer(("", self.port), Handler)
        url = f"http://localhost:{self.port}"
        print(f"🌐 MARTIN dev server → {url}")
        print(f"   Hot reload: enabled | Ctrl+C to stop\n")

        if open_browser:
            threading.Timer(0.5, lambda: webbrowser.open(url)).start()

        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\n👋 Server stopped.")
            server.shutdown()

    # ── File watcher (optional, requires watchdog) ────────────────────────────

    def watch(self, path="."):
        """Start file watcher for hot reload. Call before run()."""
        try:
            from watchdog.observers import Observer
            from watchdog.events import FileSystemEventHandler

            app_ref = self

            class ChangeHandler(FileSystemEventHandler):
                def on_modified(self, event):
                    if event.src_path.endswith(".py"):
                        app_ref._last_modified = str(time.time())
                        print(f"  ↻ Reloaded ({event.src_path})")

            observer = Observer()
            observer.schedule(ChangeHandler(), path, recursive=True)
            observer.start()
            print(f"👁️  Watching {path} for changes...")
            return observer
        except ImportError:
            print("⚠️  Install watchdog for hot reload: pip install watchdog")
            return None
