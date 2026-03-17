import unittest

from martin import Script, Stylesheet, StyleTag

from tests.snapshot_utils import assert_snapshot


class SpecialWidgetsSnapshotTests(unittest.TestCase):
    def test_script_external_snapshot(self):
        html = Script(
            src="https://cdn.example/x.js",
            defer=True,
            crossorigin="anonymous",
        ).render()
        assert_snapshot(self, "script_external.html", html)

    def test_stylesheet_external_snapshot(self):
        html = Stylesheet(
            "https://cdn.example/x.css",
            integrity="sha384-abc",
        ).render()
        assert_snapshot(self, "stylesheet_external.html", html)

    def test_style_tag_snapshot(self):
        html = StyleTag(".hero{color:red}", id="hero-css").render()
        assert_snapshot(self, "style_tag.html", html)


if __name__ == "__main__":
    unittest.main()
