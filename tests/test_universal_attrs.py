import unittest

from martin import Code, Row, TextField


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


if __name__ == "__main__":
    unittest.main()
