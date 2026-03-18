"""
Martin — Media Widgets

Widgets para mostrar contenido visual y multimedia.

    Image   — imagen responsive (<img>)
    Video   — video HTML5 (<video>)
    Icon    — ícono (emoji, SVG inline, Font Awesome, Bootstrap Icons, etc.)
    IconPack — carga hojas de estilo de librerías de iconos vía CDN
    Avatar  — avatar circular con imagen o iniciales
"""

import html as _html

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
    Ícono: emoji, carácter especial, SVG inline o librerías por clases.

        Icon("🚀")
        Icon("🚀", size=32, margin=8)
        Icon("<svg ...>", size=24)
        Icon(name="house", provider="fa", variant="solid")     # Font Awesome
        Icon(name="alarm", provider="material-symbols")         # Google Symbols
        Icon(icon_class="bi bi-airplane")                       # clases directas
        Icon(name="home-line", provider="ri")                   # genérico: ri ri-home-line
    """

    _PROVIDER_ALIASES = {
        "fa": "fontawesome",
        "font-awesome": "fontawesome",
        "fontawesome": "fontawesome",
        "bootstrap": "bootstrap-icons",
        "bootstrap-icons": "bootstrap-icons",
        "bi": "bootstrap-icons",
        "material-symbols": "material-symbols",
        "material_symbols": "material-symbols",
        "material-icons": "material-icons",
        "material_icons": "material-icons",
        "mdi": "mdi",
    }

    def __init__(
        self,
        icon=None,
        size=20,
        child=None,
        children=None,
        name=None,
        provider=None,
        variant=None,
        icon_class=None,
        class_name=None,
        base_class=None,
        name_prefix=None,
        name_suffix=None,
        **kwargs,
    ):
        self._props = Widget._extract_props(kwargs)
        self.icon = icon
        self.size = size
        self.child = child
        self.children = children
        self.name = name
        self.provider = self._normalize_provider(provider)
        self.variant = variant
        self.icon_class = icon_class
        self.class_name = class_name
        self.base_class = base_class
        self.name_prefix = name_prefix
        self.name_suffix = name_suffix

    @classmethod
    def _normalize_provider(cls, provider):
        if not provider:
            return None
        key = str(provider).strip().lower()
        return cls._PROVIDER_ALIASES.get(key, key)

    def _compose_generic_classes(self, base_class, name):
        token = str(name).strip()
        prefix = str(self.name_prefix or "").strip()
        suffix = str(self.name_suffix or "").strip()
        base = str(base_class or "").strip()
        extra = f" {self.class_name.strip()}" if self.class_name else ""

        if prefix:
            token = prefix + token
        elif base and " " not in token and not token.startswith(base + "-"):
            token = f"{base}-{token}"

        if suffix:
            token = token + suffix

        classes = " ".join(part for part in [base, token] if part).strip()
        if extra:
            classes = f"{classes}{extra}".strip()
        return "i", classes, ""

    def _font_class_icon(self):
        if self.icon_class:
            base = str(self.icon_class).strip()
            if self.class_name:
                base = f"{base} {self.class_name}".strip()
            return "i", base, ""

        if self.name and not self.provider and not (self.base_class or self.name_prefix or self.name_suffix):
            base = str(self.name).strip()
            if self.class_name:
                base = f"{base} {self.class_name}".strip()
            return "i", base, ""

        if not self.name:
            return None

        name = str(self.name).strip()
        extra = f" {self.class_name.strip()}" if self.class_name else ""

        if self.base_class or self.name_prefix or self.name_suffix:
            return self._compose_generic_classes(self.base_class, name)

        if self.provider == "fontawesome":
            v = (self.variant or "solid").strip().lower()
            fa_variant = {
                "solid": "fa-solid",
                "regular": "fa-regular",
                "brands": "fa-brands",
                "light": "fa-light",
                "thin": "fa-thin",
                "duotone": "fa-duotone",
            }.get(v, "fa-solid")
            token = name if name.startswith("fa-") else f"fa-{name}"
            return "i", f"{fa_variant} {token}{extra}", ""

        if self.provider == "bootstrap-icons":
            token = name if name.startswith("bi-") else f"bi-{name}"
            return "i", f"bi {token}{extra}", ""

        if self.provider == "mdi":
            token = name if name.startswith("mdi-") else f"mdi-{name}"
            return "i", f"mdi {token}{extra}", ""

        if self.provider == "material-icons":
            cls = f"material-icons{extra}"
            return "span", cls.strip(), name

        if self.provider == "material-symbols":
            v = (self.variant or "outlined").strip().lower()
            if v not in {"outlined", "rounded", "sharp"}:
                v = "outlined"
            cls = f"material-symbols-{v}{extra}"
            return "span", cls.strip(), name

        if self.provider:
            return self._compose_generic_classes(self.base_class or self.provider, name)

        return None

    def render(self):
        base = (
            f"font-size:{self.size}px; line-height:1; "
            f"display:inline-flex; align-items:center"
        )
        inline = self._resolve_props(base)
        has_aria_label = bool(self._get_universal_attrs().get("aria-label"))
        outer_attrs = self._attrs(
            style=inline,
            aria_hidden=(None if has_aria_label else "true"),
        )

        font_icon = self._font_class_icon()
        if font_icon:
            tag, classes, text = font_icon
            icon_attrs = self._attrs(
                **{
                    "class": classes,
                    "style": "font-size:inherit;line-height:1;display:inline-block",
                }
            )
            if text:
                txt = _html.escape(str(text))
                inner = f"<{tag}{icon_attrs}>{txt}</{tag}>"
            else:
                inner = f"<{tag}{icon_attrs}></{tag}>"
        else:
            inner = self._resolve_inner(self.icon, self.child, self.children)
        return f"<span{outer_attrs}>{inner}</span>"


# =============================================================================
# IconPack
# =============================================================================


class IconPack(Widget):
    """
    Carga librerías de iconos desde CDN para usar con `Icon(provider=...)`.

        IconPack("fontawesome")
        IconPack(["fontawesome", "bootstrap-icons", "mdi"])
        IconPack(["material-symbols", "material-icons"])
        IconPack("https://cdn.jsdelivr.net/npm/remixicon@4.2.0/fonts/remixicon.css")
        IconPack([{"name": "boxicons", "href": "https://unpkg.com/boxicons@2.1.4/css/boxicons.min.css"}])
    """

    _ALIASES = Icon._PROVIDER_ALIASES
    _CDN_MAP = {
        "fontawesome": "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/{version}/css/all.min.css",
        "bootstrap-icons": "https://cdn.jsdelivr.net/npm/bootstrap-icons@{version}/font/bootstrap-icons.min.css",
        "mdi": "https://cdn.jsdelivr.net/npm/@mdi/font@{version}/css/materialdesignicons.min.css",
        "material-icons": "https://fonts.googleapis.com/icon?family=Material+Icons",
    }
    _DEFAULT_VERSION = {
        "fontawesome": "6.5.2",
        "bootstrap-icons": "1.11.3",
        "mdi": "7.4.47",
    }

    def __init__(self, providers="fontawesome", versions=None, **kwargs):
        self._props = Widget._extract_props(kwargs)
        self.providers = providers
        self.versions = versions or {}

    def _source_list(self):
        raw = self.providers
        if isinstance(raw, str):
            raw = [raw]
        out = []
        seen = set()
        for item in raw or []:
            href = None
            if isinstance(item, dict):
                href = item.get("href") or item.get("url")
                if not href:
                    key = str(item.get("name") or item.get("provider") or "").strip().lower()
                    name = self._ALIASES.get(key, key)
                    href = self._href_for(name)
            else:
                raw_item = str(item).strip()
                if not raw_item:
                    continue
                lowered = raw_item.lower()
                if "://" in lowered or lowered.endswith(".css") or raw_item.startswith("/"):
                    href = raw_item
                else:
                    name = self._ALIASES.get(lowered, lowered)
                    href = self._href_for(name)
            hrefs = href if isinstance(href, (list, tuple)) else [href]
            for resolved in hrefs:
                if resolved and resolved not in seen:
                    seen.add(resolved)
                    out.append(resolved)
        return out

    def _href_for(self, provider):
        if provider == "material-symbols":
            return [
                "https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@24,400,0,0",
                "https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@24,400,0,0",
                "https://fonts.googleapis.com/css2?family=Material+Symbols+Sharp:opsz,wght,FILL,GRAD@24,400,0,0",
            ]
        tpl = self._CDN_MAP.get(provider)
        if not tpl:
            return None
        if "{version}" in tpl:
            version = self.versions.get(provider) or self._DEFAULT_VERSION.get(provider)
            return tpl.format(version=version)
        return tpl

    def render(self):
        links = []
        for href in self._source_list():
            links.append(
                f'<link rel="stylesheet" href="{_html.escape(str(href), quote=True)}" />'
            )
        return "".join(links)


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
