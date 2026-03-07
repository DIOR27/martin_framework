"""Martin CLI"""

import argparse, os, sys, textwrap
from pathlib import Path


# ══════════════════════════════════════════════════════════
# TEMPLATES
# ══════════════════════════════════════════════════════════

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
app = App(router=router, title="PROJECT_NAME", theme="auto")


if __name__ == "__main__":
    app.run()
"""

PAGE_HOME = """\
from martin import (
    Raw, Column, Row, Spacer, Divider,
    Heading, Text, Paragraph, Button, Icon, Badge,
    Border, Shadow, TextStyle, Glass, GradientText, MeshBackground, Colors,
)


def home():
    return Column(
        style=MeshBackground.themed(),
        children=[

            Column(
                padding=80, gap=24,
                style="align-items:center; text-align:center; min-height:80vh; justify-content:center",
                children=[

                    Row(
                        gap=8,
                        style=[
                            Glass.dark(blur=12, opacity=0.06),
                            Border(radius=999),
                            "padding:6px 16px; display:inline-flex; align-items:center",
                        ],
                        children=[
                            Raw('<span style="width:7px;height:7px;border-radius:50%%;'
                                'background:#34d399;animation:pulse 2s infinite"></span>'),
                            Text("v0.1.0 - ahora disponible",
                                 style=TextStyle(size=13, color="var(--accent)")),
                        ]
                    ),

                    Heading(
                        "PROJECT_NAME", level=1,
                        style=[
                            GradientText.aurora(),
                            TextStyle(size=72, weight="800", letter_spacing=-3),
                        ]
                    ),

                    Paragraph(
                        "Build webs con Python puro. Sin HTML, sin CSS, sin JavaScript.",
                        style=TextStyle(size=20, color="var(--text-muted)", line_height=1.6),
                    ),

                    Row(gap=12, children=[
                        Button(
                            "Empezar ->",
                            background="linear-gradient(135deg, #6366f1, #818cf8)",
                            color="white", radius=10, padding=16,
                            style="border:none; font-size:15px; font-weight:700; "
                                  "box-shadow:0 0 32px rgba(99,102,241,0.4)",
                        ),
                        Button(
                            "Ver componentes", href="/components",
                            style=[
                                Glass.dark(opacity=0.06),
                                Border(radius=10),
                                "color:var(--text-muted); font-size:15px; padding:14px 24px",
                            ]
                        ),
                    ]),
                ]
            ),

            Row(
                gap=16, padding=48,
                style="flex-wrap:wrap; justify-content:center",
                children=[_feature(i, t, d) for i, t, d in [
                    ("🧩", "Widget tree",     "Compón interfaces anidando componentes Python."),
                    ("🎨", "Estilos propios", "Glass(), GradientText(), Shadow()... sin CSS."),
                    ("⚡", "Hot reload",      "Guarda el fichero y el navegador se actualiza."),
                    ("📄", "Multi-pagina",    "Router con paginas en ficheros separados."),
                    ("📦", "Zero deps",       "Solo stdlib de Python. watchdog opcional."),
                    ("🚀", "Export",          "martin export -> HTML listo para deploy."),
                ]],
            ),

            Raw('<style>@keyframes pulse{'
                '0%%,100%%{opacity:1;transform:scale(1)}'
                '50%%{opacity:.5;transform:scale(.8)}}</style>'),
        ]
    )


def _feature(icon, title, desc):
    from martin import Column, Heading, Text, Icon, Border, Shadow, Glass, TextStyle
    return Column(
        gap=12, padding=24,
        style=[
            "background:var(--surface); border:1px solid var(--border)",
            Border(radius=16),
            Shadow(y=8, blur=24, color="rgba(0,0,0,0.1)"),
            "width:280px; transition:transform 0.2s",
        ],
        children=[
            Icon(icon, size=32),
            Heading(title, level=3,
                    style=TextStyle(size=15, weight="700", color="var(--text)")),
            Text(desc, style=TextStyle(size=13, color="var(--text-muted)", line_height=1.6)),
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
                      "El puerto por defecto es 309, en honor al 03 de septiembre."),
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
    Column, Row, Divider, Heading, Text, Badge, Icon,
    Button, TextField, Select, MultiSelect, Checkbox,
    Border, Shadow, TextStyle, Glass, GradientText, MeshBackground, Colors,
)


def components():
    return Column(
        style=MeshBackground.themed(), padding=48, gap=48,
        children=[

            Heading("Componentes",
                    style=[GradientText.aurora(), TextStyle(size=48, weight="800")]),

            _section("Buttons", [
                Row(gap=12, style="flex-wrap:wrap", children=[
                    Button("Primary",   variant="primary",   radius=8),
                    Button("Secondary", variant="secondary", radius=8),
                    Button("Danger",    variant="danger",    radius=8),
                    Button("Ghost",     variant="ghost",     radius=8),
                    Button("Custom",
                           background="linear-gradient(135deg,#7c3aed,#a855f7)",
                           color="white", radius=999, padding=14,
                           style="border:none; font-weight:700"),
                    Button("Glass",
                           style=[Glass.dark(opacity=0.08), Border(radius=8),
                                  "color:var(--accent); padding:8px 16px"]),
                ]),
            ]),

            _section("Badges", [
                Row(gap=8, style="flex-wrap:wrap", children=[
                    Badge("Python",     background=Colors.indigo, color="white"),
                    Badge("v0.1.0",     background=Colors.purple, color="white"),
                    Badge("Nuevo",      background=Colors.green,  color="white"),
                    Badge("Beta",       background=Colors.orange, color="white"),
                    Badge("Deprecated", background=Colors.red,    color="white"),
                ]),
            ]),

            _section("Inputs", [
                Column(gap=12, children=[
                    Row(gap=12, children=[
                        TextField(placeholder="Nombre", radius=8, style="flex:1"),
                        TextField(placeholder="Email", type="email", radius=8, style="flex:1"),
                    ]),
                    Select(
                        options=[("py", "Python"), ("js", "JavaScript"), ("rs", "Rust")],
                        value="py", search=True, radius=8,
                    ),
                    MultiSelect(
                        options=["Diseno", "Frontend", "Backend", "DevOps", "Testing"],
                        values=["Diseno", "Frontend"],
                        placeholder="Anadir area...",
                        tag_color="rgba(99,102,241,0.15)",
                        tag_border="rgba(99,102,241,0.3)",
                        tag_text="var(--accent)",
                        radius=8,
                    ),
                    Checkbox(label="Acepto los terminos y condiciones"),
                ]),
            ]),

            _section("Glass", [
                Row(gap=16, style="flex-wrap:wrap", children=[
                    _glass("🌑", "Glass.dark()",          Glass.dark()),
                    _glass("💜", "Glass.colored(indigo)", Glass.colored("#6366f1", 0.2)),
                    _glass("💚", "Glass.colored(green)",  Glass.colored("#34d399", 0.2)),
                ]),
            ]),

            _section("GradientText", [
                Column(gap=8, children=[
                    Heading("Aurora",    level=3, style=[GradientText.aurora(),
                            TextStyle(size=28, weight="800")]),
                    Heading("Fire",      level=3, style=[GradientText.fire(),
                            TextStyle(size=28, weight="800")]),
                    Heading("Ocean",     level=3, style=[GradientText.ocean(),
                            TextStyle(size=28, weight="800")]),
                    Heading("Rose Gold", level=3, style=[GradientText.rose_gold(),
                            TextStyle(size=28, weight="800")]),
                ]),
            ]),

            Divider(color="var(--border)"),
            Row(justify="space-between", children=[
                Text("Martin Framework",
                     style=TextStyle(size=13, color="var(--text-muted)")),
                Text("Puerto 309 · 03 de septiembre",
                     style=TextStyle(size=13, color="var(--text-muted)")),
            ]),
        ]
    )


def _section(title, children):
    from martin import Column, Heading, TextStyle, Border, Shadow
    return Column(
        gap=16, padding=28,
        style=[
            "background:var(--surface); border:1px solid var(--border)",
            Border(radius=16),
            Shadow(y=2, blur=8, color="rgba(0,0,0,0.06)"),
        ],
        children=[
            Heading(title, level=2,
                    style=TextStyle(size=12, weight="700",
                                    color="var(--text-muted)",
                                    letter_spacing=2, transform="uppercase")),
            *children,
        ]
    )


def _glass(icon, label, glass_style):
    from martin import Column, Text, Icon, Border, Shadow, TextStyle
    return Column(
        gap=8, padding=20,
        style=[glass_style, Border(radius=12), Shadow.md(), "flex:1; min-width:160px"],
        children=[
            Icon(icon, size=24),
            Text(label, style=TextStyle(size=13, color="var(--text)")),
        ]
    )
"""

GITIGNORE = "__pycache__/\n*.pyc\n.DS_Store\ndist/\n.venv/\n"

README = """\
# {name}

Proyecto Martin. Ejecuta con:

```bash
martin run
```

## Paginas
- `/`            -> `pages/home.py`
- `/about`       -> `pages/about.py`
- `/components`  -> `pages/components.py`

## Anadir una pagina nueva
1. Crea `pages/mi_pagina.py` con una funcion `mi_pagina()`
2. En `main.py`: `from pages.mi_pagina import mi_pagina`
3. Anade: `router.add("/mi-ruta", mi_pagina, title="Mi Pagina")`
"""


# ══════════════════════════════════════════════════════════
# COMANDOS
# ══════════════════════════════════════════════════════════


def _write_api_example(path):
    """Escribe pages/api_example.py en el proyecto nuevo."""
    code = 'from martin import (\n    Column, Heading, Text, Paragraph, Button,\n    Select, MultiSelect, ResultBox, ApiCall,\n    Border, Shadow, TextStyle,\n    GradientText, MeshBackground,\n)\n\n\n# ── Endpoints de esta página ──────────────────────────────\n# Martin llama a register_routes(app) automáticamente\n# cuando esta página se añade al router.\n\ndef register_routes(app):\n\n    @app.route("/api/seleccion", methods=["POST"])\n    def api_seleccion(req):\n        data     = req.json()\n        lenguaje = data.get("lang_select", {})   # id del Select\n        areas    = data.get("areas_multi",  {})   # id del MultiSelect\n        return {\n            "ok": True,\n            "recibido": {\n                "lenguaje": lenguaje.get("etiqueta"),\n                "areas":    areas.get("etiquetas", []),\n            },\n            "mensaje": (\n                f"Lenguaje: {lenguaje.get(\'etiqueta\', \'?\')}. "\n                f"Areas: {\', \'.join(areas.get(\'etiquetas\', [])) or \'ninguna\'}."\n            ),\n        }\n\n\n# ── UI de la página ───────────────────────────────────────\n\ndef api_example():\n    return Column(\n        style=MeshBackground.themed(), padding=48, gap=32,\n        children=[\n\n            Column(gap=8, children=[\n                Heading(\n                    "Ejemplo de Backend",\n                    style=[GradientText.aurora(), TextStyle(size=40, weight="800")],\n                ),\n                Paragraph(\n                    "Selecciona valores y presiona el boton. "\n                    "El boton llama a una funcion Python en el servidor.",\n                    style=TextStyle(size=16, color="var(--text-muted)"),\n                ),\n            ]),\n\n            Column(\n                gap=20, padding=28,\n                style=[\n                    "background:var(--surface); border:1px solid var(--border)",\n                    Border(radius=16),\n                    Shadow(y=4, blur=20, color="rgba(0,0,0,0.1)"),\n                    "max-width:520px; width:100%",\n                ],\n                children=[\n\n                    Column(gap=6, children=[\n                        Text("Lenguaje",\n                             style=TextStyle(size=13, weight="600",\n                                             color="var(--text-muted)")),\n                        Select(\n                            id="lang_select",\n                            options=[\n                                ("py", "Python"),\n                                ("js", "JavaScript"),\n                                ("rs", "Rust"),\n                                ("go", "Go"),\n                                ("ts", "TypeScript"),\n                            ],\n                            value="py",\n                            search=True,\n                            radius=8,\n                        ),\n                    ]),\n\n                    Column(gap=6, children=[\n                        Text("Areas de trabajo",\n                             style=TextStyle(size=13, weight="600",\n                                             color="var(--text-muted)")),\n                        MultiSelect(\n                            id="areas_multi",\n                            options=["Diseno", "Frontend", "Backend",\n                                     "DevOps", "Testing", "Mobile"],\n                            values=["Frontend"],\n                            placeholder="Anadir area...",\n                            radius=8,\n                        ),\n                    ]),\n\n                    Button(\n                        "Enviar al servidor ->",\n                        id="send_btn",\n                        background="linear-gradient(135deg, #6366f1, #818cf8)",\n                        color="white",\n                        radius=10,\n                        style=(\n                            "border:none; font-size:15px; font-weight:700;"\n                            " padding:14px 24px;"\n                            " box-shadow:0 0 24px rgba(99,102,241,0.35);"\n                        ),\n                        on_click=ApiCall(\n                            "/api/seleccion",\n                            method="POST",\n                            target="resultado",\n                            loading="Enviando...",\n                        ),\n                    ),\n\n                    ResultBox(\n                        id="resultado",\n                        format="json",\n                    ),\n\n                ],\n            ),\n        ],\n    )\n'
    path.write_text(code, encoding="utf-8")


def cmd_new(args):
    name = args.name
    target = Path(name)

    if target.exists():
        print("ERROR: La carpeta '" + name + "' ya existe.")
        sys.exit(1)

    target.mkdir()
    (target / "assets").mkdir()
    (target / "pages").mkdir()
    (target / "pages" / "__init__.py").write_text("", encoding="utf-8")

    (target / "main.py").write_text(
        MAIN_PY.replace("PROJECT_NAME", name), encoding="utf-8"
    )
    (target / "pages" / "home.py").write_text(
        PAGE_HOME.replace("PROJECT_NAME", name), encoding="utf-8"
    )
    (target / "pages" / "about.py").write_text(
        PAGE_ABOUT.replace("PROJECT_NAME", name), encoding="utf-8"
    )
    (target / "pages" / "components.py").write_text(
        PAGE_COMPONENTS.replace("PROJECT_NAME", name), encoding="utf-8"
    )
    _write_api_example(target / "pages" / "api_example.py")
    (target / ".gitignore").write_text(GITIGNORE)
    (target / "README.md").write_text(README.replace("{name}", name), encoding="utf-8")

    print("")
    print("  OK  Proyecto '" + name + "' creado")
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
        print(
            "ERROR: No se encuentra '"
            + args.file
            + "'. Estas en la carpeta del proyecto?"
        )
        sys.exit(1)

    cwd = str(Path.cwd())
    if cwd not in sys.path:
        sys.path.insert(0, cwd)

    import importlib.util

    source_file = str(main_file.resolve())
    spec = importlib.util.spec_from_file_location("_martin_main", source_file)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["_martin_main"] = mod
    spec.loader.exec_module(mod)

    from martin import App

    hot = not args.no_reload

    # Si main.py ya define un objeto `app` (App instance), usarlo directamente.
    # Esto preserva los @app.route() y cualquier config custom.
    if hasattr(mod, "app") and isinstance(mod.app, App):
        app = mod.app
        app.hot_reload = hot
        if args.port != 309:  # solo sobreescribir si se pasó explícito
            app.port = args.port
    elif hasattr(mod, "router"):
        app = App(
            router=mod.router,
            title=getattr(mod, "TITLE", Path.cwd().name),
            port=args.port,
            hot_reload=hot,
        )
    elif hasattr(mod, "build"):
        app = App(
            build=mod.build,
            title=getattr(mod, "TITLE", Path.cwd().name),
            port=args.port,
            hot_reload=hot,
        )
    else:
        print(
            "ERROR: main.py debe definir un objeto 'app', una funcion 'build()' o un 'router'."
        )
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

    spec = importlib.util.spec_from_file_location(
        "_martin_main", str(main_file.resolve())
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    from martin import App

    fmt = getattr(args, "format", "html")
    out_dir = getattr(args, "out", "dist")

    if hasattr(mod, "router"):
        app = App(
            router=mod.router,
            title=getattr(mod, "TITLE", "Martin App"),
            hot_reload=False,
        )
    elif hasattr(mod, "build"):
        app = App(
            build=mod.build, title=getattr(mod, "TITLE", "Martin App"), hot_reload=False
        )
    else:
        print("ERROR: main.py debe tener 'build' o 'router'.")
        sys.exit(1)

    print("\n  Exportando (" + fmt + ") -> " + out_dir + "/\n")

    if fmt == "split":
        from martin.exporter import export_split

        export_split(app, out_dir=out_dir, assets_src="assets")
    else:
        if hasattr(mod, "router"):
            app.export_all(out_dir=out_dir)
        else:
            out_path = Path(out_dir) / "index.html"
            out_path.parent.mkdir(parents=True, exist_ok=True)
            app.export(str(out_path))


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
        epilog=textwrap.dedent(
            """\
          Ejemplos:
            martin new mi_proyecto
            martin run
            martin run --port 8080
            martin run --no-reload
            martin export
            martin export --format split
            martin export --format split --out build
            martin version
        """
        ),
    )
    sub = parser.add_subparsers(dest="command", metavar="comando")

    p_new = sub.add_parser("new", help="Crea un nuevo proyecto")
    p_new.add_argument("name", help="Nombre del proyecto")

    p_run = sub.add_parser("run", help="Inicia el servidor de desarrollo")
    p_run.add_argument("--port", type=int, default=309, help="Puerto (default: 309)")
    p_run.add_argument("--file", default="main.py", help="Fichero de entrada")
    p_run.add_argument("--no-reload", action="store_true", help="Desactiva hot reload")

    p_exp = sub.add_parser("export", help="Exporta el proyecto")
    p_exp.add_argument("--file", default="main.py", help="Fichero de entrada")
    p_exp.add_argument(
        "--out", default="dist", help="Carpeta de destino (default: dist)"
    )
    p_exp.add_argument(
        "--format",
        default="html",
        choices=["html", "split"],
        help="html = un fichero por pagina | split = HTML + CSS + JS separados",
    )

    sub.add_parser("version", help="Muestra la version")

    args = parser.parse_args()

    if args.command == "new":
        cmd_new(args)
    elif args.command == "run":
        cmd_run(args)
    elif args.command == "export":
        cmd_export(args)
    elif args.command == "version":
        cmd_version(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
