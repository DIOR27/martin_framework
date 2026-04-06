#!/usr/bin/env python3
"""Smoke test: generate a scaffold and try to run it locally.

This script:
- Generates a scaffold using the internal render function.
- Writes files to scaffold_test_project/
- Attempts to run the generated main.py with the local martin package from this repo.
- Performs a light HTTP GET to verify the server responds.
"""

import os
import sys
import io
import json
import shutil
import subprocess
import time
from pathlib import Path

# Ensure repo root is on sys.path so local modules resolve
import sys
from pathlib import Path as _Path

_REPO_ROOT = _Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_REPO_ROOT))

# Import render function from the local scaffold module
from martin_framework.martin.scaffold import render_new_project_files


def write_scaffold(name: str, title: str, desc: str, out_dir: Path) -> dict:
    files = render_new_project_files(name, title, desc)
    for rel_path, content in files.items():
        dest = out_dir / rel_path
        dest.parent.mkdir(parents=True, exist_ok=True)
        with open(dest, "w", encoding="utf-8") as f:
            f.write(content)
    return files


def run_server_and_probe(
    project_dir: Path, port: int = 3908, timeout: int = 15
) -> tuple[bool, str]:
    # Run the generated main.py using the local repository via PYTHONPATH
    env = os.environ.copy()
    # Prepend the martin framework location so imports resolve to the local code
    martin_location = str(
        Path(__file__).resolve().parents[2] / "martin_framework" / "martin"
    )
    existing = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = martin_location + (";" + existing if existing else "")

    main_py = project_dir / "main.py"
    if not main_py.exists():
        return False, "main.py not found in scaffold."

    # Start server in a subprocess
    proc = subprocess.Popen(
        [sys.executable, str(main_py)],
        cwd=str(project_dir),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    started = False
    output = []
    try:
        # Wait a bit for the server to start
        for _ in range(timeout * 2):  # poll in 0.5s steps
            line = proc.stdout.readline()
            if line:
                output.append(line)
                if (
                    "Serving HTTP" in line
                    or "http://" in line
                    or "PID" in line
                    or "listening" in line
                ):
                    started = True
                    break
            else:
                time.sleep(0.25)
        # Probe the server if started
        import urllib.request

        status = False
        text = ""
        if started:
            try:
                with urllib.request.urlopen(
                    f"http://localhost:{port}", timeout=5
                ) as resp:
                    text = resp.read().decode("utf-8", errors="ignore")[:1000]
                    status = True
            except Exception as e:
                text = str(e)
        return status, text
    finally:
        try:
            proc.terminate()
        except Exception:
            pass
        try:
            proc.wait(timeout=5)
        except Exception:
            proc.kill()


def main():
    repo_root = Path(__file__).resolve().parents[2]
    out_dir = repo_root / "scaffold_test_project"
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    print("[step] Generating scaffold files...")
    files = write_scaffold(
        "scaffold_test_project", "Demo Scaffold", "Zero-noise scaffold test", out_dir
    )
    print(f"Generated {len(files)} files in {out_dir}")

    print(
        "[step] Running scaffold server to verify end-to-end... (this may take a moment)"
    )
    ok, excerpt = run_server_and_probe(out_dir, port=3908, timeout=20)
    if ok:
        print("[ok] Server responded. Preview excerpt from root path:\n" + excerpt)
    else:
        print("[warn] Server did not respond as expected. Excerpt/error:\n" + excerpt)

    # Summary for the report
    print("\nEnd-to-end verification completed.")
    print(f"Project dir: {out_dir}")
    if ok:
        print("Result: CLEAN scaffold rendered successfully (no noise observed).")
    else:
        print(
            "Result: Scaffold generated but server validation failed; please inspect the scaffold and environment."
        )


if __name__ == "__main__":
    main()
