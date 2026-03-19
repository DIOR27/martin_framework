import unittest

from martin import Icon, Script, Stylesheet, StyleTag, ScrollToTop, ThemeToggle, WhatsAppButton

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

    def test_scroll_to_top_render(self):
        html = ScrollToTop(icon="⇧", show_after=320, title="Subir").render()
        self.assertIn("scrollTo", html)
        self.assertIn("threshold=320", html)
        self.assertIn("Subir", html)
        self.assertIn("⇧", html)

    def test_theme_toggle_uses_opaque_background(self):
        html = ThemeToggle().render()
        self.assertIn("background:var(--dropdown-bg,var(--bg-secondary,var(--surface)))", html)
        self.assertIn("width:48px", html)
        self.assertIn("height:48px", html)
        self.assertIn("border-radius:999px", html)

    def test_whatsapp_button_render(self):
        html = WhatsAppButton(
            phone="593 999 999 999",
            message="Hola Martin",
            title="WhatsApp demo",
        ).render()
        self.assertIn("https://wa.me/593999999999?text=Hola%20Martin", html)
        self.assertIn("WhatsApp demo", html)
        self.assertIn("background:#25D366", html)
        self.assertIn("width:48px", html)
        self.assertIn("height:48px", html)
        self.assertIn('data-martin-float="1"', html)

    def test_floating_buttons_accept_icon_widget(self):
        scroll_html = ScrollToTop(
            icon=Icon(name="arrow-up", provider="fa", variant="solid")
        ).render()
        wa_html = WhatsAppButton(
            phone="593999999999",
            icon=Icon(name="whatsapp", provider="fa", variant="brands"),
        ).render()
        self.assertIn("fa-solid", scroll_html)
        self.assertIn("fa-arrow-up", scroll_html)
        self.assertIn("fa-brands", wa_html)
        self.assertIn("fa-whatsapp", wa_html)


if __name__ == "__main__":
    unittest.main()
