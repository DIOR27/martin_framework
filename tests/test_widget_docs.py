import tempfile
import unittest
from pathlib import Path

from martin import export_widget_docs, generate_widget_docs_json, generate_widget_docs_markdown


class WidgetDocsTests(unittest.TestCase):
    def test_generate_widget_docs_markdown_contains_known_widgets(self):
        content = generate_widget_docs_markdown(["Toast", "Uploader"])
        self.assertIn("# MARTIN Widget Docs", content)
        self.assertIn("### Toast", content)
        self.assertIn("### Uploader", content)
        self.assertIn("`upload_url`", content)

    def test_generate_widget_docs_json_contains_schema_fields(self):
        content = generate_widget_docs_json(["Wizard"])
        self.assertIn('"name": "Wizard"', content)
        self.assertIn('"finish_label"', content)

    def test_export_widget_docs_writes_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "WIDGETS.md"
            export_widget_docs(path, format="markdown", widget_names=["Counter"])
            self.assertTrue(path.exists())
            self.assertIn("### Counter", path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
