"""
Martin CLI
Uso:
    martin new mi_proyecto
    martin run
    martin run --port 8080 --no-reload
    martin export
    martin export --out dist/index.html
"""

import argparse, os, sys, subprocess, textwrap
from pathlib import Path


# ── Plantilla de nuevo proyecto ───────────────────────────────────────────────

MAIN_PY = """\
from martin import App, Column, Card, Row, Spacer, Divider
from martin import Heading, Text, Paragraph, Link
from martin import Image, Icon, Badge, Avatar
from martin import Button, TextField, Select, MultiSelect
from martin import Border, Padding, Margin, Shadow, Size, Background, TextStyle, CSS, Colors


def build():
    return Column(
        gap=24,
        padding=32,
        children=[

            # ── Header ──────────────────────────────────────────────
            Row(justify="space-between", children=[
                Column(gap=4, children=[
                    Heading("{name}", level=1,
                        color=Colors.indigo,
                        style=TextStyle(size=28, weight="800")),
                    Text("Mi primer proyecto con Martin",
                        color=Colors.gray_500),
                ]),
                Badge("v0.1", background=Colors.indigo),
            ]),

            Divider(),

            # ── Cards ────────────────────────────────────────────────
            Row(gap=16, children=[
                Card(padding=20, radius=12, shadow=Shadow.md(), children=[
                    Icon("🚀", size=28),
                    Heading("Rápido", level=3,
                        style=TextStyle(size=16, weight="700")),
                    Text("Cero configuración.", color=Colors.gray_500),
                ]),
                Card(padding=20, radius=12, shadow=Shadow.md(), children=[
                    Icon("🎨", level=3, size=28),
                    Heading("Expresivo",
                        style=TextStyle(size=16, weight="700")),
                    Text("Estilos componibles.", color=Colors.gray_500),
                ]),
                Card(padding=20, radius=12, shadow=Shadow.md(), children=[
                    Icon("⚡", size=28),
                    Heading("Hot reload", level=3,
                        style=TextStyle(size=16, weight="700")),
                    Text("Guarda y se actualiza.", color=Colors.gray_500),
                ]),
            ]),

            # ── Botones ──────────────────────────────────────────────
            Row(gap=8, children=[
                Button("Primary", variant="primary", radius=8),
                Button("Ghost",   variant="ghost",   radius=8),
                Button("Danger",  variant="danger",  radius=8),
                Button("Custom",  background="#7c3aed", color="white", radius=999),
            ]),

            # ── Select ───────────────────────────────────────────────
            Select(
                options=[("py","Python"), ("js","JavaScript"), ("rs","Rust")],
                value="py",
                search=True,
                radius=8,
            ),

        ]
    )


if __name__ == "__main__":
    App(build=build, title="{name}").run()
"""

GITIGNORE = """\
__pycache__/
*.pyc
.DS_Store
dist/
"""

README = """\
# {name}

Proyecto creado con [Martin](https://github.com/tu-usuario/martin).

## Iniciar
```bash
martin run
```

## Exportar estático
```bash
martin export
```
"""


# ── Comandos ─────────────────────────────────────────────────────────────────


def cmd_new(args):
    name = args.name
    target = Path(name)

    if target.exists():
        print(f"❌  La carpeta '{name}' ya existe.")
        sys.exit(1)

    target.mkdir()
    (target / "assets").mkdir()

    (target / "main.py").write_text(MAIN_PY.replace("{name}", name), encoding="utf-8")
    (target / ".gitignore").write_text(GITIGNORE)
    (target / "README.md").write_text(README.replace("{name}", name), encoding="utf-8")

    print(
        f"""
  ✅  Proyecto creado en ./{name}/

  Siguiente paso:
    cd {name}
    martin run
"""
    )


def cmd_run(args):
    """Lanza el servidor de desarrollo recargando main.py."""
    main_file = Path(args.file)
    if not main_file.exists():
        print(f"❌  No se encuentra '{main_file}'. ¿Estás en la carpeta del proyecto?")
        sys.exit(1)

    # Añadimos el directorio actual al path para que los imports funcionen
    cwd = str(Path.cwd())
    if cwd not in sys.path:
        sys.path.insert(0, cwd)

    import importlib.util

    spec = importlib.util.spec_from_file_location("_martin_main", str(main_file))
    mod = importlib.util.module_from_spec(spec)
    sys.modules["_martin_main"] = mod
    spec.loader.exec_module(mod)

    if not hasattr(mod, "build"):
        print("❌  main.py debe tener una función 'build()'.")
        sys.exit(1)

    from martin import App

    hot = not args.no_reload
    App(
        build=mod.build,
        title=getattr(mod, "TITLE", Path.cwd().name),
        port=args.port,
        hot_reload=hot,
    ).run(watch_dir=cwd)


def cmd_export(args):
    main_file = Path(args.file)
    if not main_file.exists():
        print(f"❌  No se encuentra '{main_file}'.")
        sys.exit(1)

    cwd = str(Path.cwd())
    if cwd not in sys.path:
        sys.path.insert(0, cwd)

    import importlib.util

    spec = importlib.util.spec_from_file_location("_martin_main", str(main_file))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    if not hasattr(mod, "build"):
        print("❌  main.py debe tener una función 'build()'.")
        sys.exit(1)

    from martin import App

    out = args.out
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    App(build=mod.build, title=getattr(mod, "TITLE", "Martin App")).export(out)


def cmd_version(_):
    from martin import __version__

    print(f"martin {__version__}")


# ── Entry point ───────────────────────────────────────────────────────────────


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
            martin export --out dist/index.html
            martin version
        """
        ),
    )
    sub = parser.add_subparsers(dest="command", metavar="comando")

    # new
    p_new = sub.add_parser("new", help="Crea un nuevo proyecto")
    p_new.add_argument("name", help="Nombre del proyecto")

    # run
    p_run = sub.add_parser("run", help="Inicia el servidor de desarrollo")
    p_run.add_argument("--port", type=int, default=309, help="Puerto (default: 309)")
    p_run.add_argument(
        "--file", default="main.py", help="Fichero de entrada (default: main.py)"
    )
    p_run.add_argument("--no-reload", action="store_true", help="Desactiva hot reload")

    # export
    p_exp = sub.add_parser("export", help="Exporta a HTML estático")
    p_exp.add_argument(
        "--file", default="main.py", help="Fichero de entrada (default: main.py)"
    )
    p_exp.add_argument(
        "--out", default="dist/index.html", help="Destino (default: dist/index.html)"
    )

    # version
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
