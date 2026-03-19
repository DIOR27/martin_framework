import tempfile
import textwrap
import unittest

from martin.studio import (
    describe_widget,
    get_widget_catalog,
    parse_source_file_to_design,
    render_source_file_preview_html,
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


if __name__ == "__main__":
    unittest.main()
