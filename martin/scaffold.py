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
        App,
        Router,
        NavBar,
        Footer,
        Heading,
        Text,
        Link,
        Row,
        TextStyle,
        ThemeToggle,
    )
    from pages.home import home
    from pages.components import components

    router = Router()
    router.add("/", home, title="Inicio")
    router.add("/components", components, title="Componentes")

    header = NavBar(
        brand=Heading("PROJECT_NAME", level=3, color="var(--text)", style="letter-spacing:-0.5px"),
        links=[
            Link("Inicio",       href="/",           style="text-decoration:none;color:var(--text-muted);font-size:14px"),
            Link("Componentes",  href="/components", style="text-decoration:none;color:var(--text-muted);font-size:14px"),
        ],
        actions=[ThemeToggle()],
    )

    footer = Footer(
        left=Text("© YEAR PROJECT_NAME", style=TextStyle(size=13, color="var(--text-muted)")),
        right=Row(
            [
                Link("Inicio",      href="/",           style="text-decoration:none;font-size:13px;color:var(--text-muted)"),
                Link("Componentes", href="/components", style="text-decoration:none;font-size:13px;color:var(--text-muted)"),
            ],
            gap=20,
        ),
    )

    app = App(
        router=router,
        title="PROJECT_NAME",
        theme="auto",
        header=header,
        footer=footer,
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
    .feature-card:hover { transform: translateY(-3px); box-shadow: 0 8px 32px rgba(0,0,0,.12); }
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

                # Hero
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

                # Features
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

                # Quick start
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
        ), PageConfig(title="Inicio \\u2014 PROJECT_NAME")
    """
    ).strip()
    + "\n"
)


COMPONENTS_TEMPLATE = (
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
        Badge,
        Alert,
        TextField,
        TextArea,
        Checkbox,
        Select,
        Code,
        Link,
        Image,
        Avatar,
        Divider,
        Tabs,
        Table,
        Modal,
        Raw,
        SideMenu,
        PageConfig,
    )
    from martin.widgets import __all__ as MARTIN_WIDGETS


    def _slug(name: str) -> str:
        return name.lower().replace("_", "-")


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
        "Accordion":     "Accordion([\\n    AccordionItem('\\u00bfC\\u00f3mo funciona?', Text('Abre y cierra con clic.')),\\n    AccordionItem('\\u00bfEst\\u00e1 en pip?',    Text('S\\u00ed: pip install martin')),\\n])",
        "Calendar":      "Calendar(events=[\\n    CalendarEvent(title='Lanzamiento', date='2026-06-01'),\\n])",
        "Hero":          "Hero(\\n    title='Bienvenido',\\n    subtitle='Una gran idea',\\n    actions=[Button('Empezar', href='/')],\\n)",
        "Gallery":       "Gallery([\\n    GalleryItem(src='https://picsum.photos/400/300', caption='Foto 1'),\\n    GalleryItem(src='https://picsum.photos/400/301', caption='Foto 2'),\\n])",
        "Carousel":      "Carousel([\\n    CarouselItem(child=Card(padding=24, children=[Heading('Slide 1', level=3)])),\\n    CarouselItem(child=Card(padding=24, children=[Heading('Slide 2', level=3)])),\\n])",
        "WordCloud":     "WordCloud(words=[('Python', 90), ('Web', 70), ('Martin', 60), ('UI', 50)])",
        "Map":           "Map(lat=-2.9, lng=-79.0, zoom=13)",
        "Timeline":      "Timeline([\\n    TimelineItem(title='Inicio', date='Ene 2026', body='Primer commit.'),\\n    TimelineItem(title='Alpha',  date='Mar 2026', body='Primera release.'),\\n])",
        "Chart":         "Chart(\\n    labels=['Ene', 'Feb', 'Mar'],\\n    datasets=[ChartDataset('Ventas', [10, 25, 18])],\\n)",
        "Testimonials":  "Testimonials([\\n    TestimonialItem(text='Incre\\u00edble framework.', author='Mar\\u00eda', role='Dev'),\\n    TestimonialItem(text='Python para la web.', author='Luis', role='CTO'),\\n])",
        "SlideCarousel": "SlideCarousel([\\n    SlideItem(title='Slide 1', body='Descripci\\u00f3n del slide.'),\\n    SlideItem(title='Slide 2', body='Otro contenido.'),\\n])",
        "Pricing":       "Pricing([\\n    PricingPlan(name='Free',  price='$0',  features=['1 proyecto', 'Soporte comunidad']),\\n    PricingPlan(name='Pro',   price='$9',  features=['Proyectos ilimitados', 'Soporte prioritario'], highlighted=True),\\n])",
        "FAQ":           "FAQ([\\n    FAQItem(question='\\u00bfEst\\u00e1 en pip?',        answer='S\\u00ed: pip install martin'),\\n    FAQItem(question='\\u00bfRequiere JavaScript?', answer='No, todo es Python.'),\\n])",
        "CookieBanner":  "CookieBanner(\\n    message='Usamos cookies para mejorar la experiencia.',\\n    privacy_url='/privacidad',\\n)",
        "CookieCategory":"CookieCategory(name='analytics', label='Anal\\u00edtica', description='Google Analytics')",
    }


    # Widgets con preview visual real. El resto solo muestra el snippet.
    def _preview(name: str):
        previews = {
            "Container": Column(
                [Text("Elemento dentro de Container")],
                padding=12,
                style="border:1px dashed var(--border);border-radius:8px",
            ),
            "Row": Row([Badge("A"), Badge("B"), Badge("C")], gap=8),
            "Column": Column(
                [Text("Elemento 1"), Text("Elemento 2"), Text("Elemento 3")],
                gap=6,
            ),
            "Grid": Grid(
                columns=3, gap=8,
                children=[Card(padding=10, children=[Text(f"Item {i+1}")]) for i in range(3)],
            ),
            "Card": Card(
                padding=16,
                children=[
                    Heading("Tarjeta", level=4, style="margin:0;font-size:16px"),
                    Text("Contenido de ejemplo", style="color:var(--text-muted);font-size:14px"),
                ],
            ),
            "Divider": Divider(),
            "Text": Column([
                Text("Texto normal"),
                Text("Texto muted",  style="color:var(--text-muted)"),
                Text("Texto acento", style="color:var(--accent)"),
            ], gap=6),
            "Heading": Column([
                Heading("H1 T\\u00edtulo",    level=1, style="font-size:22px;margin:0"),
                Heading("H2 Subt\\u00edtulo", level=2, style="font-size:17px;margin:0"),
                Heading("H3 Secci\\u00f3n",   level=3, style="font-size:14px;margin:0"),
            ], gap=6),
            "Paragraph": Paragraph(
                "P\\u00e1rrafo de texto de ejemplo con varias palabras para ver el flujo de l\\u00edneas.",
                style="max-width:420px;font-size:14px",
            ),
            "Link": Row([
                Link("Enlace interno",       href="/"),
                Link("Enlace externo \\u2192", href="https://github.com", target="_blank"),
            ], gap=16),
            "Code": Code('print("Hola, Martin!")', language="python", block=False),
            "Image": Image(
                "https://picsum.photos/seed/martin/400/180",
                radius=8,
                style="max-width:100%;display:block",
            ),
            "Icon": Row(
                [Text(i, style="font-size:24px") for i in ["\\U0001f680","\\u2728","\\U0001f3a8","\\u26a1","\\U0001f525","\\U0001f9e9"]],
                gap=10,
            ),
            "Avatar": Row(
                [Avatar(src=f"https://i.pravatar.cc/48?img={i}", size=40) for i in [1, 5, 10, 15]],
                gap=8,
            ),
            "Button": Row([
                Button("Primario"),
                Button("Secundario", variant="secondary"),
                Button("Ghost",      variant="ghost"),
                Button("Danger",     variant="danger"),
            ], gap=8, wrap=True),
            "TextField":  TextField(name="demo_tf", placeholder="Escribe algo...", style="max-width:320px"),
            "TextArea":   TextArea(name="demo_ta",  placeholder="Texto largo...", rows=3, style="max-width:320px"),
            "Checkbox": Column([
                Checkbox(name="cb1", label="Opci\\u00f3n A"),
                Checkbox(name="cb2", label="Opci\\u00f3n B", checked=True),
            ], gap=8),
            "Select": Select(
                name="demo_sel",
                options=["Ecuador", "Colombia", "Per\\u00fa", "Chile"],
                style="max-width:240px",
            ),
            "Badge": Row([
                Badge("Nuevo"),
                Badge("Pro",  color="var(--accent)"),
                Badge("Beta", color="orange"),
                Badge("v2.0", color="green"),
            ], gap=8),
            "Alert": Column([
                Alert("Operaci\\u00f3n completada con \\u00e9xito", kind="success"),
                Alert("Este paso es importante",                  kind="warning"),
                Alert("Ocurri\\u00f3 un error inesperado",         kind="error"),
            ], gap=8),
            "Breadcrumb": Row([
                Link("Inicio",      href="/",           style="text-decoration:none;color:var(--text-muted);font-size:14px"),
                Text("\\u203a",     style="color:var(--text-muted)"),
                Text("Componentes", style="color:var(--text);font-size:14px"),
            ], gap=8, align="center"),
            "Tabs": Tabs([
                ("General",  Text("Contenido de la pesta\\u00f1a General")),
                ("Avanzado", Text("Opciones avanzadas aqu\\u00ed")),
                ("Info",     Text("M\\u00e1s informaci\\u00f3n")),
            ]),
            "Table": Table(
                headers=["Nombre", "Rol", "Estado"],
                rows=[
                    ["Ana Garc\\u00eda", "Admin",  "Activo"],
                    ["Luis Torres",     "Dev",    "Activo"],
                    ["Mar\\u00eda P\\u00e9rez",  "Design", "Inactivo"],
                ],
                striped=True,
            ),
            "Modal": Row([
                Button("Abrir Modal", on_click="openModal('scaffold_modal_demo')"),
                Modal(
                    id="scaffold_modal_demo",
                    title="Modal de ejemplo",
                    children=[
                        Paragraph("Este es el contenido del modal. Haz clic fuera o en Cerrar para cerrar."),
                        Row([
                            Button("Cerrar", variant="ghost", on_click="closeModal('scaffold_modal_demo')"),
                        ], justify="flex-end"),
                    ],
                ),
            ], gap=12, align="center"),
            "Raw": Raw(
                '<span style="font-family:monospace;background:color-mix(in srgb,var(--accent) 10%,'
                'transparent);padding:4px 10px;border-radius:6px;font-size:13px;color:var(--accent)">'
                '&lt;HTML directo&gt;</span>'
            ),
        }
        return previews.get(name)


    # Categorías con los widgets que existen en __all__
    CATEGORIES = [
        ("Layout",           ["Container", "Row", "Column", "Grid", "Stack", "Card", "Section", "Spacer", "Divider"]),
        ("Texto",            ["Text", "Heading", "Paragraph", "Link", "Code"]),
        ("Media",            ["Image", "Video", "Icon", "Avatar"]),
        ("Formularios",      ["Button", "TextField", "TextArea", "Checkbox", "Select", "MultiSelect"]),
        ("Feedback",         ["Badge", "Alert"]),
        ("Navegaci\\u00f3n", ["NavBar", "SideMenu", "Footer", "Breadcrumb", "Tabs"]),
        ("Datos",            ["Table"]),
        ("Overlay",          ["Modal"]),
        ("Utilidad",         ["Raw", "ThemeToggle", "Ref", "ApiCall", "ResultBox"]),
        ("Marketing",        ["Hero", "Gallery", "Carousel", "WordCloud", "Map",
                               "Timeline", "Chart", "Testimonials", "SlideCarousel",
                               "Pricing", "FAQ", "Accordion", "Calendar"]),
        ("Cookies",          ["CookieBanner", "CookieCategory"]),
    ]


    def _section(widget_name: str):
        all_widgets = set(MARTIN_WIDGETS)
        if widget_name not in all_widgets:
            return None

        preview = _preview(widget_name)
        snippet = SNIPPETS.get(widget_name, f"{widget_name}(...)")

        children = [
            Heading(widget_name, level=3, style="font-size:18px;margin:0;font-weight:700"),
        ]
        if preview is not None:
            children += [
                Text(
                    "Vista previa",
                    style="font-size:11px;font-weight:600;letter-spacing:.06em;text-transform:uppercase;color:var(--text-muted)",
                ),
                Card(
                    padding=20,
                    style="background:var(--bg);border:1px solid var(--border)",
                    children=[preview],
                ),
            ]
        children += [
            Text(
                "C\\u00f3digo",
                style="font-size:11px;font-weight:600;letter-spacing:.06em;text-transform:uppercase;color:var(--text-muted)",
            ),
            Code(snippet, language="python", block=True),
            Divider(),
        ]

        return Column(
            id=f"widget-{_slug(widget_name)}",
            gap=10,
            style="scroll-margin-top:88px",
            children=children,
        )


    def _category_section(cat_name: str, widget_names: list):
        all_widgets = set(MARTIN_WIDGETS)
        sections = [_section(w) for w in widget_names if w in all_widgets]
        sections = [s for s in sections if s is not None]
        if not sections:
            return None
        return Column(
            gap=24,
            style="padding-top:8px",
            children=[
                Raw(
                    f'<div style="display:flex;align-items:center;gap:12px;margin-bottom:4px">'
                    f'<span style="font-size:11px;font-weight:700;letter-spacing:.1em;'
                    f'text-transform:uppercase;color:var(--text-muted);white-space:nowrap">{cat_name}</span>'
                    f'<div style="flex:1;height:1px;background:var(--border)"></div>'
                    f'</div>'
                ),
                *sections,
            ],
        )


    def components():
        all_widgets = set(MARTIN_WIDGETS)

        # Items para el SideMenu (solo widgets existentes)
        side_items = []
        for _cat, widget_names in CATEGORIES:
            for w in widget_names:
                if w in all_widgets:
                    side_items.append((w, f"#widget-{_slug(w)}"))

        # Secciones de contenido
        content_sections = [
            s for cat_name, widget_names in CATEGORIES
            for s in [_category_section(cat_name, widget_names)]
            if s is not None
        ]

        return Row(
            gap=0,
            align="flex-start",
            style="max-width:1300px;margin:0 auto;padding:32px 24px;box-sizing:border-box",
            children=[
                # Menú lateral
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
                # Contenido principal
                Column(
                    class_name="docs-main",
                    gap=32,
                    style="flex:1;min-width:0;max-width:860px",
                    children=[
                        Column(gap=8, children=[
                            Heading(
                                "Componentes",
                                level=1,
                                style="font-size:36px;font-weight:800;letter-spacing:-1px;margin:0",
                            ),
                            Paragraph(
                                "Widgets disponibles con preview en vivo y snippet listo para copiar.",
                                style="font-size:15px;color:var(--text-muted);margin:0",
                            ),
                        ]),
                        Divider(),
                        *content_sections,
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
