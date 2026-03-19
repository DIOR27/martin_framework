import unittest

from martin import LanguageSelector


class LanguageSelectorWidgetTests(unittest.TestCase):
    def test_renders_flags_and_i18n_runtime(self):
        html = LanguageSelector(
            locales=["es_ES", "en_US"],
            value="es_ES",
            translations={
                "es_ES": {"nav": {"home": "Inicio"}},
                "en_US": {"nav": {"home": "Home"}},
            },
        ).render()

        self.assertIn("🇪🇸", html)
        self.assertIn("English (United States)", html)
        self.assertIn("Buscar idioma...", html)
        self.assertIn("window.MartinI18n.applyLocale", html)
        self.assertIn("martin:locale-change", html)


if __name__ == "__main__":
    unittest.main()
