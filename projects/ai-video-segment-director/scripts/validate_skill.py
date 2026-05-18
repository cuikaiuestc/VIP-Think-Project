#!/usr/bin/env python3
"""Lightweight validation for ai-video-segment-director."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


REQUIRED_REFERENCES = [
    "references/workflow.md",
    "references/continuity-controls.md",
    "references/jimeng-human-handoff.md",
    "references/segment-output-contract.md",
]


def fail(message: str) -> None:
    print(f"FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def check_frontmatter(skill_md: Path) -> None:
    text = skill_md.read_text(encoding="utf-8")
    match = re.match(r"---\n(.*?)\n---\n", text, re.DOTALL)
    if not match:
        fail("SKILL.md frontmatter is missing")
    frontmatter = match.group(1)
    if "name: ai-video-segment-director" not in frontmatter:
        fail("frontmatter name is incorrect")
    if "description:" not in frontmatter:
        fail("frontmatter description is missing")
    required_terms = [
        "segmented AI video production",
        "Jimeng/Seedance",
        "returned-video continuity review",
    ]
    for term in required_terms:
        if term not in frontmatter:
            fail(f"frontmatter description missing trigger term: {term}")


def check_references(root: Path) -> None:
    for rel in REQUIRED_REFERENCES:
        path = root / rel
        if not path.exists():
            fail(f"missing reference: {rel}")


def check_test_prompts(root: Path) -> None:
    path = root / "test-prompts.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    if len(data) < 5:
        fail("test-prompts.json should contain at least five cases")
    for item in data:
        for key in ("name", "prompt", "must_check", "must_not_do"):
            if key not in item:
                fail(f"test prompt missing key {key}: {item}")


def check_sensitive_terms(root: Path) -> None:
    banned = ["/Users/", "gho_", "github_pat", "mp.weixin.qq.com"]
    text = "\n".join(
        p.read_text(encoding="utf-8")
        for p in root.rglob("*")
        if p.is_file() and p.suffix in {".md", ".json", ".yaml", ".yml"}
    )
    for term in banned:
        if term in text:
            fail(f"personalized source term found: {term}")


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    check_frontmatter(root / "SKILL.md")
    check_references(root)
    check_test_prompts(root)
    check_sensitive_terms(root)
    print("ai-video-segment-director validation passed")


if __name__ == "__main__":
    main()
