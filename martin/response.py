"""
Martin — Response
Respuesta HTTP explícita para endpoints @app.route().

Uso:
    from martin import Response

    @app.route("/api/hello")
    def hello(req):
        return Response({"message": "hola"})           # JSON 200

    @app.route("/api/error")
    def error(req):
        return Response({"error": "no encontrado"}, status=404)

    @app.route("/api/text")
    def text(req):
        return Response("hola mundo", content_type="text/plain")

    # También puedes devolver dict directamente (JSON automático):
    @app.route("/api/ping")
    def ping(req):
        return {"pong": True}
"""


class Response:
    """
    Respuesta HTTP explícita.

    Response(data)
    Response(data, status=200)
    Response(data, status=404, content_type="application/json")
    Response("texto plano", content_type="text/plain")
    Response(b"bytes", content_type="application/octet-stream")
    """

    def __init__(self, data, status=200, content_type=None, headers=None):
        self.data = data
        self.status = status
        self.content_type = content_type
        self.headers = headers or {}

    def to_bytes(self):
        """Serializa el body a bytes y determina el content-type."""
        import json

        if isinstance(self.data, bytes):
            body = self.data
            ct = self.content_type or "application/octet-stream"

        elif isinstance(self.data, str):
            body = self.data.encode("utf-8")
            ct = self.content_type or "text/plain; charset=utf-8"

        elif isinstance(self.data, (dict, list)):
            body = json.dumps(self.data, ensure_ascii=False).encode("utf-8")
            ct = self.content_type or "application/json; charset=utf-8"

        else:
            body = str(self.data).encode("utf-8")
            ct = self.content_type or "text/plain; charset=utf-8"

        return body, ct


class Request:
    """
    Objeto request pasado a los handlers de @app.route().

    req.method          → "GET" | "POST" | ...
    req.path            → "/api/hello"
    req.query           → {"q": "valor", ...}   (query string)
    req.body            → bytes (body crudo)
    req.json()          → dict  (body parseado como JSON)
    req.form()          → dict  (body parseado como form-urlencoded)
    req.headers         → dict de headers
    """

    def __init__(self, method, path, query_string, body, headers):
        self.method = method
        self.path = path
        self.headers = headers
        self._body = body
        self._query_raw = query_string

        # Parse query string
        import urllib.parse

        self.query = dict(urllib.parse.parse_qsl(query_string or ""))

    @property
    def body(self):
        return self._body

    def json(self):
        import json

        return json.loads(self._body.decode("utf-8"))

    def form(self):
        import urllib.parse

        return dict(urllib.parse.parse_qsl(self._body.decode("utf-8")))

    def __repr__(self):
        return f"<Request {self.method} {self.path}>"
