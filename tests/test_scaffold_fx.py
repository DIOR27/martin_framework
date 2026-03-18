import unittest

from martin.scaffold import render_new_project_files


class ScaffoldFxTests(unittest.TestCase):
    def test_components_template_includes_fx_showcase(self):
        files = render_new_project_files(
            name="demo_project",
            title="Demo Project",
            desc="Demo description",
        )
        components_page = files["pages/components.py"]

        self.assertIn("from martin.fx import FadeIn, SlideIn, ScaleIn, Pulse, Spin, Transition", components_page)
        self.assertIn('"FX",           "widget-fx"', components_page)
        self.assertIn('widget_name="FX"', components_page)
        self.assertIn("Motion bundled inside martin-framework", components_page)


if __name__ == "__main__":
    unittest.main()
