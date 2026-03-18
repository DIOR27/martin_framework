import unittest

from martin import (
    DataGrid,
    DataGridColumn,
    CommandPalette,
    Drawer,
    SplitPane,
    Skeleton,
    EmptyState,
    ErrorState,
    Form,
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

    def test_command_palette_drawer_and_splitpane_render(self):
        palette_html = CommandPalette(
            items=[{"label": "Open drawer", "action": "openDrawer('demo')"}],
            show_trigger=True,
        ).render()
        drawer_html = Drawer(id="demo", title="Demo drawer", children=[Text("ok")]).render()
        split_html = SplitPane(left=Text("A"), right=Text("B"), ratio=0.4).render()

        self.assertIn("metaKey", palette_html)
        self.assertIn("ctrlKey", palette_html)
        self.assertIn("_pick", palette_html)
        self.assertIn("window.openDrawer", drawer_html)
        self.assertIn("window.closeDrawer", drawer_html)
        self.assertIn("cursor:col-resize", split_html)

    def test_form_states_and_js_adapter_render(self):
        form_html = Form(
            id="f_demo",
            schema={"email": {"required": True, "email": True, "async_url": "/api/check"}},
            children=[],
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
        self.assertIn("mn-invalid", form_html)
        self.assertIn("_mnLoadScript", jsa_html)
        self.assertIn("_mnLoadCss", jsa_html)
        self.assertIn("mnSkPulse", sk_html)
        self.assertIn("Nada", es_html)
        self.assertIn("Error", er_html)


if __name__ == "__main__":
    unittest.main()
