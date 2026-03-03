from dataclasses import dataclass
from typing import Optional


@dataclass
class RenderResult:
    html: str
    css: Optional[str] = None
