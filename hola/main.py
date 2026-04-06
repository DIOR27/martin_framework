from martin import (
    App, Router,
    NavBar, Footer, LanguageSelector,
    Heading, Text, Link, Row, Button, Raw,
    TextStyle,
    load_locale_catalogs,
)
from martin.backend import Backend
from pages.home import home
from pages.components import components, register_components_backend

router = Router()
router.add("/",           home,       title="Inicio")
router.add("/components", components, title="Componentes")

_MESSAGES = load_locale_catalogs("locales")
_LANGUAGE_SWITCHER = LanguageSelector(
    path="locales",
    value="es_ES",
    translations=_MESSAGES,
    width=240,
)

# ── Navbar global ──────────────────────────────────────────────────────
# brand   → cualquier widget: Heading, Image, Row([Image, Heading]) etc.
#   Solo nombre:    brand=Heading("MiApp", level=3)
#   Solo logo:      brand=Image("/assets/logo.svg", height=32)
#   Logo + nombre:  brand=Row([Image("/assets/logo.svg", height=28),
#                              Heading("MiApp", level=4)], gap=8, align="center")
# links   → lista de Link, Button u otros widgets (centro)
# actions → botones/widgets a la derecha (login, CTA, ThemeToggle...)
# Desde una pagina: return widget, PageConfig(header=False)         # desactiva
#                   return widget, PageConfig(header=MiNavCustom()) # reemplaza
_nav = NavBar(
    brand=Heading("hola", level=3, color="var(--text)", style="letter-spacing:-0.5px"),
    links=[
        Link(Raw('<span data-i18n="nav.home">Inicio</span>'), href="/", style="color:var(--text);text-decoration:none;font-size:14px"),
        Link(Raw('<span data-i18n="nav.components">Componentes</span>'), href="/components", style="color:var(--text-muted);text-decoration:none;font-size:14px"),
    ],
    actions=[
        _LANGUAGE_SWITCHER,
        Button(Raw('<span data-i18n="nav.start">Comenzar</span>'), href="/components", radius=8),
    ],
)

_footer = Footer(
    left=Raw('<span data-i18n="footer.rights" style="font-size:13px;color:var(--text-muted)">© 2026 hola</span>'),
    right=Row([
        Link(Raw('<span data-i18n="footer.components">Componentes</span>'), href="/components",
             style="font-size:13px;text-decoration:none;color:var(--text-muted)"),
    ], gap=16),
)

app = App(
    router=router,
    title="hola",
    theme="auto",
    header=_nav,
    footer=_footer,
    # logo="logo.png",  # archivo en assets/ — reemplaza el auto-detectado
    description="Let's build an incredible idea",
    lang="es-ES",
)

backend = Backend(prefix="/api")
register_components_backend(backend)
backend.mount(app)

if __name__ == "__main__":
    app.run()
