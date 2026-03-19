import unittest
from datetime import datetime, timezone

from martin import (
    Signal,
    Computed,
    Store,
    I18n,
    L10n,
    describe_locale,
    discover_locale_codes,
    load_po_catalog,
    load_locale_catalogs,
    register_plugin,
    unregister_plugin,
    apply_plugin,
    list_plugins,
)


class StateI18nPluginsTests(unittest.TestCase):
    def test_signal_computed_and_store(self):
        count = Signal(1)
        doubled = Computed(lambda: count.get() * 2, count)
        history = []
        off = doubled.subscribe(lambda v: history.append(v), emit=True)

        self.assertEqual(doubled.get(), 2)
        count.set(3)
        self.assertEqual(doubled.get(), 6)
        self.assertEqual(history, [2, 6])
        off()

        store = Store({"theme": "dark"})
        self.assertEqual(store.get("theme"), "dark")
        store.set("theme", "light")
        self.assertEqual(store.snapshot()["theme"], "light")

    def test_i18n_and_l10n(self):
        i18n = I18n(
            messages={
                "es": {"home": {"title": "Inicio {name}"}},
                "en": {"home": {"title": "Home {name}"}},
            },
            default_locale="es",
            fallback_locale="en",
        )
        self.assertEqual(i18n.t("home.title", name="Martin"), "Inicio Martin")
        self.assertEqual(i18n.t("home.title", locale="en", name="Martin"), "Home Martin")
        self.assertEqual(i18n.t("missing.key", default="ok"), "ok")

        l10n = L10n(locale="es-EC", timezone="UTC", currency="USD")
        now = datetime(2026, 3, 18, 15, 30, tzinfo=timezone.utc)
        self.assertEqual(l10n.text_direction(), "ltr")
        self.assertTrue(l10n.format_currency(25.5).startswith("$"))
        self.assertEqual(l10n.format_date(now), "18/03/2026")
        self.assertEqual(l10n.format_time(now), "15:30")
        self.assertEqual(l10n.text_direction("ar"), "rtl")

    def test_locale_helpers_and_po_loading(self):
        info = describe_locale("es_ES")
        self.assertEqual(info["flag"], "🇪🇸")
        self.assertEqual(info["label"], "Español (España)")

        with self.subTest("discover locales from messages"):
            locales = discover_locale_codes(messages={"es_ES": {}, "en_US": {}})
            self.assertEqual(locales, ["es_ES", "en_US"])

        import tempfile
        from pathlib import Path

        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            (base / "es_ES.po").write_text(
                'msgid ""\nmsgstr ""\n"Language: es_ES\\n"\n\nmsgid "home.title"\nmsgstr "Inicio"\n',
                encoding="utf-8",
            )
            (base / "en_US.po").write_text(
                'msgid ""\nmsgstr ""\n"Language: en_US\\n"\n\nmsgid "home.title"\nmsgstr "Home"\n',
                encoding="utf-8",
            )
            self.assertEqual(load_po_catalog(base / "es_ES.po")["home"]["title"], "Inicio")
            catalogs = load_locale_catalogs(base)
            self.assertEqual(catalogs["en_US"]["home"]["title"], "Home")

    def test_plugin_registry_functions(self):
        name = "demo_plugin_state_i18n_test"
        register_plugin(name, lambda person: f"hola {person}")
        self.assertIn(name, list_plugins())
        self.assertEqual(apply_plugin(name, "diego"), "hola diego")
        unregister_plugin(name)


if __name__ == "__main__":
    unittest.main()
