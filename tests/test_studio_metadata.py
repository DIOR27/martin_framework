import unittest

from martin.studio import describe_widget, get_widget_catalog


class StudioMetadataTests(unittest.TestCase):
    def test_catalog_contains_widgets_and_categories(self):
        catalog = get_widget_catalog()
        self.assertGreater(catalog["widget_count"], 10)
        self.assertIn("layout", catalog["categories"])
        self.assertTrue(any(widget["name"] == "Button" for widget in catalog["widgets"]))

    def test_button_metadata_exposes_variant_options(self):
        button = describe_widget("Button")
        self.assertIsNotNone(button)
        variant = next(param for param in button["params"] if param["name"] == "variant")
        self.assertEqual(variant["type"], "enum")
        self.assertIn("primary", variant["options"])
        self.assertIn("ghost", variant["options"])

    def test_container_widgets_report_children_slot(self):
        column = describe_widget("Column")
        self.assertIsNotNone(column)
        self.assertTrue(column["accepts_children"])
        self.assertTrue(any(param["name"] == "padding" for param in column["params"]))


if __name__ == "__main__":
    unittest.main()
