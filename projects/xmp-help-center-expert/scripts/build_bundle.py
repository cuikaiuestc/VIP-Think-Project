#!/usr/bin/env python3
"""Build a distributable zip bundle for xmp-help-center-expert."""

from __future__ import annotations

import argparse
from pathlib import Path
import zipfile


ROOT = Path(__file__).resolve().parents[1]
EXCLUDED_PARTS = {".git", "__pycache__", ".pytest_cache", ".mypy_cache", ".venv", "dist"}
EXCLUDED_SUFFIXES = {".pyc", ".zip"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a skill bundle zip.")
    parser.add_argument("--root", type=Path, default=ROOT, help="Skill root to bundle.")
    parser.add_argument("--output", type=Path, default=None, help="Output zip path.")
    return parser.parse_args()


def should_include(path: Path, root: Path) -> bool:
    rel = path.relative_to(root)
    if any(part in EXCLUDED_PARTS for part in rel.parts):
        return False
    if path.suffix in EXCLUDED_SUFFIXES:
        return False
    return path.is_file()


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    version = (root / "VERSION").read_text(encoding="utf-8").strip()
    output = args.output or root / "dist" / f"xmp-help-center-expert-{version}.zip"
    output.parent.mkdir(parents=True, exist_ok=True)

    files = sorted(path for path in root.rglob("*") if should_include(path, root))
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in files:
            archive.write(path, path.relative_to(root).as_posix())

    print(f"Built {output}")
    print(f"Files: {len(files)}")
    print(f"Size: {output.stat().st_size} bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
