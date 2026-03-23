import unittest
from unittest.mock import patch
import tempfile
from pathlib import Path

from martin import App, Button, Text
from martin.backend import ApiCall, Backend, Mailer, MethodCall, Response, SMTPConfig


class BackendExtensionTests(unittest.TestCase):
    def test_backend_mount_dispatches_request(self):
        app = App(build=lambda: Text("ok"), hot_reload=False, theme_toggle=False)
        backend = Backend(prefix="/api")

        @backend.get("/ping")
        def ping(req):
            return {"pong": True, "path": req.path}

        backend.mount(app)
        resp = app._dispatch_request("GET", "/api/ping", "", b"", {})
        self.assertIsNotNone(resp)
        body, ct = resp.to_bytes()
        self.assertEqual(resp.status, 200)
        self.assertIn(b'"pong": true', body)
        self.assertIn("application/json", ct)

    def test_backend_returns_404_for_unknown_prefixed_route(self):
        backend = Backend(prefix="/api")
        resp = backend.handle_request("GET", "/api/missing", "", b"", {})
        self.assertEqual(resp.status, 404)

    def test_button_accepts_backend_apicall(self):
        html = Button(
            "Enviar",
            id="send_btn",
            on_click=ApiCall("/api/save", body={"name": "Martin"}),
        ).render()
        self.assertIn("fetch(", html)
        self.assertIn("/api/save", html)
        self.assertIn("send_btn", html)
        self.assertIn("__martinToastFromPayload", html)

    def test_backend_respects_response_instances(self):
        backend = Backend(prefix="/api")

        @backend.get("/text")
        def text(req):
            return Response("ok", content_type="text/plain")

        resp = backend.handle_request("GET", "/api/text", "", b"", {})
        body, ct = resp.to_bytes()
        self.assertEqual(body, b"ok")
        self.assertIn("text/plain", ct)

    def test_backend_method_rpc_dispatch(self):
        backend = Backend(prefix="/api")

        @backend.method("math.add")
        def add(ctx, a=0, b=0):
            return {"total": int(a) + int(b), "method": ctx.method_name}

        resp = backend.handle_request(
            "POST",
            "/api/_method",
            "",
            b'{"method":"math.add","params":{"a":4,"b":7}}',
            {"Content-Type": "application/json"},
        )
        self.assertEqual(resp.status, 200)
        body, _ = resp.to_bytes()
        self.assertIn(b'"total": 11', body)
        self.assertIn(b'"method": "math.add"', body)

    def test_method_call_widget_helper_renders_rpc_call(self):
        html = Button(
            "Crear",
            id="create_btn",
            on_click=MethodCall(
                "lead.create",
                params={"name": "Martin"},
                endpoint="/api/_method",
            ),
        ).render()
        self.assertIn("/api/_method", html)
        self.assertIn("lead.create", html)
        self.assertIn("create_btn", html)

    def test_backend_call_helper_builds_action_for_button(self):
        backend = Backend(prefix="/api")
        html = Button(
            "Guardar",
            id="save_btn",
            on_click=backend.call("lead.create", params={"name": "Diego"}),
        ).render()
        self.assertIn("/api/_method", html)
        self.assertIn("lead.create", html)
        self.assertIn("save_btn", html)

    @patch("martin.backend.mail.smtplib.SMTP")
    def test_mailer_sends_via_configured_smtp(self, smtp_cls):
        smtp = smtp_cls.return_value
        mailer = Mailer(
            SMTPConfig(
                host="smtp.example.com",
                port=587,
                username="user",
                password="secret",
                sender="noreply@example.com",
                use_tls=True,
            )
        )
        result = mailer.send(
            subject="Hola",
            to="diego@example.com",
            text="Mensaje de prueba",
        )
        smtp.starttls.assert_called_once()
        smtp.login.assert_called_once_with("user", "secret")
        smtp.send_message.assert_called_once()
        self.assertEqual(result["subject"], "Hola")

    def test_backend_can_configure_and_use_mailer(self):
        backend = Backend(prefix="/api")
        mailer = backend.configure_smtp(
            host="smtp.example.com",
            sender="noreply@example.com",
            username="user",
            password="secret",
        )
        self.assertIs(backend.mailer, mailer)

    def test_backend_with_toast_adds_feedback_payload(self):
        backend = Backend(prefix="/api")
        payload = backend.with_toast({"message": "ok"}, message="Saved", variant="success")
        self.assertEqual(payload["message"], "ok")
        self.assertEqual(payload["toast"]["message"], "Saved")
        self.assertEqual(payload["toast"]["variant"], "success")

    def test_request_parses_multipart_form_and_files(self):
        backend = Backend(prefix="/api")

        @backend.post("/upload")
        def upload(req):
            asset = req.file("asset")
            return {
                "title": req.form().get("title"),
                "name": asset.filename,
                "size": asset.size,
                "content_type": asset.content_type,
            }

        boundary = "----martinBoundary"
        body = (
            f"--{boundary}\r\n"
            'Content-Disposition: form-data; name="title"\r\n\r\n'
            "Demo file\r\n"
            f"--{boundary}\r\n"
            'Content-Disposition: form-data; name="asset"; filename="demo.txt"\r\n'
            "Content-Type: text/plain\r\n\r\n"
            "hello martin\r\n"
            f"--{boundary}--\r\n"
        ).encode("utf-8")
        resp = backend.handle_request(
            "POST",
            "/api/upload",
            "",
            body,
            {"Content-Type": f"multipart/form-data; boundary={boundary}"},
        )
        self.assertEqual(resp.status, 200)
        payload, _ = resp.to_bytes()
        self.assertIn(b'"title": "Demo file"', payload)
        self.assertIn(b'"name": "demo.txt"', payload)
        self.assertIn(b'"content_type": "text/plain"', payload)

    def test_backend_auth_session_flow(self):
        backend = Backend(prefix="/api")

        @backend.post("/auth/login")
        def login(req):
            return backend.login({"user": "admin"})

        @backend.get("/auth/me")
        @backend.require_auth
        def me(req):
            return {"user": backend.get_session(req)}

        login_resp = backend.handle_request("POST", "/api/auth/login", "", b"{}", {"Content-Type": "application/json"})
        self.assertEqual(login_resp.status, 200)
        cookies = login_resp.headers.get("Set-Cookie")
        self.assertTrue(cookies)
        me_resp = backend.handle_request("GET", "/api/auth/me", "", b"", {"Cookie": cookies})
        self.assertEqual(me_resp.status, 200)
        payload, _ = me_resp.to_bytes()
        self.assertIn(b'"user": {"user": "admin"}', payload)

    def test_backend_can_persist_sessions_to_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = Path(tmp) / "sessions.json"
            backend = Backend(prefix="/api", session_store=str(store))
            sid = backend.create_session({"user": "persisted"})
            self.assertTrue(store.exists())

            backend2 = Backend(prefix="/api", session_store=str(store))
            req_headers = {"Cookie": f"{backend2.session_cookie}={sid}"}
            req_resp = backend2.handle_request("GET", "/api/missing", "", b"", req_headers)
            self.assertEqual(backend2.get_session(type("Req", (), {"cookies": {backend2.session_cookie: sid}})()), {"user": "persisted"})
            self.assertEqual(req_resp.status, 404)


if __name__ == "__main__":
    unittest.main()
