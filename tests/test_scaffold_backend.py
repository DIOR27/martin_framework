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

        self.assertIn("from martin.backend import ApiCall, Backend, Ref, Response, ResultBox", components_page)
        self.assertIn("def register_components_backend(backend: Backend):", components_page)
        self.assertIn('@backend.post("/demo/contact")', components_page)
        self.assertIn('widget-backend', components_page)
        self.assertIn('ApiCall(', components_page)
        self.assertIn('ResultBox(id="backend_result", format="message")', components_page)
        self.assertIn("backend.configure_smtp(", components_page)


if __name__ == "__main__":
    unittest.main()
