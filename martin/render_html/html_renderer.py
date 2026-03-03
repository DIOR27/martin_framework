from __future__ import annotations

from martin.core.context import BuildContext
from martin.core.widget import Widget

from .dom import Element, TextNode, Document
from .html_widgets import _render_widget_to_dom
from .css_engine.style_registry import StyleRegistry
from .css_engine.css_generator import CSSGenerator
from .render_result import RenderResult


class HtmlRenderer:

    def __init__(self, pretty: bool = False, inline_css: bool = False):
        self.pretty = pretty
        self.inline_css = inline_css

    # =====================================================

    def render_document(
        self, root: Widget, context: BuildContext | None = None
    ) -> RenderResult:

        self.style_registry = StyleRegistry()

        ctx = context or BuildContext()
        ctx.container["renderer"] = self

        dom = _render_widget_to_dom(root, ctx)

        self._inject_global_assets(dom.root)

        if not isinstance(dom, Document):
            raise TypeError("Root widget must render a Document")

        css = None
        styles = self.style_registry.get_all()

        if styles:
            css = CSSGenerator().generate(styles)

            if self.inline_css:
                self._inject_inline_style(dom.root, css)
            else:
                # Insertar placeholder link (real path lo define el Builder)
                self._inject_link(dom.root, "__MARTIN_CSS__")

        if self.pretty:
            html = self._to_html_pretty(dom.root, indent=0)
        else:
            html = self._to_html(dom.root)

        return RenderResult(html=html, css=css)

    # =====================================================
    # CSS Injection
    # =====================================================

    def _inject_inline_style(self, html_root: Element, css: str) -> None:
        for child in html_root.children:
            if child.tag == "head":
                style_el = Element("style")
                style_el.add(TextNode(css))
                child.add(style_el)
                return

    def _inject_link(self, html_root: Element, placeholder: str) -> None:
        for child in html_root.children:
            if child.tag == "head":
                link_el = Element("link", {"rel": "stylesheet", "href": placeholder})
                child.add(link_el)
                return

    # =====================================================
    # HTML Serialization
    # =====================================================

    def _to_html(self, node: Element | TextNode) -> str:
        if isinstance(node, TextNode):
            return self._escape(node.text)

        attrs = self._render_attrs(node.attributes)

        if not node.children:
            return f"<{node.tag}{attrs}></{node.tag}>"

        children_html = "".join(self._to_html(c) for c in node.children)
        return f"<{node.tag}{attrs}>{children_html}</{node.tag}>"

    def _to_html_pretty(self, node: Element | TextNode, indent: int) -> str:
        space = "  " * indent

        if isinstance(node, TextNode):
            return space + self._escape(node.text)

        attrs = self._render_attrs(node.attributes)

        if not node.children:
            return f"{space}<{node.tag}{attrs}></{node.tag}>"

        opening = f"{space}<{node.tag}{attrs}>"
        children_html = "\n".join(
            self._to_html_pretty(c, indent + 1) for c in node.children
        )
        closing = f"{space}</{node.tag}>"

        return f"{opening}\n{children_html}\n{closing}"

    def _render_attrs(self, attrs: dict[str, str]) -> str:
        if not attrs:
            return ""
        return " " + " ".join(f'{k}="{self._escape(v)}"' for k, v in attrs.items())

    def _escape(self, s: str) -> str:
        return (
            s.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&#39;")
        )

    def _inject_global_assets(self, html_root):
        from .dom import Element, TextNode

        for child in html_root.children:
            if child.tag == "head":

                # Google Font
                font_link = Element(
                    "link",
                    {
                        "rel": "stylesheet",
                        "href": "https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;600;700&display=swap",
                    },
                )
                child.add(font_link)

                # Base Reset
                base_style = Element("style")
                base_style.add(
                    TextNode(
                        """
                    * { box-sizing: border-box; }

                    html, body {
                        margin: 0;
                        padding: 0;
                        font-family: 'Montserrat', sans-serif !important;
                        overflow-x: hidden;
                    }

                    body {
                        min-height: 100vh;
                    }
                    """
                    )
                )
                child.add(base_style)

                return
