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


GITIGNORE = textwrap.dedent(
    """
    __pycache__/
    *.py[cod]
    .env
    venv/
    dist/
    .DS_Store
    """
).strip() + "\n"


README_TEMPLATE = textwrap.dedent(
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
).strip() + "\n"


MAIN_TEMPLATE = textwrap.dedent(
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
    )
    from pages.home import home
    from pages.components import components

    router = Router()
    router.add("/", home, title="Inicio")
    router.add("/components", components, title="Componentes")

    header = NavBar(
        brand=Heading("PROJECT_NAME", level=3, color="var(--text)"),
        links=[
            Link("Inicio", href="/", style="text-decoration:none;color:var(--text-muted)"),
            Link("Componentes", href="/components", style="text-decoration:none;color:var(--text-muted)"),
        ],
    )

    footer = Footer(
        left=Text(
            "© YEAR PROJECT_NAME",
            style=TextStyle(size=13, color="var(--text-muted)")
        ),
        right=Row(
            [Link("Inicio", href="/"), Link("Componentes", href="/components")],
            gap=14
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
).strip() + "\n"


HOME_TEMPLATE = textwrap.dedent(
    """
    from martin import (
        Column,
        Row,
        Card,
        Heading,
        Paragraph,
        Text,
        Button,
        PageConfig,
    )


    def home():
        return Column(
            padding=48,
            gap=24,
            style="max-width:960px;margin:0 auto;min-height:72vh;justify-content:center",
            children=[
                Heading("PROJECT_NAME", level=1, style="font-size:48px;letter-spacing:-1px"),
                Paragraph(
                    "PROJECT_DESC",
                    style="font-size:18px;color:var(--text-muted);max-width:700px",
                ),
                Row(
                    gap=12,
                    children=[
                        Button("Ver componentes", href="/components"),
                        Button("GitHub", href="https://github.com", variant="ghost"),
                    ],
                ),
                Card(
                    padding=20,
                    children=[
                        Heading("Inicio rapido", level=3, style="font-size:18px"),
                        Text("1. Edita pages/home.py"),
                        Text("2. Revisa pages/components.py"),
                        Text("3. Ejecuta martin export para generar estatico"),
                    ],
                ),
            ],
        ), PageConfig(title="Inicio - PROJECT_NAME")
    """
).strip() + "\n"


COMPONENTS_TEMPLATE = textwrap.dedent(
    """
    from martin import (
        Column,
        Row,
        Card,
        Heading,
        Paragraph,
        Text,
        Code,
        Raw,
        SideMenu,
        PageConfig,
    )
    from martin.widgets import __all__ as MARTIN_WIDGETS

    WIDGETS = sorted(MARTIN_WIDGETS)

    SNIPPETS = {
        "Container": "Container(children=[Text('Contenido')], padding=16)",
        "Row": "Row([Text('A'), Text('B')], gap=8)",
        "Column": "Column([Heading('Titulo'), Paragraph('Descripcion')], gap=8)",
        "Grid": "Grid(columns=3, gap=12, children=[Card(), Card(), Card()])",
        "Card": "Card(padding=20, children=[Heading('Card'), Text('Contenido')])",
        "Heading": "Heading('Titulo principal', level=1)",
        "Text": "Text('Texto corto')",
        "Paragraph": "Paragraph('Texto largo para una descripcion')",
        "Link": "Link('Ir a inicio', href='/')",
        "Code": "Code('print(\\\"hola\\\")', language='python')",
        "Image": "Image('https://picsum.photos/320/180', radius=10)",
        "Icon": "Icon('✨', size=26)",
        "Button": "Button('Guardar', on_click='alert(\\'ok\\')')",
        "TextField": "TextField(name='email', placeholder='correo@dominio.com')",
        "Select": "Select(name='pais', options=['EC', 'CO', 'PE'])",
        "Badge": "Badge('Nuevo')",
        "Alert": "Alert('Operacion completada', kind='success')",
        "NavBar": "NavBar(brand=Heading('Marca', level=4), links=[Link('Inicio', href='/')])",
        "SideMenu": "SideMenu(title='Menu', items=[('Inicio', '/'), ('Docs', '/components')])",
        "Footer": "Footer(left=Text('© 2026'), right=Link('Inicio', href='/'))",
        "Tabs": "Tabs([('General', Text('...')), ('Avanzado', Text('...'))])",
        "Table": "Table(headers=['Nombre', 'Rol'], rows=[['Ana', 'Admin']])",
        "Modal": "Modal(id='demo', title='Demo', child=Text('Contenido'))",
        "ThemeToggle": "ThemeToggle()",
        "ApiCall": "ApiCall('/api/demo', method='GET', target='resultado')",
        "ResultBox": "ResultBox(id='resultado')",
        "Accordion": "Accordion([AccordionItem('Pregunta', Text('Respuesta'))])",
        "Calendar": "Calendar(events=[])", 
    }


    def _slug(name):
        return name.lower().replace("_", "-")


    def _example(name):
        return SNIPPETS.get(name, f"{name}(...)")


    def _section(widget_name):
        return Card(
            id=f"widget-{_slug(widget_name)}",
            padding=18,
            children=[
                Heading(widget_name, level=3, style="font-size:20px"),
                Text("Ejemplo de uso", style="font-size:13px;color:var(--text-muted)"),
                Code(_example(widget_name), language="python", block=True),
            ],
        )


    def components():
        items = [(name, f"#widget-{_slug(name)}") for name in WIDGETS]
        sections = [_section(name) for name in WIDGETS]

        responsive_css = Raw(
            "<style>"
            ".docs-layout{align-items:flex-start}"
            ".docs-content{flex:1;min-width:0}"
            "@media(max-width:900px){"
            ".docs-layout{flex-direction:column;padding:16px!important}"
            ".docs-menu{position:static!important;width:100%!important}"
            "}"
            "</style>"
        )

        return Column(
            children=[
                responsive_css,
                Row(
                    class_name="docs-layout",
                    gap=24,
                    style="max-width:1280px;margin:0 auto;padding:24px",
                    children=[
                        SideMenu(
                            class_name="docs-menu",
                            title="Widgets",
                            items=items,
                            width=260,
                            style="max-height:calc(100vh - 110px);overflow:auto",
                        ),
                        Column(
                            class_name="docs-content",
                            gap=16,
                            children=[
                                Heading("Componentes", level=1, style="font-size:38px"),
                                Paragraph(
                                    "Listado de widgets disponibles con snippet rapido para copiar.",
                                    style="color:var(--text-muted)",
                                ),
                                *sections,
                            ],
                        ),
                    ],
                ),
            ],
        ), PageConfig(title="Componentes - PROJECT_NAME")
    """
).strip() + "\n"


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
