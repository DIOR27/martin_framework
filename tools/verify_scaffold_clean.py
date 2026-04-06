#!/usr/bin/env python3
"""Verifica que el scaffold generado sea limpio (zero-noise) por defecto.

Objetivo: confirmar que no hay bloques de demostración de widgets (TODO, demos, etc.)
y que la salida sigue una estética minimalista.
"""

from pathlib import Path
import sys

SCaffold_DIR = Path(__file__).resolve().parents[2] / "scaffold_test_project"


def read(p: Path) -> str:
    with p.open("r", encoding="utf-8") as f:
        return f.read()


def main():
    if not SCaffold_DIR.exists():
        print(f" scaffold directory not found: {SCaffold_DIR}")
        sys.exit(2)
    main_py = SCaffold_DIR / "main.py"
    if not main_py.exists():
        print("main.py not found in scaffold; cannot verify.")
        sys.exit(3)
    content = read(main_py).lower()
    issues = []
    # No TODO blocks in the scaffold by default
    if "todowidget" in content or "todo" in content:
        issues.append("Found TodoWidget usage in scaffold main.py (noise).")
    # Make sure basic nav mentions exist (no noise indicators)
    if "counter" in content or "noise" in content:
        issues.append("Found noise indicators in scaffold content.")
    if issues:
        print("[FAIL] Scaffold is not clean:")
        for it in issues:
            print(" - " + it)
        sys.exit(4)
    print("[OK] Scaffold appears clean (zero-noise).")


if __name__ == "__main__":
    main()
