"""
MARTIN - Style System
Allows defining styles like:
    Border(radius=5, weight=1, style="solid", color="black")
    Padding(all=16)
    CSS("display: flex; gap: 8px")
    or combining: [Border(radius=8), Padding(h=12, v=8), CSS("opacity: 0.9")]
"""


class StyleBase:
    """Base class for all style objects."""

    def to_css(self) -> dict:
        """Returns a dict of CSS property -> value."""
        raise NotImplementedError

    def to_inline(self) -> str:
        """Returns an inline CSS string."""
        return "; ".join(f"{k}: {v}" for k, v in self.to_css().items())


# ─────────────────────────────────────────────
# CSS RAW — escape hatch for any CSS directly
# ─────────────────────────────────────────────


class CSS(StyleBase):
    """
    Use raw CSS directly.
    CSS("display: flex; gap: 8px; opacity: 0.9")
    """

    def __init__(self, raw: str):
        self.raw = raw.strip().rstrip(";")

    def to_css(self) -> dict:
        result = {}
        for part in self.raw.split(";"):
            part = part.strip()
            if ":" in part:
                key, _, val = part.partition(":")
                result[key.strip()] = val.strip()
        return result

    def to_inline(self) -> str:
        return self.raw


# ─────────────────────────────────────────────
# BORDER
# ─────────────────────────────────────────────


class Border(StyleBase):
    """
    Border(radius=5, weight=1, style="solid", color="black")
    Border(radius=16)                   → border-radius only
    Border(weight=2, color="#ff0000")   → red 2px border
    """

    def __init__(
        self,
        radius=None,
        weight=None,
        style="solid",
        color="black",
        top=None,
        right=None,
        bottom=None,
        left=None,
    ):
        self.radius = radius
        self.weight = weight
        self.style = style
        self.color = color
        # Individual sides (overrides weight/style/color if set)
        self.top = top
        self.right = right
        self.bottom = bottom
        self.left = left

    def to_css(self) -> dict:
        css = {}
        if self.radius is not None:
            css["border-radius"] = f"{self.radius}px"

        if self.weight is not None:
            css["border"] = f"{self.weight}px {self.style} {self.color}"

        # Individual sides
        for side, val in [
            ("top", self.top),
            ("right", self.right),
            ("bottom", self.bottom),
            ("left", self.left),
        ]:
            if val is not None:
                w, s, c = (
                    val if isinstance(val, tuple) else (val, self.style, self.color)
                )
                css[f"border-{side}"] = f"{w}px {s} {c}"

        return css


# ─────────────────────────────────────────────
# PADDING / MARGIN
# ─────────────────────────────────────────────


class Padding(StyleBase):
    """
    Padding(all=16)
    Padding(h=12, v=8)          → horizontal / vertical
    Padding(top=4, bottom=4)
    Padding(16, 8)              → (vertical, horizontal) shorthand
    """

    def __init__(
        self,
        *args,
        all=None,
        h=None,
        v=None,
        top=None,
        right=None,
        bottom=None,
        left=None,
    ):
        # Positional shorthand: Padding(16) or Padding(16, 8)
        if len(args) == 1:
            all = args[0]
        elif len(args) == 2:
            v, h = args[0], args[1]

        if all is not None:
            self.top = self.right = self.bottom = self.left = all
        else:
            self.top = top if top is not None else (v if v is not None else 0)
            self.bottom = bottom if bottom is not None else (v if v is not None else 0)
            self.left = left if left is not None else (h if h is not None else 0)
            self.right = right if right is not None else (h if h is not None else 0)

    def to_css(self) -> dict:
        return {"padding": f"{self.top}px {self.right}px {self.bottom}px {self.left}px"}


class Margin(StyleBase):
    """Same API as Padding but applies margin."""

    def __init__(
        self,
        *args,
        all=None,
        h=None,
        v=None,
        top=None,
        right=None,
        bottom=None,
        left=None,
    ):
        if len(args) == 1:
            all = args[0]
        elif len(args) == 2:
            v, h = args[0], args[1]

        if all is not None:
            self.top = self.right = self.bottom = self.left = all
        else:
            self.top = top if top is not None else (v if v is not None else 0)
            self.bottom = bottom if bottom is not None else (v if v is not None else 0)
            self.left = left if left is not None else (h if h is not None else 0)
            self.right = right if right is not None else (h if h is not None else 0)

    def to_css(self) -> dict:
        return {"margin": f"{self.top}px {self.right}px {self.bottom}px {self.left}px"}


# ─────────────────────────────────────────────
# SHADOW
# ─────────────────────────────────────────────


class Shadow(StyleBase):
    """
    Shadow()                        → default subtle shadow
    Shadow(x=0, y=4, blur=12, color="rgba(0,0,0,0.15)")
    Shadow.none()                   → no shadow
    """

    def __init__(
        self, x=0, y=2, blur=8, spread=0, color="rgba(0,0,0,0.15)", inset=False
    ):
        self.x = x
        self.y = y
        self.blur = blur
        self.spread = spread
        self.color = color
        self.inset = inset

    @classmethod
    def none(cls):
        return CSS("box-shadow: none")

    @classmethod
    def sm(cls):
        return cls(y=1, blur=3, color="rgba(0,0,0,0.12)")

    @classmethod
    def md(cls):
        return cls(y=4, blur=12, color="rgba(0,0,0,0.15)")

    @classmethod
    def lg(cls):
        return cls(y=8, blur=24, color="rgba(0,0,0,0.18)")

    @classmethod
    def xl(cls):
        return cls(y=16, blur=48, color="rgba(0,0,0,0.2)")

    def to_css(self) -> dict:
        inset = "inset " if self.inset else ""
        return {
            "box-shadow": f"{inset}{self.x}px {self.y}px {self.blur}px {self.spread}px {self.color}"
        }


# ─────────────────────────────────────────────
# SIZE
# ─────────────────────────────────────────────


class Size(StyleBase):
    """
    Size(width=200, height=100)
    Size(200, 100)
    Size.full()     → width: 100%
    Size.square(64) → 64x64
    """

    def __init__(self, *args, width=None, height=None):
        if len(args) == 1:
            width = height = args[0]
        elif len(args) == 2:
            width, height = args[0], args[1]
        self.width = width
        self.height = height

    @classmethod
    def full(cls):
        return cls(width="100%", height="100%")

    @classmethod
    def square(cls, size):
        return cls(size, size)

    def to_css(self) -> dict:
        css = {}
        if self.width is not None:
            css["width"] = (
                f"{self.width}px"
                if isinstance(self.width, (int, float))
                else self.width
            )
        if self.height is not None:
            css["height"] = (
                f"{self.height}px"
                if isinstance(self.height, (int, float))
                else self.height
            )
        return css


# ─────────────────────────────────────────────
# BACKGROUND
# ─────────────────────────────────────────────


class Background(StyleBase):
    """
    Background("red")
    Background("#ff5733")
    Background.gradient("135deg", "#667eea", "#764ba2")
    Background.image("url.jpg", size="cover")
    """

    def __init__(self, color: str):
        self.color = color

    @classmethod
    def gradient(cls, direction="135deg", *colors):
        if not colors:
            colors = ("#667eea", "#764ba2")
        stops = ", ".join(colors)
        obj = cls.__new__(cls)
        obj.color = None
        obj._gradient = f"linear-gradient({direction}, {stops})"
        return obj

    @classmethod
    def image(cls, url: str, size="cover", position="center", repeat="no-repeat"):
        obj = cls.__new__(cls)
        obj.color = None
        obj._image = url
        obj._size = size
        obj._position = position
        obj._repeat = repeat
        return obj

    def to_css(self) -> dict:
        if hasattr(self, "_gradient"):
            return {"background": self._gradient}
        if hasattr(self, "_image"):
            return {
                "background-image": f"url('{self._image}')",
                "background-size": self._size,
                "background-position": self._position,
                "background-repeat": self._repeat,
            }
        return {"background-color": self.color}


# ─────────────────────────────────────────────
# TEXT STYLE
# ─────────────────────────────────────────────


class TextStyle(StyleBase):
    """
    TextStyle(size=18, color="#333", weight="bold", family="Georgia")
    TextStyle(size=14, italic=True, line_height=1.6)
    """

    def __init__(
        self,
        size=None,
        color=None,
        weight=None,
        family=None,
        italic=False,
        line_height=None,
        letter_spacing=None,
        align=None,
        decoration=None,
        transform=None,
    ):
        self.size = size
        self.color = color
        self.weight = weight
        self.family = family
        self.italic = italic
        self.line_height = line_height
        self.letter_spacing = letter_spacing
        self.align = align
        self.decoration = decoration
        self.transform = transform

    def to_css(self) -> dict:
        css = {}
        if self.size is not None:
            css["font-size"] = f"{self.size}px"
        if self.color is not None:
            css["color"] = self.color
        if self.weight is not None:
            css["font-weight"] = str(self.weight)
        if self.family is not None:
            css["font-family"] = self.family
        if self.italic:
            css["font-style"] = "italic"
        if self.line_height is not None:
            css["line-height"] = str(self.line_height)
        if self.letter_spacing is not None:
            css["letter-spacing"] = f"{self.letter_spacing}px"
        if self.align is not None:
            css["text-align"] = self.align
        if self.decoration is not None:
            css["text-decoration"] = self.decoration
        if self.transform is not None:
            css["text-transform"] = self.transform
        return css


# ─────────────────────────────────────────────
# OPACITY / OVERFLOW / CURSOR
# ─────────────────────────────────────────────


class Opacity(StyleBase):
    """Opacity(0.5)"""

    def __init__(self, value: float):
        self.value = value

    def to_css(self):
        return {"opacity": str(self.value)}


class Overflow(StyleBase):
    """Overflow("hidden"), Overflow("auto")"""

    def __init__(self, value="hidden", x=None, y=None):
        self.value = value
        self.x = x
        self.y = y

    def to_css(self):
        if self.x or self.y:
            css = {}
            if self.x:
                css["overflow-x"] = self.x
            if self.y:
                css["overflow-y"] = self.y
            return css
        return {"overflow": self.value}


class Cursor(StyleBase):
    """Cursor("pointer"), Cursor("not-allowed")"""

    def __init__(self, value="pointer"):
        self.value = value

    def to_css(self):
        return {"cursor": self.value}


# ─────────────────────────────────────────────
# STYLE RESOLVER — merges everything
# ─────────────────────────────────────────────


def resolve_styles(*style_args) -> str:
    """
    Takes any mix of StyleBase instances, lists of them, or None,
    and returns a single inline CSS string.

    Usage:
        resolve_styles(Border(radius=8), Padding(16), CSS("opacity:0.9"))
        resolve_styles([Border(radius=4), Shadow.md()])
    """
    merged = {}

    def process(item):
        if item is None:
            return
        if isinstance(item, StyleBase):
            merged.update(item.to_css())
        elif isinstance(item, (list, tuple)):
            for sub in item:
                process(sub)
        elif isinstance(item, dict):
            merged.update(item)
        elif isinstance(item, str):
            # Treat raw string as CSS
            process(CSS(item))

    for arg in style_args:
        process(arg)

    return "; ".join(f"{k}: {v}" for k, v in merged.items())


# ─────────────────────────────────────────────
# COLOR CONSTANTS
# ─────────────────────────────────────────────


class Colors:
    transparent = "transparent"
    black = "#000000"
    white = "#ffffff"
    # Grays
    gray_50 = "#f9fafb"
    gray_100 = "#f3f4f6"
    gray_200 = "#e5e7eb"
    gray_300 = "#d1d5db"
    gray_400 = "#9ca3af"
    gray_500 = "#6b7280"
    gray_600 = "#4b5563"
    gray_700 = "#374151"
    gray_800 = "#1f2937"
    gray_900 = "#111827"
    # Primaries
    red = "#ef4444"
    orange = "#f97316"
    yellow = "#eab308"
    green = "#22c55e"
    blue = "#3b82f6"
    indigo = "#6366f1"
    purple = "#a855f7"
    pink = "#ec4899"

    @staticmethod
    def rgb(r, g, b):
        return f"rgb({r}, {g}, {b})"

    @staticmethod
    def rgba(r, g, b, a):
        return f"rgba({r}, {g}, {b}, {a})"

    @staticmethod
    def hex(value: str):
        return value if value.startswith("#") else f"#{value}"
