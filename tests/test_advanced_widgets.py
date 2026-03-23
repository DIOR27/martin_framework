import unittest

from martin import (
    DataGrid,
    DataGridColumn,
    Wizard,
    WizardStep,
    CommandPalette,
    Drawer,
    SplitPane,
    Skeleton,
    EmptyState,
    ErrorState,
    Form,
    ResourceForm,
    ResourceEditor,
    ResourceTable,
    ResourceDetails,
    ResourceCardList,
    ResourceStats,
    ResourceFilters,
    ResourceActions,
    ResourceBulkActions,
    ResourceToolbar,
    ResourcePaginator,
    ResourceCreateButton,
    ResourceDuplicateButton,
    ResourceDeleteButton,
    ResourceKanban,
    ResourceView,
    JSWidgetAdapter,
    Text,
)


class AdvancedWidgetsTests(unittest.TestCase):
    def test_datagrid_render_includes_pro_features(self):
        html = DataGrid(
            rows=[{"name": "Ana", "team": "A"}, {"name": "Luis", "team": "B"}],
            columns=[
                DataGridColumn("name", "Nombre", width=180, frozen=True),
                DataGridColumn("team", "Equipo", width=120),
            ],
            group_by="team",
            virtual_scroll=True,
            resizable=True,
            reorderable=True,
        ).render()
        self.assertIn("dg-resize", html)
        self.assertIn("dragstart", html)
        self.assertIn("_setGroupBy", html)
        self.assertIn("_setRows", html)
        self.assertIn("groupBy", html)
        self.assertIn("background:var(--bg-secondary,var(--surface))", html)

    def test_command_palette_drawer_and_splitpane_render(self):
        wizard_html = Wizard(
            children=[
                WizardStep(title="Brief", description="Paso inicial", child=Text("A")),
                WizardStep(title="Review", description="Paso final", child=Text("B")),
            ],
            finish_label="Done",
        ).render()
        palette_html = CommandPalette(
            items=[{"label": "Open drawer", "action": "openDrawer('demo')"}],
            show_trigger=True,
        ).render()
        drawer_html = Drawer(id="demo", title="Demo drawer", children=[Text("ok")]).render()
        split_html = SplitPane(left=Text("A"), right=Text("B"), ratio=0.4).render()

        self.assertIn("metaKey", palette_html)
        self.assertIn("ctrlKey", palette_html)
        self.assertIn("_pick", palette_html)
        self.assertIn("_panel_0", wizard_html)
        self.assertIn("Wizard", Wizard.__name__)
        self.assertIn("Done", wizard_html)
        self.assertIn("window.openDrawer", drawer_html)
        self.assertIn("window.closeDrawer", drawer_html)
        self.assertIn("cursor:col-resize", split_html)

    def test_form_states_and_js_adapter_render(self):
        form_html = Form(
            id="f_demo",
            schema={"email": {"required": True, "email": True, "async_url": "/api/check"}},
            children=[],
        ).render()
        resource_form_html = ResourceForm(
            resource="leads",
            fields=[
                {"name": "nombre", "type": "text", "required": True},
                {"name": "email", "type": "email", "required": True},
            ],
        ).render()
        resource_editor_html = ResourceEditor(
            resource="leads",
            record_id="1",
            fields=[
                {"name": "nombre", "type": "text", "required": True},
                {"name": "plan", "type": "select", "options": [("starter", "Starter"), ("pro", "Pro")]},
            ],
        ).render()
        resource_table_html = ResourceTable(
            resource="leads",
            columns=[DataGridColumn("nombre", "Nombre"), DataGridColumn("estado", "Estado")],
        ).render()
        resource_details_html = ResourceDetails(resource="leads", fields=["nombre", "email"]).render()
        resource_cards_html = ResourceCardList(resource="leads", subtitle_field="email", badge_field="estado").render()
        resource_stats_html = ResourceStats(resource="leads", metrics=[{"key": "total", "label": "Total"}]).render()
        resource_filters_html = ResourceFilters(
            target="leads_table",
            filters=[{"name": "estado", "type": "select", "options": [("Nuevo", "Nuevo")]}],
        ).render()
        resource_actions_html = ResourceActions(
            actions=[{"label": "Refresh", "on_click": "window['leads_table_refresh']&&window['leads_table_refresh']()"}]
        ).render()
        resource_toolbar_html = ResourceToolbar(
            target="leads_table",
            actions=[{"label": "Refresh", "variant": "secondary", "on_click": "window['leads_table_refresh']&&window['leads_table_refresh']()"}],
        ).render()
        resource_paginator_html = ResourcePaginator(target="leads_table").render()
        resource_bulk_html = ResourceBulkActions(
            target="leads_table",
            actions=[{"label": "Bulk", "url": "/api/resources/leads/bulk", "body": {"action": "follow_up"}}],
        ).render()
        resource_create_html = ResourceCreateButton(resource="leads", body={"nombre": "Quick", "email": "quick@martin.dev"}).render()
        resource_duplicate_html = ResourceDuplicateButton(resource="leads", record_id="1").render()
        resource_delete_html = ResourceDeleteButton(resource="leads", record_id="2").render()
        resource_kanban_html = ResourceKanban(resource="leads", group_field="estado").render()
        resource_view_html = ResourceView(
            resource="leads",
            columns=[DataGridColumn("nombre", "Nombre")],
            form_fields=[{"name": "nombre", "type": "text", "required": True}],
            filters=[{"name": "estado", "type": "select"}],
            actions=[{"label": "Refresh", "on_click": "window['leads_table_refresh']&&window['leads_table_refresh']()"}],
            toolbar_actions=[{"label": "Quick", "variant": "ghost", "on_click": "console.log('quick')"}],
            bulk_actions=[{"label": "Bulk", "url": "/api/resources/leads/bulk", "body": {"action": "follow_up"}}],
            stats_metrics=[{"key": "total", "label": "Total"}],
            detail_fields=["nombre", "email"],
            show_stats=True,
            show_paginator=True,
            show_kanban=True,
            show_bulk_actions=True,
        ).render()
        jsa_html = JSWidgetAdapter(
            init_js="el.textContent='ok';",
            data={"x": 1},
            scripts=["https://cdn.example.com/a.js"],
            stylesheets=["https://cdn.example.com/a.css"],
        ).render()
        sk_html = Skeleton(lines=3, avatar=True).render()
        es_html = EmptyState(title="Nada").render()
        er_html = ErrorState(title="Error").render()

        self.assertIn("async_url", form_html)
        self.assertIn("/api/resources/leads/save", resource_form_html)
        self.assertIn("_result", resource_form_html)
        self.assertIn("/api/resources/leads/detail", resource_editor_html)
        self.assertIn("pwSelectPick", resource_editor_html)
        self.assertIn("/api/resources/leads/list", resource_table_html)
        self.assertIn("_refresh", resource_table_html)
        self.assertIn("/api/resources/leads/detail", resource_details_html)
        self.assertIn("subtitle_field", ResourceCardList.__init__.__code__.co_varnames)
        self.assertIn("/api/resources/leads/list", resource_cards_html)
        self.assertIn("/api/resources/leads/stats", resource_stats_html)
        self.assertIn("leads_table_refresh", resource_filters_html)
        self.assertIn("Refresh", resource_actions_html)
        self.assertIn("seleccionados", resource_toolbar_html)
        self.assertIn("Página 1 de 1", resource_paginator_html)
        self.assertIn("/api/resources/leads/bulk", resource_bulk_html)
        self.assertIn("/api/resources/leads/save", resource_create_html)
        self.assertIn("/api/resources/leads/duplicate", resource_duplicate_html)
        self.assertIn("/api/resources/leads/delete", resource_delete_html)
        self.assertIn("/api/resources/leads/list?per_page=9999", resource_kanban_html)
        self.assertIn("/api/resources/leads/list", resource_view_html)
        self.assertIn("Nuevo registro", resource_view_html)
        self.assertIn("__martin_select__", resource_view_html)
        self.assertIn("/api/resources/leads/stats", resource_view_html)
        self.assertIn("mn-invalid", form_html)
        self.assertIn("_mnLoadScript", jsa_html)
        self.assertIn("_mnLoadCss", jsa_html)
        self.assertIn("mnSkPulse", sk_html)
        self.assertIn("Nada", es_html)
        self.assertIn("Error", er_html)


if __name__ == "__main__":
    unittest.main()
