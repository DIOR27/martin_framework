#!/usr/bin/env python3
from pathlib import Path

root = Path(__file__).resolve().parents[2] / "scaffold_test_project"
print(f"Scaffold dir: {root}")
for p in sorted(root.rglob("*")):
    if p.is_file():
        print(p.relative_to(root))
