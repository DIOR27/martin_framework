"""Simple backend extension for Martin apps."""

from .http import Request, Response
from .mail import Mailer, SMTPConfig


class Backend:
    """
    Backend HTTP pequeno para usar junto a `martin.App`.
    """

    def __init__(self, prefix="/api", cors=True, mailer=None):
        prefix = (prefix or "").strip()
        if prefix in {"", "/"}:
            self.prefix = ""
        else:
            self.prefix = "/" + prefix.strip("/")
        self.cors = cors
        self._routes = {}
        self.mailer = mailer

    def route(self, path, methods=None):
        if methods is None:
            methods = ["GET"]
        route_path = self._normalize_path(path)

        def decorator(fn):
            for method in methods:
                self._routes[(str(method).upper(), route_path)] = fn
            return fn

        return decorator

    def get(self, path):
        return self.route(path, methods=["GET"])

    def post(self, path):
        return self.route(path, methods=["POST"])

    def put(self, path):
        return self.route(path, methods=["PUT"])

    def delete(self, path):
        return self.route(path, methods=["DELETE"])

    def options(self, path):
        return self.route(path, methods=["OPTIONS"])

    def mount(self, app):
        previous = getattr(app, "_request_handler", None)

        def chained(method, path, query_string, body, headers):
            resp = self.handle_request(method, path, query_string, body, headers)
            if resp is not None:
                return resp
            if callable(previous):
                return previous(method, path, query_string, body, headers)
            return None

        app.set_request_handler(chained)
        return app

    def set_mailer(self, mailer):
        self.mailer = mailer
        return self

    def configure_smtp(self, **kwargs):
        self.mailer = Mailer(SMTPConfig(**kwargs))
        return self.mailer

    def send_mail(self, *args, **kwargs):
        if self.mailer is None:
            raise RuntimeError("No mailer configured. Use set_mailer() or configure_smtp().")
        return self.mailer.send(*args, **kwargs)

    def handle_request(self, method, path, query_string, body, headers):
        route_path = self._route_path_for(path)
        if route_path is None:
            return None

        method = str(method).upper()
        cors_headers = self._cors_headers(headers)

        if method == "OPTIONS":
            return Response("", status=204, headers=cors_headers)

        handler = self._routes.get((method, route_path))
        if handler is None:
            has_path = any(p == route_path for _, p in self._routes)
            if has_path:
                return Response(
                    {"error": f"Metodo {method} no permitido"},
                    status=405,
                    headers=cors_headers,
                )
            return Response(
                {"error": f"Ruta '{path}' no encontrada"},
                status=404,
                headers=cors_headers,
            )

        req = Request(method, path, query_string, body, headers)
        try:
            result = handler(req)
            resp = self._to_response(result)
        except Exception as exc:
            resp = Response({"error": "Error interno", "detail": str(exc)}, status=500)

        resp.headers = {**cors_headers, **getattr(resp, "headers", {})}
        return resp

    def _to_response(self, result):
        if isinstance(result, Response):
            return result
        if isinstance(result, (dict, list)):
            return Response(result)
        return Response(result, content_type="text/plain; charset=utf-8")

    def _normalize_path(self, path):
        text = "/" + str(path or "").strip("/")
        return "/" if text == "/" else text.rstrip("/")

    def _route_path_for(self, path):
        normalized = self._normalize_path(path)
        if self.prefix:
            if normalized == self.prefix:
                return "/"
            if not normalized.startswith(self.prefix + "/"):
                return None
            inner = normalized[len(self.prefix):]
            return self._normalize_path(inner)
        return normalized

    def _cors_headers(self, headers):
        if not self.cors:
            return {}
        return {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": headers.get(
                "Access-Control-Request-Headers",
                "Content-Type",
            ),
        }


SimpleBackend = Backend
