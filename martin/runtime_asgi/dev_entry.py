from pathlib import Path
import sys

from martin.runtime_asgi.auto_router import build_router_from_pages
from martin.runtime_asgi.app import MartinApp


project_root = Path.cwd()

if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

router = build_router_from_pages(project_root)
app = MartinApp(router)