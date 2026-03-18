import unittest

from martin import Icon, IconPack
from martin.scaffold import render_new_project_files


class IconSupportTests(unittest.TestCase):
    def test_fontawesome_icon_generation(self):
        html = Icon(name="house", provider="fa").render()
        self.assertIn('class="fa-solid fa-house"', html)
        self.assertIn('aria-hidden="true"', html)

    def test_bootstrap_icon_generation(self):
        html = Icon(name="airplane", provider="bi").render()
        self.assertIn('class="bi bi-airplane"', html)

    def test_material_symbols_generation(self):
        html = Icon(name="flight_takeoff", provider="material-symbols", variant="rounded").render()
        self.assertIn('class="material-symbols-rounded"', html)
        self.assertIn(">flight_takeoff<", html)

    def test_custom_icon_class_without_provider(self):
        html = Icon(name="fa-solid fa-user").render()
        self.assertIn('class="fa-solid fa-user"', html)

    def test_generic_provider_builds_prefixed_classes(self):
        html = Icon(name="home-line", provider="ri").render()
        self.assertIn('class="ri ri-home-line"', html)

    def test_generic_icon_allows_custom_prefix(self):
        html = Icon(name="home", base_class="bx", name_prefix="bxs-").render()
        self.assertIn('class="bx bxs-home"', html)

    def test_aria_label_disables_default_hidden_flag(self):
        html = Icon(name="house", provider="fa", aria_label="Inicio").render()
        self.assertIn('aria-label="Inicio"', html)
        self.assertNotIn('aria-hidden="true"', html)

    def test_iconpack_renders_known_cdn_links(self):
        html = IconPack(["fontawesome", "bi", "material-symbols"]).render()
        self.assertIn("cdnjs.cloudflare.com/ajax/libs/font-awesome", html)
        self.assertIn("cdn.jsdelivr.net/npm/bootstrap-icons", html)
        self.assertIn("fonts.googleapis.com/css2?family=Material+Symbols+Outlined", html)
        self.assertIn("fonts.googleapis.com/css2?family=Material+Symbols+Rounded", html)
        self.assertIn("fonts.googleapis.com/css2?family=Material+Symbols+Sharp", html)

    def test_iconpack_accepts_custom_stylesheet_urls(self):
        html = IconPack([
            "https://cdn.jsdelivr.net/npm/remixicon@4.2.0/fonts/remixicon.css",
            {"name": "boxicons", "href": "https://unpkg.com/boxicons@2.1.4/css/boxicons.min.css"},
        ]).render()
        self.assertIn("remixicon@4.2.0/fonts/remixicon.css", html)
        self.assertIn("boxicons@2.1.4/css/boxicons.min.css", html)

    def test_components_template_includes_icons_showcase(self):
        files = render_new_project_files("demo", "Demo", "Demo project")
        components = files["pages/components.py"]
        self.assertIn("IconPack", components)
        self.assertIn('widget-icons', components)
        self.assertIn('provider="fa"', components)
        self.assertIn('provider="ri"', components)


if __name__ == "__main__":
    unittest.main()
