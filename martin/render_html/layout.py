from __future__ import annotations
from typing import Optional

from martin.core.context import BuildContext
from martin.core.widget import Widget

from .html_widgets import Div


# ==========================================================
# Base Flex Container
# ==========================================================


class Flex(Div):
    def __init__(
        self,
        *children: Widget,
        direction: str = "row",
        gap: Optional[int] = None,
        align: Optional[str] = None,
        justify: Optional[str] = None,
        wrap: bool = False,
        style: Optional[dict] = None,
        **kwargs,
    ):
        flex_style = {
            "display": "flex",
            "flex_direction": direction,
        }

        if gap is not None:
            flex_style["gap"] = gap

        if align:
            flex_style["align_items"] = align

        if justify:
            flex_style["justify_content"] = justify

        if wrap:
            flex_style["flex_wrap"] = "wrap"

        if style:
            flex_style.update(style)

        super().__init__(*children, style=flex_style, **kwargs)


# ==========================================================
# Row
# ==========================================================


class Row(Flex):
    def __init__(
        self,
        *children: Widget,
        gap: Optional[int] = None,
        align: Optional[str] = None,
        justify: Optional[str] = None,
        wrap: bool = False,
        style: Optional[dict] = None,
        **kwargs,
    ):
        super().__init__(
            *children,
            direction="row",
            gap=gap,
            align=align,
            justify=justify,
            wrap=wrap,
            style=style,
            **kwargs,
        )


# ==========================================================
# Column
# ==========================================================


class Column(Flex):
    def __init__(
        self,
        *children: Widget,
        gap: Optional[int] = None,
        align: Optional[str] = None,
        justify: Optional[str] = None,
        style: Optional[dict] = None,
        **kwargs,
    ):
        super().__init__(
            *children,
            direction="column",
            gap=gap,
            align=align,
            justify=justify,
            style=style,
            **kwargs,
        )


# ==========================================================
# Grid
# ==========================================================


class Grid(Div):
    def __init__(
        self,
        *children: Widget,
        columns: int = 2,
        gap: Optional[int] = None,
        style: Optional[dict] = None,
        **kwargs,
    ):
        grid_style = {
            "display": "grid",
            "grid_template_columns": f"repeat({columns}, 1fr)",
        }

        if gap:
            grid_style["gap"] = gap

        if style:
            grid_style.update(style)

        super().__init__(*children, style=grid_style, **kwargs)
