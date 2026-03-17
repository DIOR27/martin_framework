from pathlib import Path
import os


SNAPSHOT_DIR = Path(__file__).parent / "snapshots"


def _normalize(text: str) -> str:
    lines = text.replace("\r\n", "\n").strip().split("\n")
    return "\n".join(line.rstrip() for line in lines).strip() + "\n"


def assert_snapshot(testcase, name: str, current: str):
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    path = SNAPSHOT_DIR / name
    normalized = _normalize(current)

    if os.getenv("MARTIN_UPDATE_SNAPSHOTS") == "1":
        path.write_text(normalized, encoding="utf-8")

    testcase.assertTrue(path.exists(), f"Snapshot no existe: {path}")
    expected = path.read_text(encoding="utf-8")
    testcase.assertEqual(expected, normalized)
