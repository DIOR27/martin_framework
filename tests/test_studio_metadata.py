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
from martin import get_widget_schema


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

    def test_uploader_is_exposed_in_catalog(self):
        uploader = describe_widget("Uploader")
        self.assertIsNotNone(uploader)
        params = {param["name"]: param for param in uploader["params"]}
        self.assertIn("upload_url", params)
        self.assertIn("chunk_size_mb", params)
        self.assertEqual(params["multiple"]["type"], "boolean")
        self.assertIn("layout", params)

    def test_widget_schema_registry_exposes_toast(self):
        schema = get_widget_schema("Toast")
        self.assertIsNotNone(schema)
        self.assertEqual(schema["category"], "feedback")
        self.assertTrue(any(param["name"] == "position" for param in schema["params"]))

        toast = describe_widget("Toast")
        self.assertIsNotNone(toast)
        params = {param["name"]: param for param in toast["params"]}
        self.assertIn("duration", params)
        self.assertEqual(params["duration"]["type"], "integer")
        self.assertIn("position", params)
        self.assertEqual(params["position"]["type"], "enum")

        toast_center = describe_widget("ToastCenter")
        self.assertIsNotNone(toast_center)
        center_params = {param["name"]: param for param in toast_center["params"]}
        self.assertIn("items", center_params)

    def test_widget_schema_registry_exposes_wizard(self):
        schema = get_widget_schema("Wizard")
        self.assertIsNotNone(schema)
        self.assertEqual(schema["category"], "advanced")
        self.assertTrue(any(param["name"] == "finish_label" for param in schema["params"]))

        wizard = describe_widget("Wizard")
        self.assertIsNotNone(wizard)
        self.assertTrue(wizard["accepts_children"])
        params = {param["name"]: param for param in wizard["params"]}
        self.assertIn("initial_step", params)
        self.assertEqual(params["initial_step"]["type"], "integer")

    def test_resource_widgets_are_exposed(self):
        resource_form = describe_widget("ResourceForm")
        self.assertIsNotNone(resource_form)
        form_params = {param["name"]: param for param in resource_form["params"]}
        self.assertIn("resource", form_params)
        self.assertIn("fields", form_params)

        resource_table = describe_widget("ResourceTable")
        self.assertIsNotNone(resource_table)
        table_params = {param["name"]: param for param in resource_table["params"]}
        self.assertIn("columns", table_params)
        self.assertIn("endpoint", table_params)

        resource_editor = describe_widget("ResourceEditor")
        self.assertIsNotNone(resource_editor)
        editor_params = {param["name"]: param for param in resource_editor["params"]}
        self.assertIn("record_id", editor_params)
        self.assertIn("detail_endpoint", editor_params)

        resource_details = describe_widget("ResourceDetails")
        self.assertIsNotNone(resource_details)
        details_params = {param["name"]: param for param in resource_details["params"]}
        self.assertIn("record_id", details_params)

        resource_cards = describe_widget("ResourceCardList")
        self.assertIsNotNone(resource_cards)
        cards_params = {param["name"]: param for param in resource_cards["params"]}
        self.assertIn("subtitle_field", cards_params)
        self.assertIn("badge_field", cards_params)

        resource_stats = describe_widget("ResourceStats")
        self.assertIsNotNone(resource_stats)
        stats_params = {param["name"]: param for param in resource_stats["params"]}
        self.assertIn("metrics", stats_params)

        resource_filters = describe_widget("ResourceFilters")
        self.assertIsNotNone(resource_filters)
        filters_params = {param["name"]: param for param in resource_filters["params"]}
        self.assertIn("target", filters_params)
        self.assertIn("filters", filters_params)

        resource_actions = describe_widget("ResourceActions")
        self.assertIsNotNone(resource_actions)
        actions_params = {param["name"]: param for param in resource_actions["params"]}
        self.assertIn("actions", actions_params)

        resource_bulk = describe_widget("ResourceBulkActions")
        self.assertIsNotNone(resource_bulk)
        bulk_params = {param["name"]: param for param in resource_bulk["params"]}
        self.assertIn("target", bulk_params)
        self.assertIn("actions", bulk_params)

        resource_toolbar = describe_widget("ResourceToolbar")
        self.assertIsNotNone(resource_toolbar)
        toolbar_params = {param["name"]: param for param in resource_toolbar["params"]}
        self.assertIn("search_placeholder", toolbar_params)
        self.assertIn("show_selected_count", toolbar_params)

        resource_paginator = describe_widget("ResourcePaginator")
        self.assertIsNotNone(resource_paginator)
        paginator_params = {param["name"]: param for param in resource_paginator["params"]}
        self.assertIn("per_page_options", paginator_params)

        resource_create = describe_widget("ResourceCreateButton")
        self.assertIsNotNone(resource_create)
        create_params = {param["name"]: param for param in resource_create["params"]}
        self.assertIn("body", create_params)

        resource_duplicate = describe_widget("ResourceDuplicateButton")
        self.assertIsNotNone(resource_duplicate)
        duplicate_params = {param["name"]: param for param in resource_duplicate["params"]}
        self.assertIn("record_id", duplicate_params)

        resource_delete = describe_widget("ResourceDeleteButton")
        self.assertIsNotNone(resource_delete)
        delete_params = {param["name"]: param for param in resource_delete["params"]}
        self.assertIn("record_id", delete_params)
        self.assertIn("confirm_message", delete_params)

        resource_kanban = describe_widget("ResourceKanban")
        self.assertIsNotNone(resource_kanban)
        kanban_params = {param["name"]: param for param in resource_kanban["params"]}
        self.assertIn("group_field", kanban_params)

        resource_view = describe_widget("ResourceView")
        self.assertIsNotNone(resource_view)
        view_params = {param["name"]: param for param in resource_view["params"]}
        self.assertIn("columns", view_params)
        self.assertIn("form_fields", view_params)
        self.assertIn("toolbar_actions", view_params)
        self.assertIn("bulk_actions", view_params)
        self.assertIn("stats_metrics", view_params)

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

        resource_form = describe_widget("ResourceForm")
        form_fields = next(param for param in resource_form["params"] if param["name"] == "fields")
        self.assertEqual(form_fields["editor"]["type"], "collection")

        resource_actions = describe_widget("ResourceActions")
        actions = next(param for param in resource_actions["params"] if param["name"] == "actions")
        self.assertEqual(actions["editor"]["type"], "collection")
        self.assertEqual(actions["editor"]["fields"][0]["name"], "label")

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
