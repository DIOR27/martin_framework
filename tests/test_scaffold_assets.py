import tempfile
import unittest
from pathlib import Path

from martin.scaffold import copy_default_icon, render_new_project_files


class ScaffoldAssetsTests(unittest.TestCase):
    def test_copy_default_icon_copies_visual_assets(self):
        with tempfile.TemporaryDirectory() as tmp:
            assets_dir = Path(tmp)
            copy_default_icon(assets_dir)

            self.assertTrue((assets_dir / "icon.webp").exists())
            self.assertTrue((assets_dir / "logo_martin_glow.svg").exists())
            self.assertTrue((assets_dir / "logo_martin_frame.svg").exists())
            self.assertTrue((assets_dir / "logo_martin_stack.svg").exists())
            self.assertTrue((assets_dir / "art_dog_field_sunrise.svg").exists())
            self.assertTrue((assets_dir / "art_dog_field_twilight.svg").exists())
            self.assertTrue((assets_dir / "art_dog_hill_breeze.svg").exists())
            self.assertTrue((assets_dir / "art_dog_meadow_neon.svg").exists())

    def test_components_template_uses_new_carousel_art_and_brand_logos(self):
        files = render_new_project_files(
            name="demo_project",
            title="Demo Project",
            desc="Demo description",
        )
        components_page = files["pages/components.py"]

        self.assertIn("/assets/art_dog_field_sunrise.svg", components_page)
        self.assertIn("/assets/art_dog_field_twilight.svg", components_page)
        self.assertIn("/assets/art_dog_hill_breeze.svg", components_page)
        self.assertIn("/assets/art_dog_meadow_neon.svg", components_page)
        self.assertIn("/assets/logo_martin_glow.svg", components_page)
        self.assertIn("/assets/logo_martin_frame.svg", components_page)
        self.assertIn("/assets/logo_martin_stack.svg", components_page)
        self.assertIn('CarouselItem(image="/assets/icon.webp", title="Martin icon")', components_page)


if __name__ == "__main__":
    unittest.main()
