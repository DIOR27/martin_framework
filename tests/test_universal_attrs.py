import unittest

from martin import App, Button, Code, Row, ScrollToTop, Text, TextField, ThemeToggle


class UniversalAttrsTests(unittest.TestCase):
    def test_row_accepts_aria_data_role_tabindex(self):
        html = Row(
            children=[],
            aria_label="Fila principal",
            data_testid="row-main",
            role="group",
            tabindex=0,
        ).render()
        self.assertIn('aria-label="Fila principal"', html)
        self.assertIn('data-testid="row-main"', html)
        self.assertIn('role="group"', html)
        self.assertIn('tabindex="0"', html)

    def test_textfield_accepts_attrs_dict(self):
        html = TextField(
            placeholder="Email",
            attrs={"aria-describedby": "email-help", "data-e2e": "email-input"},
        ).render()
        self.assertIn('aria-describedby="email-help"', html)
        self.assertIn('data-e2e="email-input"', html)

    def test_code_block_skips_script_link_and_applies_on_main_container(self):
        Code._id_counter = 0
        html = Code(
            "x = 1",
            language="python",
            attrs={"data-e2e": "code-block"},
        ).render()
        self.assertIn('data-e2e="code-block"', html)
        self.assertIn('<div id="code_1"', html)

    def test_button_can_render_as_floating_widget(self):
        html = Button(
            "WhatsApp",
            href="https://wa.me/593000000000",
            floating=True,
            float_position="bottom-left",
            float_offset=24,
            float_gap=16,
        ).render()
        self.assertIn('data-martin-float="1"', html)
        self.assertIn('data-martin-float-pos="bottom-left"', html)
        self.assertIn('data-martin-float-offset="24px"', html)
        self.assertIn('data-martin-float-gap="16px"', html)
        self.assertIn("__martinFloatLayout", html)

    def test_theme_toggle_stays_inline_by_default_and_supports_floating(self):
        inline_html = ThemeToggle().render()
        self.assertNotIn('data-martin-float="1"', inline_html)
        self.assertIn('var NEXT={"dark":"light","light":"auto","auto":"dark"}', inline_html)
        self.assertIn("width:48px", inline_html)
        self.assertIn("height:48px", inline_html)
        self.assertIn("border-radius:999px", inline_html)

        floating_html = ThemeToggle(floating=True, float_position="top-right").render()
        self.assertIn('data-martin-float="1"', floating_html)
        self.assertIn('data-martin-float-pos="top-right"', floating_html)

    def test_app_default_theme_toggle_uses_floating_stack_system(self):
        app = App(build=lambda: Text("ok"), hot_reload=False, theme_toggle=True)
        html = app._render("/")
        self.assertIn('data-martin-float="1"', html)
        self.assertIn('data-martin-float-pos="bottom-right"', html)
        self.assertIn("__martinFloatLayout", html)

    def test_scroll_to_top_uses_floating_stack_by_default(self):
        html = ScrollToTop().render()
        self.assertIn('data-martin-float="1"', html)
        self.assertIn('data-martin-float-pos="bottom-right"', html)
        self.assertIn("__martinFloatLayout", html)
        self.assertIn("width:48px", html)
        self.assertIn("height:48px", html)
        self.assertIn("getComputedStyle", html)
        self.assertNotIn("offsetParent===null", html)


if __name__ == "__main__":
    unittest.main()
