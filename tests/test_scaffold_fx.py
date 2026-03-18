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

        self.assertIn("HoverLift", components_page)
        self.assertIn("HoverGlow", components_page)
        self.assertIn("Hover(", components_page)
        self.assertIn("Stagger", components_page)
        self.assertIn("ReducedMotion", components_page)
        self.assertIn("RevealOnScroll", components_page)
        self.assertIn('"FX",           "widget-fx"', components_page)
        self.assertIn('widget_name="FX"', components_page)
        self.assertIn("Hover presets", components_page)
        self.assertIn("FX Hover Gallery", components_page)
        self.assertIn("Color + Border", components_page)
        self.assertIn("CTA Card", components_page)
        self.assertIn("Feature Item", components_page)
        self.assertIn("Boton con hover glow", components_page)
        self.assertIn('filename="fx_hover.py"', components_page)
        self.assertIn('filename="fx_hover_gallery.py"', components_page)
        self.assertIn("Motion bundled inside martin-framework", components_page)


if __name__ == "__main__":
    unittest.main()
