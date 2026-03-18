"""Scaffold templates para `martin new`."""

from datetime import datetime
from pathlib import Path
import shutil
import textwrap


DEFAULT_PROJECT_DESC = "Let's build an incredible idea"

ICON_CANDIDATES = [
    ("assets/default_icon.webp", "icon.webp"),
    ("assets/default_icon.png", "icon.png"),
    ("default_icon.webp", "icon.webp"),
    ("default_icon.png", "icon.png"),
]


GITIGNORE = (
    textwrap.dedent(
        """
    __pycache__/
    *.py[cod]
    .env
    venv/
    dist/
    .DS_Store
    """
    ).strip()
    + "\n"
)


README_TEMPLATE = (
    textwrap.dedent(
        """
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
    ).strip()
    + "\n"
)


MAIN_TEMPLATE = (
    textwrap.dedent(
        """
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
        brand=Heading("PROJECT_NAME", level=3, color="var(--text)", style="letter-spacing:-0.5px"),
        links=[
            Link("Inicio",       href="/",           style="color:var(--text);text-decoration:none;font-size:14px"),
            Link("Componentes",  href="/components", style="color:var(--text-muted);text-decoration:none;font-size:14px"),
        ],
        actions=[
            Button("Comenzar", href="/components", radius=8),
        ],
    )

    _footer = Footer(
        left=Text("© YEAR PROJECT_NAME", style=TextStyle(size=13, color="var(--text-muted)")),
        right=Row([
            Link("Componentes", href="/components",
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
        description="PROJECT_DESC",
        lang="es",
    )

    if __name__ == "__main__":
        app.run()
    """
    ).strip()
    + "\n"
)


HOME_TEMPLATE = (
    textwrap.dedent(
        """
    from martin import (
        Column,
        Row,
        Grid,
        Card,
        Heading,
        Paragraph,
        Text,
        Button,
        Code,
        Divider,
        Raw,
        PageConfig,
    )


    _HERO_CSS = Raw(\"\"\"<style>
    .hero-gradient {
        background: linear-gradient(135deg, var(--accent) 0%, color-mix(in srgb, var(--accent) 60%, transparent) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .feature-card { transition: transform .2s, box-shadow .2s; }
    .feature-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 32px rgba(0,0,0,.12);
    }
    </style>\"\"\")


    _FEATURES = [
        ("\\u26a1", "R\\u00e1pido",     "Servidor de desarrollo con hot-reload. Exporta HTML est\\u00e1tico listo para producci\\u00f3n."),
        ("\\U0001f9e9", "Composable",   "Construye interfaces complejas con widgets simples y reutilizables."),
        ("\\U0001f3a8", "Elegante",     "Tema oscuro/claro autom\\u00e1tico. CSS moderno listo para usar desde el primer momento."),
        ("\\U0001f40d", "Solo Python",  "Sin HTML, sin CSS, sin JavaScript. Todo se expresa en Python puro."),
    ]


    def home():
        features = [
            Card(
                class_name="feature-card",
                padding=24,
                radius=14,
                children=[
                    Row([
                        Text(icon, style="font-size:26px"),
                        Heading(title, level=3, style="font-size:16px;margin:0"),
                    ], gap=10, align="center"),
                    Paragraph(desc, style="font-size:14px;color:var(--text-muted);margin-top:8px;line-height:1.6"),
                ],
            )
            for icon, title, desc in _FEATURES
        ]

        return Column(
            gap=0,
            children=[
                _HERO_CSS,

                # ── Hero ──────────────────────────────────────────────────
                Column(
                    gap=20,
                    padding=64,
                    style="max-width:860px;margin:0 auto;align-items:center;text-align:center;padding-top:96px;padding-bottom:80px",
                    children=[
                        Row([
                            Text(
                                "PROJECT_NAME",
                                style=(
                                    "font-size:13px;font-weight:600;letter-spacing:.08em;"
                                    "text-transform:uppercase;color:var(--accent);"
                                    "background:color-mix(in srgb,var(--accent) 12%,transparent);"
                                    "padding:4px 12px;border-radius:999px;"
                                    "border:1px solid color-mix(in srgb,var(--accent) 30%,transparent)"
                                ),
                            ),
                        ], justify="center"),
                        Heading(
                            "PROJECT_DESC",
                            level=1,
                            class_name="hero-gradient",
                            style="font-size:clamp(36px,6vw,64px);font-weight:800;letter-spacing:-2px;line-height:1.1;margin:0",
                        ),
                        Paragraph(
                            "Construido con Martin Framework \\u2014 Python para la web, sin complicaciones.",
                            style="font-size:18px;color:var(--text-muted);max-width:560px;line-height:1.6;margin:0",
                        ),
                        Row(
                            gap=12,
                            justify="center",
                            style="margin-top:8px",
                            children=[
                                Button("Ver componentes", href="/components", style="padding:11px 24px;font-size:15px"),
                                Button("GitHub", href="https://github.com", variant="ghost", style="padding:11px 24px;font-size:15px"),
                            ],
                        ),
                    ],
                ),

                # ── Features ──────────────────────────────────────────────
                Column(
                    padding=48,
                    gap=28,
                    style="max-width:1100px;margin:0 auto;padding-top:0",
                    children=[
                        Divider(),
                        Heading("\\u00bfPor qu\\u00e9 Martin?", level=2, style="font-size:26px;font-weight:700;text-align:center"),
                        Grid(columns=2, gap=16, children=features),
                    ],
                ),

                # ── Quick start ────────────────────────────────────────────
                Column(
                    padding=48,
                    gap=20,
                    style="max-width:760px;margin:0 auto",
                    children=[
                        Divider(),
                        Heading("Inicio r\\u00e1pido", level=2, style="font-size:26px;font-weight:700"),
                        Code(
                            "martin new mi_proyecto\\ncd mi_proyecto\\nmartin run",
                            language="bash",
                            block=True,
                        ),
                        Paragraph(
                            "Tu aplicaci\\u00f3n estar\\u00e1 disponible en http://localhost:3908",
                            style="font-size:14px;color:var(--text-muted)",
                        ),
                    ],
                ),
            ],
        ), PageConfig(title="Inicio \\u2014 PROJECT_NAME", description="PROJECT_DESC")
    """
    ).strip()
    + "\n"
)


COMPONENTS_TEMPLATE = (
    textwrap.dedent(
        """
    from martin import (
        Container, Column, Row, Grid, Card, Section, Divider, Spacer,
        Heading, Text, Paragraph, Link, Code, Button, Icon, Badge, Alert,
        Image, Avatar, IconPack, NavBar, Footer, Tabs, Breadcrumb,
        Table, Modal, TextField, TextArea, Select, MultiSelect, Checkbox,
        Slider, ColorPicker, DatePicker,
        WordCloud, Map, Timeline, TimelineItem, Hero,
        Gallery, GalleryItem, Carousel, CarouselItem,
        Border, Shadow, TextStyle, Glass, GradientText, MeshBackground, Colors,
        SideMenu, Raw,
        PageConfig,
    )
    from martin.fx import (
        FadeIn, SlideIn, ScaleIn, Pulse, Spin, Transition,
        HoverLift, HoverGlow, Stagger, ReducedMotion, RevealOnScroll,
    )
    from martin.widgets import __all__ as MARTIN_WIDGETS


    def _slug(name: str) -> str:
        return name.lower().replace("_", "-")


    def _sec(title, subtitle, children, widget_name=None):
        anchor_id = f"widget-{_slug(widget_name or title)}"
        return Card(
            id=anchor_id,
            padding=24,
            style="scroll-margin-top:88px",
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


    def _sections():
        all_w = set(MARTIN_WIDGETS)

        secs = []

        # ── Layout ────────────────────────────────────────────────────────
        if "Card" in all_w:
            secs.append(_sec("Layout", "Row, Column, Grid, Card, Section — los bloques estructurales.", [
                Row([
                    Card(padding=20, children=[Column(gap=8, children=[
                        Text("Card 1", style=TextStyle(size=14, weight="700")),
                        Text("Contenido dentro de un Card.", style=TextStyle(size=12, color="var(--text-muted)")),
                    ])]),
                    Card(padding=20, children=[Column(gap=8, children=[
                        Text("Card 2", style=TextStyle(size=14, weight="700")),
                        Text("Usa var(--surface) y var(--border).", style=TextStyle(size=12, color="var(--text-muted)")),
                    ])]),
                    Card(padding=20, children=[Column(gap=8, children=[
                        Text("Card 3", style=TextStyle(size=14, weight="700")),
                        Text("Funciona en dark y light mode.", style=TextStyle(size=12, color="var(--text-muted)")),
                    ])]),
                ], gap=16, wrap=True),
                Grid(columns=3, gap=16, children=[
                    Container(padding=16, radius=8,
                              background="var(--surface-2,var(--surface))",
                              style="border:1px solid var(--border);text-align:center",
                              children=[Text(f"Celda {i+1}", style=TextStyle(size=13, color="var(--text-muted)"))],
                              ) for i in range(3)
                ]),
            ], widget_name="Layout"))

        # ── Texto ─────────────────────────────────────────────────────────
        if "Heading" in all_w:
            secs.append(_sec("Texto", "Heading (h1-h6), Text, Paragraph, Link, Code.", [
                Heading("Heading nivel 1", level=1),
                Heading("Heading nivel 2", level=2),
                Heading("Heading nivel 3", level=3),
                Paragraph("Paragraph para bloques de texto. Tiene line-height:1.6 por defecto. "
                           "Ideal para descripciones, onboardings o contenido editorial.",
                           style=TextStyle(size=15, color="var(--text-muted)")),
                Row(gap=8, wrap=True, children=[
                    Text("Text normal"),
                    Text("Text muted",  color="var(--text-muted)"),
                    Text("Text accent", color="var(--accent)"),
                    Text("Text bold",   style=TextStyle(weight="700")),
                    Text("Text small",  style=TextStyle(size=12)),
                    Code("inline code"),
                    Link("Un enlace", href="#"),
                ]),
                Code('def hola():\\n    return 42', block=True, language="python"),
            ], widget_name="Texto"))

        # ── Code ──────────────────────────────────────────────────────────
        if "Code" in all_w:
            secs.append(_sec("Code", "Syntax highlighting, bot\\u00f3n copiar, numeraci\\u00f3n, modo editable.", [
                Column(gap=20, children=[
                    Code("from martin import App, Router, Column, Heading\\n\\nrouter = Router()\\nrouter.add('/', lambda: Column([Heading('Hola')]))\\nApp(router=router).run()",
                         language="python", filename="main.py", copy=True),
                    Code('[\\n  { "id": 1, "nombre": "Ana", "rol": "Admin" },\\n  { "id": 2, "nombre": "Pedro", "rol": "Editor" }\\n]',
                         language="json", line_numbers=True, copy=True, filename="data.json"),
                    Code("pip install martin\\nmartin new mi_proyecto\\ncd mi_proyecto\\nmartin run",
                         language="bash", copy=True),
                ]),
            ], widget_name="Code"))

        # ── Badge & Alert ─────────────────────────────────────────────────
        if "Badge" in all_w:
            secs.append(_sec("Badge & Alert", "Badge para etiquetas. Alert para mensajes de estado.", [
                Row(gap=8, wrap=True, children=[
                    Badge("Nuevo"),
                    Badge("Pro",     background=Colors.indigo),
                    Badge("Beta",    background="#f59e0b"),
                    Badge("Error",   background="#ef4444"),
                    Badge("v2.0",    background="var(--surface-2,var(--surface))",
                                     color="var(--text)", radius=4),
                ]),
                Column(gap=8, children=[
                    Alert("Operaci\\u00f3n completada exitosamente.", variant="success", title="Listo"),
                    Alert("Revisa los datos antes de continuar.", variant="warning"),
                    Alert("El email ya est\\u00e1 en uso.", variant="error"),
                    Alert("Tienes 3 notificaciones nuevas.", variant="info"),
                ]),
            ], widget_name="Badge"))

        # ── Button ────────────────────────────────────────────────────────
        if "Button" in all_w:
            secs.append(_sec("Button", "Variantes, con enlace y con acci\\u00f3n JS.", [
                Row(gap=8, wrap=True, children=[
                    Button("Primary"),
                    Button("Secondary", variant="secondary"),
                    Button("Danger",    variant="danger"),
                    Button("Ghost",     variant="ghost"),
                    Button("Link",      variant="link"),
                ]),
                Row(gap=8, wrap=True, children=[
                    Button("Con icono \\U0001f680"),
                    Button("Enlace externo", href="https://example.com", variant="secondary"),
                    Button("Acci\\u00f3n JS", on_click="alert('Hola desde Martin!')", variant="ghost"),
                    Button("Disabled", disabled=True),
                ]),
            ], widget_name="Button"))

        # ── Inputs ────────────────────────────────────────────────────────
        if "TextField" in all_w:
            secs.append(_sec("Inputs", "TextField, TextArea, Select, MultiSelect, Checkbox.", [
                Column(gap=16, children=[
                    Grid(columns=2, gap=16, children=[
                        TextField(placeholder="Nombre completo"),
                        TextField(placeholder="Email", type="email"),
                        TextField(placeholder="Password", type="password"),
                        TextField(placeholder="Buscar...", radius=999),
                    ]),
                    TextArea(placeholder="Escribe tu mensaje...", rows=3, max_length=280),
                    Select(
                        options=[("es","Espa\\u00f1ol"), ("en","English"), ("fr","Franc\\u00e9s"),
                                 ("de","Alem\\u00e1n"), ("pt","Portugu\\u00e9s")],
                        placeholder="Selecciona idioma",
                        search=True,
                    ),
                    MultiSelect(
                        options=["Python", "JavaScript", "Rust", "Go", "TypeScript", "Swift"],
                        placeholder="Lenguajes favoritos",
                    ),
                    Row(gap=16, wrap=True, children=[
                        Checkbox("Acepto los t\\u00e9rminos"),
                        Checkbox("Recibir notificaciones", checked=True),
                        Checkbox("Modo avanzado"),
                    ]),
                ]),
            ], widget_name="TextField"))

        # ── Slider ────────────────────────────────────────────────────────
        if "Slider" in all_w:
            secs.append(_sec("Slider", "Control deslizante simple o de rango doble.", [
                Column(gap=24, children=[
                    Slider(label="Volumen", min=0, max=100, value=70, format="{v}%"),
                    Slider(label="Temperatura", min=16, max=30, value=22, step=1,
                           format="{v}\\u00b0C", show_ticks=True, color="#f59e0b"),
                    Slider(
                        label="Rango de precio",
                        min=0, max=1000, value=150, value_max=600,
                        range=True, format="${v}", step=10, color=Colors.indigo,
                    ),
                ]),
            ], widget_name="Slider"))

        # ── ColorPicker ───────────────────────────────────────────────────
        if "ColorPicker" in all_w:
            secs.append(_sec("ColorPicker", "Selector de color con swatch, hex editable y presets.", [
                Row(gap=32, wrap=True, children=[
                    ColorPicker(
                        label="Color de marca",
                        value="#6366f1",
                        presets=["#6366f1","#f59e0b","#ef4444","#22c55e","#0ea5e9","#8b5cf6","#ec4899"],
                    ),
                    ColorPicker(
                        label="Color de fondo",
                        value="#1e293b",
                        show_hex=True,
                    ),
                ]),
            ], widget_name="ColorPicker"))

        # ── DatePicker ────────────────────────────────────────────────────
        if "DatePicker" in all_w:
            secs.append(_sec("DatePicker", "Selector de fecha simple o rango al estilo reservas de hotel/vuelo.", [
                Column(gap=24, children=[
                    DatePicker(label="Fecha de nacimiento", value="2000-01-15"),
                    DatePicker(
                        label="Fechas de estancia",
                        range=True,
                        value="2026-06-10",
                        value_end="2026-06-17",
                        label_start="Check-in",
                        label_end="Check-out",
                        min_date="2026-01-01",
                    ),
                    DatePicker(
                        label="Vuelo de ida y vuelta",
                        range=True,
                        label_start="Ida",
                        label_end="Vuelta",
                        placeholder_start="\\u00bfCu\\u00e1ndo sales?",
                        placeholder_end="\\u00bfCu\\u00e1ndo vuelves?",
                    ),
                ]),
            ], widget_name="DatePicker"))

        # ── Avatar & Image ────────────────────────────────────────────────
        if "Avatar" in all_w:
            secs.append(_sec("Avatar & Image", "Avatares con imagen o iniciales. Im\\u00e1genes con estilos.", [
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
            ], widget_name="Avatar"))

        # ── Icons ─────────────────────────────────────────────────────────
        if "Icon" in all_w and "IconPack" in all_w:
            secs.append(_sec("Icons", "Soporte para Font Awesome y cualquier libreria de iconos basada en clases CSS.", [
                IconPack([
                    "fontawesome",
                    "bootstrap-icons",
                    "material-symbols",
                    "https://cdn.jsdelivr.net/npm/remixicon@4.2.0/fonts/remixicon.css",
                ]),
                Row(gap=16, wrap=True, children=[
                    Card(
                        padding=18,
                        radius=14,
                        style="min-width:170px",
                        children=[
                            Row(gap=10, align="center", children=[
                                Icon(name="house", provider="fa", variant="solid", size=22, color=Colors.indigo),
                                Text("Font Awesome", style=TextStyle(size=14, weight="700")),
                            ]),
                            Paragraph(
                                "Usa `provider='fa'` y variantes como `solid`, `regular` o `brands`.",
                                style=TextStyle(size=13, color="var(--text-muted)", line_height=1.6),
                            ),
                        ],
                    ),
                    Card(
                        padding=18,
                        radius=14,
                        style="min-width:170px",
                        children=[
                            Row(gap=10, align="center", children=[
                                Icon(name="airplane", provider="bi", size=22, color="#38bdf8"),
                                Text("Bootstrap Icons", style=TextStyle(size=14, weight="700")),
                            ]),
                            Paragraph(
                                "Tambien funciona con `provider='bi'` para iconos ligeros basados en clases.",
                                style=TextStyle(size=13, color="var(--text-muted)", line_height=1.6),
                            ),
                        ],
                    ),
                    Card(
                        padding=18,
                        radius=14,
                        style="min-width:170px",
                        children=[
                            Row(gap=10, align="center", children=[
                                Icon(name="flight_takeoff", provider="material-symbols", variant="rounded", size=24, color="#22c55e"),
                                Text("Material Symbols", style=TextStyle(size=14, weight="700")),
                            ]),
                            Paragraph(
                                "Para Google Symbols usa `provider='material-symbols'` y variantes como `rounded`.",
                                style=TextStyle(size=13, color="var(--text-muted)", line_height=1.6),
                            ),
                        ],
                    ),
                    Card(
                        padding=18,
                        radius=14,
                        style="min-width:170px",
                        children=[
                            Row(gap=10, align="center", children=[
                                Icon(name="home-line", provider="ri", size=24, color="#f59e0b"),
                                Text("Custom CSS Library", style=TextStyle(size=14, weight="700")),
                            ]),
                            Paragraph(
                                "Tambien puedes cargar cualquier CSS externa y usar prefijos genericos o `icon_class`.",
                                style=TextStyle(size=13, color="var(--text-muted)", line_height=1.6),
                            ),
                        ],
                    ),
                ]),
                Code(
                    "from martin import Row, IconPack, Icon\\n\\n"
                    "Row(children=[\\n"
                    "    IconPack([\\n"
                    "        \\\"fontawesome\\\",\\n"
                    "        \\\"https://cdn.jsdelivr.net/npm/remixicon@4.2.0/fonts/remixicon.css\\\",\\n"
                    "    ]),\\n"
                    "    Icon(name=\\\"house\\\", provider=\\\"fa\\\", variant=\\\"solid\\\"),\\n"
                    "    Icon(name=\\\"airplane\\\", provider=\\\"bi\\\"),\\n"
                    "    Icon(name=\\\"home-line\\\", provider=\\\"ri\\\"),\\n"
                    "    Icon(icon_class=\\\"mdi mdi-calendar\\\"),\\n"
                    "])",
                    block=True,
                    language="python",
                    filename="icons_demo.py",
                    copy=True,
                ),
            ], widget_name="Icons"))

        # ── Tabs ──────────────────────────────────────────────────────────
        if "Tabs" in all_w:
            secs.append(_sec("Tabs", "Navegaci\\u00f3n por pesta\\u00f1as con contenido diferente en cada una.", [
                Tabs([
                    ("General", Column(gap=12, padding=8, children=[
                        Heading("Configuraci\\u00f3n general", level=4),
                        TextField(placeholder="Nombre de usuario"),
                        TextField(placeholder="Email"),
                        Button("Guardar cambios"),
                    ])),
                    ("Seguridad", Column(gap=12, padding=8, children=[
                        Heading("Seguridad", level=4),
                        TextField(placeholder="Contrase\\u00f1a actual", type="password"),
                        TextField(placeholder="Nueva contrase\\u00f1a",  type="password"),
                        Button("Actualizar", variant="danger"),
                    ])),
                    ("Notificaciones", Column(gap=12, padding=8, children=[
                        Heading("Notificaciones", level=4),
                        Checkbox("Notificaciones por email", checked=True),
                        Checkbox("Notificaciones push"),
                        Checkbox("Resumen semanal", checked=True),
                    ])),
                ]),
            ], widget_name="Tabs"))

        # ── Table ─────────────────────────────────────────────────────────
        if "Table" in all_w:
            secs.append(_sec("Table", "Tabla interactiva: sort por columna, b\\u00fasqueda y paginaci\\u00f3n.", [
                Table(
                    headers=["Nombre", "Ciudad", "Rol", "Estado", "Acci\\u00f3n"],
                    rows=[
                        [Row([Avatar(initials="AG", background=Colors.indigo, color="#fff", width=28, height=28), Spacer(8), Text("Ana Garc\\u00eda")],   align="center"), "Bogot\\u00e1",   Text("Admin"),  Badge("Activo",    background="#22c55e"),                               Button("Ver", variant="ghost", padding=4, radius=4)],
                        [Row([Avatar(initials="PL", background="#f59e0b",    color="#fff", width=28, height=28), Spacer(8), Text("Pedro L\\u00f3pez")],  align="center"), "Medell\\u00edn", Text("Editor"), Badge("Inactivo",  background="var(--border)", color="var(--text-muted)"), Button("Ver", variant="ghost", padding=4, radius=4)],
                        [Row([Avatar(initials="MS", background="#ef4444",    color="#fff", width=28, height=28), Spacer(8), Text("Mar\\u00eda Silva")],  align="center"), "Cali",           Text("Viewer"), Badge("Activo",    background="#22c55e"),                               Button("Ver", variant="ghost", padding=4, radius=4)],
                        [Row([Avatar(initials="JR", background="#8b5cf6",    color="#fff", width=28, height=28), Spacer(8), Text("Juan Ram\\u00edrez")], align="center"), "Cartagena",      Text("Admin"),  Badge("Activo",    background="#22c55e"),                               Button("Ver", variant="ghost", padding=4, radius=4)],
                        [Row([Avatar(initials="LT", background="#ec4899",    color="#fff", width=28, height=28), Spacer(8), Text("Laura Torres")],       align="center"), "Bogot\\u00e1",   Text("Editor"), Badge("Pendiente", background="#f59e0b"),                               Button("Ver", variant="ghost", padding=4, radius=4)],
                    ],
                    striped=True, searchable=True, sortable=True, page_size=4,
                ),
            ], widget_name="Table"))

        # ── Modal ─────────────────────────────────────────────────────────
        if "Modal" in all_w:
            secs.append(_sec("Modal", "Ventana modal. Usa openModal(id) para abrirla.", [
                Row(gap=8, children=[
                    Button("Abrir modal",  on_click="openModal('demo_modal')"),
                    Button("Modal grande", on_click="openModal('big_modal')", variant="ghost"),
                ]),
                Modal(
                    id="demo_modal",
                    title="Confirmar acci\\u00f3n",
                    children=[
                        Text("\\u00bfEst\\u00e1s seguro de que quieres continuar? Esta acci\\u00f3n no se puede deshacer.",
                             style=TextStyle(size=14, color="var(--text-muted)", line_height=1.6)),
                        Row([
                            Button("Cancelar",  variant="ghost",  on_click="closeModal('demo_modal')"),
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
            ], widget_name="Modal"))

        # ── Breadcrumb ────────────────────────────────────────────────────
        if "Breadcrumb" in all_w:
            secs.append(_sec("Breadcrumb", "Ruta de navegaci\\u00f3n.", [
                Breadcrumb([("Inicio", "/"), ("Productos", "/productos"), ("Zapatillas", None)]),
            ], widget_name="Breadcrumb"))

        # ── GradientText & Glass ──────────────────────────────────────────
        secs.append(_sec("GradientText & Glass", "Estilos especiales de texto y fondo.", [
            Column(gap=12, children=[
                Heading("Aurora gradient",
                        style=[GradientText.aurora(), TextStyle(size=32, weight="800")]),
                Heading("Indigo mint",
                        style=[GradientText.indigo_mint(), TextStyle(size=32, weight="800")]),
                Heading("Sunrise",
                        style=[GradientText.rose_gold(), TextStyle(size=32, weight="800")]),
            ]),
            Row(gap=16, wrap=True, children=[
                Column(gap=8, padding=20,
                       style=[Glass.dark(blur=16, opacity=0.08), Border(radius=12), "width:180px;text-align:center"],
                       children=[Icon("\\U0001f52e", size=32), Text("Glass dark",  style=TextStyle(size=14, weight="600"))]),
                Column(gap=8, padding=20,
                       style=[Glass.light(blur=16, opacity=0.5), Border(radius=12), "width:180px;text-align:center"],
                       children=[Icon("\\u2728",    size=32), Text("Glass light", style=TextStyle(size=14, weight="600"))]),
            ]),
        ], widget_name="GradientText"))

        # ── FX ────────────────────────────────────────────────────────────
        secs.append(_sec("FX", "Animaciones, hover, reveal on scroll y utilidades de timing desde martin.fx.", [
            Paragraph(
                "Usa `from martin.fx import ...` como namespace oficial. "
                "Tambien puedes importar desde `martin_fx` si prefieres un alias directo. "
                "Los efectos funcionan como estilos nativos dentro de `style=[...]`.",
                style=TextStyle(size=14, color="var(--text-muted)", line_height=1.6),
            ),
            Row(gap=16, wrap=True, children=[
                Card(
                    padding=20,
                    radius=16,
                    shadow=Shadow.md(),
                    style=[
                        FadeIn(duration=0.45),
                        RevealOnScroll(direction="up", distance=28),
                        Transition("transform", duration=0.25, timing="ease-out"),
                        HoverLift(distance=8),
                        "width:220px",
                    ],
                    children=[
                        Text("FadeIn", style=TextStyle(size=13, color="var(--accent)", weight="700")),
                        Heading("Entrada suave", level=3, style=TextStyle(size=18, weight="700")),
                        Paragraph(
                            "Ideal para tarjetas, avisos y bloques de contenido que aparecen al cargar.",
                            style=TextStyle(size=13, color="var(--text-muted)", line_height=1.6),
                        ),
                    ],
                ),
                Card(
                    padding=20,
                    radius=16,
                    shadow=Shadow.md(),
                    style=[
                        SlideIn(direction="up", distance=28, delay=0.08),
                        HoverGlow(Colors.indigo),
                        "width:220px",
                    ],
                    children=[
                        Text("SlideIn", style=TextStyle(size=13, color="var(--accent)", weight="700")),
                        Heading("Movimiento con profundidad", level=3, style=TextStyle(size=18, weight="700")),
                        Paragraph(
                            "Da contexto visual sin escribir CSS manual ni keyframes por separado.",
                            style=TextStyle(size=13, color="var(--text-muted)", line_height=1.6),
                        ),
                    ],
                ),
                Card(
                    padding=20,
                    radius=16,
                    shadow=Shadow.md(),
                    style=[ScaleIn(start=0.92, delay=0.16), ReducedMotion.all(), "width:220px"],
                    children=[
                        Row(gap=10, align="center", children=[
                            Icon("\\u2726", size=22, style=[Spin(duration=3.5)]),
                            Text("ScaleIn + Spin", style=TextStyle(size=13, color="var(--accent)", weight="700")),
                        ]),
                        Heading("Presets combinables", level=3, style=TextStyle(size=18, weight="700")),
                        Paragraph(
                            "Mezcla animaciones de entrada con loops sutiles para logos, iconos o CTA.",
                            style=TextStyle(size=13, color="var(--text-muted)", line_height=1.6),
                        ),
                        Badge("Pulse activo", style=[Pulse(duration=1.8)], background=Colors.indigo, color="#fff"),
                    ],
                ),
            ]),
            Grid(columns=3, gap=14, children=[
                Card(
                    padding=18,
                    radius=14,
                    style=[
                        RevealOnScroll(direction="left", distance=24, delay=Stagger.delay(i, step=0.08)),
                        Transition("transform", duration=0.22).hover("translateY(-4px)", shadow="0 14px 26px rgba(15,23,42,0.12)"),
                    ],
                    children=[
                        Text(f"Item {i+1}", style=TextStyle(size=14, weight="700")),
                        Paragraph(
                            "Stagger organiza el delay de listas y grids sin calcular CSS manual.",
                            style=TextStyle(size=13, color="var(--text-muted)", line_height=1.55),
                        ),
                    ],
                )
                for i in range(3)
            ]),
            Code(
                "from martin import Card, Text\\n"
                "from martin.fx import SlideIn, Transition, HoverLift, RevealOnScroll\\n\\n"
                "Card(\\n"
                "    padding=24,\\n"
                "    radius=18,\\n"
                "    style=[\\n"
                "        RevealOnScroll(direction='up', distance=24),\\n"
                "        SlideIn(direction='up', distance=32, delay=0.1),\\n"
                "        Transition('transform', duration=0.25, timing='ease-out'),\\n"
                "        HoverLift(distance=8),\\n"
                "    ],\\n"
                "    children=[Text('Motion bundled inside martin-framework')],\\n"
                ")",
                block=True,
                language="python",
                filename="fx_demo.py",
                copy=True,
            ),
            Code(
                "from martin import Card\\n"
                "from martin.fx import RevealOnScroll, ReducedMotion, Stagger\\n\\n"
                "cards = [\\n"
                "    Card(\\n"
                "        f'Feature {i+1}',\\n"
                "        style=[\\n"
                "            RevealOnScroll(delay=Stagger.delay(i, step=0.07)),\\n"
                "            ReducedMotion.all(),\\n"
                "        ],\\n"
                "    )\\n"
                "    for i in range(4)\\n"
                "]",
                block=True,
                language="python",
                filename="fx_stagger.py",
                copy=True,
            ),
        ], widget_name="FX"))

        # ── Timeline ──────────────────────────────────────────────────────
        if "Timeline" in all_w:
            secs.append(_sec("Timeline", "L\\u00ednea de tiempo vertical.", [
                Timeline(items=[
                    TimelineItem(title="Proyecto iniciado",
                                 description="Se crea el repositorio y la estructura base.",
                                 date="Enero 2024", icon="\\U0001f680", color=Colors.indigo),
                    TimelineItem(title="Primera versi\\u00f3n",
                                 description="Widgets b\\u00e1sicos: Container, Row, Column, Button.",
                                 date="Marzo 2024", icon="\\u2705", color="#22c55e"),
                    TimelineItem(title="Refactor v0.2",
                                 description="Coherencia total de API. NavBar, Footer, Tabs, Table, Modal.",
                                 date="2025", icon="\\u26a1", color="#f59e0b", tag="Actual"),
                ]),
            ], widget_name="Timeline"))

        # ── Hero ──────────────────────────────────────────────────────────
        if "Hero" in all_w:
            secs.append(_sec("Hero", "Banner principal de p\\u00e1gina.", [
                Hero(
                    badge=Badge("Ejemplo de Hero"),
                    title=Heading("Construye r\\u00e1pido.", level=2,
                                  style=[GradientText.aurora(), TextStyle(size=40, weight="800")]),
                    subtitle=Paragraph("Un Hero con imagen, layout split y fondo con mesh.",
                                       style=TextStyle(size=15, color="var(--text-muted)")),
                    actions=[
                        Button("Empezar", background=Colors.indigo, color="#fff", radius=10),
                        Button("Ver docs", variant="ghost", radius=10),
                    ],
                    image=Image("/assets/icon.webp", radius=16, width=200,
                                style="box-shadow:0 24px 48px rgba(0,0,0,0.3)"),
                    background=MeshBackground.themed(),
                    layout="split", align="left", min_height=320,
                ),
            ], widget_name="Hero"))

        # ── Gallery ───────────────────────────────────────────────────────
        if "Gallery" in all_w:
            secs.append(_sec("Gallery", "Galer\\u00eda de im\\u00e1genes con lightbox.", [
                Gallery(
                    items=[
                        GalleryItem("/assets/icon.webp", title="Imagen 1", description="Descripci\\u00f3n 1"),
                        GalleryItem("/assets/icon.webp", title="Imagen 2"),
                        GalleryItem("/assets/icon.webp", title="Imagen 3", span_cols=2),
                        GalleryItem("/assets/icon.webp", title="Imagen 4"),
                        GalleryItem("/assets/icon.webp", title="Imagen 5", url="https://example.com"),
                        GalleryItem("/assets/icon.webp", title="Imagen 6"),
                    ],
                    columns=3, gap=8, img_height=180, radius=8, lightbox=True,
                ),
            ], widget_name="Gallery"))

        # ── Carousel ──────────────────────────────────────────────────────
        if "Carousel" in all_w:
            secs.append(_sec("Carousel", "Carrusel de tarjetas y cinta de logos.", [
                Carousel(
                    items=[
                        CarouselItem(image="/assets/icon.webp")
                        for i in range(4)
                    ],
                    mode="slides", visible=3, gap=12, loop=True, autoplay=2500,
                    arrows=False, dots=True, img_height=320, mobile_visible=1,
                ),
                Spacer(16),
                Text("Modo brands:", style=TextStyle(size=12, weight="600", color="var(--text-muted)")),
                Carousel(
                    items=[CarouselItem(image="/assets/icon.webp", title=f"Marca {c}") for c in "ABCDE"],
                    mode="brands", brand_height=48, brand_gap=64, speed=25,
                    brand_filter="grayscale(100%) opacity(0.5)",
                ),
            ], widget_name="Carousel"))

        # ── Map ───────────────────────────────────────────────────────────
        if "Map" in all_w:
            secs.append(_sec("Map", "Mapa interactivo con marcadores.", [
                Map(
                    zoom=6, height=400, route=True,
                    markers=[
                        (-2.897, -79.004, "Cuenca",    "Patrimonio de la Humanidad", "#6366f1", "CUE"),
                        (-0.220, -78.512, "Quito",     "Capital del Ecuador",        "#f59e0b", "UIO"),
                        (-2.203, -79.890, "Guayaquil", "Puerto principal",            "#22c55e", "GYE"),
                        (-1.012, -77.810, "Ba\\u00f1os",     "Puerta al Oriente",          "#ef4444", "BNS"),
                        (-0.934, -78.615, "Riobamba",  "Ciudad de las primicias",    "#8b5cf6", "RIO"),
                    ],
                ),
            ], widget_name="Map"))

        # ── WordCloud ─────────────────────────────────────────────────────
        if "WordCloud" in all_w:
            secs.append(_sec("WordCloud", "Nube de palabras interactiva.", [
                WordCloud(
                    words={"Python":10,"Martin":9,"Web":8,"Widget":7,"CSS":6,
                           "HTML":5,"JavaScript":5,"Framework":4,"API":4,"Router":3},
                    width=560, height=360,
                ),
            ], widget_name="WordCloud"))

        return secs


    _MENU_ITEMS = [
        ("Layout",       "widget-layout"),
        ("Texto",        "widget-texto"),
        ("Code",         "widget-code"),
        ("Badge & Alert","widget-badge"),
        ("Button",       "widget-button"),
        ("Inputs",       "widget-textfield"),
        ("Slider",       "widget-slider"),
        ("ColorPicker",  "widget-colorpicker"),
        ("DatePicker",   "widget-datepicker"),
        ("Avatar",       "widget-avatar"),
        ("Icons",        "widget-icons"),
        ("NavBar",       "widget-navbar"),
        ("Tabs",         "widget-tabs"),
        ("Table",        "widget-table"),
        ("Modal",        "widget-modal"),
        ("Breadcrumb",   "widget-breadcrumb"),
        ("GradientText", "widget-gradienttext"),
        ("FX",           "widget-fx"),
        ("Timeline",     "widget-timeline"),
        ("Hero",         "widget-hero"),
        ("Gallery",      "widget-gallery"),
        ("Carousel",     "widget-carousel"),
        ("Map",          "widget-map"),
        ("WordCloud",    "widget-wordcloud"),
    ]


    def components():
        side_items = [(label, f"#{anchor}") for label, anchor in _MENU_ITEMS]

        return Row(
            gap=0,
            align="flex-start",
            style=[
                MeshBackground.themed(),
                "max-width:1300px;margin:0 auto;padding:32px 24px;box-sizing:border-box;min-height:100vh",
            ],
            children=[
                Raw(
                    "<style>"
                    "@media(max-width:960px){"
                    ".docs-side{display:none!important}"
                    ".docs-main{max-width:100%!important}"
                    "}"
                    "</style>"
                ),
                SideMenu(
                    class_name="docs-side",
                    title="Widgets",
                    items=side_items,
                    width=210,
                    sticky=True,
                    top=80,
                    style="max-height:calc(100vh - 100px);overflow-y:auto;flex-shrink:0;margin-right:28px",
                ),
                Column(
                    class_name="docs-main",
                    gap=24,
                    style="flex:1;min-width:0;max-width:900px",
                    children=[
                        Column(gap=8, children=[
                            Heading("Componentes",
                                    style=[GradientText.aurora(), TextStyle(size=48, weight="800")]),
                            Paragraph(
                                "Widgets disponibles con demos en vivo. "
                                "Haz clic en cualquier elemento para ver c\\u00f3mo funciona.",
                                style=TextStyle(size=16, color="var(--text-muted)"),
                            ),
                        ]),
                        *_sections(),
                    ],
                ),
            ],
        ), PageConfig(title="Componentes \\u2014 PROJECT_NAME")
    """
    ).strip()
    + "\n"
)


def copy_default_icon(assets_dir: Path):
    """Copia un icono base al nuevo proyecto si existe en el paquete."""
    pkg_dir = Path(__file__).parent
    for icon_name, dest_name in ICON_CANDIDATES:
        src = pkg_dir / icon_name
        if src.exists():
            shutil.copy(src, assets_dir / dest_name)
            return


def render_new_project_files(name: str, title: str, desc: str):
    """Renderiza los archivos base para `martin new`."""
    year = str(datetime.now().year)
    main_src = (
        MAIN_TEMPLATE.replace("PROJECT_NAME", title)
        .replace("PROJECT_DESC", desc)
        .replace("YEAR", year)
    )
    return {
        "main.py": main_src,
        "pages/__init__.py": "",
        "pages/home.py": HOME_TEMPLATE.replace("PROJECT_NAME", title).replace(
            "PROJECT_DESC", desc
        ),
        "pages/components.py": COMPONENTS_TEMPLATE.replace("PROJECT_NAME", title),
        ".gitignore": GITIGNORE,
        "README.md": README_TEMPLATE.format(name=name),
    }
