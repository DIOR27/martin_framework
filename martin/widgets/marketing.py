"""
Martin — Marketing/Content Widgets

Auto-extracted from former compound module.
"""

from ..widget import Widget

__all__ = [
    "Hero",
    "GalleryItem",
    "Gallery",
    "CarouselItem",
    "Carousel",
    "AccordionItem",
    "Accordion",
    "TestimonialItem",
    "Testimonials",
    "SlideItem",
    "SlideCarousel",
    "PricingPlan",
    "Pricing",
    "FAQItem",
    "FAQ",
]


class Hero(Widget):
    """
    Hero banner de página completa con imagen/video de fondo, contenido
    centrado y soporte para overlay, badge, título, subtítulo, acciones
    y un widget de imagen/media lateral o de fondo.

    Uso básico:
        Hero(
            title="Construye rápido.",
            subtitle="Un framework Python con UI declarativa.",
        )

    Uso completo:
        Hero(
            badge=Badge("v2.0", background=Colors.indigo, color="white"),
            title=Heading("Construye rápido.", level=1,
                          style=[GradientText.aurora(), TextStyle(size=64, weight="800")]),
            subtitle=Paragraph("Un framework Python con UI declarativa estilo Flutter.",
                               style=TextStyle(size=20, color="var(--text-muted)")),
            actions=[
                Button("Empezar", href="/docs", background=Colors.indigo, color="white", radius=12),
                Button("GitHub",  href="https://github.com", radius=12),
            ],
            image=Image("/assets/screenshot.png", radius=16,
                        style="box-shadow:0 32px 80px rgba(0,0,0,0.4)"),
            background=MeshBackground.themed(),
            align="left",          # "center" | "left"
            layout="split",        # "split" | "centered"
            min_height=600,
            overlay=False,
        )

    Fondo con imagen URL:
        Hero(
            title="Bienvenido",
            bg_image="/assets/hero.jpg",
            overlay=True,
            overlay_color="rgba(0,0,0,0.55)",
        )

    Parámetros:
        title           str | Widget     título principal (str genera un <h1> por defecto)
        subtitle        str | Widget     subtítulo o descripción
        badge           str | Widget     etiqueta pequeña encima del título
        actions         list[Widget]     botones / links de acción
        image           str | Widget     imagen o widget media lateral / decorativa
        bg_image        str              URL de imagen de fondo CSS
        bg_video        str              URL de video de fondo (muted, loop, autoplay)
        background      str | StyleBase  fondo del hero (color, MeshBackground, CSS…)
        overlay         bool             capa semitransparente sobre bg_image/bg_video
        overlay_color   str              color del overlay (default: rgba(0,0,0,0.45))
        align           str              "center" | "left" | "right"
        layout          str              "centered" (solo contenido) |
                                         "split"    (contenido + imagen lado a lado)
        min_height      int              alto mínimo en px (default: 520)
        padding         int              padding interno (sobrescribible via kwargs)
    """

    def __init__(
        self,
        title=None,
        subtitle=None,
        badge=None,
        actions=None,
        actions_align=None,       # "center"|"left"|"right" — por defecto sigue a `align`
        actions_direction="row",  # "row" | "column"
        image=None,
        bg_image=None,
        bg_video=None,
        background=None,
        overlay=False,
        overlay_color="rgba(0,0,0,0.45)",
        align="center",
        layout=None,          # None = auto: "split" si hay image, "centered" si no
        min_height=520,
        **kwargs,
    ):
        self._props            = Widget._extract_props(kwargs)
        self.title             = title
        self.subtitle          = subtitle
        self.badge             = badge
        self.actions           = actions or []
        self.actions_align     = actions_align    # None = hereda de align
        self.actions_direction = actions_direction
        self.image             = image
        self.bg_image          = bg_image
        self.bg_video          = bg_video
        self.background        = background
        self.overlay           = overlay
        self.overlay_color     = overlay_color
        self.align             = align  # "center" | "left" | "right"
        self.layout            = layout or ("split" if image else "centered")
        self.min_height        = min_height

    # ── helpers ──────────────────────────────────────────────────────────────

    def _render_node(self, node, default_tag=None, default_style=""):
        """Renderiza un string como widget simple o llama .render() si es Widget."""
        if node is None:
            return ""
        if isinstance(node, Widget):
            return node.render()
        # string → envolver en tag por defecto si se indica
        if default_tag:
            return f'<{default_tag} style="{default_style}">{node}</{default_tag}>'
        return str(node)

    def _background_css(self):
        """Devuelve el CSS de fondo del wrapper externo."""
        from ..styles import resolve_styles, StyleBase
        parts = []

        if self.bg_image:
            parts.append(
                f"background-image:url('{self.bg_image}');"
                f"background-size:cover;background-position:center;"
                f"background-repeat:no-repeat;"
            )
        elif self.background is not None:
            if isinstance(self.background, StyleBase):
                parts.append(resolve_styles(self.background))
            else:
                parts.append(str(self.background))
        else:
            parts.append("background:var(--bg-secondary);")

        return " ".join(parts)

    # ── render ────────────────────────────────────────────────────────────────

    def render(self):
        from ..styles import resolve_styles

        min_h   = self.min_height
        align   = self.align       # center | left | right
        layout  = self.layout      # centered | split
        text_align = align if align != "right" else "right"

        # ── Fondo ─────────────────────────────────────────────────────────
        bg_css = self._background_css()

        # Props universales (padding, margin, width, etc.) sobre el wrapper
        extra_css = self._resolve_props(
            f"position:relative;min-height:{min_h}px;"
            f"display:flex;flex-direction:column;"
            f"justify-content:center;overflow:hidden;"
        )

        wrapper_open = f'<div style="{extra_css} {bg_css}">'
        wrapper_close = '</div>'

        # ── Video de fondo ────────────────────────────────────────────────
        video_html = ""
        if self.bg_video:
            video_html = (
                '<video autoplay muted loop playsinline '
                'style="position:absolute;top:0;left:0;width:100%;height:100%;'
                'object-fit:cover;z-index:0;">'
                f'<source src="{self.bg_video}">'
                '</video>'
            )

        # ── Overlay ───────────────────────────────────────────────────────
        overlay_html = ""
        if self.overlay and (self.bg_image or self.bg_video):
            overlay_html = (
                f'<div style="position:absolute;top:0;left:0;width:100%;height:100%;'
                f'background:{self.overlay_color};z-index:1;"></div>'
            )

        # ── Contenido ─────────────────────────────────────────────────────
        # Badge
        badge_html = ""
        if self.badge is not None:
            badge_html = (
                '<div style="margin-bottom:16px;">'
                + self._render_node(self.badge,
                    default_tag="span",
                    default_style=(
                        "display:inline-block;font-size:12px;font-weight:700;"
                        "letter-spacing:1px;text-transform:uppercase;"
                        "color:var(--accent);background:rgba(99,102,241,0.12);"
                        "padding:4px 12px;border-radius:999px;"
                    ))
                + '</div>'
            )

        # Título
        title_html = ""
        if self.title is not None:
            title_html = (
                '<div style="margin-bottom:12px;">'
                + self._render_node(self.title,
                    default_tag="h1",
                    default_style=(
                        "font-size:clamp(36px,6vw,72px);font-weight:800;"
                        "line-height:1.1;letter-spacing:-1px;"
                        "color:var(--text);margin:0;"
                    ))
                + '</div>'
            )

        # Subtítulo
        subtitle_html = ""
        if self.subtitle is not None:
            subtitle_html = (
                '<div style="margin-bottom:32px;">'
                + self._render_node(self.subtitle,
                    default_tag="p",
                    default_style=(
                        "font-size:clamp(16px,2vw,20px);line-height:1.6;"
                        "color:var(--text-muted);margin:0;"
                    ))
                + '</div>'
            )

        # Acciones
        actions_html = ""
        if self.actions:
            eff_align = self.actions_align or align
            justify_map = {"center": "center", "left": "flex-start", "right": "flex-end"}
            justify = justify_map.get(eff_align, "center")
            rendered = "".join(
                a.render() if isinstance(a, Widget) else str(a)
                for a in self.actions
            )
            if self.actions_direction == "column":
                align_items = justify_map.get(eff_align, "center")
                actions_html = (
                    f'<div style="display:flex;flex-direction:column;gap:12px;align-items:{align_items};">'
                    + rendered
                    + '</div>'
                )
            else:
                actions_html = (
                    f'<div style="display:flex;flex-wrap:wrap;gap:12px;justify-content:{justify};">'
                    + rendered
                    + '</div>'
                )

        # Columna de texto
        text_col = (
            f'<div style="display:flex;flex-direction:column;'
            f'align-items:{"center" if align=="center" else ("flex-end" if align=="right" else "flex-start")};'
            f'text-align:{text_align};">'
            + badge_html + title_html + subtitle_html + actions_html
            + '</div>'
        )

        # ── Imagen / media ────────────────────────────────────────────────
        image_html = ""
        if self.image is not None:
            rendered_img = self._render_node(
                self.image,
                default_tag="img",
                default_style="max-width:100%;height:auto;display:block;",
            )
            image_html = (
                '<div style="display:flex;align-items:center;justify-content:center;flex-shrink:0;">'
                + rendered_img
                + '</div>'
            )

        # ── Ensamblado según layout ───────────────────────────────────────
        if layout == "split" and image_html:
            # Split: texto izquierda, imagen derecha (o invertido con align=right)
            if align == "right":
                cols = image_html + text_col
            else:
                cols = text_col + image_html

            inner_html = (
                '<div style="'
                'display:grid;'
                'grid-template-columns:1fr 1fr;'
                'gap:48px;'
                'align-items:center;'
                'width:100%;max-width:1100px;'
                'margin:0 auto;'
                'padding:64px 32px;'
                '">'
                + cols
                + '</div>'
                # Responsive: en móvil apila verticalmente
                + '<style>'
                '@media(max-width:768px){'
                '.mn-hero-split{grid-template-columns:1fr!important;}'
                '}'
                '</style>'
            )
            # Re-do with class for responsive
            inner_html = (
                '<div class="mn-hero-split" style="'
                'display:grid;'
                'grid-template-columns:1fr 1fr;'
                'gap:48px;'
                'align-items:center;'
                'width:100%;max-width:1100px;'
                'margin:0 auto;'
                'padding:64px 32px;'
                '">'
                + cols
                + '</div>'
                + '<style>'
                '@media(max-width:768px){'
                '.mn-hero-split{grid-template-columns:1fr!important;}'
                '}'
                '</style>'
            )
        else:
            # Centered: todo centrado verticalmente y en columna
            inner_html = (
                '<div style="'
                'width:100%;max-width:800px;'
                'margin:0 auto;'
                'padding:80px 32px;'
                '">'
                + text_col
                + '</div>'
            )
            if image_html:
                # imagen debajo del texto en centered
                inner_html = (
                    '<div style="'
                    'width:100%;max-width:900px;'
                    'margin:0 auto;'
                    'padding:64px 32px 48px;'
                    'display:flex;flex-direction:column;align-items:center;gap:40px;'
                    '">'
                    + text_col
                    + image_html
                    + '</div>'
                )

        # contenido sobre overlay/video
        content_wrapper = (
            f'<div style="position:relative;z-index:2;width:100%;'
            f'display:flex;justify-content:center;">'
            + inner_html
            + '</div>'
        )

        return (
            wrapper_open
            + video_html
            + overlay_html
            + content_wrapper
            + wrapper_close
        )


# ══════════════════════════════════════════════════════════
# GALLERY
# ══════════════════════════════════════════════════════════

class GalleryItem:
    """
    Elemento individual de una Gallery.

    GalleryItem(
        src="/assets/foto.jpg",       # URL de la imagen (requerido)
        title="Título",               # mostrado en lightbox y tooltip
        description="Descripción",   # mostrado en lightbox
        alt="texto alternativo",
        url="https://...",            # si no hay lightbox, abre este URL
        url_target="_blank",          # "_self" | "_blank"
        span_cols=1,                  # cuántas columnas ocupa (masonry: ignorado)
        span_rows=1,                  # cuántas filas ocupa   (masonry: ignorado)
    )
    """
    def __init__(self, src, title=None, description=None, alt=None,
                 url=None, url_target="_blank", span_cols=1, span_rows=1):
        self.src         = src
        self.title       = title
        self.description = description
        self.alt         = alt or title or ""
        self.url         = url
        self.url_target  = url_target
        self.span_cols   = span_cols
        self.span_rows   = span_rows

class Gallery(Widget):
    """
    Galería de imágenes con lightbox opcional y soporte masonry.

    Uso básico:
        Gallery(items=[
            GalleryItem("/assets/a.jpg", title="Foto A", description="Desc A"),
            GalleryItem("/assets/b.jpg", title="Foto B"),
        ])

    Opciones:
        items        list[GalleryItem]  imágenes de la galería
        columns      int | str          columnas (int = fijo, "auto" = responsive)
                                        default: 3
        rows         int | None         filas máximas visibles (None = todas)
        gap          int                espacio entre items en px  (default: 8)
        masonry      bool               layout masonry (columnas de altura variable)
        img_height   int                alto de cada imagen en px  (default: 220)
                                        ignorado en masonry
        radius       int                radio de esquinas de las imágenes
        lightbox     bool               clic abre lightbox con título/descripción
                                        (default: True)
        object_fit   str                "cover"|"contain"|"fill"  (default: "cover")
    """

    _id_counter = 0

    def __init__(self, items=None, columns=3, rows=None, gap=8,
                 masonry=False, img_height=220, lightbox=True,
                 object_fit="cover", **kwargs):
        self._props      = Widget._extract_props(kwargs)
        self.items       = items or []
        self.columns     = columns
        self.rows        = rows
        self.gap         = gap
        self.masonry     = masonry
        self.img_height  = img_height
        self.lightbox    = lightbox
        self.object_fit  = object_fit
        Gallery._id_counter += 1
        self.uid = f"gal_{Gallery._id_counter}"

    def render(self):
        import json as _json
        uid      = self.uid
        gap      = self.gap
        items    = self.items
        masonry  = self.masonry
        lightbox = self.lightbox
        obj_fit  = self.object_fit
        img_h    = self.img_height
        radius_val = self._props.get("radius") or 0
        radius_css = f"border-radius:{radius_val}px;" if radius_val else ""

        # Resolver columnas
        if self.columns == "auto":
            cols_css = "repeat(auto-fill, minmax(200px, 1fr))"
        else:
            cols_css = f"repeat({self.columns}, 1fr)"

        # ── Estilos del wrapper ──────────────────────────────────────────
        if masonry:
            # CSS columns (multi-column layout) para efecto masonry real
            grid_style = (
                f"column-count:{self.columns};"
                f"column-gap:{gap}px;"
            )
            extra = self._resolve_props()
            wrapper_style = f"{grid_style}{extra}"
        else:
            row_constraint = f"grid-template-rows:repeat({self.rows}, {img_h}px);" if self.rows else ""
            grid_style = (
                f"display:grid;"
                f"grid-template-columns:{cols_css};"
                f"gap:{gap}px;"
                f"{row_constraint}"
            )
            if self.rows:
                grid_style += "overflow:hidden;"
            extra = self._resolve_props()
            wrapper_style = f"{grid_style}{extra}"

        # ── Items HTML ───────────────────────────────────────────────────
        items_html = ""
        lightbox_data = []  # [{src, title, description}]

        for idx, item in enumerate(items):
            if not isinstance(item, GalleryItem):
                continue

            item_radius = radius_css
            img_style = (
                f"width:100%;display:block;"
                f"object-fit:{obj_fit};"
                f"{item_radius}"
            )
            if not masonry:
                img_style += f"height:{img_h}px;"
            else:
                img_style += "height:auto;"

            # span cols/rows en grid (no masonry)
            span_style = ""
            if not masonry:
                if item.span_cols > 1:
                    span_style += f"grid-column:span {item.span_cols};"
                if item.span_rows > 1:
                    span_style += f"grid-row:span {item.span_rows};"

            # cursor
            cursor = "pointer" if (lightbox or item.url) else "default"

            # item wrapper
            if masonry:
                wrapper_item_style = f"break-inside:avoid;margin-bottom:{gap}px;{item_radius}overflow:hidden;cursor:{cursor};"
            else:
                wrapper_item_style = f"{span_style}{item_radius}overflow:hidden;cursor:{cursor};"

            # acción al hacer clic
            if lightbox:
                onclick = f"_galOpen('{uid}',{idx})"
            elif item.url:
                target = item.url_target or "_blank"
                onclick = f"window.open('{item.url}','{target}')"
            else:
                onclick = ""

            onclick_attr = f' onclick="{onclick}"' if onclick else ""

            # hover overlay con título
            overlay_html = ""
            if item.title:
                overlay_html = (
                    f'<div style="position:absolute;bottom:0;left:0;right:0;'
                    f'background:linear-gradient(transparent,rgba(0,0,0,0.65));'
                    f'color:#fff;font-size:13px;font-weight:600;'
                    f'padding:20px 10px 8px;opacity:0;transition:opacity .25s;"'
                    f' class="{uid}_caption">'
                    f'{item.title}</div>'
                )

            items_html += (
                f'<div style="position:relative;{wrapper_item_style}"{onclick_attr}'
                f' onmouseenter="this.querySelector(\'[class*=_caption]\')&&(this.querySelector(\'[class*=_caption]\').style.opacity=1)"'
                f' onmouseleave="this.querySelector(\'[class*=_caption]\')&&(this.querySelector(\'[class*=_caption]\').style.opacity=0)"'
                f'>'
                f'<img src="{item.src}" alt="{item.alt}" style="{img_style}" loading="lazy">'
                f'{overlay_html}'
                f'</div>'
            )

            lightbox_data.append({
                "src":   item.src,
                "title": item.title or "",
                "desc":  item.description or "",
            })

        # ── Lightbox HTML ────────────────────────────────────────────────
        lightbox_html = ""
        lightbox_js   = ""
        if lightbox:
            lightbox_html = (
                f'<div id="{uid}_lb" style="'
                f'display:none;position:fixed;top:0;left:0;width:100%;height:100%;'
                f'background:rgba(0,0,0,0.92);z-index:9999;'
                f'align-items:center;justify-content:center;flex-direction:column;">'

                # Botón cerrar
                f'<button onclick="_galClose(\'{uid}\')" style="'
                f'position:absolute;top:20px;right:24px;'
                f'background:none;border:none;color:#fff;font-size:28px;'
                f'cursor:pointer;line-height:1;z-index:1;">✕</button>'

                # Botón prev
                f'<button onclick="_galPrev(\'{uid}\')" style="'
                f'position:absolute;left:16px;top:50%;transform:translateY(-50%);'
                f'background:rgba(255,255,255,0.1);border:none;color:#fff;'
                f'font-size:28px;width:48px;height:48px;border-radius:50%;'
                f'cursor:pointer;backdrop-filter:blur(8px);">‹</button>'

                # Botón next
                f'<button onclick="_galNext(\'{uid}\')" style="'
                f'position:absolute;right:16px;top:50%;transform:translateY(-50%);'
                f'background:rgba(255,255,255,0.1);border:none;color:#fff;'
                f'font-size:28px;width:48px;height:48px;border-radius:50%;'
                f'cursor:pointer;backdrop-filter:blur(8px);">›</button>'

                # Imagen
                f'<img id="{uid}_lb_img" src="" alt="" style="'
                f'max-width:90vw;max-height:75vh;object-fit:contain;'
                f'border-radius:8px;box-shadow:0 8px 48px rgba(0,0,0,0.6);">'

                # Info
                f'<div id="{uid}_lb_info" style="'
                f'text-align:center;margin-top:16px;max-width:600px;padding:0 24px;">'
                f'<div id="{uid}_lb_title" style="'
                f'color:#fff;font-size:17px;font-weight:700;margin-bottom:6px;"></div>'
                f'<div id="{uid}_lb_desc" style="'
                f'color:rgba(255,255,255,0.7);font-size:14px;line-height:1.6;"></div>'
                f'</div>'

                # Contador
                f'<div id="{uid}_lb_count" style="'
                f'position:absolute;bottom:20px;left:50%;transform:translateX(-50%);'
                f'color:rgba(255,255,255,0.5);font-size:13px;"></div>'

                f'</div>'
            )

            data_js = _json.dumps(lightbox_data)
            lightbox_js = (
                f'(function(){{'
                f'var _d={data_js};'
                f'var _i=0;'
                f'function _show(n){{'
                f'  _i=(n+_d.length)%_d.length;'
                f'  var it=_d[_i];'
                f'  document.getElementById("{uid}_lb_img").src=it.src;'
                f'  document.getElementById("{uid}_lb_title").textContent=it.title;'
                f'  document.getElementById("{uid}_lb_desc").textContent=it.desc;'
                f'  document.getElementById("{uid}_lb_count").textContent=(_i+1)+" / "+_d.length;'
                f'  document.getElementById("{uid}_lb_info").style.display='
                f'    (it.title||it.desc)?"block":"none";'
                f'}}'
                f'window._galOpen=window._galOpen||{{}};'
                f'window._galClose=window._galClose||{{}};'
                f'window._galPrev=window._galPrev||{{}};'
                f'window._galNext=window._galNext||{{}};'
                f'window._galOpen["{uid}"]=function(idx){{'
                f'  _show(idx);'
                f'  var lb=document.getElementById("{uid}_lb");'
                f'  lb.style.display="flex";'
                f'  document.body.style.overflow="hidden";'
                f'}};'
                f'window._galClose["{uid}"]=function(){{'
                f'  document.getElementById("{uid}_lb").style.display="none";'
                f'  document.body.style.overflow="";'
                f'}};'
                f'window._galPrev["{uid}"]=function(){{_show(_i-1);}};'
                f'window._galNext["{uid}"]=function(){{_show(_i+1);}};'
                # Fix onclick attrs to use the registry
                f'document.addEventListener("DOMContentLoaded",function(){{'
                f'  document.querySelectorAll("[onclick]").forEach(function(el){{'
                f'    var oc=el.getAttribute("onclick");'
                f'    if(oc&&oc.includes("_galOpen(\'{uid}\'")){{'
                f'      var m=oc.match(/[0-9]+/);'
                f'      if(m)el.addEventListener("click",function(){{window._galOpen["{uid}"](+m[0]);}});'
                f'    }}'
                f'    if(oc&&oc.includes("_galClose(\'{uid}\'")){{'
                f'      el.addEventListener("click",function(){{window._galClose["{uid}"]();}});'
                f'    }}'
                f'    if(oc&&oc.includes("_galPrev(\'{uid}\'")){{'
                f'      el.addEventListener("click",function(){{window._galPrev["{uid}"]();}});'
                f'    }}'
                f'    if(oc&&oc.includes("_galNext(\'{uid}\'")){{'
                f'      el.addEventListener("click",function(){{window._galNext["{uid}"]();}});'
                f'    }}'
                f'  }});'
                # keyboard nav
                f'  document.addEventListener("keydown",function(e){{'
                f'    var lb=document.getElementById("{uid}_lb");'
                f'    if(!lb||lb.style.display==="none")return;'
                f'    if(e.key==="Escape")window._galClose["{uid}"]();'
                f'    if(e.key==="ArrowLeft")window._galPrev["{uid}"]();'
                f'    if(e.key==="ArrowRight")window._galNext["{uid}"]();'
                f'  }});'
                # close on backdrop click
                f'  document.getElementById("{uid}_lb").addEventListener("click",function(e){{'
                f'    if(e.target===this)window._galClose["{uid}"]();'
                f'  }});'
                f'}});'
                f'}})();'
            )

        # ── Responsive CSS ───────────────────────────────────────────────
        responsive_css = ""
        if not masonry and isinstance(self.columns, int) and self.columns > 2:
            responsive_css = (
                f'<style>'
                f'@media(max-width:640px){{'
                f'#{uid}{{grid-template-columns:repeat(2,1fr)!important;}}'
                f'}}'
                f'@media(max-width:400px){{'
                f'#{uid}{{grid-template-columns:1fr!important;}}'
                f'}}'
                f'</style>'
            )

        # ── Ensamblado ───────────────────────────────────────────────────
        html = (
            responsive_css
            + f'<div id="{uid}" style="{wrapper_style}">'
            + items_html
            + '</div>'
            + lightbox_html
            + (f'<script>{lightbox_js}</script>' if lightbox_js else "")
        )
        return self._wrap_url(html)


# ══════════════════════════════════════════════════════════
# CAROUSEL
# ══════════════════════════════════════════════════════════

class CarouselItem:
    """
    Elemento individual de un Carousel.

    CarouselItem(
        # Slide normal
        child=Card(...),          # cualquier widget como contenido
        # O bien imagen directa
        image="/assets/foto.jpg",
        title="Título del slide",
        subtitle="Subtítulo o descripción",
        # URL al hacer clic (si no hay lightbox u otro handler)
        url=None,
        url_target="_blank",
    )

    Modo brands — basta con:
        CarouselItem(image="/assets/logo.svg", title="Marca X", url="https://...")
    """
    def __init__(self, child=None, image=None, title=None, subtitle=None,
                 url=None, url_target="_blank"):
        self.child      = child
        self.image      = image
        self.title      = title
        self.subtitle   = subtitle
        self.url        = url
        self.url_target = url_target

class Carousel(Widget):
    """
    Carrusel de slides o cinta de marcas (logos).

    ── Modo slides ────────────────────────────────────────────────────────

        Carousel(
            items=[
                CarouselItem(image="/assets/a.jpg", title="Slide 1", subtitle="Desc"),
                CarouselItem(child=Card(children=[Heading("Hola")])),
                CarouselItem(image="/assets/b.jpg", title="Slide 2",
                             url="https://...", url_target="_blank"),
            ],
            mode="slides",
            visible=1,          # cuántos slides se ven a la vez
            mobile_visible=1,   # en móvil mostrar solo 1 (o el valor indicado)
            gap=16,             # espacio entre slides
            loop=True,          # vuelve al inicio al llegar al final
            autoplay=0,         # 0 = desactivado; ms entre avance automático (ej: 3000)
            arrows=True,        # mostrar flechas prev/next
            dots=True,          # mostrar indicadores de posición
            img_height=320,     # alto de imagen en px (si el item usa image=)
            radius=12,          # radio de esquinas de cada slide
        )

    ── Modo brands ────────────────────────────────────────────────────────

        Carousel(
            items=[
                CarouselItem(image="/assets/logo-a.svg", title="Empresa A",
                             url="https://a.com"),
                CarouselItem(image="/assets/logo-b.png", title="Empresa B"),
            ],
            mode="brands",
            brand_height=48,        # alto de cada logo en px
            brand_filter="grayscale(100%) opacity(0.5)",  # filtro CSS por defecto
            brand_filter_hover=None,  # None = sin filtro al hover (color completo)
            brand_gap=64,           # espacio entre logos
            speed=30,               # segundos para completar un ciclo
            loop=True,              # siempre True en brands, loop infinito
        )

    Parámetros comunes:
        items          list[CarouselItem]
        mode           "slides" | "brands"
        loop           bool
        autoplay       int   ms (solo slides; 0 = desactivado)
        mobile_visible int   visibles en móvil (default: 1)
        mobile_arrows  bool  mostrar flechas en móvil (default: False)
        radius         int   border-radius de cada item
        url / url_target     prop universal del widget wrapper
    """

    _id_counter = 0

    def __init__(self, items=None, mode="slides",
                 # slides
                 visible=1, gap=16, loop=True, autoplay=0,
                 arrows=True, dots=True, img_height=320,
                 mobile_visible=1, mobile_arrows=False, mobile_breakpoint=768,
                 # brands
                 brand_height=48,
                 brand_filter="grayscale(100%) opacity(0.55)",
                 brand_filter_hover=None,
                 brand_gap=64, speed=30,
                 **kwargs):
        self._props        = Widget._extract_props(kwargs)
        self.items         = items or []
        self.mode          = mode
        self.visible       = visible
        self.gap           = gap
        self.loop          = loop
        self.autoplay      = autoplay
        self.arrows        = arrows
        self.dots          = dots
        self.img_height    = img_height
        self.mobile_visible = mobile_visible
        self.mobile_arrows = mobile_arrows
        self.mobile_breakpoint = mobile_breakpoint
        self.brand_height  = brand_height
        self.brand_filter  = brand_filter
        self.brand_filter_hover = brand_filter_hover  # None = sin filtro (color)
        self.brand_gap     = brand_gap
        self.speed         = speed
        Carousel._id_counter += 1
        self.uid = f"car_{Carousel._id_counter}"

    # ── helpers ───────────────────────────────────────────────────────────

    def _render_item_content(self, item, radius_css):
        """Renderiza el contenido de un CarouselItem como HTML."""
        if item.child is not None:
            content = item.child.render() if isinstance(item.child, Widget) else str(item.child)
        elif item.image:
            img_style = (
                f"width:100%;height:{self.img_height}px;"
                f"object-fit:cover;display:block;{radius_css}"
            )
            content = f'<img src="{item.image}" alt="{item.title or ""}" style="{img_style}" loading="lazy">'
            if item.title or item.subtitle:
                overlay = (
                    f'<div style="padding:16px 20px;">'
                    + (f'<div style="font-size:16px;font-weight:700;color:var(--text);margin-bottom:4px;">{item.title}</div>' if item.title else "")
                    + (f'<div style="font-size:13px;color:var(--text-muted);line-height:1.5;">{item.subtitle}</div>' if item.subtitle else "")
                    + '</div>'
                )
                content += overlay
        else:
            content = ""
            if item.title:
                content += f'<div style="font-size:18px;font-weight:700;color:var(--text);margin-bottom:8px;">{item.title}</div>'
            if item.subtitle:
                content += f'<div style="font-size:14px;color:var(--text-muted);line-height:1.6;">{item.subtitle}</div>'

        # Wrap en <a> si tiene url
        if item.url:
            rel = ' rel="noopener noreferrer"' if item.url_target == "_blank" else ""
            content = (
                f'<a href="{item.url}" target="{item.url_target}"{rel}'
                f' style="display:block;text-decoration:none;">'
                + content + '</a>'
            )
        return content

    # ── render brands ─────────────────────────────────────────────────────

    def _render_brands(self):
        uid   = self.uid
        items = [i for i in self.items if isinstance(i, CarouselItem) and i.image]
        h     = self.brand_height
        gap   = self.brand_gap
        speed = self.speed
        flt   = self.brand_filter
        flt_h = self.brand_filter_hover if self.brand_filter_hover is not None else "none"
        extra = self._resolve_props()

        def _logo(item):
            img_s = (
                "height:" + str(h) + "px;width:auto;max-width:180px;"
                + "object-fit:contain;display:block;"
                + "filter:" + flt + ";transition:filter .35s ease;"
            )
            me  = "onmouseenter=\"this.querySelector('img').style.filter='" + flt_h + "'\""
            ml  = "onmouseleave=\"this.querySelector('img').style.filter='" + flt + "'\""
            hjs = " " + me + " " + ml
            img = '<img src="' + item.image + '" alt="' + (item.title or "") + '" style="' + img_s + '">'
            s   = "display:inline-flex;align-items:center;flex-shrink:0;padding:0 " + str(gap // 2) + "px;"
            if item.url:
                rel = ' rel="noopener noreferrer"' if item.url_target == "_blank" else ""
                return ('<a href="' + item.url + '" target="' + item.url_target + '"' + rel
                        + ' style="' + s + 'text-decoration:none;"' + hjs + '>' + img + '</a>')
            return '<div style="' + s + '"' + hjs + '>' + img + '</div>'

        logos = "".join(_logo(i) for i in items)
        wrapper_style = "width:100%;overflow:hidden;position:relative;" + extra

        fade = (
            '<div style="position:absolute;top:0;left:0;bottom:0;width:60px;'
            + 'background:linear-gradient(to right,var(--bg,#0d1117),transparent);'
            + 'z-index:2;pointer-events:none;"></div>'
            + '<div style="position:absolute;top:0;right:0;bottom:0;width:60px;'
            + 'background:linear-gradient(to left,var(--bg,#0d1117),transparent);'
            + 'z-index:2;pointer-events:none;"></div>'
        )

        # JS: starts with g1 only, then clones groups until track fills 2x wrapper width.
        # rAF resets pos when it reaches g1.offsetWidth => seamless loop regardless of count.
        js = (
            '<script>(function(){'
            + 'var uid="' + uid + '";'
            + 'var secs=' + str(speed) + ';'
            + 'var track=document.getElementById(uid+"_track");'
            + 'var g1=document.getElementById(uid+"_g1");'
            + 'if(!track||!g1)return;'
            + 'var paused=false,pos=0,last=null,w=0;'
            + 'function fill(){'
            +   'w=g1.offsetWidth;'
            +   'if(w<4)return;'
            +   'var old=track.querySelectorAll("[data-clone]");'
            +   'for(var i=0;i<old.length;i++)old[i].remove();'
            +   'var needed=(track.parentElement?track.parentElement.offsetWidth:800)*2+w;'
            +   'var total=w;'
            +   'while(total<needed){'
            +     'var c=g1.cloneNode(true);'
            +     'c.removeAttribute("id");'
            +     'c.setAttribute("aria-hidden","true");'
            +     'c.setAttribute("data-clone","1");'
            +     'track.appendChild(c);'
            +     'total+=w;'
            +   '}'
            + '}'
            + 'function step(ts){'
            +   'if(!last)last=ts;'
            +   'var dt=Math.min(ts-last,100);'
            +   'if(!paused&&w>0){'
            +     'pos+=dt/1000*(w/secs);'
            +     'if(pos>=w)pos-=w;'
            +     'track.style.transform="translateX(-"+pos.toFixed(2)+"px)";'
            +   '}'
            +   'last=ts;'
            +   'requestAnimationFrame(step);'
            + '}'
            + 'var wrap=document.getElementById(uid);'
            + 'if(wrap){'
            +   'wrap.addEventListener("mouseenter",function(){paused=true;});'
            +   'wrap.addEventListener("mouseleave",function(){paused=false;last=null;});'
            + '}'
            + 'function start(){fill();requestAnimationFrame(step);}'
            + 'if(document.readyState==="loading"){'
            +   'document.addEventListener("DOMContentLoaded",start);'
            + '}else{start();}'
            + 'window.addEventListener("load",function(){fill();});'
            + 'window.addEventListener("resize",function(){pos=0;fill();});'
            + '})();</script>'
        )

        html = (
            '<div id="' + uid + '" style="' + wrapper_style + '">'
            + fade
            + '<div id="' + uid + '_track" style="display:flex;align-items:center;padding:20px 0;will-change:transform;">'
            + '<div id="' + uid + '_g1" style="display:flex;align-items:center;flex-shrink:0;">'
            + logos + '</div>'
            + '</div></div>'
            + js
        )
        return self._wrap_url(html)


        # ── render slides ─────────────────────────────────────────────────────

    def _render_slides(self):
        uid      = self.uid
        items    = [i for i in self.items if isinstance(i, CarouselItem)]
        n        = len(items)
        gap      = self.gap
        visible  = max(1, int(self.visible))
        mobile_visible = self.mobile_visible
        if mobile_visible is None:
            mobile_visible = visible
        mobile_visible = max(1, int(mobile_visible))
        bp = max(320, int(self.mobile_breakpoint or 768))
        mobile_arrows = bool(self.mobile_arrows)
        loop     = self.loop
        autoplay = self.autoplay
        arrows   = self.arrows
        dots     = self.dots
        radius_val = self._props.get("radius") or 0
        radius_css = "border-radius:" + str(radius_val) + "px;" if radius_val else ""
        extra    = self._resolve_props()

        # Número de posiciones navegables
        positions = max(n if loop else (n - visible + 1), 1)
        mobile_positions = max(n if loop else (n - min(mobile_visible, max(n, 1)) + 1), 1)
        max_positions = max(positions, mobile_positions)

        slide_width = "calc((100% - " + str(gap * (visible - 1)) + "px) / " + str(visible) + ")"

        # Slides normales
        slides_html = ""
        for idx, item in enumerate(items):
            content_s = self._render_item_content(item, radius_css)
            slides_html += (
                '<div id="' + uid + '_s' + str(idx) + '" style="'
                'flex-shrink:0;width:' + slide_width + ';'
                'background:var(--surface);'
                'border:1px solid var(--border);'
                'overflow:hidden;' + radius_css + '">'
                + content_s + '</div>'
            )

        # Si loop=True, clonamos los primeros `visible` slides al final
        # y los últimos `visible` al inicio → infinite clone technique
        clones_after  = ""
        clones_before = ""
        clone_count = min(max(visible, mobile_visible), n) if loop else 0
        if loop:
            for idx in range(clone_count):
                content_s = self._render_item_content(items[idx], radius_css)
                clones_after += (
                    '<div data-clone="after" style="'
                    'flex-shrink:0;width:' + slide_width + ';'
                    'background:var(--surface);'
                    'border:1px solid var(--border);'
                    'overflow:hidden;' + radius_css + '">'
                    + content_s + '</div>'
                )
            for idx in range(n - clone_count, n):
                content_s = self._render_item_content(items[idx], radius_css)
                clones_before += (
                    '<div data-clone="before" style="'
                    'flex-shrink:0;width:' + slide_width + ';'
                    'background:var(--surface);'
                    'border:1px solid var(--border);'
                    'overflow:hidden;' + radius_css + '">'
                    + content_s + '</div>'
                )

        # Dots: one per navigable position
        dots_html = ""
        if dots and max_positions > 1:
            dot_items = ""
            for i in range(max_positions):
                active = "var(--accent)" if i == 0 else "var(--border)"
                scale  = "transform:scale(1.3);" if i == 0 else ""
                dot_items += (
                    '<button id="' + uid + '_dot' + str(i) + '" style="'
                    'width:8px;height:8px;border-radius:50%;border:none;cursor:pointer;'
                    'transition:all .25s;padding:0;background:' + active + ';' + scale + '"></button>'
                )
            dots_html = (
                '<div style="display:flex;justify-content:center;gap:8px;margin-top:16px;">'
                + dot_items + '</div>'
            )

        # Arrows — fuera del viewport con overflow:hidden, dentro del wrapper con overflow:visible
        btn_base = (
            "position:absolute;top:50%;transform:translateY(-50%);"
            "background:var(--surface);border:1px solid var(--border);"
            "color:var(--text);width:40px;height:40px;border-radius:50%;"
            "cursor:pointer;font-size:22px;display:flex;align-items:center;"
            "justify-content:center;z-index:4;transition:background .2s;"
            "box-shadow:0 2px 12px rgba(0,0,0,0.2);"
        )
        arrows_html = ""
        if arrows:
            arrows_html = (
                '<button id="' + uid + '_prev" style="' + btn_base + 'left:-20px;">&#8249;</button>'
                '<button id="' + uid + '_next" style="' + btn_base + 'right:-20px;">&#8250;</button>'
            )

        # Layout: wrapper has overflow:visible so arrows aren't clipped
        # viewport clips the slides track
        wrapper_style = "position:relative;overflow:visible;" + extra
        track_style   = "display:flex;gap:" + str(gap) + "px;will-change:transform;"

        html = (
            '<div style="' + wrapper_style + '">'
            + '<div id="' + uid + '_viewport" style="overflow:hidden;position:relative;">'
            + '<div id="' + uid + '_track" style="' + track_style + '">'
            + (clones_before if loop else "")
            + slides_html
            + (clones_after if loop else "")
            + '</div>'
            + '</div>'
            + arrows_html
            + dots_html
            + '</div>'
        )

        # JS — offset calculation accounts for clone padding when loop=True
        clone_offset = "vis" if loop else "0"

        js = (
            ';(function(){'
            'if(!window._car)window._car={};'
            'var uid="' + uid + '",n=' + str(n) + ',dvis=' + str(visible) + ',mvis=' + str(mobile_visible) + ',gap=' + str(gap) + ','
            'bp=' + str(bp) + ',mobileArrows=' + ('true' if mobile_arrows else 'false') + ','
            'loop=' + ('true' if loop else 'false') + ','
            'positions=' + str(positions) + ','
            'maxDots=' + str(max_positions) + ','
            'autoplay=' + str(autoplay) + ';'
            'var cur=0,curVis=dvis,isMobile=false;'  # cur = index into real slides (0..n-1)
            'var transitioning=false;'
            'var track=document.getElementById(uid+"_track");'
            'var vp=document.getElementById(uid+"_viewport");'
            'if(!track||!vp||n<=0)return;'

            'function _vis(){'
            '  isMobile=!!(window.matchMedia&&window.matchMedia("(max-width:"+bp+"px)").matches);'
            '  var v=isMobile?mvis:dvis;'
            '  v=Math.max(1,Math.min(v,n));'
            '  return v;'
            '}'

            'function _positions(){'
            '  if(loop)return Math.max(n,1);'
            '  return Math.max(n-curVis+1,1);'
            '}'

            'function _sw(){'
            '  return vp?(vp.offsetWidth-gap*(curVis-1))/curVis:0;'
            '}'

            # offset: if loop, track starts with `vis` clone slides before real slides
            'function _offset(idx){'
            '  var sw=_sw();'
            '  var base=loop?' + str(clone_count) + ':0;'
            '  return (base+idx)*(sw+gap);'
            '}'

            'function _syncDots(){'
            '  for(var i=0;i<maxDots;i++){'
            '    var d=document.getElementById(uid+"_dot"+i);'
            '    if(!d)continue;'
            '    d.style.display=i<positions?"inline-block":"none";'
            '  }'
            '}'

            'function _syncArrows(){'
            '  var show=(!isMobile)||mobileArrows;'
            '  var bpv=document.getElementById(uid+"_prev");'
            '  var bnx=document.getElementById(uid+"_next");'
            '  if(bpv)bpv.style.display=show?"flex":"none";'
            '  if(bnx)bnx.style.display=show?"flex":"none";'
            '}'

            'function _updateDots(){'
            '  var disp=((cur%n)+n)%n;'
            '  var dotIdx=loop?disp:Math.min(cur,positions-1);'
            '  for(var i=0;i<maxDots;i++){'
            '    var d=document.getElementById(uid+"_dot"+i);'
            '    if(d){'
            '      var active=i===dotIdx;'
            '      d.style.background=active?"var(--accent)":"var(--border)";'
            '      d.style.transform=active?"scale(1.3)":"scale(1)";'
            '    }'
            '  }'
            '}'

            'function _moveTo(idx,animate){'
            '  track.style.transition=animate?"transform .4s cubic-bezier(.4,0,.2,1)":"none";'
            '  track.style.transform="translateX(-"+_offset(idx)+"px)";'
            '}'

            'function _go(idx){'
            '  if(loop){cur=((idx%n)+n)%n;}'
            '  else{'
            '    var mx=Math.max(n-curVis,0);'
            '    cur=Math.max(0,Math.min(idx,mx));'
            '  }'
            '  _moveTo(cur,true);'
            '  _updateDots();'
            '}'

            'function _syncMode(){'
            '  curVis=_vis();'
            '  positions=_positions();'
            '  if(!loop){'
            '    var mx=Math.max(n-curVis,0);'
            '    if(cur>mx)cur=mx;'
            '  }else{cur=((cur%n)+n)%n;}'
            '  var wcss="calc((100% - "+(gap*(curVis-1))+"px) / "+curVis+")";'
            '  for(var i=0;i<track.children.length;i++)track.children[i].style.width=wcss;'
            '  _syncDots();'
            '  _syncArrows();'
            '  _moveTo(cur,false);'
            '  _updateDots();'
            '}'

            # After transition ends, if loop, silently jump when at clone boundary
            'track.addEventListener("transitionend",function(){'
            '  if(!loop){transitioning=false;return;}'
            '  if(cur>=n){cur=cur%n;_moveTo(cur,false);}'
            '  else if(cur<0){cur=((cur%n)+n)%n;_moveTo(cur,false);}'
            '  _updateDots();'
            '  transitioning=false;'
            '});'

            'window._car[uid]={'
            '  go:function(i){_go(i);},'
            '  next:function(){'
            '    if(transitioning)return;'
            '    if(!loop&&cur>=n-curVis)return;'
            '    transitioning=true;'
            '    cur=cur+1;'
            '    _moveTo(cur,true);'
            '    _updateDots();'
            '  },'
            '  prev:function(){'
            '    if(transitioning)return;'
            '    if(!loop&&cur<=0)return;'
            '    transitioning=true;'
            '    cur=cur-1;'
            '    _moveTo(cur,true);'
            '    _updateDots();'
            '  }'
            '};'

            # Wire arrows
            'var bp=document.getElementById(uid+"_prev");'
            'var bn=document.getElementById(uid+"_next");'
            'if(bp)bp.addEventListener("click",function(){window._car[uid].prev();});'
            'if(bn)bn.addEventListener("click",function(){window._car[uid].next();});'
            # Wire dots
            '(function(){'
            '  for(var i=0;i<maxDots;i++){'
            '    (function(idx){'
            '      var d=document.getElementById(uid+"_dot"+idx);'
            '      if(d)d.addEventListener("click",function(){if(idx<positions)_go(idx);});'
            '    })(i);'
            '  }'
            '})();'

            # Keyboard
            'var root=document.getElementById(uid+"_viewport");'
            'if(root)root.addEventListener("keydown",function(e){'
            '  if(e.key==="ArrowLeft")window._car[uid].prev();'
            '  if(e.key==="ArrowRight")window._car[uid].next();'
            '});'

            # Swipe
            'var tx=0;'
            'if(vp){'
            '  vp.addEventListener("touchstart",function(e){tx=e.touches[0].clientX;},{passive:true});'
            '  vp.addEventListener("touchend",function(e){'
            '    var dx=tx-e.changedTouches[0].clientX;'
            '    if(Math.abs(dx)>40){if(dx>0)window._car[uid].next();else window._car[uid].prev();}'
            '  });'
            '}'

            # Autoplay
            'if(autoplay>0){'
            '  var t=setInterval(function(){window._car[uid].next();},autoplay);'
            '  if(vp){'
            '    vp.addEventListener("mouseenter",function(){clearInterval(t);});'
            '    vp.addEventListener("mouseleave",function(){'
            '      t=setInterval(function(){window._car[uid].next();},autoplay);'
            '    });'
            '  }'
            '}'

            # Init position (accounting for clones at start)
            'function _init(){'
            '  _syncMode();'
            '}'
            'if(document.readyState==="loading"){'
            '  document.addEventListener("DOMContentLoaded",_init);'
            '} else {_init();}'
            'window.addEventListener("resize",function(){_syncMode();});'
            '})();'
        )

        return self._wrap_url(html + '<script>' + js + '</script>')


    # ── render ────────────────────────────────────────────────────────────

    def render(self):
        if self.mode == "brands":
            return self._render_brands()
        return self._render_slides()

class AccordionItem:
    """
    Elemento individual de un Accordion.

        AccordionItem(
            title="¿Cómo funciona?",
            child=Paragraph("El sistema funciona así..."),
            # o bien:
            content="Texto simple de respuesta",
            open=False,  # abierto por defecto
        )
    """
    def __init__(self, title, content=None, child=None, children=None, open=False):
        self.title    = title
        self.content  = content
        self.child    = child
        self.children = children
        self.open     = open

class Accordion(Widget):
    """
    Acordeón: lista de secciones plegables.

    Uso:
        Accordion(items=[
            AccordionItem("¿Qué es MARTIN?",
                          content="MARTIN es un framework Python para construir webs."),
            AccordionItem("¿Cómo instalo?",
                          child=Code("pip install martin", language="bash"), open=True),
            AccordionItem("¿Tiene dark mode?",
                          children=[Text("Sí, completamente."), Badge("Auto")]),
        ])

    Parámetros:
        items        list[AccordionItem]  ítems del acordeón
        multiple     bool    permite varios abiertos a la vez (default: False)
        variant      str     "default" | "bordered" | "separated"
        icon         str     "chevron" | "plus" | "arrow"  — icono del toggle
        radius       int     radio de bordes
    """

    _id_counter = 0

    def __init__(self, items=None, multiple=False, variant="default",
                 icon="chevron", **kwargs):
        self._props   = Widget._extract_props(kwargs)
        self.items    = items or []
        self.multiple = multiple
        self.variant  = variant
        self.icon     = icon
        Accordion._id_counter += 1
        self.uid = f"acc_{Accordion._id_counter}"

    def _icon_svg(self, closed=True):
        if self.icon == "plus":
            if closed:
                return '<svg width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M8 3v10M3 8h10" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>'
            else:
                return '<svg width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M3 8h10" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>'
        elif self.icon == "arrow":
            return '<svg width="14" height="14" viewBox="0 0 14 14" fill="none" style="transition:transform .25s"><path d="M2 5l5 5 5-5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>'
        else:  # chevron (default)
            return '<svg width="16" height="16" viewBox="0 0 16 16" fill="none" style="transition:transform .25s"><path d="M4 6l4 4 4-4" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>'

    def render(self):
        import json as _json
        uid      = self.uid
        multiple = _json.dumps(self.multiple)
        extra    = self._resolve_props()
        radius   = self._props.get("radius", 12)
        r_css    = f"{radius}px"

        # Variant styles
        if self.variant == "separated":
            wrapper_style = f"display:flex;flex-direction:column;gap:8px;{extra}"
            item_base = (f"border:1px solid var(--border);border-radius:{r_css};"
                         f"background:var(--surface);overflow:hidden")
        elif self.variant == "bordered":
            wrapper_style = f"border:1px solid var(--border);border-radius:{r_css};overflow:hidden;{extra}"
            item_base = "border-bottom:1px solid var(--border)"
        else:  # default
            wrapper_style = f"border:1px solid var(--border);border-radius:{r_css};overflow:hidden;{extra}"
            item_base = "border-bottom:1px solid var(--border)"

        items_html = ""
        for i, item in enumerate(self.items):
            iid     = f"{uid}_i{i}"
            is_open = item.open
            is_last = (i == len(self.items) - 1)

            # Resolve content
            if item.children:
                body_html = Widget._render_children(item.children)
            elif item.child is not None:
                body_html = item.child.render() if isinstance(item.child, Widget) else str(item.child)
            elif item.content is not None:
                body_html = item.content.render() if isinstance(item.content, Widget) else str(item.content)
            else:
                body_html = ""

            # Title
            title_html = item.title.render() if isinstance(item.title, Widget) else str(item.title)

            # Border on last item in default/bordered
            item_style = item_base
            if self.variant != "separated" and is_last:
                item_style = item_base.replace("border-bottom:1px solid var(--border)", "")

            icon_id = f"{uid}_ico{i}"
            body_open    = "1" if is_open else "0"
            icon_rot     = "rotate(180deg)" if is_open else "rotate(0deg)"

            items_html += (
                f'<div style="{item_style}">'
                f'  <button id="{iid}_btn" onclick="{uid}_toggle({i})" '
                f'    style="width:100%;display:flex;align-items:center;justify-content:space-between;'
                f'           padding:16px 20px;background:none;border:none;cursor:pointer;'
                f'           text-align:left;gap:12px;color:var(--text);">'
                f'    <span style="font-size:15px;font-weight:600;flex:1">{title_html}</span>'
                f'    <span id="{icon_id}" style="flex-shrink:0;color:var(--text-muted);'
                f'          transform:{icon_rot};transition:transform .25s;display:flex">'
                f'      {self._icon_svg()}'
                f'    </span>'
                f'  </button>'
                f'  <div id="{iid}_body" data-open="{body_open}" style="max-height:0;overflow:hidden;'
                f'       padding:0 20px 0;font-size:14px;color:var(--text-muted);line-height:1.7;'
                f'       opacity:0;transform:translateY(-4px);'
                f'       transition:max-height .28s cubic-bezier(.4,0,.2,1),'
                f'                  opacity .2s ease,transform .2s ease,padding .24s ease;">'
                f'    {body_html}'
                f'  </div>'
                f'</div>'
            )

        n = len(self.items)
        js = f"""
<script>(function(){{
  var uid={_json.dumps(uid)}, n={n}, multi={multiple};
  var TRANS="max-height .28s cubic-bezier(.4,0,.2,1),opacity .2s ease,transform .2s ease,padding .24s ease";

  function bodyEl(i){{ return document.getElementById(uid+"_i"+i+"_body"); }}
  function iconEl(i){{ return document.getElementById(uid+"_ico"+i); }}

  function setOpen(i, open, animate){{
    var b = bodyEl(i), ic = iconEl(i);
    if(!b) return;

    if(!animate) b.style.transition = "none";

    if(open){{
      if(b.style.maxHeight === "none") b.style.maxHeight = b.scrollHeight + "px";
      requestAnimationFrame(function(){{
        b.style.maxHeight = b.scrollHeight + "px";
        b.style.opacity = "1";
        b.style.transform = "translateY(0)";
        b.style.padding = "0 20px 16px";
      }});
      b.setAttribute("data-open", "1");
      if(ic) ic.style.transform = "rotate(180deg)";
    }} else {{
      if(b.style.maxHeight === "none"){{
        b.style.maxHeight = b.scrollHeight + "px";
        b.offsetHeight;
      }}
      b.style.maxHeight = b.scrollHeight + "px";
      requestAnimationFrame(function(){{
        b.style.maxHeight = "0px";
        b.style.opacity = "0";
        b.style.transform = "translateY(-4px)";
        b.style.padding = "0 20px 0";
      }});
      b.setAttribute("data-open", "0");
      if(ic) ic.style.transform = "rotate(0deg)";
    }}

    if(!animate){{
      b.offsetHeight;
      b.style.transition = TRANS;
    }}
  }}

  for(var i = 0; i < n; i++){{
    (function(idx){{
      var b = bodyEl(idx);
      if(!b) return;
      b.style.transition = TRANS;
      b.addEventListener("transitionend", function(e){{
        if(e.propertyName === "max-height" && b.getAttribute("data-open") === "1"){{
          b.style.maxHeight = "none";
        }}
      }});
      var initiallyOpen = b.getAttribute("data-open") === "1";
      setOpen(idx, initiallyOpen, false);
    }})(i);
  }}

  window[uid+"_toggle"] = function(idx){{
    var b = bodyEl(idx);
    if(!b) return;
    var isOpen = b.getAttribute("data-open") === "1";
    if(!multi){{
      for(var j = 0; j < n; j++) if(j !== idx) setOpen(j, false, true);
    }}
    setOpen(idx, !isOpen, true);
  }};
}})();</script>
"""

        return (
            f'<div id="{uid}" style="{wrapper_style}">'
            + items_html
            + f'</div>'
            + js
        )


# ══════════════════════════════════════════════════════════
# TESTIMONIALS
# ══════════════════════════════════════════════════════════

class TestimonialItem:
    """
    Testimonio individual.

        TestimonialItem(
            name="Ana García",
            role="CEO, Empresa X",
            avatar="/assets/ana.jpg",   # URL o None (usa iniciales)
            text="Increíble producto, cambió nuestra forma de trabajar.",
            rating=5,                   # 1-5, None = oculta estrellas
            company_logo="/assets/logo.svg",  # opcional
        )
    """
    def __init__(self, name, text, role=None, avatar=None,
                 rating=None, company_logo=None):
        self.name         = name
        self.text         = text
        self.role         = role
        self.avatar       = avatar
        self.rating       = rating
        self.company_logo = company_logo

class Testimonials(Widget):
    """
    Sección de testimonios. Puede mostrarse en cuadrícula o como carrusel.

    Uso:
        Testimonials(items=[
            TestimonialItem("Ana García", "Excelente producto.", role="CEO", rating=5),
            TestimonialItem("Luis Ruiz",  "Lo recomiendo mucho.", role="Dev", rating=4),
            TestimonialItem("Sara Paz",   "Cambió mi flujo de trabajo.", rating=5),
        ])

        # Como carrusel automático:
        Testimonials(items=[...], mode="carousel", autoplay=True)

    Parámetros:
        items        list[TestimonialItem]
        mode         str   "grid" | "carousel"  (default: "grid")
        columns      int   columnas en modo grid (default: 3)
        autoplay     bool  autoplay en carousel (default: True)
        interval     int   ms entre slides en carousel (default: 5000)
        card_radius  int   radio de las tarjetas
        show_quotes  bool  muestra comillas decorativas (default: True)
        accent       str   color de acento para estrellas y comillas
    """

    _id_counter = 0

    def __init__(self, items=None, mode="grid", columns=3,
                 autoplay=True, interval=5000,
                 card_radius=16, show_quotes=True,
                 accent="var(--accent)", **kwargs):
        self._props      = Widget._extract_props(kwargs)
        self.items       = items or []
        self.mode        = mode
        self.columns     = columns
        self.autoplay    = autoplay
        self.interval    = interval
        self.card_radius = card_radius
        self.show_quotes = show_quotes
        self.accent      = accent
        Testimonials._id_counter += 1
        self.uid = f"tsm_{Testimonials._id_counter}"

    def _render_card(self, item, uid_prefix=""):
        """Render a single testimonial card."""
        # Stars
        stars_html = ""
        if item.rating:
            stars = ""
            for i in range(5):
                color = self.accent if i < item.rating else "var(--border)"
                stars += f'<svg width="14" height="14" viewBox="0 0 14 14" fill="{color}"><path d="M7 1l1.5 3.5L12 5l-2.5 2.5.5 3.5L7 9.5 4 11l.5-3.5L2 5l3.5-.5z"/></svg>'
            stars_html = f'<div style="display:flex;gap:3px;margin-bottom:12px">{stars}</div>'

        # Avatar
        if item.avatar:
            avatar_html = (
                f'<img src="{item.avatar}" alt="{item.name}" '
                f'style="width:44px;height:44px;border-radius:50%;object-fit:cover;flex-shrink:0">'
            )
        else:
            initials = "".join(p[0].upper() for p in item.name.split()[:2])
            avatar_html = (
                f'<div style="width:44px;height:44px;border-radius:50%;'
                f'background:var(--accent);color:#fff;display:flex;align-items:center;'
                f'justify-content:center;font-weight:700;font-size:15px;flex-shrink:0">'
                f'{initials}</div>'
            )

        # Role
        role_html = (
            f'<span style="font-size:12px;color:var(--text-muted)">{item.role}</span>'
            if item.role else ""
        )

        # Company logo
        logo_html = (
            f'<img src="{item.company_logo}" alt="logo" '
            f'style="height:24px;object-fit:contain;opacity:0.6;margin-bottom:8px">'
            if item.company_logo else ""
        )

        # Quote decoration
        quote_html = ""
        if self.show_quotes:
            quote_html = (
                f'<div style="font-size:40px;line-height:1;color:{self.accent};'
                f'opacity:0.3;font-family:Georgia,serif;margin-bottom:4px">&ldquo;</div>'
            )

        return (
            f'<div style="background:var(--surface);border:1px solid var(--border);'
            f'border-radius:{self.card_radius}px;padding:24px;display:flex;'
            f'flex-direction:column;gap:0">'
            + logo_html
            + quote_html
            + stars_html
            + f'<p style="font-size:14px;color:var(--text);line-height:1.7;'
              f'flex:1;margin:0 0 16px">{item.text}</p>'
            + f'<div style="display:flex;align-items:center;gap:12px">'
            + avatar_html
            + f'<div><div style="font-size:14px;font-weight:600;color:var(--text)">{item.name}</div>'
            + role_html
            + f'</div></div>'
            + f'</div>'
        )

    def render(self):
        extra = self._resolve_props()
        uid   = self.uid

        if self.mode == "carousel":
            return self._render_carousel(extra)

        # Grid mode
        cols  = self.columns
        cols_css = f"repeat({cols}, 1fr)"
        grid_style = (
            f"display:grid;grid-template-columns:{cols_css};gap:20px;{extra}"
        )
        cards = "".join(self._render_card(item) for item in self.items)
        responsive = (
            f'<style>'
            f'@media(max-width:768px){{#{uid}{{grid-template-columns:repeat(2,1fr)!important;}}}}'
            f'@media(max-width:480px){{#{uid}{{grid-template-columns:1fr!important;}}}}'
            f'</style>'
        )
        return f'{responsive}<div id="{uid}" style="{grid_style}">{cards}</div>'

    def _render_carousel(self, extra):
        uid      = self.uid
        n        = len(self.items)
        interval = self.interval
        autoplay = self.autoplay

        slides = ""
        for i, item in enumerate(self.items):
            card = self._render_card(item, uid_prefix=uid)
            slides += (
                f'<div id="{uid}_s{i}" style="flex-shrink:0;width:100%;'
                f'padding:4px;box-sizing:border-box">{card}</div>'
            )

        # Dots
        dots_html = ""
        for i in range(n):
            dots_html += (
                f'<span id="{uid}_d{i}" onclick="{uid}_go({i})" '
                f'style="width:8px;height:8px;border-radius:50%;cursor:pointer;'
                f'background:{self.accent if i==0 else "var(--border)"};'
                f'transition:background .3s;display:inline-block"></span>'
            )

        js = (
            f'<script>(function(){{'
            f'  var uid="{uid}",n={n},cur=0,timer=null;'
            f'  function go(idx){{'
            f'    var track=document.getElementById(uid+"_track");'
            f'    if(!track)return;'
            f'    cur=((idx%n)+n)%n;'
            f'    track.style.transform="translateX(-"+cur*100+"%)";\n'
            f'    for(var i=0;i<n;i++){{'
            f'      var d=document.getElementById(uid+"_d"+i);'
            f'      if(d)d.style.background=i===cur?"{self.accent}":"var(--border)";'
            f'    }}'
            f'  }}'
            f'  window[uid+"_go"]=go;'
            f'  window[uid+"_prev"]=function(){{go(cur-1);}};'
            f'  window[uid+"_next"]=function(){{go(cur+1);}};'
            f'  {"timer=setInterval(function(){go(cur+1);},"+str(interval)+");" if autoplay else ""}'
            f'}})();</script>'
        )

        return (
            f'<div id="{uid}" style="position:relative;overflow:hidden;{extra}">'
            f'  <div id="{uid}_track" style="display:flex;transition:transform .45s cubic-bezier(.4,0,.2,1)">'
            + slides
            + f'  </div>'
            f'  <button onclick="{uid}_prev()" style="position:absolute;left:8px;top:50%;transform:translateY(-50%);'
            f'    background:var(--surface);border:1px solid var(--border);border-radius:50%;'
            f'    width:36px;height:36px;cursor:pointer;display:flex;align-items:center;'
            f'    justify-content:center;color:var(--text);font-size:18px;z-index:2">&#8249;</button>'
            f'  <button onclick="{uid}_next()" style="position:absolute;right:8px;top:50%;transform:translateY(-50%);'
            f'    background:var(--surface);border:1px solid var(--border);border-radius:50%;'
            f'    width:36px;height:36px;cursor:pointer;display:flex;align-items:center;'
            f'    justify-content:center;color:var(--text);font-size:18px;z-index:2">&#8250;</button>'
            f'  <div style="display:flex;justify-content:center;gap:8px;margin-top:16px;padding-bottom:8px">'
            + dots_html
            + f'  </div>'
            + f'</div>'
            + js
        )


# ══════════════════════════════════════════════════════════
# SLIDE CAROUSEL (general — acepta cualquier Widget)
# ══════════════════════════════════════════════════════════

class SlideItem:
    """
    Ítem del SlideCarousel general. Acepta cualquier Widget como contenido.

        SlideItem(child=Card([Heading("Hola"), Text("Mundo")]))
        SlideItem(child=Image("/assets/foto.jpg"))
        SlideItem(child=Column([...]))
    """
    def __init__(self, child):
        self.child = child

class SlideCarousel(Widget):
    """
    Carrusel general que acepta cualquier Widget como slide.
    Extensión del Carousel original para contenido arbitrario.

    Uso:
        SlideCarousel(items=[
            SlideItem(Card([Heading("Slide 1"), Text("Descripción")])),
            SlideItem(Column([Image("/assets/a.jpg"), Paragraph("Pie de foto")])),
            SlideItem(child=MyCustomWidget()),
        ])

        # Con múltiples slides visibles:
        SlideCarousel(items=[...], visible=3, gap=16)

    Parámetros:
        items        list[SlideItem | Widget]  slides (acepta también Widgets directos)
        visible      int    slides visibles a la vez (default: 1)
        gap          int    espacio entre slides en px (default: 0)
        loop         bool   bucle infinito (default: True)
        autoplay     bool   avance automático (default: False)
        interval     int    ms entre slides en autoplay (default: 4000)
        arrows       bool   flechas de navegación (default: True)
        dots         bool   indicadores de posición (default: True)
        arrow_style  str    "default" | "minimal" | "pill"
        transition   str    "slide" | "fade"
    """

    _id_counter = 0

    def __init__(self, items=None, visible=1, gap=0,
                 loop=True, autoplay=False, interval=4000,
                 arrows=True, dots=True,
                 arrow_style="default", transition="slide", **kwargs):
        self._props     = Widget._extract_props(kwargs)
        self.items      = items or []
        self.visible    = visible
        self.gap        = gap
        self.loop       = loop
        self.autoplay   = autoplay
        self.interval   = interval
        self.arrows     = arrows
        self.dots       = dots
        self.arrow_style = arrow_style
        self.transition  = transition
        SlideCarousel._id_counter += 1
        self.uid = f"sc_{SlideCarousel._id_counter}"

    def _resolve_item(self, item):
        """Convierte SlideItem o Widget directo a HTML."""
        if isinstance(item, SlideItem):
            child = item.child
            return child.render() if isinstance(child, Widget) else str(child)
        elif isinstance(item, Widget):
            return item.render()
        return str(item)

    def render(self):
        uid      = self.uid
        items    = self.items
        n        = len(items)
        visible  = self.visible
        gap      = self.gap
        loop     = self.loop
        autoplay = self.autoplay
        interval = self.interval
        extra    = self._resolve_props()
        radius   = self._props.get("radius", 0)
        r_css    = f"border-radius:{radius}px;" if radius else ""

        slide_width = f"calc((100% - {gap*(visible-1)}px) / {visible})"

        # Build slides
        slides_html = ""
        for i, item in enumerate(items):
            content = self._resolve_item(item)
            slides_html += (
                f'<div id="{uid}_s{i}" style="flex-shrink:0;width:{slide_width};'
                f'overflow:hidden;{r_css}box-sizing:border-box">'
                + content
                + f'</div>'
            )

        # Clones for infinite loop
        clones_after  = ""
        clones_before = ""
        if loop and n > 0:
            for i in range(min(visible, n)):
                content = self._resolve_item(items[i % n])
                clones_after += (
                    f'<div style="flex-shrink:0;width:{slide_width};overflow:hidden;{r_css}box-sizing:border-box">'
                    + content + '</div>'
                )
                content = self._resolve_item(items[(n - 1 - i) % n])
                clones_before = (
                    f'<div style="flex-shrink:0;width:{slide_width};overflow:hidden;{r_css}box-sizing:border-box">'
                    + content + '</div>'
                ) + clones_before

        positions  = max(n - visible + 1, 1)
        offset     = visible if loop else 0
        gap_css    = f"gap:{gap}px;" if gap else ""

        # Arrows
        arrow_css_base = (
            "position:absolute;top:50%;transform:translateY(-50%);z-index:5;"
            "cursor:pointer;border:none;display:flex;align-items:center;justify-content:center;"
            "transition:opacity .2s"
        )
        if self.arrow_style == "minimal":
            arrow_extra = "background:none;color:var(--text);font-size:28px;padding:4px;opacity:0.7"
        elif self.arrow_style == "pill":
            arrow_extra = ("background:var(--accent);color:#fff;border-radius:999px;"
                           "width:44px;height:44px;font-size:18px;box-shadow:0 4px 16px rgba(0,0,0,0.2)")
        else:
            arrow_extra = ("background:var(--surface);color:var(--text);"
                           "border:1px solid var(--border);border-radius:50%;"
                           "width:40px;height:40px;font-size:20px")

        prev_btn = (
            f'<button onclick="{uid}_prev()" style="{arrow_css_base};{arrow_extra};left:8px">'
            f'&#8249;</button>'
        ) if self.arrows else ""

        next_btn = (
            f'<button onclick="{uid}_next()" style="{arrow_css_base};{arrow_extra};right:8px">'
            f'&#8250;</button>'
        ) if self.arrows else ""

        # Dots
        dots_html = ""
        if self.dots:
            dot_items = ""
            for i in range(positions):
                is_first = (i == 0)
                dot_items += (
                    f'<span id="{uid}_dot{i}" onclick="{uid}_goPos({i})" '
                    f'style="width:{12 if is_first else 8}px;height:8px;border-radius:999px;cursor:pointer;'
                    f'background:{"var(--accent)" if is_first else "var(--border)"};'
                    f'transition:all .3s;display:inline-block"></span>'
                )
            dots_html = (
                f'<div id="{uid}_dots" style="display:flex;justify-content:center;'
                f'gap:6px;margin-top:12px">{dot_items}</div>'
            )

        # JS
        js = (
            f'<script>(function(){{'
            f'  var uid="{uid}",n={n},vis={visible},loop={str(loop).lower()},'
            f'      gap={gap},offset={offset},pos=0,positions={positions};'
            f'  var track=document.getElementById(uid+"_track");'
            f'  var animating=false;'
            f'  function slideWidth(){{'
            f'    var tw=track.parentElement.offsetWidth;'
            f'    return (tw-gap*(vis-1))/vis;'
            f'  }}'
            f'  function setPos(p,animate){{'
            f'    var sw=slideWidth();'
            f'    var x=(p+offset)*(sw+gap);'
            f'    if(animate===false)track.style.transition="none";'
            f'    else track.style.transition="transform .4s cubic-bezier(.4,0,.2,1)";'
            f'    track.style.transform="translateX(-"+x+"px)";'
            f'  }}'
            f'  function updateDots(p){{'
            f'    for(var i=0;i<positions;i++){{'
            f'      var d=document.getElementById(uid+"_dot"+i);'
            f'      if(d){{d.style.background=i===p?"var(--accent)":"var(--border)";'
            f'            d.style.width=i===p?"12px":"8px";}}'
            f'    }}'
            f'  }}'
            f'  function go(newPos){{'
            f'    if(animating)return;'
            f'    pos=((newPos%positions)+positions)%positions;'
            f'    setPos(pos,true);'
            f'    updateDots(pos);'
            f'    if(loop){{'
            f'      animating=true;'
            f'      setTimeout(function(){{'
            f'        if(newPos<0){{setPos(positions-1,false);pos=positions-1;}}'
            f'        else if(newPos>=positions){{setPos(0,false);pos=0;}}'
            f'        animating=false;'
            f'      }},420);'
            f'    }}'
            f'  }}'
            f'  window[uid+"_prev"]=function(){{go(pos-1);}};'
            f'  window[uid+"_next"]=function(){{go(pos+1);}};'
            f'  window[uid+"_goPos"]=function(p){{go(p);}};'
            f'  setPos(0,false);'
            f'  {"setInterval(function(){go(pos+1);},"+str(interval)+");" if autoplay else ""}'
            f'  window.addEventListener("resize",function(){{setPos(pos,false);}});'
            f'}})();</script>'
        )

        return (
            f'<div id="{uid}" style="position:relative;overflow:hidden;{extra}">'
            + prev_btn + next_btn
            + f'  <div id="{uid}_track" style="display:flex;{gap_css}will-change:transform">'
            + (clones_before if loop else "")
            + slides_html
            + (clones_after if loop else "")
            + f'  </div>'
            + f'</div>'
            + dots_html
            + js
        )


# ══════════════════════════════════════════════════════════
# PRICING
# ══════════════════════════════════════════════════════════

class PricingPlan:
    """
    Plan de precios individual.

        PricingPlan(
            name="Pro",
            price=29,
            currency="$",
            period="mes",
            description="Para equipos en crecimiento",
            features=["Feature A", "Feature B", "Feature C"],
            cta_label="Empezar gratis",
            cta_url="/signup",
            featured=True,          # resalta este plan
            badge="Más popular",    # etiqueta opcional
        )
    """
    def __init__(self, name, price, currency="$", period="mes",
                 description=None, features=None,
                 cta_label="Empezar", cta_url="#",
                 featured=False, badge=None,
                 cta_on_click=None,
                 price_yearly=None):   # precio anual opcional para toggle
        self.name         = name
        self.price        = price
        self.currency     = currency
        self.period       = period
        self.description  = description
        self.features     = features or []
        self.cta_label    = cta_label
        self.cta_url      = cta_url
        self.featured     = featured
        self.badge        = badge
        self.cta_on_click = cta_on_click
        self.price_yearly = price_yearly

class Pricing(Widget):
    """
    Sección de planes de precios.

    Uso:
        Pricing(plans=[
            PricingPlan("Gratis", 0, features=["5 proyectos", "1 GB"]),
            PricingPlan("Pro", 29, features=["Ilimitado", "10 GB", "Soporte"],
                        featured=True, badge="Más popular"),
            PricingPlan("Enterprise", 99, features=["Todo lo de Pro", "SLA", "SSO"]),
        ])

        # Con toggle mensual/anual:
        Pricing(plans=[...], toggle=True)

    Parámetros:
        plans        list[PricingPlan]
        columns      int    columnas (default: auto según número de planes)
        toggle       bool   muestra toggle mensual/anual (default: False)
        toggle_discount str  texto del descuento anual (default: "Ahorra 20%")
        accent       str    color de acento
        radius       int    radio de las tarjetas
        check_icon   str    icono SVG/HTML para los features (default: ✓ estilizado)
    """

    _id_counter = 0

    def __init__(self, plans=None, columns=None, toggle=False,
                 toggle_discount="Ahorra 20%",
                 accent="var(--accent)", **kwargs):
        self._props          = Widget._extract_props(kwargs)
        self.plans           = plans or []
        self.columns         = columns or len(plans or [1])
        self.toggle          = toggle
        self.toggle_discount = toggle_discount
        self.accent          = accent
        Pricing._id_counter += 1
        self.uid = f"prc_{Pricing._id_counter}"

    def _check_icon(self):
        return (
            f'<svg width="16" height="16" viewBox="0 0 16 16" fill="none" style="flex-shrink:0">'
            f'<circle cx="8" cy="8" r="7" fill="{self.accent}" opacity="0.15"/>'
            f'<path d="M5 8l2 2 4-4" stroke="{self.accent}" stroke-width="1.8" '
            f'stroke-linecap="round" stroke-linejoin="round"/></svg>'
        )

    def _discount_pct(self):
        import re

        m = re.search(r"(\d+(?:[.,]\d+)?)\s*%", str(self.toggle_discount or ""))
        if not m:
            return 20.0
        try:
            val = float(m.group(1).replace(",", "."))
        except Exception:
            return 20.0
        return max(0.0, min(90.0, val))

    @staticmethod
    def _fmt_price(value, currency):
        if isinstance(value, (int, float)):
            if float(value).is_integer():
                num = str(int(value))
            else:
                num = f"{value:.2f}".rstrip("0").rstrip(".")
            return f"{currency}{num}"
        return str(value)

    @staticmethod
    def _year_period(period):
        p = str(period or "").strip().lower()
        if p in {"mes", "meses"}:
            return "año"
        if p in {"month", "months", "mo", "monthly"}:
            return "year"
        return str(period or "")

    def _render_plan(self, plan, uid):
        radius   = self._props.get("radius", 16)
        featured = plan.featured

        card_style = (
            f"background:{'var(--accent)' if featured else 'var(--surface)'};"
            f"border:2px solid {'var(--accent)' if featured else 'var(--border)'};"
            f"border-radius:{radius}px;padding:32px 28px;"
            f"display:flex;flex-direction:column;gap:0;position:relative;"
            f"{'box-shadow:0 20px 60px rgba(99,102,241,0.3);transform:scale(1.03);' if featured else ''}"
        )

        text_color   = "#fff" if featured else "var(--text)"
        muted_color  = "rgba(255,255,255,0.75)" if featured else "var(--text-muted)"
        border_color = "rgba(255,255,255,0.2)" if featured else "var(--border)"

        badge_html = ""
        if plan.badge:
            badge_style = (
                f"position:absolute;top:-12px;left:50%;transform:translateX(-50%);"
                f"background:{'#fff' if featured else 'var(--accent)'};"
                f"color:{'var(--accent)' if featured else '#fff'};"
                f"font-size:11px;font-weight:700;padding:4px 14px;border-radius:999px;"
                f"white-space:nowrap;letter-spacing:.5px"
            )
            badge_html = f'<span style="{badge_style}">{plan.badge}</span>'

        desc_html = (
            f'<p style="font-size:13px;color:{muted_color};margin:8px 0 20px;line-height:1.5">'
            f'{plan.description}</p>'
        ) if plan.description else '<div style="margin-bottom:20px"></div>'

        # Price — with yearly data-attr for toggle
        price_val = plan.price
        price_yearly_val = plan.price_yearly
        if self.toggle and price_yearly_val is None and isinstance(price_val, (int, float)):
            factor = 1.0 - (self._discount_pct() / 100.0)
            auto_yearly = float(price_val) * 12.0 * factor
            price_yearly_val = int(auto_yearly) if auto_yearly.is_integer() else round(auto_yearly, 2)

        price_display = self._fmt_price(price_val, plan.currency)
        yearly_attr = (
            f' data-yearly="{self._fmt_price(price_yearly_val, plan.currency)}"'
            if price_yearly_val is not None
            else ""
        )
        monthly_attr = f' data-monthly="{price_display}"'
        period_month = str(plan.period)
        period_year = self._year_period(plan.period)
        period_attrs = f' data-period-monthly="/{period_month}" data-period-yearly="/{period_year}"'

        price_html = (
            f'<div style="margin-bottom:4px">'
            f'  <span id="{uid}_price_{id(plan)}" {monthly_attr}{yearly_attr} '
            f'    style="font-size:40px;font-weight:800;color:{text_color};line-height:1">'
            f'    {price_display}'
            f'  </span>'
            + (f'<span {period_attrs} style="font-size:14px;color:{muted_color};margin-left:4px">/{period_month}</span>'
               if isinstance(price_val, (int,float)) else "")
            + f'</div>'
        )

        # Features
        features_html = ""
        for feat in plan.features:
            feat_txt = feat.render() if isinstance(feat, Widget) else str(feat)
            features_html += (
                f'<div style="display:flex;align-items:flex-start;gap:10px;'
                f'padding:9px 0;border-bottom:1px solid {border_color}">'
                + self._check_icon()
                + f'<span style="font-size:14px;color:{text_color};line-height:1.5">{feat_txt}</span>'
                + f'</div>'
            )

        # CTA
        cta_style = (
            f"display:block;width:100%;margin-top:24px;padding:12px 20px;"
            # f"border-radius:{radius//2}px;font-size:15px;font-weight:600;"
            f"cursor:pointer;text-align:center;text-decoration:none;"
            f"transition:opacity .2s;box-sizing:border-box;"
            + (f"background:#fff;color:var(--accent);border:none;" if featured
               else f"background:var(--accent);color:#fff;border:none;")
        )
        click_attr = f' onclick="{plan.cta_on_click}"' if plan.cta_on_click else ""
        cta_html = (
            f'<a href="{plan.cta_url}" style="{cta_style}"{click_attr}>'
            f'{plan.cta_label}</a>'
        )

        return (
            f'<div style="{card_style}">'
            + badge_html
            + f'<div style="font-size:18px;font-weight:700;color:{text_color};margin-bottom:6px">{plan.name}</div>'
            + desc_html
            + price_html
            + f'<div style="flex:1">{features_html}</div>'
            + cta_html
            + f'</div>'
        )

    def render(self):
        uid   = self.uid
        extra = self._resolve_props()
        cols  = self.columns

        # Toggle
        toggle_html = ""
        if self.toggle:
            toggle_html = (
                f'<div style="display:flex;align-items:center;justify-content:center;'
                f'gap:12px;margin-bottom:32px">'
                f'  <span id="{uid}_lbl_m" style="font-size:14px;font-weight:600;color:var(--text)">Mensual</span>'
                f'  <div onclick="{uid}_toggleBilling()" id="{uid}_toggle_track" '
                f'    style="width:48px;height:26px;background:var(--border);border-radius:999px;'
                f'           cursor:pointer;position:relative;transition:background .25s">'
                f'    <div id="{uid}_toggle_thumb" '
                f'      style="position:absolute;top:3px;left:3px;width:20px;height:20px;'
                f'             background:#fff;border-radius:50%;transition:left .25s;'
                f'             box-shadow:0 1px 4px rgba(0,0,0,0.2)"></div>'
                f'  </div>'
                f'  <span id="{uid}_lbl_y" style="font-size:14px;color:var(--text-muted)">'
                f'    Anual <span style="font-size:11px;background:var(--accent);color:#fff;'
                f'      padding:2px 8px;border-radius:999px;margin-left:4px">{self.toggle_discount}</span>'
                f'  </span>'
                f'</div>'
                f'<script>(function(){{'
                f'  var uid="{uid}",yearly=false;'
                f'  window[uid+"_toggleBilling"]=function(){{'
                f'    yearly=!yearly;'
                f'    var track=document.getElementById(uid+"_toggle_track");'
                f'    var thumb=document.getElementById(uid+"_toggle_thumb");'
                f'    var lm=document.getElementById(uid+"_lbl_m");'
                f'    var ly=document.getElementById(uid+"_lbl_y");'
                f'    track.style.background=yearly?"var(--accent)":"var(--border)";'
                f'    thumb.style.left=yearly?"25px":"3px";'
                f'    lm.style.color=yearly?"var(--text-muted)":"var(--text)";'
                f'    ly.style.color=yearly?"var(--text)":"var(--text-muted)";'
                f'    var root=document.getElementById(uid+"_wrap")||document;'
                f'    root.querySelectorAll("[data-monthly]").forEach(function(el){{'
                f'      el.textContent=yearly?el.getAttribute("data-yearly")||el.getAttribute("data-monthly"):'
                f'                           el.getAttribute("data-monthly");'
                f'    }});'
                f'    root.querySelectorAll("[data-period-monthly]").forEach(function(el){{'
                f'      el.textContent=yearly?el.getAttribute("data-period-yearly")||el.getAttribute("data-period-monthly"):'
                f'                           el.getAttribute("data-period-monthly");'
                f'    }});'
                f'  }};'
                f'}})();</script>'
            )

        plans_html = "".join(self._render_plan(p, uid) for p in self.plans)

        grid_style = (
            f"display:grid;grid-template-columns:repeat({cols},1fr);"
            f"gap:20px;align-items:center;{extra}"
        )
        responsive = (
            f'<style>'
            f'@media(max-width:768px){{#{uid}_grid{{grid-template-columns:1fr!important;}}}}'
            f'</style>'
        )

        return (
            f'<div id="{uid}_wrap">'
            + responsive
            + toggle_html
            + f'<div id="{uid}_grid" style="{grid_style}">'
            + plans_html
            + f"</div></div>"
        )


# ══════════════════════════════════════════════════════════
# FAQ
# ══════════════════════════════════════════════════════════

class FAQItem:
    """
    Pregunta-respuesta para FAQ.

        FAQItem("¿Puedo cancelar en cualquier momento?",
                "Sí, puedes cancelar tu suscripción en cualquier momento sin penalización.")
        FAQItem("¿Hay prueba gratuita?",
                child=Column([Text("Sí, 14 días gratis."), Button("Probar ahora")]))
    """
    def __init__(self, question, answer=None, child=None, open=False):
        self.question = question
        self.answer   = answer
        self.child    = child
        self.open     = open

class FAQ(Widget):
    """
    Sección de preguntas frecuentes. Construida sobre Accordion.

    Uso:
        FAQ(items=[
            FAQItem("¿Qué es MARTIN?", "Un framework Python para construir webs."),
            FAQItem("¿Cómo instalo?", child=Code("pip install martin")),
        ])

        # Con buscador integrado:
        FAQ(items=[...], searchable=True)

        # Dos columnas:
        FAQ(items=[...], columns=2)

    Parámetros:
        items        list[FAQItem]
        searchable   bool   buscador de preguntas (default: False)
        columns      int    1 o 2 columnas (default: 1)
        variant      str    heredado de Accordion: "default"|"bordered"|"separated"
        multiple     bool   permite varios abiertos (default: False)
    """

    _id_counter = 0

    def __init__(self, items=None, searchable=False, columns=1,
                 variant="separated", multiple=False, **kwargs):
        self._props     = Widget._extract_props(kwargs)
        self.items      = items or []
        self.searchable = searchable
        self.columns    = columns
        self.variant    = variant
        self.multiple   = multiple
        FAQ._id_counter += 1
        self.uid = f"faq_{FAQ._id_counter}"

    def render(self):
        uid   = self.uid
        extra = self._resolve_props()

        # Build AccordionItems from FAQItems
        acc_items = [
            AccordionItem(
                title=item.question,
                content=item.answer,
                child=item.child,
                open=item.open,
            )
            for item in self.items
        ]

        search_html = ""
        if self.searchable:
            search_html = (
                f'<input type="text" placeholder="Buscar preguntas..." '
                f'id="{uid}_search" oninput="{uid}_search_fn(this.value)" '
                f'style="width:100%;padding:10px 16px;margin-bottom:20px;'
                f'border:1px solid var(--border-input);border-radius:999px;'
                f'background:var(--input-bg);color:var(--input-color);'
                f'font-size:14px;outline:none;box-sizing:border-box">'
            )

        if self.columns == 2:
            mid   = len(acc_items) // 2 + len(acc_items) % 2
            left  = acc_items[:mid]
            right = acc_items[mid:]
            acc_left  = Accordion(items=left,  variant=self.variant, multiple=self.multiple)
            acc_right = Accordion(items=right, variant=self.variant, multiple=self.multiple)
            accordion_html = (
                f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:16px">'
                + acc_left.render()
                + acc_right.render()
                + f'</div>'
            )
        else:
            acc = Accordion(items=acc_items, variant=self.variant, multiple=self.multiple)
            accordion_html = acc.render()

        search_js = ""
        if self.searchable:
            search_js = (
                f'<script>(function(){{'
                f'  window["{uid}_search_fn"]=function(q){{'
                f'    q=q.toLowerCase();'
                f'    document.querySelectorAll("#{uid}_content [id^=acc_]>div").forEach(function(item){{'
                f'      var btn=item.querySelector("button");'
                f'      if(!btn)return;'
                f'      var txt=btn.textContent.toLowerCase();'
                f'      item.style.display=txt.includes(q)?"block":"none";'
                f'    }});'
                f'  }};'
                f'}})();</script>'
            )

        return (
            f'<div id="{uid}" style="{extra}">'
            + search_html
            + f'<div id="{uid}_content">'
            + accordion_html
            + f'</div>'
            + f'</div>'
            + search_js
        )


# ══════════════════════════════════════════════════════════
# CHART — Gráficos interactivos con Chart.js
# ══════════════════════════════════════════════════════════

