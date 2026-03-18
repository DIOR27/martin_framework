import json
import tempfile
import unittest
from pathlib import Path

from martin import App, Text
from martin.cli import _build_parser
from martin.exporter import export_with_backend


class ExportWithBackendTests(unittest.TestCase):
    def test_cli_parser_accepts_with_backend_flag(self):
        parser = _build_parser()
        args = parser.parse_args(["export", "--with-backend"])
        self.assertTrue(args.with_backend)

    def test_export_with_backend_generates_runtime_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "main.py").write_text(
                "from martin import App, Text\n"
                "app = App(build=lambda: Text('ok'))\n",
                encoding="utf-8",
            )

            out_dir = root / "dist"
            app = App(build=lambda: Text("hola"), hot_reload=False, theme_toggle=False)

            export_with_backend(
                app,
                out_dir=str(out_dir),
                assets_src=str(root / "assets"),
                source_file="main.py",
                project_root=str(root),
                fmt="split",
            )

            self.assertTrue((out_dir / "server.py").exists())
            self.assertTrue((out_dir / ".env.example").exists())
            self.assertTrue((out_dir / "_backend_src" / "main.py").exists())
            self.assertTrue((out_dir / "route-map.json").exists())

            route_map = json.loads((out_dir / "route-map.json").read_text(encoding="utf-8"))
            self.assertEqual(route_map["/"], "index.html")

            server_text = (out_dir / "server.py").read_text(encoding="utf-8")
            self.assertIn("APP._dispatch_request", server_text)
            self.assertIn('_backend_src', server_text)
            self.assertIn("route-map.json", server_text)


if __name__ == "__main__":
    unittest.main()
