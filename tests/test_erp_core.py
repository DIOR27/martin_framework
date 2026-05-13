"""Integration tests for Martin ERP core (ORM + Module + Backend Bridge + Hooks)."""

import json
import os
import tempfile
import unittest
from pathlib import Path


class ORMTests(unittest.TestCase):
    """Test ORM CRUD operations."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.orig_cwd = os.getcwd()
        os.chdir(self.tmpdir)

    def tearDown(self):
        os.chdir(self.orig_cwd)

    def test_basic_crud(self):
        from martin.orm import Model, Char, Text, Integer, Boolean, Selection

        class Product(Model):
            _name = "test_product"
            _fields = {
                "name": Char(required=True),
                "description": Text(),
                "price": Integer(default=0),
                "active": Boolean(default=True),
                "status": Selection(selection=[("draft", "Draft"), ("published", "Published")], default="draft"),
            }

        # Create
        pid = Product.create({"name": "Widget", "price": 100, "description": "A widget"})
        self.assertGreater(pid, 0)

        # Read
        rec = Product.read(pid)
        self.assertEqual(len(rec), 1)
        self.assertEqual(rec[0]["name"], "Widget")
        self.assertEqual(rec[0]["price"], 100)
        self.assertTrue(rec[0]["active"])
        self.assertEqual(rec[0]["status"], "draft")

        # Search
        results = Product.search([("price", ">=", 50)])
        self.assertGreaterEqual(len(results), 1)

        count = Product.search_count([("active", "=", True)])
        self.assertGreaterEqual(count, 1)

        # Update
        Product.write(pid, {"price": 150, "status": "published"})
        rec = Product.read(pid)
        self.assertEqual(rec[0]["price"], 150)
        self.assertEqual(rec[0]["status"], "published")

        # Delete
        Product.unlink(pid)
        self.assertEqual(Product.read(pid), [])

    def test_query_parser(self):
        from martin.orm import parse

        # Basic equal
        q = parse([("name", "=", "John")])
        self.assertIn("name", q.sql)
        self.assertEqual(q.params, ["John"])

        # OR
        q = parse(["|", ("name", "=", "A"), ("name", "=", "B")])
        self.assertIn("OR", q.sql)

        # NOT
        q = parse(["!", ("active", "=", True)])
        self.assertIn("NOT", q.sql)

        # ilike
        q = parse([("email", "ilike", "test")])
        self.assertIn("LOWER", q.sql)

        # IN
        q = parse([("id", "in", [1, 2, 3])])
        self.assertIn("IN", q.sql)
        self.assertEqual(len(q.params), 3)

        # Empty domain
        q = parse([])
        self.assertEqual(q.sql, "")

    def test_field_defaults(self):
        from martin.orm import Char, Boolean, Integer
        c = Char(required=True, label="Name")
        self.assertEqual(c.to_column_type(), "VARCHAR(255)")
        self.assertEqual(c.py_to_db("hello"), "hello")

        b = Boolean(default=True)
        self.assertEqual(b.db_to_py(1), True)
        self.assertEqual(b.db_to_py(0), False)
        self.assertEqual(b.db_to_py(None), True)  # default=True

        b2 = Boolean(default=False)
        self.assertEqual(b2.db_to_py(None), False)  # default=False

        i = Integer(default=0)
        self.assertEqual(i.to_column_type(), "INTEGER")


class ModuleSystemTests(unittest.TestCase):
    """Test module discovery, loading, dependency resolution."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.orig_cwd = os.getcwd()
        os.chdir(self.tmpdir)
        self._setup_modules()

    def tearDown(self):
        from martin.module import ModuleRegistry
        ModuleRegistry.reset()
        os.chdir(self.orig_cwd)

    def _setup_modules(self):
        modules_dir = Path("modules")
        modules_dir.mkdir()

        # Base
        base = modules_dir / "base"
        base.mkdir()
        (base / "__init__.py").write_text("")
        (base / "manifest.py").write_text('manifest = {"name": "Base", "version": "1.0.0", "depends": []}\n')

        # Contacts (depends on base)
        contacts = modules_dir / "contacts"
        contacts.mkdir()
        (contacts / "__init__.py").write_text("")
        (contacts / "manifest.py").write_text('manifest = {"name": "Contacts", "version": "1.0.0", "depends": ["base"]}\n')

    def test_discovery_and_deps(self):
        from martin.module import ModuleRegistry

        ModuleRegistry.discover("modules")
        self.assertEqual(len(ModuleRegistry.all()), 2)

        ordered = ModuleRegistry.resolve_dependencies()
        names = [m.name for m in ordered]
        self.assertEqual(names, ["base", "contacts"])

    def test_circular_dep_detection(self):
        from martin.module import ModuleRegistry

        circ_a = Path("modules") / "circ_a"
        circ_a.mkdir()
        (circ_a / "__init__.py").write_text("")
        (circ_a / "manifest.py").write_text('manifest = {"name": "CircA", "depends": ["circ_b"]}\n')

        circ_b = Path("modules") / "circ_b"
        circ_b.mkdir()
        (circ_b / "__init__.py").write_text("")
        (circ_b / "manifest.py").write_text('manifest = {"name": "CircB", "depends": ["circ_a"]}\n')

        ModuleRegistry.discover("modules")
        with self.assertRaises(ValueError):
            ModuleRegistry.resolve_dependencies()

    def test_hooks(self):
        from martin.module import register_hook, resolve_hooks, clear_hooks

        register_hook("test.slot", lambda ctx: "alpha", priority=10, module="mod_a")
        register_hook("test.slot", lambda ctx: "beta", priority=50, module="mod_b")

        results = resolve_hooks("test.slot")
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0], "alpha")
        self.assertEqual(results[1], "beta")
        clear_hooks("test.slot")

    def test_load_and_orm_integration(self):
        from martin.module import ModuleRegistry
        from martin.orm import Model, Char, create_all_tables, ModelRegistry

        # Create a module with a model
        inv_dir = Path("modules") / "inventory"
        inv_dir.mkdir()
        (inv_dir / "__init__.py").write_text(
            "from .models import *\n"
        )
        (inv_dir / "manifest.py").write_text('manifest = {"name": "Inventory", "version": "1.0.0", "depends": ["base"]}\n')
        (inv_dir / "models").mkdir()
        (inv_dir / "models" / "__init__.py").write_text(
            "from .product import Product\n"
        )
        (inv_dir / "models" / "product.py").write_text(
            "from martin.orm import Model, Char, Integer\n"
            "class Product(Model):\n"
            '    _name = "product"\n'
            '    _fields = {\n'
            '        "name": Char(required=True),\n'
            '        "price": Integer(default=0),\n'
            "    }\n"
        )

        ModuleRegistry.discover("modules")
        ModuleRegistry.resolve_dependencies()
        ModuleRegistry.load_all()

        self.assertIsNotNone(ModelRegistry.get("product"))
        create_all_tables()

        # CRUD via the loaded model
        Product = ModelRegistry.get("product")
        pid = Product.create({"name": "Test Product", "price": 99})
        rec = Product.read(pid)
        self.assertEqual(rec[0]["name"], "Test Product")

        ModuleRegistry.reset()


class BackendBridgeTests(unittest.TestCase):
    """Test ORM + Backend REST bridge."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.orig_cwd = os.getcwd()
        os.chdir(self.tmpdir)

    def tearDown(self):
        os.chdir(self.orig_cwd)

    def test_auto_register_endpoints(self):
        from martin.orm import Model, Char, Boolean, auto_register_model, create_all_tables
        from martin.backend import Backend
        from martin.backend.http import Request

        class Contact(Model):
            _name = "test_rest"
            _fields = {"name": Char(required=True), "email": Char(), "active": Boolean(default=True)}

        create_all_tables()
        cid = Contact.create({"name": "Test"})

        backend = Backend(prefix="/api")
        auto_register_model(backend, Contact)

        def req(method, path, qs="", body=b""):
            return Request(method, path, qs, body, {})

        # Search
        resp = backend.handle_request("GET", "/api/resources/test_rest/search", "domain=[]", b"", {})
        self.assertEqual(resp.status, 200)
        data = json.loads(resp.data) if isinstance(resp.data, str) else resp.data
        self.assertGreaterEqual(data["total"], 1)

        # Detail
        resp = backend.handle_request("GET", f"/api/resources/test_rest/detail", f"id={cid}", b"", {})
        data = json.loads(resp.data) if isinstance(resp.data, str) else resp.data
        self.assertEqual(data["data"]["name"], "Test")

        # Create
        resp = backend.handle_request("POST", "/api/resources/test_rest/save", "",
                                       b'{"name":"New","email":"n@t.com"}', {"Content-Type": "application/json"})
        data = json.loads(resp.data) if isinstance(resp.data, str) else resp.data
        self.assertGreater(data["id"], 0)

        # Update
        resp = backend.handle_request("PATCH", "/api/resources/test_rest/update", "",
                                       json.dumps({"ids": [cid], "email": "updated@t.com"}).encode(),
                                       {"Content-Type": "application/json"})
        data = json.loads(resp.data) if isinstance(resp.data, str) else resp.data
        self.assertGreaterEqual(data["updated"], 1)
        rec = Contact.read(cid)
        self.assertEqual(rec[0]["email"], "updated@t.com")

        # Delete
        resp = backend.handle_request("POST", "/api/resources/test_rest/delete", "",
                                       json.dumps({"ids": [cid]}).encode(), {"Content-Type": "application/json"})
        data = json.loads(resp.data) if isinstance(resp.data, str) else resp.data
        self.assertGreaterEqual(data["deleted"], 1)
        self.assertEqual(Contact.read(cid), [])

    def test_list_pagination(self):
        from martin.orm import Model, Char, auto_register_model, create_all_tables
        from martin.backend import Backend

        class Item(Model):
            _name = "test_item"
            _fields = {"name": Char()}

        create_all_tables()
        for i in range(5):
            Item.create({"name": f"Item {i}"})

        backend = Backend(prefix="/api")
        auto_register_model(backend, Item)

        resp = backend.handle_request("GET", "/api/resources/test_item/list", "page=1&per_page=2", b"", {})
        data = json.loads(resp.data) if isinstance(resp.data, str) else resp.data
        self.assertEqual(len(data["data"]), 2)
        self.assertEqual(data["total"], 5)
        self.assertEqual(data["pages"], 3)


class WidgetHookTests(unittest.TestCase):
    """Test widget slot/hook system."""

    def test_widget_slot_declaration(self):
        from martin.widget import Widget

        class TestWidget(Widget):
            _slots = {"test_slot": {"desc": "A test slot"}}

        w = TestWidget()
        result = w.render_slot("nonexistent")
        self.assertEqual(result, "")

    def test_slot_contributions(self):
        from martin.widget import Widget
        from martin.module import register_hook, clear_hooks

        class TestWidget(Widget):
            _slots = {"my_slot": {}}

        register_hook("TestWidget.my_slot", lambda ctx: "<ext/>", priority=10, module="test")
        register_hook("TestWidget.my_slot", lambda ctx: "<core/>", priority=50, module="test2")

        w = TestWidget()
        result = w.render_slot("my_slot", {"foo": "bar"})
        self.assertIn("<ext/>", result)
        self.assertIn("<core/>", result)
        # Priority order: ext (10) before core (50)
        self.assertLess(result.index("<ext/>"), result.index("<core/>"))
        clear_hooks("TestWidget.my_slot")

    def test_resource_widget_slots_declared(self):
        from martin.widgets.advanced import ResourceForm, ResourceTable, ResourceDetails, ResourceView

        self.assertIn("form_fields", ResourceForm._slots)
        self.assertIn("header_buttons", ResourceForm._slots)
        self.assertIn("footer_actions", ResourceForm._slots)
        self.assertIn("toolbar_buttons", ResourceTable._slots)
        self.assertIn("extra_columns", ResourceTable._slots)
        self.assertIn("detail_fields", ResourceDetails._slots)
        self.assertIn("action_buttons", ResourceDetails._slots)


class CLIModuleTests(unittest.TestCase):
    """Test CLI module commands."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.orig_cwd = os.getcwd()
        os.chdir(self.tmpdir)

    def tearDown(self):
        os.chdir(self.orig_cwd)

    def test_module_create(self):
        from martin.cli import _cmd_module_create

        class Args:
            name = "testmod"
            desc = "Test module"
            dir = "modules"
            module_command = "create"

        _cmd_module_create(Args())

        mod_dir = Path("modules/testmod")
        self.assertTrue(mod_dir.exists())
        self.assertTrue((mod_dir / "manifest.py").exists())
        self.assertTrue((mod_dir / "models" / "testmod.py").exists())
        self.assertTrue((mod_dir / "views" / "__init__.py").exists())

        manifest = (mod_dir / "manifest.py").read_text()
        self.assertIn("testmod", manifest)

    def test_module_list(self):
        from martin.module import ModuleRegistry
        from martin.cli import _cmd_module_list

        # Create a module first
        mod_dir = Path("modules/mymod")
        mod_dir.mkdir(parents=True)
        (mod_dir / "__init__.py").write_text("")
        (mod_dir / "manifest.py").write_text('manifest = {"name": "MyMod", "version": "1.0.0", "depends": []}\n')

        class Args:
            dir = "modules"
            module_command = "list"

        # Just verify no crash
        _cmd_module_list(Args())
        ModuleRegistry.reset()


if __name__ == "__main__":
    unittest.main()
