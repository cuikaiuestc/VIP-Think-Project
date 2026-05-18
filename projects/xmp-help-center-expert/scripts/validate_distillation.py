#!/usr/bin/env python3
"""Validate distilled reference structure and retrieval expectations."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import subprocess


REQUIRED_MARKERS = [
    "source:",
    "category:",
    "captured_at:",
    "## Key Rules",
    "## Use Cases",
    "## Limitations",
    "## Source Trace",
]

REQUIRED_IMAGE_FIELDS = [
    "image_id",
    "image_path",
    "thumbnail_path",
    "source_url",
    "source_hash",
    "captured_at",
    "visual_summary",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate a distilled knowledge base.")
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="Target skill root.")
    parser.add_argument("--config", type=Path, help="distill_config.json path.")
    parser.add_argument("--write", action="store_true", help="Write validation report.")
    parser.add_argument("--report", type=Path, help="Report path.")
    return parser.parse_args()


def load_config(root: Path, config_path: Path | None) -> dict:
    path = config_path or root / "distill_config.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}


def validate_structure(root: Path) -> tuple[list[str], dict[str, int], list[Path]]:
    references = root / "references"
    bad = []
    by_category: dict[str, int] = {}
    files = list(references.rglob("*.md"))
    for path in files:
        text = path.read_text(encoding="utf-8", errors="ignore")
        missing = [marker for marker in REQUIRED_MARKERS if marker not in text]
        if missing and "09-patterns" not in path.parts:
            bad.append(f"{path.relative_to(root)} missing {', '.join(missing)}")
        match = re.search(r"^category:\s*(.+)$", text, re.MULTILINE)
        category = match.group(1).strip() if match else path.parent.name
        by_category[category] = by_category.get(category, 0) + 1
    return bad, by_category, files


def validate_image_index(root: Path) -> tuple[list[str], int]:
    index_path = root / "references" / "image_index.jsonl"
    if not index_path.exists():
        return [], 0
    bad = []
    count = 0
    for line_number, line in enumerate(index_path.read_text(encoding="utf-8", errors="ignore").splitlines(), start=1):
        if not line.strip():
            continue
        count += 1
        try:
            item = json.loads(line)
        except json.JSONDecodeError as exc:
            bad.append(f"references/image_index.jsonl:{line_number} invalid json: {exc}")
            continue
        missing = [field for field in REQUIRED_IMAGE_FIELDS if not item.get(field)]
        if missing:
            bad.append(f"references/image_index.jsonl:{line_number} missing {', '.join(missing)}")
        for path_field in ("image_path", "thumbnail_path"):
            value = item.get(path_field)
            if value and not (root / value).exists():
                bad.append(f"references/image_index.jsonl:{line_number} {path_field} not found: {value}")
    return bad, count


def search(root: Path, query: str, limit: int = 5) -> list[str]:
    script = Path(__file__).with_name("search_kb.py")
    output = subprocess.check_output(
        ["python3", str(script), "--root", str(root), query, "--limit", str(limit)],
        text=True,
    )
    return [line.split("] ", 1)[1] for line in output.splitlines() if line.startswith("[")]


def check_queries(root: Path, config: dict) -> list[dict]:
    rows = []
    expectations = config.get("validation_queries", {})
    for case_id, item in expectations.items():
        query = item["query"] if isinstance(item, dict) else str(item)
        expected = item.get("expected", []) if isinstance(item, dict) else []
        limit = int(item.get("limit", 5)) if isinstance(item, dict) else 5
        results = search(root, query, limit=limit)
        ok = True
        if expected:
            ok = all(any(fragment in path for path in results) for fragment in expected)
        rows.append({"id": case_id, "ok": ok, "query": query, "expected": expected, "results": results})
    return rows


def render_report(root: Path, config: dict) -> str:
    bad, by_category, files = validate_structure(root)
    image_bad, image_count = validate_image_index(root)
    rows = check_queries(root, config)
    passed = sum(1 for row in rows if row["ok"])
    lines = [
        "# Distillation Validation Report",
        "",
        "## Structure",
        "",
        f"- Reference files: {len(files)}",
        f"- Structure failures: {len(bad)}",
        f"- Image evidence items: {image_count}",
        f"- Image evidence failures: {len(image_bad)}",
        f"- Max file size: {max((p.stat().st_size for p in files), default=0)} bytes",
        "",
        "## Category Distribution",
        "",
    ]
    lines.extend(f"- `{category}`: {count}" for category, count in sorted(by_category.items()))
    lines.extend(["", "## Retrieval Checks", "", f"- Passed: {passed}/{len(rows)}", ""])
    if rows:
        lines.extend(["| OK | Case | Query | Expected | Top Results |", "|---|---|---|---|---|"])
        for row in rows:
            expected = ", ".join(row["expected"])
            results = "<br>".join(f"`{path}`" for path in row["results"])
            lines.append(f"| {'yes' if row['ok'] else 'no'} | {row['id']} | {row['query']} | {expected} | {results} |")
    if bad:
        lines.extend(["", "## Structure Failures", ""])
        lines.extend(f"- {item}" for item in bad)
    if image_bad:
        lines.extend(["", "## Image Evidence Failures", ""])
        lines.extend(f"- {item}" for item in image_bad)
    return "\n".join(lines) + "\n"


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    config = load_config(root, args.config)
    report = render_report(root, config)
    print(report)
    if args.write:
        report_path = args.report or root / "distill_validation.md"
        report_path.write_text(report, encoding="utf-8")
    bad, _, _ = validate_structure(root)
    image_bad, _ = validate_image_index(root)
    rows = check_queries(root, config)
    if bad or image_bad or any(not row["ok"] for row in rows):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
