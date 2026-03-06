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

router = Router()
router.add("/",            home,       title="Inicio")
router.add("/about",       about,      title="Acerca de")
router.add("/components",  components, title="Componentes")

if __name__ == "__main__":
    App(router=router, title="{name}").run()
"""

PAGE_HOME = """\
from martin import (
    Raw,
    Column, Row, Card, Spacer, Divider,
    Heading, Text, Paragraph, Button, Icon, Badge,
    Border, Shadow, TextStyle, Glass, GradientText, MeshBackground, Colors,
)


def home():
    return Column(
        style=MeshBackground.dark(),
        children=[

            # ── Hero ────────────────────────────────────────────────────────
            Column(
                padding=80, gap=24,
                style="align-items: center; text-align: center; min-height: 80vh; justify-content: center",
                children=[

                    # Badge animado
                    Row(
                        gap=8,
                        style=[
                            Glass.dark(blur=12, opacity=0.06),
                            Border(radius=999),
                            "padding: 6px 16px; display: inline-flex; align-items: center",
                        ],
                        children=[
                            Raw(\'<span style="width:7px;height:7px;border-radius:50%;background:#34d399;animation:pulse 2s infinite"></span>\'),
                            Text("v0.1.0 · ahora disponible",
                                style=TextStyle(size=13, color="#a5b4fc")),
                        ]
                    ),

                    # Título con gradiente
                    Heading(
                        "{name}",
                        level=1,
                        style=[
                            GradientText.aurora(),
                            TextStyle(size=72, weight="800", letter_spacing=-3),
                        ]
                    ),

                    Paragraph(
                        "Build webs con Python puro. Sin HTML, sin CSS, sin JavaScript.",
                        style=TextStyle(size=20, color=Colors.rgba(148,163,184,0.85), line_height=1.6),
                    ),

                    Row(gap=12, children=[
                        Button("Empezar →",
                            background="linear-gradient(135deg, #6366f1, #818cf8)",
                            color="white",
                            radius=10,
                            padding=16,
                            style="border: none; font-size: 15px; font-weight: 700; box-shadow: 0 0 32px rgba(99,102,241,0.4)"
                        ),
                        Button("Ver componentes",
                            href="/components",
                            style=[
                                Glass.dark(opacity=0.06),
                                Border(radius=10),
                                "color: #cbd5e1; font-size: 15px; padding: 14px 24px",
                            ]
                        ),
                    ]),
                ]
            ),

            # ── Feature cards ────────────────────────────────────────────────
            Row(
                gap=16, padding=48,
                style="flex-wrap: wrap; justify-content: center",
                children=[_feature(icon, title, desc) for icon, title, desc in [
                    ("🧩", "Widget tree",      "Compón interfaces anidando componentes Python."),
                    ("🎨", "Estilos propios",  "Glass(), GradientText(), Shadow()... sin CSS."),
                    ("⚡", "Hot reload",       "Guarda el fichero y el navegador se actualiza."),
                    ("📄", "Multi-página",     "Router con páginas en ficheros separados."),
                    ("📦", "Zero deps",        "Solo stdlib de Python. watchdog opcional."),
                    ("🚀", "Export estático",  "martin export → HTML listo para deploy."),
                ]]
            ),

            # ── CSS para animación pulse ─────────────────────────────────────
            Raw(\'<style>@keyframes pulse{0%,100%{opacity:1;transform:scale(1)}50%{opacity:.5;transform:scale(.8)}}</style>\'),
        ]
    )


def _feature(icon, title, desc):
    from martin import Column, Heading, Text, Icon, Border, Shadow, Glass, TextStyle, Colors
    return Column(
        gap=12, padding=24,
        style=[
            Glass.dark(blur=20, opacity=0.07),
            Border(radius=16),
            Shadow(y=8, blur=24, color="rgba(0,0,0,0.2)"),
            "width: 280px; transition: transform 0.2s, box-shadow 0.2s",
            "cursor: default",
        ],
        children=[
            Icon(icon, size=32),
            Heading(title, level=3, style=TextStyle(size=15, weight="700", color="#f1f5f9")),
            Text(desc, style=TextStyle(size=13, color=Colors.rgba(203,213,225,0.75), line_height=1.6)),
        ]
    )
"""

PAGE_ABOUT = """\
from martin import (
    Raw,
    Column, Row, Card, Divider, Spacer,
    Heading, Text, Paragraph, Link, Avatar, Badge, Icon,
    Border, Shadow, TextStyle, Glass, GradientText, MeshBackground, Colors,
)


def about():
    return Column(
        style=MeshBackground.dark(),
        padding=64,
        gap=48,
        children=[

            # Header
            Column(gap=12, children=[
                Heading("Acerca de",
                    style=[GradientText.indigo_mint(), TextStyle(size=48, weight="800")]),
                Paragraph(
                    "Martin es un framework Python para construir interfaces web "
                    "usando componentes, al estilo de Flutter.",
                    style=TextStyle(size=18, color=Colors.rgba(148,163,184,0.85), line_height=1.7),
                ),
            ]),

            Divider(color="rgba(255,255,255,0.08)"),

            # Info cards
            Row(gap=16, style="flex-wrap: wrap", children=[

                Column(
                    gap=16, padding=28,
                    style=[Glass.dark(blur=20), Border(radius=16), Shadow.md(), "flex: 1; min-width: 240px"],
                    children=[
                        Icon("🎯", size=28),
                        Heading("Misión", level=3, style=TextStyle(size=16, weight="700", color="#f1f5f9")),
                        Text("Hacer el desarrollo web tan expresivo y placentero como Flutter.",
                            style=TextStyle(size=14, color=Colors.rgba(203,213,225,0.8), line_height=1.6)),
                    ]
                ),

                Column(
                    gap=16, padding=28,
                    style=[Glass.dark(blur=20), Border(radius=16), Shadow.md(), "flex: 1; min-width: 240px"],
                    children=[
                        Icon("🔧", size=28),
                        Heading("Stack", level=3, style=TextStyle(size=16, weight="700", color="#f1f5f9")),
                        Text("Python puro · stdlib · Sin dependencias obligatorias · watchdog opcional.",
                            style=TextStyle(size=14, color=Colors.rgba(203,213,225,0.8), line_height=1.6)),
                    ]
                ),

                Column(
                    gap=16, padding=28,
                    style=[Glass.dark(blur=20), Border(radius=16), Shadow.md(), "flex: 1; min-width: 240px"],
                    children=[
                        Icon("📅", size=28),
                        Heading("Puerto", level=3, style=TextStyle(size=16, weight="700", color="#f1f5f9")),
                        Text("El puerto por defecto es 309, en honor al 03 de septiembre. ♥",
                            style=TextStyle(size=14, color=Colors.rgba(203,213,225,0.8), line_height=1.6)),
                    ]
                ),
            ]),

            Link("← Volver al inicio", href="/",
                style=TextStyle(size=14, color="#818cf8")),
        ]
    )
"""

PAGE_COMPONENTS = """\
from martin import (
    Raw,
    Column, Row, Grid, Card, Spacer, Divider,
    Heading, Text, Paragraph, Code, Badge, Avatar, Icon,
    Button, TextField, Select, MultiSelect, Checkbox,
    Border, Shadow, Padding, TextStyle,
    Glass, GradientText, MeshBackground, Colors,
)


def components():
    return Column(
        style=MeshBackground.dark(),
        padding=48,
        gap=48,
        children=[

            Heading("Componentes",
                style=[GradientText.aurora(), TextStyle(size=48, weight="800")]),

            # ── Botones ──────────────────────────────────────────────────────
            _section("Buttons", [
                Row(gap=12, style="flex-wrap: wrap", children=[
                    Button("Primary",   variant="primary",   radius=8),
                    Button("Secondary", variant="secondary", radius=8),
                    Button("Danger",    variant="danger",    radius=8),
                    Button("Ghost",     variant="ghost",     radius=8),
                    Button("Custom",
                        background="linear-gradient(135deg,#7c3aed,#a855f7)",
                        color="white", radius=999, padding=14,
                        style="border:none;font-weight:700"),
                    Button("Glass",
                        style=[Glass.dark(opacity=0.08), Border(radius=8),
                               "color:#a5b4fc;padding:8px 16px"]),
                ]),
            ]),

            # ── Badges ───────────────────────────────────────────────────────
            _section("Badges", [
                Row(gap=8, style="flex-wrap: wrap", children=[
                    Badge("Python",     background=Colors.indigo,  color="white"),
                    Badge("v0.1.0",     background=Colors.purple,  color="white"),
                    Badge("Nuevo",      background=Colors.green,   color="white"),
                    Badge("Beta",       background=Colors.orange,  color="white"),
                    Badge("Deprecated", background=Colors.red,     color="white"),
                    Badge("Glass",
                        style=[Glass.dark(opacity=0.1), Border(radius=999),
                               "color:#a5b4fc;padding:4px 12px;font-size:12px;font-weight:600"]),
                ]),
            ]),

            # ── Inputs ───────────────────────────────────────────────────────
            _section("Inputs", [
                Column(gap=12, children=[
                    Row(gap=12, children=[
                        TextField(placeholder="Nombre", radius=8, style="flex:1"),
                        TextField(placeholder="Email", type="email", radius=8, style="flex:1"),
                    ]),
                    Select(
                        options=[("py","🐍 Python"),("js","🌐 JavaScript"),("rs","🦀 Rust")],
                        value="py", search=True, radius=8,
                    ),
                    MultiSelect(
                        options=["Diseño","Frontend","Backend","DevOps","Testing","Documentación"],
                        values=["Diseño","Frontend"],
                        placeholder="Añadir área...",
                        tag_color="rgba(99,102,241,0.2)",
                        tag_border="rgba(99,102,241,0.4)",
                        tag_text="#a5b4fc",
                        radius=8,
                    ),
                    Checkbox(label="Acepto los términos y condiciones"),
                ]),
            ]),

            # ── Glass cards ──────────────────────────────────────────────────
            _section("Glass", [
                Row(gap=16, style="flex-wrap:wrap", children=[
                    Column(
                        gap=8, padding=20,
                        style=[Glass.dark(), Border(radius=12), Shadow.md(), "flex:1;min-width:160px"],
                        children=[Icon("🌑",size=24), Text("Glass.dark()", style=TextStyle(size=13,color="#e2e8f0"))],
                    ),
                    Column(
                        gap=8, padding=20,
                        style=[Glass.light(opacity=0.15), Border(radius=12), Shadow.md(), "flex:1;min-width:160px;background:rgba(255,255,255,0.12)"],
                        children=[Icon("☀️",size=24), Text("Glass.light()", style=TextStyle(size=13,color="#e2e8f0"))],
                    ),
                    Column(
                        gap=8, padding=20,
                        style=[Glass.colored("#6366f1",0.2), Border(radius=12), Shadow.md(), "flex:1;min-width:160px"],
                        children=[Icon("💜",size=24), Text("Glass.colored()", style=TextStyle(size=13,color="#e2e8f0"))],
                    ),
                    Column(
                        gap=8, padding=20,
                        style=[Glass.colored("#34d399",0.2), Border(radius=12), Shadow.md(), "flex:1;min-width:160px"],
                        children=[Icon("💚",size=24), Text("Glass.colored('#34d399')", style=TextStyle(size=13,color="#e2e8f0"))],
                    ),
                ]),
            ]),

            # ── Gradiente texto ──────────────────────────────────────────────
            _section("GradientText", [
                Column(gap=8, children=[
                    Heading("Aurora",    level=3, style=[GradientText.aurora(),    TextStyle(size=28,weight="800")]),
                    Heading("Indigo",    level=3, style=[GradientText.indigo_mint(),TextStyle(size=28,weight="800")]),
                    Heading("Fire",      level=3, style=[GradientText.fire(),      TextStyle(size=28,weight="800")]),
                    Heading("Ocean",     level=3, style=[GradientText.ocean(),     TextStyle(size=28,weight="800")]),
                    Heading("Rose Gold", level=3, style=[GradientText.rose_gold(), TextStyle(size=28,weight="800")]),
                ]),
            ]),

            Divider(color="rgba(255,255,255,0.08)"),
            Row(justify="space-between", children=[
                Text("Martin Framework", style=TextStyle(size=13, color=Colors.rgba(148,163,184,0.5))),
                Text("Puerto 309 · 03 de septiembre ♥", style=TextStyle(size=13, color=Colors.rgba(148,163,184,0.5))),
            ]),
        ]
    )


def _section(title, children):
    from martin import Column, Heading, TextStyle, Glass, Border, Shadow, Colors
    return Column(
        gap=16, padding=28,
        style=[Glass.dark(blur=16, opacity=0.06), Border(radius=16), Shadow.sm()],
        children=[
            Heading(title, level=2,
                style=TextStyle(size=13, weight="700", color=Colors.rgba(148,163,184,0.6),
                                letter_spacing=2, transform="uppercase")),
            *children,
        ]
    )
"""

GITIGNORE = "__pycache__/\n*.pyc\n.DS_Store\ndist/\n"

README = """\
# {name}

Proyecto Martin. Ejecuta con:

```bash
martin run
```

## Páginas
- `/`            → `pages/home.py`
- `/about`       → `pages/about.py`
- `/components`  → `pages/components.py`

## Añadir una página nueva
1. Crea `pages/mi_pagina.py` con una función `mi_pagina()`
2. En `main.py`: `from pages.mi_pagina import mi_pagina`
3. Añade: `router.add("/mi-ruta", mi_pagina, title="Mi Página")`
"""


# ══════════════════════════════════════════════════════════
# COMANDOS
# ══════════════════════════════════════════════════════════


def cmd_new(args):
    name = args.name
    target = Path(name)

    if target.exists():
        print(f"❌  La carpeta '{name}' ya existe.")
        sys.exit(1)

    target.mkdir()
    (target / "assets").mkdir()
    (target / "pages").mkdir()
    (target / "pages" / "__init__.py").write_text("", encoding="utf-8")

    (target / "main.py").write_text(MAIN_PY.replace("{name}", name), encoding="utf-8")
    (target / "pages" / "home.py").write_text(
        PAGE_HOME.replace("{name}", name), encoding="utf-8"
    )
    (target / "pages" / "about.py").write_text(
        PAGE_ABOUT.replace("{name}", name), encoding="utf-8"
    )
    (target / "pages" / "components.py").write_text(
        PAGE_COMPONENTS.replace("{name}", name), encoding="utf-8"
    )
    (target / ".gitignore").write_text(GITIGNORE)
    (target / "README.md").write_text(README.replace("{name}", name), encoding="utf-8")

    print(
        f"""
  ✅  Proyecto '{name}' creado

  Estructura:
    {name}/
    ├── main.py          ← punto de entrada + router
    ├── pages/
    │   ├── home.py      ← página /
    │   ├── about.py     ← página /about
    │   └── components.py← página /components
    └── assets/

  Siguiente:
    cd {name}
    martin run
"""
    )


def cmd_run(args):
    main_file = Path(args.file)
    if not main_file.exists():
        print(f"❌  No se encuentra '{main_file}'. ¿Estás en la carpeta del proyecto?")
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

    # Soporte para router o build function
    if hasattr(mod, "router"):
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
        print("❌  main.py debe tener una función 'build()' o un objeto 'router'.")
        sys.exit(1)

    app.run(watch_dir=cwd, source_file=source_file)


def cmd_export(args):
    main_file = Path(args.file)
    if not main_file.exists():
        print(f"❌  No se encuentra '{main_file}'.")
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

    if hasattr(mod, "router"):
        app = App(router=mod.router, title=getattr(mod, "TITLE", "Martin App"))
        app.export_all(out_dir=args.out if args.out != "dist/index.html" else "dist")
    elif hasattr(mod, "build"):
        app = App(build=mod.build, title=getattr(mod, "TITLE", "Martin App"))
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        app.export(args.out)
    else:
        print("❌  main.py debe tener 'build' o 'router'.")
        sys.exit(1)


def cmd_version(_):
    from martin import __version__

    print(f"martin {__version__}")


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

    p_exp = sub.add_parser("export", help="Exporta a HTML estático")
    p_exp.add_argument("--file", default="main.py", help="Fichero de entrada")
    p_exp.add_argument("--out", default="dist/index.html", help="Destino")

    sub.add_parser("version", help="Muestra la versión")

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
