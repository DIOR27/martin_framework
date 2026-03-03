from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Iterable, Optional, Union, List

from .context import BuildContext


BuildResult = Union["Widget", Iterable["Widget"], None]


class Widget(ABC):
    """
    Unidad declarativa de UI. Inmutable por convención.
    """

    __slots__ = ("key",)

    def __init__(self, key: Optional[str] = None):
        self.key = key

    @abstractmethod
    def build(self, context: BuildContext) -> BuildResult:
        raise NotImplementedError


class StatelessWidget(Widget):
    """
    Widget sin estado.
    """

    pass


def normalize_build_result(result: BuildResult) -> List[Widget]:
    """
    Normaliza el resultado de build a una lista plana de Widgets.
    """
    if result is None:
        return []
    if isinstance(result, Widget):
        return [result]
    # iterable de widgets
    return [w for w in result if w is not None]
