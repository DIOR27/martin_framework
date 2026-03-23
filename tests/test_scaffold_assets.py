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
            self.assertTrue((assets_dir / "art_dog_day_blossom.svg").exists())
            self.assertTrue((assets_dir / "art_dog_day_garden.svg").exists())

    def test_components_template_uses_new_carousel_art_and_brand_logos(self):
        files = render_new_project_files(
            name="demo_project",
            title="Demo Project",
            desc="Demo description",
        )
        components_page = files["pages/components.py"]
        main_file = files["main.py"]

        self.assertIn("/assets/art_dog_field_sunrise.svg", components_page)
        self.assertIn("/assets/art_dog_field_twilight.svg", components_page)
        self.assertIn("/assets/art_dog_hill_breeze.svg", components_page)
        self.assertIn("/assets/art_dog_meadow_neon.svg", components_page)
        self.assertIn("/assets/art_dog_day_blossom.svg", components_page)
        self.assertIn("/assets/art_dog_day_garden.svg", components_page)
        self.assertIn("/assets/logo_martin_glow.svg", components_page)
        self.assertIn("/assets/logo_martin_frame.svg", components_page)
        self.assertIn("/assets/logo_martin_stack.svg", components_page)
        self.assertIn('CarouselItem(image="/assets/icon.webp", title="Martin icon")', components_page)
        self.assertIn("masonry=True", components_page)
        self.assertIn('"Advanced Pack"', components_page)
        self.assertIn("DataGrid(", components_page)
        self.assertIn("CommandPalette(", components_page)
        self.assertIn("JSWidgetAdapter(", components_page)
        self.assertIn("widget-advanced-pack", components_page)
        self.assertIn("Wizard(", components_page)
        self.assertIn("WizardStep(", components_page)
        self.assertIn("widget-wizard", components_page)
        self.assertIn("Calendar(", components_page)
        self.assertIn("CalendarEvent(", components_page)
        self.assertIn("widget-calendar", components_page)
        self.assertIn("LanguageSelector(", components_page)
        self.assertIn("Counter(", components_page)
        self.assertIn("Field(", components_page)
        self.assertIn("Toast(", components_page)
        self.assertIn("ToastCenter(", components_page)
        self.assertIn("ScrollToTop(", components_page)
        self.assertIn("WhatsAppButton(", components_page)
        self.assertIn("widget-counter", components_page)
        self.assertIn("widget-toast", components_page)
        self.assertIn("Uploader(", components_page)
        self.assertIn("ResourceForm(", components_page)
        self.assertIn("ResourceEditor(", components_page)
        self.assertIn("ResourceTable(", components_page)
        self.assertIn("ResourceDetails(", components_page)
        self.assertIn("ResourceCardList(", components_page)
        self.assertIn("ResourceFilters(", components_page)
        self.assertIn("ResourceActions(", components_page)
        self.assertIn("ResourceBulkActions(", components_page)
        self.assertIn("ResourceToolbar(", components_page)
        self.assertIn("ResourceCreateButton(", components_page)
        self.assertIn("ResourceDuplicateButton(", components_page)
        self.assertIn("ResourceDeleteButton(", components_page)
        self.assertIn("ResourceView(", components_page)
        self.assertIn("widget-toastcenter", components_page)
        self.assertIn("widget-resources", components_page)
        self.assertIn("widget-auth", components_page)
        self.assertIn("widget-uploader", components_page)
        self.assertIn("widget-scrolltotop", components_page)
        self.assertIn('_t("components.title", "Componentes")', components_page)
        self.assertIn('repeat(auto-fit, minmax(220px, 1fr))', components_page)
        self.assertIn('repeat(auto-fit, minmax(180px, 1fr))', components_page)
        self.assertIn('/demo/validate/email', components_page)
        self.assertIn("Signal, Computed, Store, I18n, L10n, PluginRegistry", components_page)
        self.assertIn("LanguageSelector(", main_file)
        self.assertIn('path="locales"', main_file)
        self.assertIn("load_locale_catalogs", main_file)
        self.assertIn("locales/es_ES.po", files)
        self.assertIn("locales/en_US.po", files)


if __name__ == "__main__":
    unittest.main()
