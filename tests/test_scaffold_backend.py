import unittest

from martin.scaffold import render_new_project_files


class ScaffoldBackendTests(unittest.TestCase):
    def test_main_template_mounts_backend_extension(self):
        files = render_new_project_files(
            name="demo_project",
            title="Demo Project",
            desc="Demo description",
        )
        main_file = files["main.py"]

        self.assertIn("from martin.backend import Backend", main_file)
        self.assertIn("register_components_backend", main_file)
        self.assertIn("backend = Backend(prefix=\"/api\")", main_file)
        self.assertIn("backend.mount(app)", main_file)

    def test_components_template_includes_backend_demo(self):
        files = render_new_project_files(
            name="demo_project",
            title="Demo Project",
            desc="Demo description",
        )
        components_page = files["pages/components.py"]

        self.assertIn("from martin.backend import ApiCall, Backend, MethodCall, Ref, Response, ResultBox", components_page)
        self.assertIn("def register_components_backend(backend: Backend):", components_page)
        self.assertIn('@backend.post("/demo/contact")', components_page)
        self.assertIn('@backend.post("/demo/validate/email")', components_page)
        self.assertIn('@backend.post("/demo/upload")', components_page)
        self.assertIn('@backend.get("/resources/leads/list")', components_page)
        self.assertIn('@backend.get("/resources/leads/stats")', components_page)
        self.assertIn('@backend.get("/resources/leads/detail")', components_page)
        self.assertIn('@backend.post("/resources/leads/save")', components_page)
        self.assertIn('@backend.post("/resources/leads/delete")', components_page)
        self.assertIn('@backend.post("/resources/leads/duplicate")', components_page)
        self.assertIn('@backend.post("/resources/leads/bulk")', components_page)
        self.assertIn('@backend.post("/auth/login")', components_page)
        self.assertIn('@backend.post("/auth/logout")', components_page)
        self.assertIn('@backend.get("/auth/me")', components_page)
        self.assertIn('@backend.method("demo.lead.create")', components_page)
        self.assertIn('widget-backend', components_page)
        self.assertIn('ApiCall(', components_page)
        self.assertIn('MethodCall(', components_page)
        self.assertIn('"/api/_method"', components_page)
        self.assertIn('ResultBox(id="backend_result", format="message")', components_page)
        self.assertIn('ResultBox(id="backend_method_result", format="json")', components_page)
        self.assertIn("backend.configure_smtp(", components_page)
        self.assertIn('upload_url="/api/demo/upload"', components_page)
        self.assertIn("/api/resources/leads/list", components_page)
        self.assertIn("/api/resources/leads/stats", components_page)
        self.assertIn("/api/resources/leads/detail", components_page)
        self.assertIn("/api/resources/leads/save", components_page)
        self.assertIn("/api/resources/leads/delete", components_page)
        self.assertIn("/api/resources/leads/duplicate", components_page)
        self.assertIn("/api/resources/leads/bulk", components_page)
        self.assertIn("/api/auth/login", components_page)
        self.assertIn("/api/auth/me", components_page)
        self.assertIn("session_store='.martin/sessions.json'", components_page)


if __name__ == "__main__":
    unittest.main()
