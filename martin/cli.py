"""Martin CLI"""
import argparse, os, sys, textwrap
from pathlib import Path


# ══════════════════════════════════════════════════════════
# TEMPLATES
# ══════════════════════════════════════════════════════════

GITIGNORE = """
__pycache__/
*.py[cod]
.env
venv/
dist/
.DS_Store
"""

README = """
# {name}

Proyecto construido con Martin Framework.

## Inicio rapido

```bash
martin run
```

## Exportar

```bash
martin export
```
"""

MAIN_PY = """\
from martin import App, Router
from pages.home import home
from pages.about import about
from pages.components import components
from pages.api_example import api_example

router = Router()
router.add("/",            home,        title="Inicio")
router.add("/about",       about,       title="Acerca de")
router.add("/components",  components,  title="Componentes")
router.add("/api-example", api_example, title="Backend")

# Martin registra automaticamente los endpoints de cada pagina
# si el modulo tiene una funcion register_routes(app).
from martin import NavBar, Footer, Heading, Text, Link, Button, Row, TextStyle

# ── Navbar global ──────────────────────────────────────────────────────
# brand   → cualquier widget: Heading, Image, Row([Image, Heading]) etc.
#   Solo nombre:    brand=Heading("MiApp", level=3)
#   Solo logo:      brand=Image("/assets/logo.svg", height=32)
#   Logo + nombre:  brand=Row([Image("/assets/logo.svg", height=28),
#                              Heading("MiApp", level=4)], gap=8, align="center")
# links   → lista de Link, Button u otros widgets (centro)
# actions → botones/widgets a la derecha (login, CTA, ThemeToggle...)
# Desde una pagina: return widget, PageConfig(header=False)       # desactiva
#                   return widget, PageConfig(header=MiNavCustom()) # reemplaza
_nav = NavBar(
    brand=Heading("PROJECT_NAME", level=3, color="var(--text)"),
    # brand=Row([Image("/assets/logo.svg", height=28),
    #            Heading("PROJECT_NAME", level=4)], gap=8, align="center"),
    links=[
        Link("Inicio",      href="/",           style="color:var(--text);text-decoration:none;font-size:14px"),
        Link("Componentes", href="/components", style="color:var(--text-muted);text-decoration:none;font-size:14px"),
        Link("Acerca de",   href="/about",      style="color:var(--text-muted);text-decoration:none;font-size:14px"),
    ],
    actions=[
        # ThemeToggle(),          # boton dark/light
        Button("Comenzar", href="/components", radius=8),
    ],
)

_footer = Footer(
    left=Text("\u00a9 2025 PROJECT_NAME",
              style=TextStyle(size=13, color="var(--text-muted)")),
    right=Row([
        Link("Componentes", href="/components",
             style="font-size:13px;text-decoration:none;color:var(--text-muted)"),
        Link("Acerca de",   href="/about",
             style="font-size:13px;text-decoration:none;color:var(--text-muted)"),
    ], gap=16),
)

app = App(
    router=router,
    title="PROJECT_NAME",
    theme="auto",
    header=_nav,
    footer=_footer,
    # logo="logo.png",  # archivo en assets/ — reemplaza el auto-detectado
    # SEO global del sitio
    site_url="https://tu-dominio.com",
    description="Descripcion de tu sitio para buscadores.",
    keywords=["palabra1", "palabra2"],
    og_image="https://tu-dominio.com/og.png",
    twitter_handle="@tu_usuario",
    lang="es",
)


if __name__ == "__main__":
    app.run()
"""

PAGE_HOME = """\
from martin import (
    Column, Row, Grid, Section, Card, Spacer, Divider,
    Heading, Text, Paragraph, Button, Link, Icon, Badge,
    NavBar, Footer,
    Border, Shadow, TextStyle, Glass, GradientText, MeshBackground, Colors,
)


def home():
    from martin import PageConfig

    nav = NavBar(
        brand=Heading("PROJECT_NAME", level=3, color="var(--text)"),
        links=[
            Link("Inicio",      href="/",           style="color:var(--text);text-decoration:none;font-size:14px"),
            Link("Componentes", href="/components", style="color:var(--text-muted);text-decoration:none;font-size:14px"),
            Link("Acerca de",   href="/about",      style="color:var(--text-muted);text-decoration:none;font-size:14px"),
        ],
        actions=[Button("Comenzar", href="/components", radius=8)],
    )

    hero = Section(
        id="hero",
        style="text-align:center;align-items:center;display:flex;flex-direction:column;gap:24px;min-height:85vh;justify-content:center",
        children=[
            Badge("v0.2.0 \u2014 ahora disponible"),
            Heading(
                "PROJECT_NAME", level=1,
                style=[GradientText.aurora(), TextStyle(size=72, weight="800", letter_spacing=-3)],
            ),
            Paragraph(
                "PROJECT_DESC",
                style=TextStyle(size=20, color="var(--text-muted)", line_height=1.7),
                width=580,
            ),
            Row(gap=12, children=[
                Button("Empezar \u2192", href="/components",
                       background=Colors.indigo, color="#fff",
                       radius=10, padding=16,
                       style="font-size:15px;font-weight:700;border:none"),
                Button("Ver en GitHub", href="https://github.com",
                       variant="ghost", radius=10, padding=16,
                       style="font-size:15px"),
            ]),
        ],
    )

    features = Section(
        id="features",
        background="var(--surface)",
        style="display:flex;flex-direction:column;gap:48px;align-items:center",
        children=[
            Column(gap=8, style="text-align:center;align-items:center", children=[
                Heading("Todo es un widget", level=2,
                        style=TextStyle(size=36, weight="800")),
                Paragraph("Construye cualquier interfaz anidando widgets Python. Sin HTML, sin CSS manual.",
                          style=TextStyle(size=16, color="var(--text-muted)")),
            ]),
            Grid(
                columns="repeat(auto-fill, minmax(260px, 1fr))",
                gap=20, width="100%%",
                children=[_feature(icon, title, desc) for icon, title, desc in [
                    ("\U0001f9e9", "Widget tree",     "Compón interfaces anidando componentes Python, como Flutter."),
                    ("\U0001f3a8", "Estilos propios", "Glass(), GradientText(), Shadow()... sin escribir CSS."),
                    ("\u26a1",     "Hot reload",      "Guarda el fichero y el navegador se actualiza al instante."),
                    ("\U0001f5fa\ufe0f", "Multi-pagina", "Router declarativo. Cada pagina en su propio fichero."),
                    ("\U0001f4e6", "Zero deps",       "Solo stdlib de Python. Sin dependencias de terceros."),
                    ("\U0001f680", "Export estatico", "martin export \u2192 HTML/CSS/JS listo para cualquier hosting."),
                ]],
            ),
        ],
    )

    page = Column(
        style=MeshBackground.themed(),
        children=[hero, features],
    )
    return page, PageConfig(title="PROJECT_NAME", description="PROJECT_DESC")


def _feature(icon, title, desc):
    from martin import Card, Column, Heading, Text, Icon, TextStyle
    return Card(
        padding=24,
        children=[
            Column(gap=12, children=[
                Icon(icon, size=32),
                Heading(title, level=3, style=TextStyle(size=15, weight="700")),
                Text(desc, style=TextStyle(size=13, color="var(--text-muted)", line_height=1.6)),
            ])
        ]
    )
"""

PAGE_ABOUT = """\
from martin import (
    Column, Row, Divider, Heading, Text, Paragraph, Link, Icon,
    Border, Shadow, TextStyle, Glass, GradientText, MeshBackground, Colors,
)


def about():
    return Column(
        style=MeshBackground.themed(), padding=64, gap=48,
        children=[

            Column(gap=12, children=[
                Heading("Acerca de",
                        style=[GradientText.indigo_mint(),
                               TextStyle(size=48, weight="800")]),
                Paragraph(
                    "Martin es un framework Python para construir interfaces web "
                    "usando componentes, al estilo de Flutter.",
                    style=TextStyle(size=18, color="var(--text-muted)", line_height=1.7),
                ),
            ]),

            Divider(color="var(--border)"),

            Row(gap=16, style="flex-wrap:wrap", children=[
                _card("🎯", "Mision",
                      "Hacer el desarrollo web tan expresivo y placentero como Flutter."),
                _card("🔧", "Stack",
                      "Python puro · stdlib · Sin dependencias · watchdog opcional."),
                _card("📅", "Puerto",
                      "El puerto por defecto es 3908."),
            ]),

            Link("<- Volver al inicio", href="/",
                 style=TextStyle(size=14, color="var(--accent)")),
        ]
    )


def _card(icon, title, desc):
    from martin import Column, Heading, Text, Icon, Border, Shadow, TextStyle
    return Column(
        gap=16, padding=28,
        style=[
            "background:var(--surface); border:1px solid var(--border)",
            Border(radius=16),
            Shadow(y=4, blur=16, color="rgba(0,0,0,0.08)"),
            "flex:1; min-width:240px",
        ],
        children=[
            Icon(icon, size=28),
            Heading(title, level=3,
                    style=TextStyle(size=16, weight="700", color="var(--text)")),
            Text(desc, style=TextStyle(size=14, color="var(--text-muted)", line_height=1.6)),
        ]
    )
"""

PAGE_COMPONENTS = """\
from martin import (
    Container, Column, Row, Grid, Stack, Card, Section, Divider, Spacer,
    Heading, Text, Paragraph, Link, Code, Button, Icon, Badge, Alert,
    Image, Avatar, NavBar, Footer, Tabs, Breadcrumb,
    Table, Modal, TextField, Select, MultiSelect, Checkbox,
    WordCloud, Map, Timeline, TimelineItem, Hero,
    Gallery, GalleryItem, Carousel, CarouselItem,
    CookieBanner, CookieCategory,
    Border, Shadow, TextStyle, Glass, GradientText, MeshBackground, Colors,
)


def _section(title, subtitle, children):
    from martin import Column, Row, Text, Divider, TextStyle, Card
    return Card(
        padding=24,
        style="margin-bottom:0",
        children=[
            Column(gap=4, style="margin-bottom:16px", children=[
                Text(title.upper(),
                     style=TextStyle(size=11, weight="700", color="var(--text-muted)",
                                     letter_spacing=1)),
                Text(subtitle, style=TextStyle(size=13, color="var(--text-muted)")),
            ]),
            Column(gap=12, children=children),
        ],
    )


def components():
    from martin import PageConfig
    return Column(
        style=MeshBackground.themed(), padding=48, gap=24,
        children=[

            Heading("Componentes",
                    style=[GradientText.aurora(), TextStyle(size=48, weight="800")]),

            _section("Layout", "Row, Column, Grid, Card, Section — los bloques estructurales.", [
            Row([
                            Card(padding=20, children=[Column(gap=8, children=[
                                Text("Card 1", style=TextStyle(size=14, weight="700")),
                                Text("Contenido dentro de un Card.", style=TextStyle(size=12, color="var(--text-muted)")),
                            ])]),
                            Card(padding=20, children=[Column(gap=8, children=[
                                Text("Card 2", style=TextStyle(size=14, weight="700")),
                                Text("Cada Card usa var(--surface) y var(--border).", style=TextStyle(size=12, color="var(--text-muted)")),
                            ])]),
                            Card(padding=20, children=[Column(gap=8, children=[
                                Text("Card 3", style=TextStyle(size=14, weight="700")),
                                Text("Funciona en dark y light mode.", style=TextStyle(size=12, color="var(--text-muted)")),
                            ])]),
                        ], gap=16, wrap=True),
                        Grid(columns=3, gap=16, children=[
                            Container(padding=16, radius=8, background="var(--surface-2,var(--surface))",
                                      style="border:1px solid var(--border);text-align:center",
                                      children=[Text(f"Celda {i+1}",
                                                    style=TextStyle(size=13, color="var(--text-muted)"))
                                                for i in range(1)]) for _ in range(3)
                        ]),
            ]),

            _section("Texto", "Heading (h1-h6), Text, Paragraph, Link, Code.", [
            Heading("Heading nivel 1", level=1),
                        Heading("Heading nivel 2", level=2),
                        Heading("Heading nivel 3", level=3),
                        Paragraph("Paragraph para bloques de texto. Tiene line-height:1.6 por defecto. "
                                  "Ideal para descripciones, onboardings o contenido editorial.",
                                  style=TextStyle(size=15, color="var(--text-muted)")),
                        Row(gap=8, wrap=True, children=[
                            Text("Text normal"),
                            Text("Text muted",   color="var(--text-muted)"),
                            Text("Text accent",  color="var(--accent)"),
                            Text("Text bold",    style=TextStyle(weight="700")),
                            Text("Text small",   style=TextStyle(size=12)),
                            Code("inline code"),
                            Link("Un enlace", href="#"),
                        ]),
                        Code("def hola():\\n    return 42", block=True, language="python"),
            ]),

            _section("Badge & Alert", "Badge para etiquetas. Alert para mensajes de estado.", [
            Row(gap=8, wrap=True, children=[
                            Badge("Nuevo"),
                            Badge("Pro",     background=Colors.indigo),
                            Badge("Beta",    background="#f59e0b"),
                            Badge("Error",   background="#ef4444"),
                            Badge("v2.0",    background="var(--surface-2,var(--surface))",
                                             color="var(--text)", radius=4),
                        ]),
                        Column(gap=8, children=[
                            Alert("Operacion completada exitosamente.", variant="success", title="Listo"),
                            Alert("Revisa los datos antes de continuar.", variant="warning"),
                            Alert("El email ya esta en uso.", variant="error"),
                            Alert("Tienes 3 notificaciones nuevas.", variant="info"),
                        ]),
            ]),

            _section("Button", "Variantes, con enlace y con accion JS.", [
            Row(gap=8, wrap=True, children=[
                            Button("Primary"),
                            Button("Secondary", variant="secondary"),
                            Button("Danger",    variant="danger"),
                            Button("Ghost",     variant="ghost"),
                            Button("Link",      variant="link"),
                        ]),
                        Row(gap=8, wrap=True, children=[
                            Button("Con icono 🚀"),
                            Button("Enlace externo", href="https://example.com", variant="secondary"),
                            Button("Accion JS", on_click="alert('Hola desde Martin!')", variant="ghost"),
                            Button("Disabled", disabled=True),
                        ]),
            ]),

            _section("Inputs", "TextField, Select, MultiSelect, Checkbox.", [
            Grid(columns=2, gap=16, children=[
                            TextField(placeholder="Nombre completo"),
                            TextField(placeholder="Email", type="email"),
                            TextField(placeholder="Password", type="password"),
                            TextField(placeholder="Buscar...", radius=999),
                        ]),
                        Select(
                            options=[("es","Espanol"), ("en","English"), ("fr","Frances"),
                                     ("de","Aleman"), ("pt","Portugues")],
                            placeholder="Selecciona idioma",
                            search=True,
                        ),
                        MultiSelect(
                            options=["Python", "JavaScript", "Rust", "Go", "TypeScript", "Swift"],
                            placeholder="Lenguajes favoritos",
                        ),
                        Row(gap=16, wrap=True, children=[
                            Checkbox("Acepto los terminos"),
                            Checkbox("Recibir notificaciones", checked=True),
                            Checkbox("Modo avanzado"),
                        ]),
            ]),

            _section("Avatar & Image", "Avatares con imagen o iniciales. Imagenes con estilos.", [
            Row(gap=12, align="center", wrap=True, children=[
                            Avatar(initials="AB"),
                            Avatar(initials="CD", background=Colors.indigo, color="#fff"),
                            Avatar(initials="EF", background="#f59e0b", color="#fff", width=56, height=56),
                            Avatar(initials="GH", background="#ef4444", color="#fff"),
                            Avatar("/assets/icon.webp"),
                        ]),
                        Row(gap=16, wrap=True, children=[
                            Image("/assets/icon.webp"),
                            Image("/assets/icon.webp", radius=12, width=80, height=80),
                            Image("/assets/icon.webp", radius=999, width=80, height=80, shadow=True),
                        ]),
            ]),

            _section("NavBar & Footer", "Cabecera y pie de pagina totalmente declarativos.", [
                # brand puede ser Heading, Image (logo), Row([Image, Text]) etc.
                # links acepta Link, Button u otros widgets
                # actions va a la derecha: login, CTA, ThemeToggle...
                NavBar(
                    brand=Row([
                        Image("/assets/icon.webp", width=28, height=28, radius=6),
                        Text("MiApp", style=TextStyle(weight="800", size=17)),
                    ], gap=8, align="center"),
                    links=[
                        Link("Inicio",    href="/",        style="color:var(--text);text-decoration:none;font-size:14px;font-weight:500"),
                        Link("Productos", href="/productos",style="color:var(--text-muted);text-decoration:none;font-size:14px"),
                        Link("Blog",      href="/blog",    style="color:var(--text-muted);text-decoration:none;font-size:14px"),
                    ],
                    actions=[
                        Button("Login",    variant="ghost", radius=8),
                        Button("Registro", radius=8),
                    ],
                ),
                Spacer(16),
                Footer(
                    left=Text("\u00a9 2025 MiApp", style=TextStyle(size=13, color="var(--text-muted)")),
                    center=Row([
                        Link("Terminos",   href="/terminos",   style="font-size:13px;color:var(--text-muted);text-decoration:none"),
                        Link("Privacidad", href="/privacidad", style="font-size:13px;color:var(--text-muted);text-decoration:none"),
                    ], gap=16),
                    right=Row([
                        Button("Twitter", variant="ghost", padding=6, radius=6),
                        Button("GitHub",  variant="ghost", padding=6, radius=6),
                    ], gap=4),
                )
            ]),

            _section("Tabs", "Navegacion por pestanas con contenido diferente en cada una.", [
            Tabs([
                            ("General", Column(gap=12, padding=8, children=[
                                Heading("Configuracion general", level=4),
                                TextField(placeholder="Nombre de usuario"),
                                TextField(placeholder="Email"),
                                Button("Guardar cambios"),
                            ])),
                            ("Seguridad", Column(gap=12, padding=8, children=[
                                Heading("Seguridad", level=4),
                                TextField(placeholder="Contrasena actual", type="password"),
                                TextField(placeholder="Nueva contrasena", type="password"),
                                Button("Actualizar", variant="danger"),
                            ])),
                            ("Notificaciones", Column(gap=12, padding=8, children=[
                                Heading("Notificaciones", level=4),
                                Checkbox("Notificaciones por email", checked=True),
                                Checkbox("Notificaciones push"),
                                Checkbox("Resumen semanal", checked=True),
                            ])),
                        ]),
            ]),

            _section("Table", "Tabla interactiva: sort por columna, busqueda y paginacion.", [
            Table(
                            headers=["Nombre", "Ciudad", "Rol", "Estado", "Accion"],
                            rows=[
                                [Row([Avatar(initials="AG", background=Colors.indigo, color="#fff", width=28, height=28), Spacer(8), Text("Ana Garcia")],   align="center"), "Bogota",    Text("Admin"),  Badge("Activo",    background="#22c55e"),                               Button("Ver", variant="ghost", padding=4, radius=4)],
                                [Row([Avatar(initials="PL", background="#f59e0b",    color="#fff", width=28, height=28), Spacer(8), Text("Pedro Lopez")],  align="center"), "Medellin",  Text("Editor"), Badge("Inactivo",  background="var(--border)", color="var(--text-muted)"), Button("Ver", variant="ghost", padding=4, radius=4)],
                                [Row([Avatar(initials="MS", background="#ef4444",    color="#fff", width=28, height=28), Spacer(8), Text("Maria Silva")],  align="center"), "Cali",      Text("Viewer"), Badge("Activo",    background="#22c55e"),                               Button("Ver", variant="ghost", padding=4, radius=4)],
                                [Row([Avatar(initials="JR", background="#8b5cf6",    color="#fff", width=28, height=28), Spacer(8), Text("Juan Ramirez")], align="center"), "Cartagena", Text("Admin"),  Badge("Activo",    background="#22c55e"),                               Button("Ver", variant="ghost", padding=4, radius=4)],
                                [Row([Avatar(initials="LT", background="#ec4899",    color="#fff", width=28, height=28), Spacer(8), Text("Laura Torres")], align="center"), "Bogota",    Text("Editor"), Badge("Pendiente", background="#f59e0b"),                               Button("Ver", variant="ghost", padding=4, radius=4)],
                                [Row([Avatar(initials="CM", background="#14b8a6",    color="#fff", width=28, height=28), Spacer(8), Text("Carlos Mora")],  align="center"), "Cali",      Text("Viewer"), Badge("Inactivo",  background="var(--border)", color="var(--text-muted)"), Button("Ver", variant="ghost", padding=4, radius=4)],
                            ],
                            striped=True, searchable=True, sortable=True, page_size=4,
                        ),
            ]),

            _section("Modal", "Ventana modal. Usa openModal(id) para abrirla.", [
            Row(gap=8, children=[
                            Button("Abrir modal", on_click="openModal('demo_modal')"),
                            Button("Modal grande", on_click="openModal('big_modal')", variant="ghost"),
                        ]),
                        Modal(
                            id="demo_modal",
                            title="Confirmar accion",
                            children=[
                                Text("¿Estas seguro de que quieres continuar? Esta accion no se puede deshacer.",
                                     style=TextStyle(size=14, color="var(--text-muted)", line_height=1.6)),
                                Row([
                                    Button("Cancelar", variant="ghost", on_click="closeModal('demo_modal')"),
                                    Button("Confirmar", variant="danger", on_click="closeModal('demo_modal')"),
                                ], gap=8, justify="flex-end", style="margin-top:16px"),
                            ],
                        ),
                        Modal(
                            id="big_modal",
                            title="Formulario de contacto",
                            max_width=600,
                            children=[
                                Column(gap=12, children=[
                                    Grid(columns=2, gap=12, children=[
                                        TextField(placeholder="Nombre"),
                                        TextField(placeholder="Email", type="email"),
                                    ]),
                                    TextField(placeholder="Asunto"),
                                    TextField(placeholder="Mensaje"),
                                    Row([
                                        Button("Cancelar", variant="secondary", on_click="closeModal('big_modal')"),
                                        Button("Enviar mensaje"),
                                    ], gap=8, justify="flex-end"),
                                ]),
                            ],
                        ),
            ]),

            _section("Breadcrumb", "Ruta de navegacion.", [
            Breadcrumb([
                            ("Inicio",    "/"),
                            ("Productos", "/productos"),
                            ("Zapatillas", None),
                        ]),
            ]),

            _section("GradientText & Glass", "Estilos especiales de texto y fondo.", [
            Column(gap=12, children=[
                            Heading("Aurora gradient",
                                    style=[GradientText.aurora(), TextStyle(size=32, weight="800")]),
                            Heading("Indigo mint",
                                    style=[GradientText.indigo_mint(), TextStyle(size=32, weight="800")]),
                            Heading("Sunrise",
                                    style=[GradientText.rose_gold(), TextStyle(size=32, weight="800")]),
                        ]),
                        Row(gap=16, wrap=True, children=[
                            Column(
                                gap=8, padding=20,
                                style=[Glass.dark(blur=16, opacity=0.08),
                                       Border(radius=12), "width:180px;text-align:center"],
                                children=[Icon("🔮", size=32), Text("Glass dark", style=TextStyle(size=14, weight="600"))],
                            ),
                            Column(
                                gap=8, padding=20,
                                style=[Glass.light(blur=16, opacity=0.5),
                                       Border(radius=12), "width:180px;text-align:center"],
                                children=[Icon("✨", size=32), Text("Glass light", style=TextStyle(size=14, weight="600"))],
                            ),
                        ]),
            ]),

            _section("Timeline", "Linea de tiempo vertical.", [
            Timeline(items=[
                            TimelineItem(
                                title="Proyecto iniciado",
                                description="Se crea el repositorio y la estructura base del proyecto.",
                                date="Enero 2024", icon="🚀", color=Colors.indigo,
                            ),
                            TimelineItem(
                                title="Primera version",
                                description="Se publican los widgets basicos: Container, Row, Column, Button.",
                                date="Marzo 2024", icon="✅", color="#22c55e",
                            ),
                            TimelineItem(
                                title="Refactor v0.2",
                                description="Coherencia total de API. Nuevos widgets: NavBar, Footer, Tabs, Table, Modal.",
                                date="2025", icon="⚡", color="#f59e0b", tag="Actual",
                            ),
                        ]),
            ]),

            _section("Hero", "Banner principal de pagina.", [
            Hero(
                            badge=Badge("Ejemplo de Hero"),
                            title=Heading("Construye rapido.", level=2,
                                          style=[GradientText.aurora(), TextStyle(size=40, weight="800")]),
                            subtitle=Paragraph(
                                "Un Hero con imagen, layout split y fondo con mesh.",
                                style=TextStyle(size=15, color="var(--text-muted)"),
                            ),
                            actions=[
                                Button("Empezar", background=Colors.indigo, color="#fff", radius=10),
                                Button("Ver docs", variant="ghost", radius=10),
                            ],
                            image=Image("/assets/icon.webp", radius=16, width=200,
                                        style="box-shadow:0 24px 48px rgba(0,0,0,0.3)"),
                            background=MeshBackground.themed(),
                            layout="split", align="left", min_height=320,
                        ),
            ]),

            _section("Gallery", "Galeria de imagenes con lightbox.", [
            Gallery(
                            items=[
                                GalleryItem("/assets/icon.webp", title="Imagen 1", description="Descripcion de la imagen 1"),
                                GalleryItem("/assets/icon.webp", title="Imagen 2"),
                                GalleryItem("/assets/icon.webp", title="Imagen 3", span_cols=2),
                                GalleryItem("/assets/icon.webp", title="Imagen 4"),
                                GalleryItem("/assets/icon.webp", title="Imagen 5", description="Con enlace", url="https://example.com"),
                                GalleryItem("/assets/icon.webp", title="Imagen 6"),
                            ],
                            columns=3, gap=8, img_height=180, radius=8, lightbox=True,
                        ),
            ]),

            _section("Carousel - Slides", "Carrusel de tarjetas con flechas y dots.", [
            Carousel(
                            items=[
                                CarouselItem(image="/assets/icon.webp", title="Slide 1",
                                             subtitle="Descripcion del primer slide."),
                                CarouselItem(image="/assets/icon.webp", title="Slide 2",
                                             subtitle="Descripcion del segundo slide."),
                                CarouselItem(image="/assets/icon.webp", title="Slide 3",
                                             subtitle="Con link al hacer clic.", url="https://example.com"),
                                CarouselItem(image="/assets/icon.webp", title="Slide 4",
                                             subtitle="Ultimo slide."),
                            ],
                            mode="slides", visible=3, gap=16, loop=True, autoplay=3000,
                        ),
            ]),

            _section("Carousel - Brands", "Cinta infinita de logos.", [
            Carousel(
                            items=[
                                CarouselItem(image="/assets/icon.webp", title="Marca A", url="https://example.com"),
                                CarouselItem(image="/assets/icon.webp", title="Marca B"),
                                CarouselItem(image="/assets/icon.webp", title="Marca C", url="https://example.com"),
                                CarouselItem(image="/assets/icon.webp", title="Marca D"),
                                CarouselItem(image="/assets/icon.webp", title="Marca E"),
                            ],
                            mode="brands", brand_height=48, brand_gap=64, speed=25,
                            brand_filter="grayscale(100%) opacity(0.5)",
                        ),
            ]),

            _section("Map", "Mapa interactivo con marcadores.", [
            Map(
                            zoom=6,
                            height=400,
                            route=True,
                            markers=[
                                (-2.897, -79.004, "Cuenca",   "Patrimonio de la Humanidad", "#6366f1", "CUE"),
                                (-0.220, -78.512, "Quito",    "Capital del Ecuador",        "#f59e0b", "UIO"),
                                (-2.203, -79.890, "Guayaquil","Puerto principal",           "#22c55e", "GYE"),
                                (-1.012, -77.810, "Banos",    "Puerta al Oriente",          "#ef4444", "BNS"),
                                (-0.934, -78.615, "Riobamba", "Ciudad de las primicias",    "#8b5cf6", "RIO"),
                            ],
                        ),
            ]),

            _section("WordCloud", "Nube de palabras interactiva.", [
            WordCloud(
                            words={"Python":10,"Martin":9,"Web":8,"Widget":7,"CSS":6,
                                   "HTML":5,"JavaScript":5,"Framework":4,"API":4,"Router":3},
                            width=600, height=280,
                        ),
            ]),

            _section("CookieBanner", "Banner de cookies GDPR con persistencia.", [
            CookieBanner(
                            title="Este sitio usa cookies",
                            description="Usamos cookies propias y de terceros para mejorar tu experiencia.",
                            categories=[
                                CookieCategory("necessary", "Necesarias",
                                               "Imprescindibles para el funcionamiento.",
                                               default=True, required=True),
                                CookieCategory("analytics", "Analiticas",
                                               "Mejoran el sitio.", default=False),
                                CookieCategory("marketing", "Marketing",
                                               "Publicidad relevante.", default=False),
                            ],
                            position="bottom",
                            storage_key="martin_cookie_consent_demo",
                            privacy_url="/about",
                        ),
            ]),

        ]
    ), PageConfig(title="Componentes")
"""



# ══════════════════════════════════════════════════════════
# COMANDOS
# ══════════════════════════════════════════════════════════


def _write_api_example(path):
    """Escribe pages/api_example.py en el proyecto nuevo."""
    code = 'from martin import (\n    Column, Heading, Text, Paragraph, Button,\n    Select, MultiSelect, ResultBox, ApiCall,\n    Border, Shadow, TextStyle,\n    GradientText, MeshBackground,\n)\n\n\n# ── Endpoints de esta página ──────────────────────────────\n# Martin llama a register_routes(app) automáticamente\n# cuando esta página se añade al router.\n\ndef register_routes(app):\n\n    @app.route("/api/seleccion", methods=["POST"])\n    def api_seleccion(req):\n        data     = req.json()\n        lenguaje = data.get("lang_select", {})   # id del Select\n        areas    = data.get("areas_multi",  {})   # id del MultiSelect\n        return {\n            "ok": True,\n            "recibido": {\n                "lenguaje": lenguaje.get("etiqueta"),\n                "areas":    areas.get("etiquetas", []),\n            },\n            "mensaje": (\n                f"Lenguaje: {lenguaje.get(\'etiqueta\', \'?\')}. "\n                f"Areas: {\', \'.join(areas.get(\'etiquetas\', [])) or \'ninguna\'}."\n            ),\n        }\n\n\n# ── UI de la página ───────────────────────────────────────\n\ndef api_example():\n    return Column(\n        style=MeshBackground.themed(), padding=48, gap=32,\n        children=[\n\n            Column(gap=8, children=[\n                Heading(\n                    "Ejemplo de Backend",\n                    style=[GradientText.aurora(), TextStyle(size=40, weight="800")],\n                ),\n                Paragraph(\n                    "Selecciona valores y presiona el boton. "\n                    "El boton llama a una funcion Python en el servidor.",\n                    style=TextStyle(size=16, color="var(--text-muted)"),\n                ),\n            ]),\n\n            Column(\n                gap=20, padding=28,\n                style=[\n                    "background:var(--surface); border:1px solid var(--border)",\n                    Border(radius=16),\n                    Shadow(y=4, blur=20, color="rgba(0,0,0,0.1)"),\n                    "max-width:520px; width:100%",\n                ],\n                children=[\n\n                    Column(gap=6, children=[\n                        Text("Lenguaje",\n                             style=TextStyle(size=13, weight="600",\n                                             color="var(--text-muted)")),\n                        Select(\n                            id="lang_select",\n                            options=[\n                                ("py", "Python"),\n                                ("js", "JavaScript"),\n                                ("rs", "Rust"),\n                                ("go", "Go"),\n                                ("ts", "TypeScript"),\n                            ],\n                            value="py",\n                            search=True,\n                            radius=8,\n                        ),\n                    ]),\n\n                    Column(gap=6, children=[\n                        Text("Areas de trabajo",\n                             style=TextStyle(size=13, weight="600",\n                                             color="var(--text-muted)")),\n                        MultiSelect(\n                            id="areas_multi",\n                            options=["Diseno", "Frontend", "Backend",\n                                     "DevOps", "Testing", "Mobile"],\n                            values=["Frontend"],\n                            placeholder="Anadir area...",\n                            radius=8,\n                        ),\n                    ]),\n\n                    Button(\n                        "Enviar al servidor ->",\n                        id="send_btn",\n                        background="linear-gradient(135deg, #6366f1, #818cf8)",\n                        color="white",\n                        radius=10,\n                        style=(\n                            "border:none; font-size:15px; font-weight:700;"\n                            " padding:14px 24px;"\n                            " box-shadow:0 0 24px rgba(99,102,241,0.35);"\n                        ),\n                        on_click=ApiCall(\n                            "/api/seleccion",\n                            method="POST",\n                            target="resultado",\n                            loading="Enviando...",\n                        ),\n                    ),\n\n                    ResultBox(\n                        id="resultado",\n                        format="json",\n                    ),\n\n                ],\n            ),\n        ],\n    )\n'
    path.write_text(code, encoding="utf-8")

def _prompt(label, default=""):
    """Pregunta interactiva con valor por defecto."""
    hint = f" [{default}]" if default else ""
    try:
        val = input(f"  {label}{hint}: ").strip()
    except (EOFError, KeyboardInterrupt):
        print("")
        val = ""
    return val or default


def cmd_new(args):
    name   = args.name
    target = Path(name)

    if target.exists():
        print("ERROR: La carpeta '" + name + "' ya existe.")
        sys.exit(1)

    # ── Preguntas interactivas ─────────────────────────────
    print("")
    print("  Nuevo proyecto Martin · '" + name + "'")
    print("  " + "─" * 38)

    title = _prompt("Título del proyecto", default=name)
    desc  = _prompt("Descripción", default="Let's build an incredible idea")

    print("")

    # ── Crear estructura ───────────────────────────────────
    target.mkdir()
    (target / "assets").mkdir()

    # Copiar icono por defecto (el usuario puede reemplazarlo)
    _pkg_dir = Path(__file__).parent
    import shutil as _sh
    for _icon_name, _dest_name in [
        ("assets/default_icon.webp", "icon.webp"),
        ("assets/default_icon.png",  "icon.png"),
        ("default_icon.webp",        "icon.webp"),
        ("default_icon.png",         "icon.png"),
    ]:
        _src = _pkg_dir / _icon_name
        if _src.exists():
            _sh.copy(_src, target / "assets" / _dest_name)
            break
    (target / "pages").mkdir()
    (target / "pages" / "__init__.py").write_text("", encoding="utf-8")

    main_src = (MAIN_PY
                .replace("PROJECT_NAME", title)
                .replace("Descripcion de tu sitio para buscadores.", desc))

    (target / "main.py").write_text(main_src, encoding="utf-8")
    (target / "pages" / "home.py").write_text(
        PAGE_HOME.replace("PROJECT_NAME", title).replace("PROJECT_DESC", desc),
        encoding="utf-8")
    (target / "pages" / "about.py").write_text(
        PAGE_ABOUT.replace("PROJECT_NAME", title), encoding="utf-8")
    (target / "pages" / "components.py").write_text(
        PAGE_COMPONENTS.replace("PROJECT_NAME", title), encoding="utf-8")
    _write_api_example(target / "pages" / "api_example.py")
    (target / ".gitignore").write_text(GITIGNORE)
    (target / "README.md").write_text(
        README.replace("{name}", name), encoding="utf-8")

    print("  ✓  Proyecto '" + name + "' creado")
    print("")
    print("  Título      : " + title)
    print("  Descripción : " + desc)
    print("")
    print("  Estructura:")
    print("    " + name + "/")
    print("    |-- main.py")
    print("    |-- pages/")
    print("    |   |-- home.py")
    print("    |   |-- about.py")
    print("    |   +-- components.py")
    print("    +-- assets/")
    print("")
    print("  Siguiente:")
    print("    cd " + name)
    print("    martin run")
    print("")


def cmd_run(args):
    main_file = Path(args.file)
    if not main_file.exists():
        print("ERROR: No se encuentra '" + args.file + "'. Estas en la carpeta del proyecto?")
        sys.exit(1)

    cwd = str(Path.cwd())
    if cwd not in sys.path:
        sys.path.insert(0, cwd)

    import importlib.util
    source_file = str(main_file.resolve())
    spec = importlib.util.spec_from_file_location("_martin_main", source_file)
    mod  = importlib.util.module_from_spec(spec)
    sys.modules["_martin_main"] = mod
    spec.loader.exec_module(mod)

    from martin import App
    hot = not args.no_reload

    # Si main.py ya define un objeto `app` (App instance), usarlo directamente.
    # Esto preserva los @app.route() y cualquier config custom.
    if hasattr(mod, "app") and isinstance(mod.app, App):
        app = mod.app
        app.hot_reload = hot
        if args.port != 3908:          # solo sobreescribir si se pasó explícito
            app.port = args.port
    elif hasattr(mod, "router"):
        app = App(router=mod.router,
                  title=getattr(mod, "TITLE", Path.cwd().name),
                  port=args.port, hot_reload=hot)
    elif hasattr(mod, "build"):
        app = App(build=mod.build,
                  title=getattr(mod, "TITLE", Path.cwd().name),
                  port=args.port, hot_reload=hot)
    else:
        print("ERROR: main.py debe definir un objeto 'app', una funcion 'build()' o un 'router'.")
        sys.exit(1)

    app.run(watch_dir=cwd, source_file=source_file)


def cmd_export(args):
    main_file = Path(args.file)
    if not main_file.exists():
        print("ERROR: No se encuentra '" + args.file + "'.")
        sys.exit(1)

    cwd = str(Path.cwd())
    if cwd not in sys.path:
        sys.path.insert(0, cwd)

    import importlib.util
    spec = importlib.util.spec_from_file_location("_martin_main", str(main_file.resolve()))
    mod  = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    from martin import App
    fmt     = getattr(args, "format", "html")
    out_dir = getattr(args, "out", "dist")

    if hasattr(mod, "router"):
        app = App(router=mod.router,
                  title=getattr(mod, "TITLE", "Martin App"),
                  hot_reload=False)
    elif hasattr(mod, "build"):
        app = App(build=mod.build,
                  title=getattr(mod, "TITLE", "Martin App"),
                  hot_reload=False)
    else:
        print("ERROR: main.py debe tener 'build' o 'router'.")
        sys.exit(1)

    print("\n  Exportando (" + fmt + ") -> " + out_dir + "/\n")

    if fmt == "split":
        from martin.exporter import export_split
        export_split(app, out_dir=out_dir, assets_src="assets")
    else:
        from martin.exporter import export_html
        export_html(app, out_dir=out_dir)


def cmd_version(args):
    from martin import __version__
    print("martin " + __version__)


# ══════════════════════════════════════════════════════════
# ENTRY POINT
# ══════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        prog="martin",
        description="Martin — Python web framework",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
          Ejemplos:
            martin new mi_proyecto
            martin run
            martin run --port 8080
            martin run --no-reload
            martin export
            martin export --out build
            martin export --format html
            martin version
        """)
    )
    sub = parser.add_subparsers(dest="command", metavar="comando")

    p_new = sub.add_parser("new", help="Crea un nuevo proyecto")
    p_new.add_argument("name", help="Nombre del proyecto")

    p_run = sub.add_parser("run", help="Inicia el servidor de desarrollo")
    p_run.add_argument("--port",      type=int, default=3908,   help="Puerto (default: 309)")
    p_run.add_argument("--file",      default="main.py",       help="Fichero de entrada")
    p_run.add_argument("--no-reload", action="store_true",     help="Desactiva hot reload")

    p_exp = sub.add_parser("export", help="Exporta el proyecto")
    p_exp.add_argument("--file",   default="main.py",  help="Fichero de entrada")
    p_exp.add_argument("--out",    default="dist",     help="Carpeta de destino (default: dist)")
    p_exp.add_argument("--format", default="split",    choices=["html", "split"],
                       help="html = un fichero por pagina | split = HTML + CSS + JS separados")

    sub.add_parser("version", help="Muestra la version")

    args = parser.parse_args()

    commands = {
        "new":     cmd_new,
        "run":     cmd_run,
        "export":  cmd_export,
        "version": cmd_version,
    }

    cmd = commands.get(args.command)
    if cmd:
        cmd(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
