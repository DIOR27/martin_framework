import unittest

import martin
from martin import App, Text
from martin.backend import Request
from martin.widget import Widget


class RequestAndSecurityTests(unittest.TestCase):
    def test_request_query_multi_and_json(self):
        req = Request(
            method="POST",
            path="/api/demo",
            query_string="a=1&a=2&b=3",
            body=b'{"ok": true}',
            headers={"Content-Type": "application/json"},
        )
        self.assertEqual(req.query["a"], "2")
        self.assertEqual(req.query_multi["a"], ["1", "2"])
        self.assertEqual(req.json()["ok"], True)

    def test_request_json_silent_default(self):
        req = Request(
            method="POST",
            path="/api/demo",
            query_string="",
            body=b"{bad json",
            headers={"Content-Type": "application/json"},
        )
        self.assertEqual(req.json(default={"fallback": 1}, silent=True), {"fallback": 1})

    def test_widget_attrs_escape(self):
        attrs = Widget._attrs(title='a"b<c>')
        self.assertIn('title="a&quot;b&lt;c&gt;"', attrs)

    def test_app_wrap_escapes_meta(self):
        app = App(
            build=lambda: Text("ok"),
            title='Title <script>alert("x")</script>',
            description='desc "quoted" <b>tag</b>',
            hot_reload=False,
            theme_toggle=False,
        )
        html = app._render("/")
        self.assertIn("&lt;script&gt;alert(&quot;x&quot;)&lt;/script&gt;", html)
        self.assertNotIn('<meta name="description" content="desc "quoted"', html)
        self.assertIn("desc &quot;quoted&quot; &lt;b&gt;tag&lt;/b&gt;", html)

    def test_core_no_longer_exports_api_helpers(self):
        self.assertFalse(hasattr(martin, "ApiCall"))
        self.assertFalse(hasattr(martin, "Response"))


if __name__ == "__main__":
    unittest.main()
