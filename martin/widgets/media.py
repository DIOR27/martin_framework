"""
Martin — Media Widgets

Widgets para mostrar contenido visual y multimedia.

    Image   — imagen responsive (<img>)
    Video   — video HTML5 (<video>)
    Icon    — ícono (emoji, SVG inline, carácter especial)
    Avatar  — avatar circular con imagen o iniciales
"""

from ..widget import Widget


# =============================================================================
# Image
# =============================================================================


class Image(Widget):
    """
    Imagen responsive.

        Image("/foto.jpg")
        Image("/foto.jpg", radius=12, width=300, height=200)
        Image("/foto.jpg", url="/galeria", url_target="_self")

    Acepta cualquier prop universal: shadow, radius, width, height, etc.
    """

    def __init__(self, src, alt="", id=None, class_name=None, **kwargs):
        self._props = Widget._extract_props(kwargs)
        self.src = src
        self.alt = alt
        self.id = id
        self.class_name = class_name

    def render(self):
        inline = self._resolve_props()
        attrs = self._attrs(
            src=self.src,
            alt=self.alt,
            style=inline or None,
            id=self.id,
            **{"class": self.class_name},
        )
        return self._wrap_url(f"<img{attrs}>")


# =============================================================================
# Video
# =============================================================================


class Video(Widget):
    """
    Video HTML5.

        Video("/clip.mp4")
        Video("/clip.mp4", autoplay=True, muted=True, loop=True)
        Video("/clip.mp4", controls=False, width=640, radius=12)
    """

    def __init__(
        self, src, controls=True, autoplay=False, loop=False, muted=False, **kwargs
    ):
        self._props = Widget._extract_props(kwargs)
        self.src = src
        self.controls = controls
        self.autoplay = autoplay
        self.loop = loop
        self.muted = muted

    def render(self):
        inline = self._resolve_props()
        attrs = self._attrs(
            controls=self.controls,
            autoplay=self.autoplay,
            loop=self.loop,
            muted=self.muted,
            style=inline or None,
        )
        return f'<video{attrs}><source src="{self.src}"></video>'


# =============================================================================
# Icon
# =============================================================================


class Icon(Widget):
    """
    Ícono: emoji, carácter especial, SVG inline, etc.

        Icon("🚀")
        Icon("🚀", size=32, margin=8)
        Icon("<svg ...>", size=24)
    """

    def __init__(self, icon=None, size=20, child=None, children=None, **kwargs):
        self._props = Widget._extract_props(kwargs)
        self.icon = icon
        self.size = size
        self.child = child
        self.children = children

    def render(self):
        base = (
            f"font-size:{self.size}px; line-height:1; "
            f"display:inline-flex; align-items:center"
        )
        inline = self._resolve_props(base)
        inner = self._resolve_inner(self.icon, self.child, self.children)
        return f'<span style="{inline}" aria-hidden="true">{inner}</span>'


# =============================================================================
# Avatar
# =============================================================================


class Avatar(Widget):
    """
    Avatar circular con imagen o iniciales.

        Avatar("/user.jpg")                                     # con imagen
        Avatar(initials="JD")                                   # con iniciales
        Avatar(initials="AB", background="#6366f1", color="#fff", width=48)

    Por defecto: 40×40 px, completamente circular.
    """

    def __init__(self, src=None, initials=None, **kwargs):
        self._props = Widget._extract_props(kwargs)
        self.src = src
        self.initials = initials
        # Defaults si no se proporcionaron
        if not self._props.get("width"):
            self._props["width"] = 40
        if not self._props.get("height"):
            self._props["height"] = 40
        if self._props.get("radius") is None:
            self._props["radius"] = 999

    def render(self):
        base = (
            "overflow:hidden; display:inline-flex; align-items:center; "
            "justify-content:center; flex-shrink:0"
        )
        inline = self._resolve_props(base)
        w = self._props.get("width", 40)

        if self.src:
            return (
                f'<div style="{inline}">'
                f'<img src="{self.src}" alt="" '
                f'style="width:100%;height:100%;object-fit:cover"></div>'
            )

        fs = (w // 3) if isinstance(w, (int, float)) else 14
        bg = self._props.get("background") or "var(--surface-2)"
        col = self._props.get("color") or "var(--text)"
        return (
            f'<div style="{inline};background:{bg};color:{col};'
            f'font-weight:600;font-size:{fs}px">'
            f'{self.initials or "?"}</div>'
        )
