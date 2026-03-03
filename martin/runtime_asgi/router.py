from __future__ import annotations
import re
from typing import Callable, Dict, Any, Type

from martin.core.widget import Widget


class Route:
    """
    Representa una ruta declarativa.
    """

    def __init__(self, path: str, page: Type[Widget]):
        self.path = path
        self.page = page
        self.pattern = self._compile_path(path)

    def _compile_path(self, path: str):
        # convierte /blog/{slug} -> regex
        pattern = re.sub(r"{(\w+)}", r"(?P<\1>[^/]+)", path)
        return re.compile(f"^{pattern}$")

    def match(self, url: str):
        return self.pattern.match(url)


class Router:
    """
    Router simple SSR.
    """

    def __init__(self):
        self.routes: list[Route] = []

    def add(self, route: Route):
        self.routes.append(route)

    def resolve(self, url: str) -> tuple[Type[Widget], Dict[str, Any]] | None:
        for route in self.routes:
            match = route.match(url)
            if match:
                return route.page, match.groupdict()

        return None
