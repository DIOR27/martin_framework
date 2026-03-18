"""Simple backend extension for Martin apps."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable
import inspect

from .http import Request, Response
from .mail import Mailer, SMTPConfig


@dataclass
class BackendContext:
    """
    Contexto de ejecución para métodos RPC del backend.
    """

    backend: "Backend"
    request: Request
    method_name: str = ""

    @property
    def query(self):
        return self.request.query

    @property
    def headers(self):
        return self.request.headers

    def json(self, default=None, silent=False):
        return self.request.json(default=default, silent=silent)


class Backend:
    """
    Backend HTTP sencillo para usar junto a `martin.App`.

    Incluye:
    - rutas REST (`get`, `post`, `put`, `delete`)
    - RPC por método (`@backend.method(...)` + `backend.call(...)`)
    - hooks (`before_request`, `after_request`)
    - SMTP opcional
    """

    def __init__(
        self,
        prefix="/api",
        cors=True,
        mailer=None,
        method_path="/_method",
    ):
        prefix = (prefix or "").strip()
        if prefix in {"", "/"}:
            self.prefix = ""
        else:
            self.prefix = "/" + prefix.strip("/")
        self.cors = cors
        self._routes: dict[tuple[str, str], Callable[..., Any]] = {}
        self._methods: dict[str, Callable[..., Any]] = {}
        self._before_hooks: list[Callable[[Request], Any]] = []
        self._after_hooks: list[Callable[[Request, Response], Any]] = []
        self.mailer = mailer
        self.method_path = self._normalize_path(method_path or "/_method")

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

    def method(self, name=None):
        """
        Registra un método RPC invocable desde widgets.
        """

        def decorator(fn):
            key = str(name or getattr(fn, "__name__", "")).strip()
            if not key:
                raise ValueError("Method name cannot be empty.")
            self._methods[key] = fn
            return fn

        return decorator

    action = method

    def call(
        self,
        method_name,
        params=None,
        args=None,
        kwargs=None,
        target=None,
        loading="Procesando...",
        on_success=None,
        on_error=None,
        endpoint=None,
    ):
        """
        Crea una acción JS lista para `Button(on_click=...)`.
        """
        from .widgets import MethodCall

        ep = endpoint
        if not ep:
            ep = (self.prefix + self.method_path) if self.prefix else self.method_path

        return MethodCall(
            method=method_name,
            params=params,
            args=args,
            kwargs=kwargs,
            endpoint=ep,
            target=target,
            loading=loading,
            on_success=on_success,
            on_error=on_error,
        )

    def before_request(self, fn):
        self._before_hooks.append(fn)
        return fn

    def after_request(self, fn):
        self._after_hooks.append(fn)
        return fn

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

        req = Request(method, path, query_string, body, headers)

        if method == "POST" and route_path == self.method_path:
            resp = self._handle_method_request(req)
            resp.headers = {**cors_headers, **getattr(resp, "headers", {})}
            return resp

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

        try:
            for hook in self._before_hooks:
                maybe = hook(req)
                if maybe is not None:
                    resp = self._to_response(maybe)
                    resp.headers = {**cors_headers, **getattr(resp, "headers", {})}
                    return resp

            result = handler(req)
            resp = self._to_response(result)

            for hook in self._after_hooks:
                maybe_resp = hook(req, resp)
                if maybe_resp is not None:
                    resp = self._to_response(maybe_resp)
        except Exception as exc:
            resp = Response({"error": "Error interno", "detail": str(exc)}, status=500)

        resp.headers = {**cors_headers, **getattr(resp, "headers", {})}
        return resp

    def _handle_method_request(self, req: Request) -> Response:
        payload = req.json(default={}, silent=True) or {}
        method_name = str(payload.get("method") or payload.get("action") or "").strip()
        if not method_name:
            return Response({"error": "Campo 'method' requerido."}, status=400)

        fn = self._methods.get(method_name)
        if fn is None:
            return Response({"error": f"Metodo '{method_name}' no registrado."}, status=404)

        ctx = BackendContext(self, req, method_name=method_name)
        args = payload.get("args", [])
        kwargs = payload.get("kwargs", {})
        params = payload.get("params", None)

        if args is None:
            args = []
        if kwargs is None:
            kwargs = {}
        if not isinstance(args, list):
            args = [args]
        if not isinstance(kwargs, dict):
            kwargs = {}

        try:
            result = self._invoke_method(fn, ctx, args, kwargs, params)
            return self._to_response(result)
        except Exception as exc:
            return Response(
                {
                    "error": "Error ejecutando metodo backend.",
                    "method": method_name,
                    "detail": str(exc),
                },
                status=500,
            )

    @staticmethod
    def _can_bind(fn, args, kwargs):
        try:
            inspect.signature(fn).bind_partial(*args, **kwargs)
            return True
        except TypeError:
            return False

    def _invoke_method(self, fn, ctx: BackendContext, args, kwargs, params):
        candidates = []

        if params is not None and not args and not kwargs:
            if isinstance(params, dict):
                candidates.extend(
                    [
                        ((ctx,), params),
                        ((), params),
                        ((ctx, params), {}),
                        ((params,), {}),
                    ]
                )
            elif isinstance(params, list):
                candidates.extend(
                    [
                        ((ctx, *tuple(params)), {}),
                        (tuple(params), {}),
                    ]
                )
            else:
                candidates.extend(
                    [
                        ((ctx, params), {}),
                        ((params,), {}),
                    ]
                )
        else:
            candidates.extend(
                [
                    ((ctx, *tuple(args)), kwargs),
                    (tuple(args), kwargs),
                ]
            )

        for c_args, c_kwargs in candidates:
            if self._can_bind(fn, c_args, c_kwargs):
                return fn(*c_args, **c_kwargs)

        first_args, first_kwargs = candidates[0]
        return fn(*first_args, **first_kwargs)

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
            inner = normalized[len(self.prefix) :]
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

