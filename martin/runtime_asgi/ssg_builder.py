import hashlib
from pathlib import Path

from martin.render_html.render_result import RenderResult


class SSGBuilder:

    def __init__(self, output_dir: str = "dist"):
        self.output_dir = Path(output_dir)
        self.assets_dir = self.output_dir / "assets"

    def build(self, result: RenderResult, filename: str = "index.html") -> None:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.assets_dir.mkdir(parents=True, exist_ok=True)

        html = result.html

        if result.css:
            hash_name = hashlib.sha1(result.css.encode()).hexdigest()[:8]
            css_filename = f"martin-{hash_name}.css"
            css_path = self.assets_dir / css_filename

            css_path.write_text(result.css, encoding="utf-8")

            html = html.replace("__MARTIN_CSS__", f"/assets/{css_filename}")

        html_path = self.output_dir / filename
        html_path.write_text("<!DOCTYPE html>\n" + html, encoding="utf-8")
