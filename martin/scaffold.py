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
        TextStyle, ThemeToggle,
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
            ThemeToggle(),
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
        # SEO global del sitio
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
        Column, Row, Grid, Section, Card,
        Heading, Text, Paragraph, Button, Icon, Badge,
        Border, Shadow, TextStyle, Glass, GradientText, MeshBackground, Colors,
        PageConfig,
    )


    def home():
        hero = Section(
            id="hero",
            style=(
                "text-align:center;align-items:center;display:flex;"
                "flex-direction:column;gap:24px;min-height:85vh;justify-content:center"
            ),
            children=[
                Badge("v0.2.0 \\u2014 ahora disponible"),
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
                    Button(
                        "Empezar \\u2192", href="/components",
                        background=Colors.indigo, color="#fff",
                        radius=10, padding=16,
                        style="font-size:15px;font-weight:700;border:none",
                    ),
                    Button(
                        "Ver en GitHub", href="https://github.com",
                        variant="ghost", radius=10, padding=16,
                        style="font-size:15px",
                    ),
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
                    Paragraph(
                        "Construye cualquier interfaz anidando widgets Python. Sin HTML, sin CSS manual.",
                        style=TextStyle(size=16, color="var(--text-muted)"),
                    ),
                ]),
                Grid(
                    columns="repeat(auto-fill, minmax(260px, 1fr))",
                    gap=20, width="100%%",
                    children=[_feature(icon, title, desc) for icon, title, desc in [
                        ("\\U0001f9e9", "Widget tree",      "Comp\\u00f3n interfaces anidando componentes Python, como Flutter."),
                        ("\\U0001f3a8", "Estilos propios",  "Glass(), GradientText(), Shadow()... sin escribir CSS."),
                        ("\\u26a1",     "Hot reload",       "Guarda el fichero y el navegador se actualiza al instante."),
                        ("\\U0001f5fa\\ufe0f", "Multi-p\\u00e1gina", "Router declarativo. Cada p\\u00e1gina en su propio fichero."),
                        ("\\U0001f4e6", "Zero deps",        "Solo stdlib de Python. Sin dependencias de terceros."),
                        ("\\U0001f680", "Export est\\u00e1tico", "martin export \\u2192 HTML/CSS/JS listo para cualquier hosting."),
                    ]],
                ),
            ],
        )

        return Column(
            style=MeshBackground.themed(),
            children=[hero, features],
        ), PageConfig(title="Inicio \\u2014 PROJECT_NAME", description="PROJECT_DESC")


    def _feature(icon, title, desc):
        return Card(
            padding=24,
            children=[
                Column(gap=12, children=[
                    Icon(icon, size=32),
                    Heading(title, level=3, style=TextStyle(size=15, weight="700")),
                    Text(desc,  style=TextStyle(size=13, color="var(--text-muted)", line_height=1.6)),
                ]),
            ],
        )
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
        Image, Avatar, NavBar, Footer, Tabs, Breadcrumb,
        Table, Modal, TextField, TextArea, Select, MultiSelect, Checkbox,
        WordCloud, Map, Timeline, TimelineItem, Hero,
        Gallery, GalleryItem, Carousel, CarouselItem,
        CookieBanner, CookieCategory,
        Border, Shadow, TextStyle, Glass, GradientText, MeshBackground, Colors,
        SideMenu, Raw,
        PageConfig,
    )
    from martin.widgets import __all__ as MARTIN_WIDGETS


    # ── Helpers ──────────────────────────────────────────────────────────────

    def _slug(name: str) -> str:
        return name.lower().replace("_", "-")


    def _sec(title, subtitle, children, widget_name=None):
        \"\"\"Tarjeta de sección con ancla para el SideMenu.\"\"\"
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


    # ── Snippets de código ────────────────────────────────────────────────────

    SNIPPETS: dict = {
        "Container":     "Container(children=[Text('Contenido')], padding=16)",
        "Row":           "Row([Text('A'), Text('B')], gap=8)",
        "Column":        "Column([Heading('Titulo'), Paragraph('Desc')], gap=8)",
        "Grid":          "Grid(columns=3, gap=12, children=[Card(), Card(), Card()])",
        "Stack":         "Stack([Image('bg.jpg'), Text('Sobre imagen')])",
        "Card":          "Card(padding=20, children=[Heading('Card'), Text('Texto')])",
        "Section":       "Section(children=[Heading('Seccion')], padding=48)",
        "Spacer":        "Spacer(height=32)",
        "Divider":       "Divider()",
        "Text":          "Text('Texto corto')",
        "Heading":       "Heading('Titulo principal', level=1)",
        "Paragraph":     "Paragraph('Texto largo para descripcion...')",
        "Link":          "Link('Ir a inicio', href='/')",
        "Code":          "Code('print(\\"hola\\")', language='python')",
        "Image":         "Image('https://picsum.photos/320/180', radius=10)",
        "Video":         "Video(src='https://example.com/video.mp4')",
        "Icon":          "Icon('\\u2728', size=26)",
        "Avatar":        "Avatar(src='https://i.pravatar.cc/64', size=48)",
        "Button":        "Button('Guardar', on_click='alert(\\'ok\\')')",
        "TextField":     "TextField(name='email', placeholder='correo@dominio.com')",
        "TextArea":      "TextArea(name='bio', placeholder='Cu\\u00e9ntanos algo...')",
        "Checkbox":      "Checkbox(name='acepto', label='Acepto los t\\u00e9rminos')",
        "Select":        "Select(name='pais', options=['Ecuador', 'Colombia', 'Peru'])",
        "MultiSelect":   "MultiSelect(name='tags', options=['Python', 'Web', 'UI'])",
        "Badge":         "Badge('Nuevo', color='var(--accent)')",
        "Alert":         "Alert('Operaci\\u00f3n completada', kind='success')",
        "NavBar":        "NavBar(brand=Heading('Marca', level=4), links=[Link('Inicio', href='/')])",
        "SideMenu":      "SideMenu(title='Menu', items=[('Inicio', '/'), ('Docs', '/components')])",
        "Footer":        "Footer(left=Text('\\u00a9 2026'), right=Link('Inicio', href='/'))",
        "Breadcrumb":    "Breadcrumb([('Inicio', '/'), ('Componentes', '/components')])",
        "Tabs":          "Tabs([('General', Text('Tab 1')), ('Avanzado', Text('Tab 2'))])",
        "Table":         "Table(headers=['Nombre', 'Rol'], rows=[['Ana', 'Admin'], ['Luis', 'Dev']])",
        "Modal":         "Modal(\\n    id='demo',\\n    title='Confirmaci\\u00f3n',\\n    children=[\\n        Text('\\u00bfEst\\u00e1s seguro?'),\\n        Button('Cerrar', on_click=\\"closeModal('demo')\\"),\\n    ],\\n)",
        "ThemeToggle":   "ThemeToggle()",
        "ApiCall":       "ApiCall('/api/demo', method='GET', target='resultado')",
        "ResultBox":     "ResultBox(id='resultado')",
        "Raw":           "Raw('<b>HTML directo</b>')",
        "Ref":           "Ref(id='mi_valor')",
        "Accordion":     "Accordion([\\n    AccordionItem('\\u00bfC\\u00f3mo funciona?', Text('Abre y cierra con clic.')),\\n])",
        "Calendar":      "Calendar(events=[CalendarEvent(title='Lanzamiento', date='2026-06-01')])",
        "Hero":          "Hero(\\n    title='Bienvenido',\\n    subtitle='Una gran idea',\\n    actions=[Button('Empezar', href='/')],\\n)",
        "Gallery":       "Gallery([\\n    GalleryItem(src='https://picsum.photos/400/300', caption='Foto 1'),\\n])",
        "Carousel":      "Carousel([\\n    CarouselItem(image='/assets/icon.webp', title='Slide 1', subtitle='Desc.'),\\n])",
        "WordCloud":     "WordCloud(words=[('Python', 90), ('Web', 70), ('Martin', 60)])",
        "Map":           "Map(lat=-2.9, lng=-79.0, zoom=13)",
        "Timeline":      "Timeline([\\n    TimelineItem(title='Inicio', date='Ene 2026', body='Primer commit.'),\\n])",
        "Chart":         "Chart(\\n    labels=['Ene', 'Feb', 'Mar'],\\n    datasets=[ChartDataset('Ventas', [10, 25, 18])],\\n)",
        "Testimonials":  "Testimonials([\\n    TestimonialItem(text='Incre\\u00edble.', author='Mar\\u00eda', role='Dev'),\\n])",
        "SlideCarousel": "SlideCarousel([\\n    SlideItem(title='Slide 1', body='Descripci\\u00f3n.'),\\n])",
        "Pricing":       "Pricing([\\n    PricingPlan(name='Pro', price='$9', features=['Feature A'], highlighted=True),\\n])",
        "FAQ":           "FAQ([\\n    FAQItem(question='\\u00bfEst\\u00e1 en pip?', answer='S\\u00ed: pip install martin'),\\n])",
        "CookieBanner":  "CookieBanner(\\n    message='Usamos cookies para mejorar la experiencia.',\\n    privacy_url='/privacidad',\\n)",
        "CookieCategory":"CookieCategory(name='analytics', label='Anal\\u00edtica', description='Google Analytics')",
    }


    # ── Secciones con widgets reales ─────────────────────────────────────────

    def _sections():
        all_w = set(MARTIN_WIDGETS)

        secs = []

        # Layout
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
                    Container(
                        padding=16, radius=8,
                        background="var(--surface-2,var(--surface))",
                        style="border:1px solid var(--border);text-align:center",
                        children=[Text(f"Celda {i+1}", style=TextStyle(size=13, color="var(--text-muted)"))],
                    ) for i in range(3)
                ]),
            ], widget_name="Layout"))

        # Texto
        if "Heading" in all_w:
            secs.append(_sec("Texto", "Heading (h1-h6), Text, Paragraph, Link, Code.", [
                Heading("Heading nivel 1", level=1),
                Heading("Heading nivel 2", level=2),
                Heading("Heading nivel 3", level=3),
                Paragraph(
                    "Paragraph para bloques de texto. Tiene line-height:1.6 por defecto. "
                    "Ideal para descripciones, onboardings o contenido editorial.",
                    style=TextStyle(size=15, color="var(--text-muted)"),
                ),
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

        # Code
        if "Code" in all_w:
            secs.append(_sec("Code", "Bloques de c\\u00f3digo: syntax highlighting, bot\\u00f3n copiar, numeraci\\u00f3n, modo editable.", [
                Column(gap=20, children=[
                    Code(
                        content="from martin import App, Router, Column, Heading\\n\\nrouter = Router()\\nrouter.add('/', lambda: Column([Heading('Hola')]))\\nApp(router=router).run()",
                        language="python", filename="main.py", copy=True,
                    ),
                    Code(
                        content='[\\n  { "id": 1, "nombre": "Ana", "rol": "Admin" },\\n  { "id": 2, "nombre": "Pedro", "rol": "Editor" }\\n]',
                        language="json", line_numbers=True, copy=True, filename="data.json",
                    ),
                    Code(
                        content="pip install martin\\nmartin new mi_proyecto\\ncd mi_proyecto\\nmartin run",
                        language="bash", copy=True,
                    ),
                ]),
            ], widget_name="Code"))

        # Badge & Alert
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

        # Button
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

        # Inputs
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

        # Avatar & Image
        if "Avatar" in all_w:
            secs.append(_sec("Avatar & Image", "Avatares con imagen o iniciales. Im\\u00e1genes con estilos.", [
                Row(gap=12, align="center", wrap=True, children=[
                    Avatar(initials="AB"),
                    Avatar(initials="CD", background=Colors.indigo, color="#fff"),
                    Avatar(initials="EF", background="#f59e0b",    color="#fff", width=56, height=56),
                    Avatar(initials="GH", background="#ef4444",    color="#fff"),
                    Avatar("/assets/icon.webp"),
                ]),
                Row(gap=16, wrap=True, children=[
                    Image("/assets/icon.webp"),
                    Image("/assets/icon.webp", radius=12, width=80, height=80),
                    Image("/assets/icon.webp", radius=999, width=80, height=80, shadow=True),
                ]),
            ], widget_name="Avatar"))

        # NavBar & Footer
        if "NavBar" in all_w:
            secs.append(_sec("NavBar & Footer", "Cabecera y pie de p\\u00e1gina totalmente declarativos.", [
                NavBar(
                    brand=Row([
                        Image("/assets/icon.webp", width=28, height=28, radius=6),
                        Text("MiApp", style=TextStyle(weight="800", size=17)),
                    ], gap=8, align="center"),
                    links=[
                        Link("Inicio",    href="/",         style="color:var(--text);text-decoration:none;font-size:14px;font-weight:500"),
                        Link("Productos", href="/productos", style="color:var(--text-muted);text-decoration:none;font-size:14px"),
                        Link("Blog",      href="/blog",     style="color:var(--text-muted);text-decoration:none;font-size:14px"),
                    ],
                    actions=[
                        Button("Login",    variant="ghost", radius=8),
                        Button("Registro", radius=8),
                    ],
                ),
                Spacer(16),
                Footer(
                    left=Text("\\u00a9 2025 MiApp", style=TextStyle(size=13, color="var(--text-muted)")),
                    center=Row([
                        Link("T\\u00e9rminos",  href="/terminos",   style="font-size:13px;color:var(--text-muted);text-decoration:none"),
                        Link("Privacidad", href="/privacidad", style="font-size:13px;color:var(--text-muted);text-decoration:none"),
                    ], gap=16),
                    right=Row([
                        Button("Twitter", variant="ghost", padding=6, radius=6),
                        Button("GitHub",  variant="ghost", padding=6, radius=6),
                    ], gap=4),
                ),
            ], widget_name="NavBar"))

        # Tabs
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
                        TextField(placeholder="Nueva contrase\\u00f1a", type="password"),
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

        # Table
        if "Table" in all_w:
            secs.append(_sec("Table", "Tabla interactiva: sort por columna, b\\u00fasqueda y paginaci\\u00f3n.", [
                Table(
                    headers=["Nombre", "Ciudad", "Rol", "Estado", "Acci\\u00f3n"],
                    rows=[
                        [Row([Avatar(initials="AG", background=Colors.indigo, color="#fff", width=28, height=28), Spacer(8), Text("Ana Garc\\u00eda")],   align="center"), "Bogot\\u00e1",  Text("Admin"),  Badge("Activo",    background="#22c55e"),                               Button("Ver", variant="ghost", padding=4, radius=4)],
                        [Row([Avatar(initials="PL", background="#f59e0b",    color="#fff", width=28, height=28), Spacer(8), Text("Pedro L\\u00f3pez")],  align="center"), "Medell\\u00edn", Text("Editor"), Badge("Inactivo",  background="var(--border)", color="var(--text-muted)"), Button("Ver", variant="ghost", padding=4, radius=4)],
                        [Row([Avatar(initials="MS", background="#ef4444",    color="#fff", width=28, height=28), Spacer(8), Text("Mar\\u00eda Silva")],  align="center"), "Cali",          Text("Viewer"), Badge("Activo",    background="#22c55e"),                               Button("Ver", variant="ghost", padding=4, radius=4)],
                        [Row([Avatar(initials="JR", background="#8b5cf6",    color="#fff", width=28, height=28), Spacer(8), Text("Juan Ram\\u00edrez")], align="center"), "Cartagena",     Text("Admin"),  Badge("Activo",    background="#22c55e"),                               Button("Ver", variant="ghost", padding=4, radius=4)],
                        [Row([Avatar(initials="LT", background="#ec4899",    color="#fff", width=28, height=28), Spacer(8), Text("Laura Torres")],       align="center"), "Bogot\\u00e1",  Text("Editor"), Badge("Pendiente", background="#f59e0b"),                               Button("Ver", variant="ghost", padding=4, radius=4)],
                    ],
                    striped=True, searchable=True, sortable=True, page_size=4,
                ),
            ], widget_name="Table"))

        # Modal
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

        # Breadcrumb
        if "Breadcrumb" in all_w:
            secs.append(_sec("Breadcrumb", "Ruta de navegaci\\u00f3n.", [
                Breadcrumb([
                    ("Inicio",     "/"),
                    ("Productos",  "/productos"),
                    ("Zapatillas", None),
                ]),
            ], widget_name="Breadcrumb"))

        # GradientText & Glass
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
                Column(
                    gap=8, padding=20,
                    style=[Glass.dark(blur=16, opacity=0.08),
                           Border(radius=12), "width:180px;text-align:center"],
                    children=[Icon("\\U0001f52e", size=32), Text("Glass dark", style=TextStyle(size=14, weight="600"))],
                ),
                Column(
                    gap=8, padding=20,
                    style=[Glass.light(blur=16, opacity=0.5),
                           Border(radius=12), "width:180px;text-align:center"],
                    children=[Icon("\\u2728", size=32), Text("Glass light", style=TextStyle(size=14, weight="600"))],
                ),
            ]),
        ], widget_name="GradientText"))

        # Timeline
        if "Timeline" in all_w:
            secs.append(_sec("Timeline", "L\\u00ednea de tiempo vertical.", [
                Timeline(items=[
                    TimelineItem(
                        title="Proyecto iniciado",
                        description="Se crea el repositorio y la estructura base del proyecto.",
                        date="Enero 2024", icon="\\U0001f680", color=Colors.indigo,
                    ),
                    TimelineItem(
                        title="Primera versi\\u00f3n",
                        description="Se publican los widgets b\\u00e1sicos: Container, Row, Column, Button.",
                        date="Marzo 2024", icon="\\u2705", color="#22c55e",
                    ),
                    TimelineItem(
                        title="Refactor v0.2",
                        description="Coherencia total de API. Nuevos widgets: NavBar, Footer, Tabs, Table, Modal.",
                        date="2025", icon="\\u26a1", color="#f59e0b", tag="Actual",
                    ),
                ]),
            ], widget_name="Timeline"))

        # Hero
        if "Hero" in all_w:
            secs.append(_sec("Hero", "Banner principal de p\\u00e1gina.", [
                Hero(
                    badge=Badge("Ejemplo de Hero"),
                    title=Heading("Construye r\\u00e1pido.", level=2,
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
            ], widget_name="Hero"))

        # Gallery
        if "Gallery" in all_w:
            secs.append(_sec("Gallery", "Galer\\u00eda de im\\u00e1genes con lightbox.", [
                Gallery(
                    items=[
                        GalleryItem("/assets/icon.webp", title="Imagen 1", description="Descripci\\u00f3n de la imagen 1"),
                        GalleryItem("/assets/icon.webp", title="Imagen 2"),
                        GalleryItem("/assets/icon.webp", title="Imagen 3", span_cols=2),
                        GalleryItem("/assets/icon.webp", title="Imagen 4"),
                        GalleryItem("/assets/icon.webp", title="Imagen 5", description="Con enlace", url="https://example.com"),
                        GalleryItem("/assets/icon.webp", title="Imagen 6"),
                    ],
                    columns=3, gap=8, img_height=180, radius=8, lightbox=True,
                ),
            ], widget_name="Gallery"))

        # Carousel
        if "Carousel" in all_w:
            secs.append(_sec("Carousel", "Carrusel de tarjetas con flechas y dots.", [
                Carousel(
                    items=[
                        CarouselItem(image="/assets/icon.webp", title="Slide 1", subtitle="Descripci\\u00f3n del primer slide."),
                        CarouselItem(image="/assets/icon.webp", title="Slide 2", subtitle="Descripci\\u00f3n del segundo slide."),
                        CarouselItem(image="/assets/icon.webp", title="Slide 3", subtitle="Con link al hacer clic.", url="https://example.com"),
                        CarouselItem(image="/assets/icon.webp", title="Slide 4", subtitle="\\u00daltimo slide."),
                    ],
                    mode="slides", visible=3, gap=16, loop=True, autoplay=3000,
                ),
                Spacer(16),
                Text("Modo brands (cinta infinita de logos):",
                     style=TextStyle(size=12, weight="600", color="var(--text-muted)")),
                Carousel(
                    items=[
                        CarouselItem(image="/assets/icon.webp", title="Marca A", url="https://example.com"),
                        CarouselItem(image="/assets/icon.webp", title="Marca B"),
                        CarouselItem(image="/assets/icon.webp", title="Marca C"),
                        CarouselItem(image="/assets/icon.webp", title="Marca D"),
                        CarouselItem(image="/assets/icon.webp", title="Marca E"),
                    ],
                    mode="brands", brand_height=48, brand_gap=64, speed=25,
                    brand_filter="grayscale(100%) opacity(0.5)",
                ),
            ], widget_name="Carousel"))

        # Map
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

        # WordCloud
        if "WordCloud" in all_w:
            secs.append(_sec("WordCloud", "Nube de palabras interactiva.", [
                WordCloud(
                    words={"Python":10,"Martin":9,"Web":8,"Widget":7,"CSS":6,
                           "HTML":5,"JavaScript":5,"Framework":4,"API":4,"Router":3},
                    width=600, height=280,
                ),
            ], widget_name="WordCloud"))

        # CookieBanner
        if "CookieBanner" in all_w:
            secs.append(_sec("CookieBanner", "Banner de cookies GDPR con persistencia.", [
                CookieBanner(
                    title="Este sitio usa cookies",
                    description="Usamos cookies propias y de terceros para mejorar tu experiencia.",
                    categories=[
                        CookieCategory("necessary", "Necesarias",
                                       "Imprescindibles para el funcionamiento.",
                                       default=True, required=True),
                        CookieCategory("analytics", "Anal\\u00edticas",
                                       "Mejoran el sitio.", default=False),
                        CookieCategory("marketing", "Marketing",
                                       "Publicidad relevante.", default=False),
                    ],
                    position="bottom",
                    storage_key="martin_cookie_consent_demo",
                    privacy_url="/about",
                ),
            ], widget_name="CookieBanner"))

        return secs


    # ── Menú lateral ─────────────────────────────────────────────────────────

    _MENU_ITEMS = [
        ("Layout",       "widget-layout"),
        ("Texto",        "widget-texto"),
        ("Code",         "widget-code"),
        ("Badge & Alert","widget-badge"),
        ("Button",       "widget-button"),
        ("Inputs",       "widget-textfield"),
        ("Avatar",       "widget-avatar"),
        ("NavBar",       "widget-navbar"),
        ("Tabs",         "widget-tabs"),
        ("Table",        "widget-table"),
        ("Modal",        "widget-modal"),
        ("Breadcrumb",   "widget-breadcrumb"),
        ("GradientText", "widget-gradienttext"),
        ("Timeline",     "widget-timeline"),
        ("Hero",         "widget-hero"),
        ("Gallery",      "widget-gallery"),
        ("Carousel",     "widget-carousel"),
        ("Map",          "widget-map"),
        ("WordCloud",    "widget-wordcloud"),
        ("CookieBanner", "widget-cookiebanner"),
    ]


    # ── Vista principal ───────────────────────────────────────────────────────

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
                            Heading(
                                "Componentes",
                                style=[GradientText.aurora(), TextStyle(size=48, weight="800")],
                            ),
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
