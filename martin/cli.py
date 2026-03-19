"""Martin CLI"""

import argparse
import importlib.util
import sys
import textwrap
from pathlib import Path

from .scaffold import (
    DEFAULT_PROJECT_DESC,
    copy_default_icon,
    render_new_project_files,
)


def _prompt(label, default=""):
    """Pregunta interactiva con valor por defecto."""
    hint = f" [{default}]" if default else ""
    try:
        val = input(f"  {label}{hint}: ").strip()
    except (EOFError, KeyboardInterrupt):
        print("")
        val = ""
    return val or default


def _write_project_files(target: Path, files: dict):
    """Escribe archivos relativos al root del proyecto."""
    for rel_path, content in files.items():
        path = target / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


def _print_new_project_summary(name: str, title: str, desc: str):
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
    print("    |   +-- components.py")
    print("    +-- assets/")
    print("")
    print("  Siguiente:")
    print("    cd " + name)
    print("    martin run")
    print("")


def _ensure_cwd_on_syspath():
    cwd = str(Path.cwd())
    if cwd not in sys.path:
        sys.path.insert(0, cwd)
    return cwd


def _load_module_from_file(main_file: Path, module_name: str):
    source_file = str(main_file.resolve())
    spec = importlib.util.spec_from_file_location(module_name, source_file)
    if spec is None or spec.loader is None:
        raise RuntimeError("No se pudo cargar el módulo: " + source_file)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = mod
    spec.loader.exec_module(mod)
    return mod, source_file


def cmd_new(args):
    name = args.name
    target = Path(name)

    if target.exists():
        print("ERROR: La carpeta '" + name + "' ya existe.")
        sys.exit(1)

    print("")
    print("  Nuevo proyecto Martin · '" + name + "'")
    print("  " + "─" * 38)

    title = _prompt("Título del proyecto", default=name)
    desc = _prompt("Descripción", default=DEFAULT_PROJECT_DESC)

    print("")

    target.mkdir()
    assets_dir = target / "assets"
    assets_dir.mkdir()
    copy_default_icon(assets_dir)

    files = render_new_project_files(name=name, title=title, desc=desc)
    _write_project_files(target, files)
    _print_new_project_summary(name, title, desc)


def cmd_run(args):
    main_file = Path(args.file)
    if not main_file.exists():
        print("ERROR: No se encuentra '" + args.file + "'. Estas en la carpeta del proyecto?")
        sys.exit(1)

    cwd = _ensure_cwd_on_syspath()
    mod, source_file = _load_module_from_file(main_file, "_martin_main")

    from martin import App

    hot = not args.no_reload

    if hasattr(mod, "app") and isinstance(mod.app, App):
        app = mod.app
        app.hot_reload = hot
        if args.port != 3908:
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
        print("ERROR: main.py debe definir un objeto 'app', una funcion 'build()' o un 'router'.")
        sys.exit(1)

    app.run(open_browser=bool(getattr(args, "open", False)), watch_dir=cwd, source_file=source_file)


def cmd_export(args):
    main_file = Path(args.file)
    if not main_file.exists():
        print("ERROR: No se encuentra '" + args.file + "'.")
        sys.exit(1)

    _ensure_cwd_on_syspath()
    mod, _ = _load_module_from_file(main_file, "_martin_export_main")

    from martin import App

    fmt = getattr(args, "format", "html")
    out_dir = getattr(args, "out", "dist")
    with_backend = bool(getattr(args, "with_backend", False))

    if hasattr(mod, "router"):
        app = App(
            router=mod.router,
            title=getattr(mod, "TITLE", "Martin App"),
            hot_reload=False,
        )
    elif hasattr(mod, "build"):
        app = App(
            build=mod.build,
            title=getattr(mod, "TITLE", "Martin App"),
            hot_reload=False,
        )
    else:
        print("ERROR: main.py debe tener 'build' o 'router'.")
        sys.exit(1)

    mode_label = fmt + (" + backend" if with_backend else "")
    print("\n  Exportando (" + mode_label + ") -> " + out_dir + "/\n")

    if with_backend:
        from martin.exporter import export_with_backend

        export_with_backend(
            app,
            out_dir=out_dir,
            assets_src="assets",
            source_file=str(main_file),
            project_root=str(Path.cwd()),
            fmt=fmt,
        )
    elif fmt == "split":
        from martin.exporter import export_split

        export_split(app, out_dir=out_dir, assets_src="assets")
    else:
        from martin.exporter import export_html

        export_html(app, out_dir=out_dir)


def cmd_version(args):
    from martin import __version__

    print("martin " + __version__)


def _build_parser():
    parser = argparse.ArgumentParser(
        prog="martin",
        description="Martin — Python web framework",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent(
            """\
          Ejemplos:
            martin new mi_proyecto
            martin run
            martin run --open
            martin run --port 8080
            martin run --no-reload
            martin export
            martin export --out build
            martin export --format html
            martin export --with-backend
            martin version
        """
        ),
    )
    sub = parser.add_subparsers(dest="command", metavar="comando")

    p_new = sub.add_parser("new", help="Crea un nuevo proyecto")
    p_new.add_argument("name", help="Nombre del proyecto")

    p_run = sub.add_parser("run", help="Inicia el servidor de desarrollo")
    p_run.add_argument("--port", type=int, default=3908, help="Puerto (default: 3908)")
    p_run.add_argument("--file", default="main.py", help="Fichero de entrada")
    p_run.add_argument("--no-reload", action="store_true", help="Desactiva hot reload")
    p_run.add_argument("--open", action="store_true", help="Abre el navegador al iniciar")

    p_exp = sub.add_parser("export", help="Exporta el proyecto")
    p_exp.add_argument("--file", default="main.py", help="Fichero de entrada")
    p_exp.add_argument("--out", default="dist", help="Carpeta de destino (default: dist)")
    p_exp.add_argument(
        "--format",
        default="split",
        choices=["html", "split"],
        help="html = un fichero por pagina | split = HTML + CSS + JS separados",
    )
    p_exp.add_argument(
        "--with-backend",
        action="store_true",
        help="Genera export hibrido: frontend estatico + runtime Python para backend",
    )

    sub.add_parser("version", help="Muestra la version")
    return parser


def main():
    parser = _build_parser()
    args = parser.parse_args()

    commands = {
        "new": cmd_new,
        "run": cmd_run,
        "export": cmd_export,
        "version": cmd_version,
    }

    cmd = commands.get(args.command)
    if cmd:
        cmd(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
