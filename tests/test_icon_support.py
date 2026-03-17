import unittest

from martin import Icon, IconPack


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

    def test_aria_label_disables_default_hidden_flag(self):
        html = Icon(name="house", provider="fa", aria_label="Inicio").render()
        self.assertIn('aria-label="Inicio"', html)
        self.assertNotIn('aria-hidden="true"', html)

    def test_iconpack_renders_known_cdn_links(self):
        html = IconPack(["fontawesome", "bi", "material-symbols"]).render()
        self.assertIn("cdnjs.cloudflare.com/ajax/libs/font-awesome", html)
        self.assertIn("cdn.jsdelivr.net/npm/bootstrap-icons", html)
        self.assertIn("fonts.googleapis.com/css2?family=Material+Symbols+Outlined", html)


if __name__ == "__main__":
    unittest.main()
