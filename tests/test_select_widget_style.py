import unittest

from martin import Select
from martin.exporter import BASE_CSS


class SelectWidgetStyleTests(unittest.TestCase):
    def test_native_select_includes_theme_fallback_style(self):
        Select._id_counter = 0
        html = Select(
            id="plan_select",
            options=[("starter", "Starter"), ("pro", "Pro"), ("enterprise", "Enterprise")],
            value="starter",
            search=False,
        ).render()
        self.assertIn("color-scheme: light dark", html)
        self.assertIn("option style=", html)
        self.assertIn("var(--dropdown-bg", html)

    def test_export_base_css_styles_select_options(self):
        self.assertIn("select option, select optgroup", BASE_CSS)
        self.assertIn("color-scheme: dark", BASE_CSS)
        self.assertIn("color-scheme: light", BASE_CSS)


if __name__ == "__main__":
    unittest.main()

