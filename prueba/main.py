from martin import (
    App, Router,
    NavBar, Footer,
    Heading, Text, Link, Row, Button,
    TextStyle,
)
from pages.home import home
from pages.components import components

router = Router()
router.add("/",           home,       title="Inicio")
router.add("/components", components, title="Componentes")

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
    brand=Heading("prueba", level=3, color="var(--text)", style="letter-spacing:-0.5px"),
    links=[
        Link("Inicio",       href="/",           style="color:var(--text);text-decoration:none;font-size:14px"),
        Link("Componentes",  href="/components", style="color:var(--text-muted);text-decoration:none;font-size:14px"),
    ],
    actions=[
        Button("Comenzar", href="/components", radius=8),
    ],
)

_footer = Footer(
    left=Text("© 2026 prueba", style=TextStyle(size=13, color="var(--text-muted)")),
    right=Row([
        Link("Componentes", href="/components",
             style="font-size:13px;text-decoration:none;color:var(--text-muted)"),
    ], gap=16),
)

app = App(
    router=router,
    title="prueba",
    theme="auto",
    header=_nav,
    footer=_footer,
    # logo="logo.png",  # archivo en assets/ — reemplaza el auto-detectado
    description="Let's build an incredible idea",
    lang="es",
)

if __name__ == "__main__":
    app.run()
