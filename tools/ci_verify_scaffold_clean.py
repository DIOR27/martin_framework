#!/usr/bin/env python3
"""CI helper: verify that the generated scaffold is zero-noise by default.

This script renders a scaffold into a temporary directory and checks that
the generated main.py does not contain noise/demo blocks (like TODOs).
"""

import os
import sys
import tempfile
from pathlib import Path


def render_ci_scaffold(name: str, title: str, desc: str, tmp_dir: Path) -> Path:
    from martin_framework.martin.scaffold import render_new_project_files

    files = render_new_project_files(name, title, desc)
    root = tmp_dir / name
    root.mkdir(parents=True, exist_ok=True)
    for rel, content in files.items():
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            f.write(content)
    return root


def is_clean(main_py_path: Path) -> (bool, list[str]):
    issues = []
    try:
        content = main_py_path.read_text(encoding="utf-8").lower()
    except Exception:
        return False, ["Cannot read main.py for inspection."]
    if "todo" in content:
        issues.append("TODO keyword found in scaffold (noise).")
    if "todowidget" in content:
        issues.append("TodoWidget usage detected in scaffold (noise).")
    if "noise" in content or "demonstration" in content:
        issues.append("Noise indicators detected in scaffold content.")
    return (len(issues) == 0), issues


def main():
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        root = render_ci_scaffold("ci_scaffold", "CI Scaffold", "CI test", base)
        main_py = root / "main.py"
        clean, issues = is_clean(main_py)
        if clean:
            print("[OK] CI scaffold: clean (zero-noise).")
            sys.exit(0)
        else:
            print("[ERR] CI scaffold: found noise in generated scaffold:")
            for i in issues:
                print("- ", i)
            sys.exit(1)


if __name__ == "__main__":
    main()
