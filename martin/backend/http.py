"""HTTP primitives for martin.backend."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class UploadedFile:
    """Archivo recibido en una petición multipart."""

    name: str
    filename: str
    content_type: str
    content: bytes

    @property
    def size(self):
        return len(self.content or b"")

    def text(self, encoding="utf-8", errors="replace"):
        return (self.content or b"").decode(encoding, errors)


class Response:
    """Respuesta HTTP explicita para `martin.backend.Backend`."""

    def __init__(self, data, status=200, content_type=None, headers=None):
        self.data = data
        self.status = status
        self.content_type = content_type
        self.headers = headers or {}

    def set_cookie(
        self,
        name,
        value,
        *,
        path="/",
        http_only=True,
        same_site="Lax",
        max_age=None,
    ):
        parts = [f"{name}={value}", f"Path={path}"]
        if max_age is not None:
            parts.append(f"Max-Age={int(max_age)}")
        if http_only:
            parts.append("HttpOnly")
        if same_site:
            parts.append(f"SameSite={same_site}")
        cookie = "; ".join(parts)
        existing = self.headers.get("Set-Cookie")
        if existing:
            if isinstance(existing, list):
                existing.append(cookie)
            else:
                self.headers["Set-Cookie"] = [existing, cookie]
        else:
            self.headers["Set-Cookie"] = cookie
        return self

    def delete_cookie(self, name, *, path="/"):
        return self.set_cookie(name, "", path=path, max_age=0)

    def to_bytes(self):
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
    """Objeto request para handlers de `Backend.route(...)`."""

    def __init__(self, method, path, query_string, body, headers):
        self.method = method
        self.path = path
        self.headers = headers
        self._body = body
        self._query_raw = query_string
        self._multipart_cache = None

        import urllib.parse

        self.query = dict(urllib.parse.parse_qsl(query_string or ""))
        self.query_multi = urllib.parse.parse_qs(query_string or "")
        raw_cookie = ""
        for key, value in (headers or {}).items():
            if str(key).lower() == "cookie":
                raw_cookie = str(value or "")
                break
        self.cookies = {}
        if raw_cookie:
            for pair in raw_cookie.split(";"):
                if "=" not in pair:
                    continue
                name, value = pair.split("=", 1)
                self.cookies[name.strip()] = value.strip()

    @property
    def body(self):
        return self._body

    def json(self, default=None, silent=False):
        import json

        if not self._body:
            return default
        try:
            return json.loads(self._body.decode("utf-8"))
        except Exception:
            if silent:
                return default
            raise

    def form(self, default=None, silent=False):
        import urllib.parse

        multipart = self._multipart()
        if multipart is not None:
            return dict(multipart["form"])

        if not self._body:
            return default if default is not None else {}
        try:
            return dict(urllib.parse.parse_qsl(self._body.decode("utf-8")))
        except Exception:
            if silent:
                return default if default is not None else {}
            raise

    def files(self, default=None):
        multipart = self._multipart()
        if multipart is None:
            return default if default is not None else {}
        return dict(multipart["files"])

    def file(self, name, default=None):
        files = self.files(default={})
        value = files.get(name, default)
        if isinstance(value, list):
            return value[0] if value else default
        return value

    def _content_type(self):
        headers = self.headers or {}
        for key, value in headers.items():
            if str(key).lower() == "content-type":
                return str(value or "")
        return ""

    def _multipart(self):
        if self._multipart_cache is not None:
            return self._multipart_cache

        content_type = self._content_type()
        body = self._body or b""
        if not body or "multipart/form-data" not in content_type.lower():
            self._multipart_cache = None
            return None

        try:
            from email.parser import BytesParser
            from email.policy import default
        except Exception:
            self._multipart_cache = None
            return None

        try:
            raw = b"Content-Type: " + content_type.encode("utf-8") + b"\r\n\r\n" + body
            message = BytesParser(policy=default).parsebytes(raw)
            form = {}
            files = {}
            for part in message.iter_parts():
                disposition = part.get_content_disposition()
                if disposition != "form-data":
                    continue
                name = part.get_param("name", header="content-disposition")
                if not name:
                    continue
                filename = part.get_filename()
                payload = part.get_payload(decode=True) or b""
                if filename:
                    item = UploadedFile(
                        name=str(name),
                        filename=str(filename),
                        content_type=str(part.get_content_type() or "application/octet-stream"),
                        content=payload,
                    )
                    if name in files:
                        if isinstance(files[name], list):
                            files[name].append(item)
                        else:
                            files[name] = [files[name], item]
                    else:
                        files[name] = item
                else:
                    charset = part.get_content_charset() or "utf-8"
                    form[str(name)] = payload.decode(charset, "replace")
            self._multipart_cache = {"form": form, "files": files}
            return self._multipart_cache
        except Exception:
            self._multipart_cache = None
            return None

    def __repr__(self):
        return f"<Request {self.method} {self.path}>"
