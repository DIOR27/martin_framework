from pathlib import Path
import importlib
import sys

from martin.runtime_asgi.router import Router, Route


def build_router_from_pages(project_root: Path) -> Router:
    router = Router()

    pages_dir = project_root / "pages"
    if not pages_dir.exists():
        return router

    # Asegurar que el proyecto esté en sys.path
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    for file in pages_dir.rglob("*.py"):
        route_path = file.relative_to(pages_dir).with_suffix("")
        url = _file_to_url(route_path)

        module_path = f"pages.{'.'.join(route_path.parts)}"
        module = importlib.import_module(module_path)

        if hasattr(module, "Page"):
            page_cls = module.Page
        elif hasattr(module, "page"):
            page_cls = module.page
        else:
            continue

        router.add(Route(url, page_cls))

    return router


def _file_to_url(path):
    parts = []

    for part in path.parts:
        if part == "index":
            continue
        if part.startswith("[") and part.endswith("]"):
            parts.append("{" + part[1:-1] + "}")
        else:
            parts.append(part)

    return "/" + "/".join(parts)
