"""Helpers de rutas para navegación y estado activo."""

from urllib.parse import urlparse


def normalize_path(value):
    """
    Normaliza una ruta para comparaciones de navegación.

    Devuelve `None` para enlaces externos o no enrutable (hash puro, mailto, etc).
    """
    if value is None:
        return None

    raw = str(value).strip()
    if not raw:
        return None

    lowered = raw.lower()
    if lowered.startswith(("mailto:", "tel:", "javascript:")):
        return None
    if raw.startswith("#"):
        return None

    parsed = urlparse(raw)
    if parsed.scheme or parsed.netloc:
        return None

    path = parsed.path or "/"
    if not path.startswith("/"):
        path = "/" + path

    if path.endswith(".html"):
        path = path[: -len(".html")] or "/"
        if path == "/index":
            path = "/"

    if path != "/":
        path = path.rstrip("/") or "/"

    return path


def paths_match(current_path, candidate_path):
    """Compara rutas normalizadas para marcar enlaces activos."""
    current = normalize_path(current_path)
    candidate = normalize_path(candidate_path)
    if not current or not candidate:
        return False
    return current == candidate
