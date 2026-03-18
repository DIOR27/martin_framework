import unittest
from unittest.mock import patch

from martin import App, Button, Text
from martin.backend import ApiCall, Backend, Mailer, Response, SMTPConfig


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

    def test_backend_respects_response_instances(self):
        backend = Backend(prefix="/api")

        @backend.get("/text")
        def text(req):
            return Response("ok", content_type="text/plain")

        resp = backend.handle_request("GET", "/api/text", "", b"", {})
        body, ct = resp.to_bytes()
        self.assertEqual(body, b"ok")
        self.assertIn("text/plain", ct)

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


if __name__ == "__main__":
    unittest.main()
