from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Union


@dataclass
class TextNode:
    text: str


@dataclass
class Element:
    tag: str
    attributes: Dict[str, str] = field(default_factory=dict)
    children: List[Union["Element", TextNode]] = field(default_factory=list)

    def add(self, child: Union["Element", TextNode]) -> None:
        self.children.append(child)


@dataclass
class Document:
    """
    Representa un documento HTML completo.
    """

    root: Element  # debe ser <html>
