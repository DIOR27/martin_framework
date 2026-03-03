from __future__ import annotations
from typing import Optional

from martin.core.widget import Widget
from .html_widgets import Div, Text
from .layout import Column


# ==========================================================
# Container (centrado y ancho máximo)
# ==========================================================


class Container(Div):
    def __init__(
        self,
        *children: Widget,
        max_width: int = 1200,
        padding: int = 24,
        style: Optional[dict] = None,
        **kwargs,
    ):
        base_style = {
            "max_width": max_width,
            "margin": "0 auto",
            "padding": padding,
            "width": "100%",
        }

        if style:
            base_style.update(style)

        super().__init__(*children, style=base_style, **kwargs)


# ==========================================================
# Section (bloque vertical con espaciado)
# ==========================================================


class Section(Div):
    def __init__(
        self,
        *children: Widget,
        padding_y: int = 64,
        background: Optional[str] = None,
        style: Optional[dict] = None,
        **kwargs,
    ):
        base_style = {
            "padding_top": padding_y,
            "padding_bottom": padding_y,
        }

        if background:
            base_style["background"] = background

        if style:
            base_style.update(style)

        super().__init__(*children, style=base_style, **kwargs)


# ==========================================================
# Card
# ==========================================================


class Card(Div):
    def __init__(
        self,
        *children: Widget,
        padding: int = 24,
        radius: int = 12,
        shadow: bool = True,
        style: Optional[dict] = None,
        **kwargs,
    ):
        base_style = {
            "padding": padding,
            "border_radius": radius,
            "background": "white",
        }

        if shadow:
            base_style["box_shadow"] = "0 4px 12px rgba(0,0,0,0.1)"

        if style:
            base_style.update(style)

        super().__init__(*children, style=base_style, **kwargs)


# ==========================================================
# Button
# ==========================================================


class Button(Div):
    def __init__(self, label: str, style: Optional[dict] = None, **kwargs):
        base_style = {
            "display": "inline-block",
            "padding": "12px 24px",
            "background": "#111",
            "color": "white",
            "border_radius": 8,
            "cursor": "pointer",
            "text_align": "center",
            "hover": {"background": "#333"},
        }

        if style:
            base_style.update(style)

        super().__init__(Text(label), style=base_style, **kwargs)
