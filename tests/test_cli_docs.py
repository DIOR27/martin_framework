import tempfile
import unittest
from pathlib import Path

from martin.cli import _build_parser, cmd_docs


class CliDocsTests(unittest.TestCase):
    def test_docs_command_writes_output_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "widgets.json"
            parser = _build_parser()
            args = parser.parse_args(["docs", "--format", "json", "--out", str(out), "--widgets", "Toast"])
            cmd_docs(args)
            self.assertTrue(out.exists())
            self.assertIn('"name": "Toast"', out.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
