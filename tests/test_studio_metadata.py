import tempfile
import textwrap
import unittest

from martin.studio import (
    describe_widget,
    get_widget_catalog,
    parse_source_file_to_design,
    render_source_file_preview_html,
    update_source_function,
)


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

    def test_universal_floating_props_are_exposed_in_catalog(self):
        button = describe_widget("Button")
        self.assertIsNotNone(button)
        params = {param["name"]: param for param in button["params"]}
        self.assertIn("floating", params)
        self.assertEqual(params["floating"]["type"], "boolean")
        self.assertIn("float_position", params)
        self.assertEqual(params["float_position"]["type"], "enum")
        self.assertIn("bottom-right", params["float_position"]["options"])
        self.assertIn("float_gap", params)
        self.assertEqual(params["float_gap"]["default"], 12)
        self.assertIn("visible", params)
        self.assertEqual(params["visible"]["type"], "condition")
        self.assertEqual(params["visible"]["editor"]["type"], "condition")

    def test_counter_is_exposed_in_catalog(self):
        counter = describe_widget("Counter")
        self.assertIsNotNone(counter)
        params = {param["name"]: param for param in counter["params"]}
        self.assertIn("mode", params)
        self.assertEqual(params["mode"]["type"], "enum")
        self.assertIn("countdown", params["mode"]["options"])

    def test_complex_widget_params_expose_editor_metadata(self):
        calendar = describe_widget("Calendar")
        self.assertIsNotNone(calendar)
        events = next(param for param in calendar["params"] if param["name"] == "events")
        self.assertEqual(events["editor"]["type"], "collection")
        self.assertEqual(events["editor"]["fields"][0]["name"], "title")

        wordcloud = describe_widget("WordCloud")
        self.assertIsNotNone(wordcloud)
        words = next(param for param in wordcloud["params"] if param["name"] == "words")
        self.assertEqual(words["editor"]["type"], "key_value")
        self.assertEqual(words["editor"]["value_type"], "integer")

    def test_parser_extracts_root_widget_from_source_file(self):
        source = textwrap.dedent(
            """
            from martin import Column, Heading, Paragraph

            def home():
                return Column(
                    gap=12,
                    children=[
                        Heading("Hola", level=1),
                        Paragraph("Texto"),
                    ],
                )
            """
        )
        with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8") as handle:
            handle.write(source)
            temp_path = handle.name

        design = parse_source_file_to_design(temp_path)
        self.assertEqual(design["root"]["type"], "Column")
        self.assertEqual(design["root"]["props"]["gap"], 12)
        self.assertEqual(design["root"]["children"][0]["type"], "Heading")

    def test_render_source_file_preview_html(self):
        source = textwrap.dedent(
            """
            from martin import Column, Heading

            def home():
                return Column(children=[Heading("Preview test", level=1)])
            """
        )
        with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8") as handle:
            handle.write(source)
            temp_path = handle.name

        html = render_source_file_preview_html(temp_path)
        self.assertIn("Preview test", html)
        self.assertIn("<html", html)

    def test_parser_prefers_page_function_over_helper(self):
        source = textwrap.dedent(
            """
            from martin import Raw, Column, Heading

            def _t(key, fallback):
                return Raw(f"<span>{fallback}</span>")

            def home():
                return Column(children=[Heading("Hola", level=1)])
            """
        )
        with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8") as handle:
            handle.write(source)
            temp_path = handle.name

        design = parse_source_file_to_design(temp_path)
        self.assertEqual(design["root"]["type"], "Column")

    def test_parser_uses_translation_helper_fallback_text(self):
        source = textwrap.dedent(
            """
            from martin import Column, Heading

            def _t(key, fallback, tag="span"):
                return fallback

            def home():
                return Column(children=[Heading(_t("hero.title", "Hello world"), level=1)])
            """
        )
        with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8") as handle:
            handle.write(source)
            temp_path = handle.name

        design = parse_source_file_to_design(temp_path)
        self.assertEqual(design["root"]["children"][0]["props"]["content"], "Hello world")

    def test_update_source_function_preserves_other_symbols(self):
        source = textwrap.dedent(
            """
            from martin import Column, Heading

            def helper():
                return 1

            def home():
                return Column(children=[Heading("Old", level=1)])
            """
        )
        with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8") as handle:
            handle.write(source)
            temp_path = handle.name

        update_source_function(
            temp_path,
            "home",
            textwrap.dedent(
                """
                def home():
                    return Column(children=[Heading("New", level=1)])
                """
            ),
            ["Column", "Heading", "Button"],
        )
        with open(temp_path, "r", encoding="utf-8") as handle:
            updated = handle.read()
        self.assertIn('def helper():', updated)
        self.assertIn('"New"', updated)
        self.assertIn("Button", updated)


if __name__ == "__main__":
    unittest.main()
