import unittest

from martin import App, Text
from martin.cli import _build_parser


class CliRunTests(unittest.TestCase):
    def test_run_parser_defaults_to_not_opening_browser(self):
        parser = _build_parser()
        args = parser.parse_args(["run"])
        self.assertFalse(args.open)

    def test_run_parser_accepts_open_flag(self):
        parser = _build_parser()
        args = parser.parse_args(["run", "--open"])
        self.assertTrue(args.open)

    def test_app_run_defaults_to_no_browser(self):
        app = App(build=lambda: Text("ok"), hot_reload=False, theme_toggle=False)
        defaults = App.run.__defaults__ or ()
        self.assertTrue(defaults)
        self.assertFalse(defaults[0])


if __name__ == "__main__":
    unittest.main()
