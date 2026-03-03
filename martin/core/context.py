from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Optional, Dict


@dataclass
class BuildContext:
    """
    Contexto de construcción agnóstico al runtime.
    """

    theme: Optional[Any] = None
    request: Optional[Any] = None
    route: Optional[str] = None

    # 🔥 Contenedor interno para dependencias del renderer
    container: Dict[str, Any] = field(default_factory=dict)
