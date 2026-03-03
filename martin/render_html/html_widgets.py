from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional, Dict

from martin.core.context import BuildContext
from martin.core.widget import Widget, StatelessWidget, normalize_build_result

from .dom import Element, TextNode, Document


# ==========================================================
# Base HTML Widget
# ==========================================================


class HtmlWidget(Widget, ABC):
    """
    Widget renderizable directamente a DOM.
    Solo existe en el target HTML.
    """

    @abstractmethod
    def render(self, context: BuildContext) -> Element | TextNode | Document:
        raise NotImplementedError

    # HtmlWidget no usa build() normalmente
    def build(self, context: BuildContext):
        return None


class Div(HtmlWidget):
    def __init__(
        self,
        *children: Widget,
        attrs: Optional[Dict[str, str]] = None,
        style: Optional[dict] = None,
        key: Optional[str] = None,
    ):
        super().__init__(key=key)
        self._children = list(children)
        self._attrs = attrs or {}
        self._style = style

    def render(self, context: BuildContext) -> Element:
        el = Element("div", attributes=dict(self._attrs))

        if self._style:
            renderer = context.container["renderer"]
            class_name = renderer.style_registry.register(self._style)

            existing = el.attributes.get("class")
            el.attributes["class"] = (
                f"{existing} {class_name}" if existing else class_name
            )

        for child in self._children:
            el.add(_render_widget_to_dom(child, context))

        return el


# ==========================================================
# Primitive Widgets
# ==========================================================


class Text(Div):
    def __init__(
        self,
        text: str,
        style: dict | None = None,
        **kwargs
    ):
        super().__init__(
            TextNode(text),
            style=style,
            **kwargs
        )


# ==========================================================
# Page Widget (Document Root)
# ==========================================================


class Page(HtmlWidget):
    """
    Widget raíz que genera el documento HTML completo.
    """

    def __init__(
        self,
        *children: Widget,
        title: str = "MARTIN",
        key: Optional[str] = None,
    ):
        super().__init__(key=key)
        self.title = title
        self.children = list(children)

    def render(self, context: BuildContext) -> Document:
        html = Element("html")

        # -----------------------
        # HEAD
        # -----------------------
        head = Element("head")

        head.add(Element("meta", {"charset": "utf-8"}))
        head.add(Element("meta", {
            "name": "viewport",
            "content": "width=device-width, initial-scale=1"
        }))

        title_el = Element("title")
        title_el.add(TextNode(self.title))
        head.add(title_el)
        
        # Fuente Montserrat
        link_font = Element("link", {
            "rel": "stylesheet",
            "href": "https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;600;700&display=swap"
        })
        head.add(link_font)

        # Reset global base
        base_style = Element("style")
        base_style.add(TextNode("""
        * {
            box-sizing: border-box;
        }

        html, body {
            margin: 0;
            padding: 0;
            font-family: 'Montserrat', sans-serif;
            overflow-x: hidden;
        }

        body {
            min-height: 100vh;
        }
        """))
        head.add(base_style)

        # -----------------------
        # BODY
        # -----------------------
        body = Element("body")

        for child in self.children:
            body.add(_render_widget_to_dom(child, context))

        html.add(head)
        html.add(body)

        return Document(root=html)


# ==========================================================
# Internal Resolver
# ==========================================================


def _render_widget_to_dom(widget, context):
    from .dom import Element, TextNode

    # 1️⃣ Si ya es DOM, devolver tal cual
    if isinstance(widget, (Element, TextNode)):
        return widget

    # 2️⃣ Si es Widget, renderizar
    if hasattr(widget, "render"):
        return widget.render(context)

    # 3️⃣ Si es string plano, convertir a TextNode
    if isinstance(widget, str):
        return TextNode(widget)

    raise TypeError(f"Unsupported node type: {type(widget)}")
