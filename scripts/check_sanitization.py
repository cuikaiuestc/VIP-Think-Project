#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {".git", ".venv", "__pycache__"}
SKIP_SUFFIXES = {".xlsx", ".pyc"}

CHECKS = {
    "private_home_path": re.compile(r"/Users/takuya|/Users/[^/\s]+/Documents/Codex/projects/投放自动化"),
    "report_identifier": re.compile(r"\breport_id\b", re.IGNORECASE),
    "mainland_phone": re.compile(r"(?<!\d)1[3-9]\d{9}(?!\d)"),
    "ipv4_address": re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"),
    "access_key_shape": re.compile(r"\b(?:sk-[A-Za-z0-9_-]{16,}|ghp_[A-Za-z0-9_]{16,}|AKIA[0-9A-Z]{16})\b"),
    "cookie_assignment": re.compile(r"(?i)\bcookie\s*[:=]\s*['\"][^'\"]{8,}"),
    "password_assignment": re.compile(r"(?i)\bpassword\s*[:=]\s*['\"][^'\"]{6,}"),
    "token_assignment": re.compile(r"(?i)\btoken\s*[:=]\s*['\"][^'\"]{8,}"),
    "secret_assignment": re.compile(r"(?i)\bsecret\s*[:=]\s*['\"][^'\"]{8,}"),
    "real_ad_account_shape": re.compile(r"\bact_\d{6,}\b"),
}


def iter_files() -> list[Path]:
    files: list[Path] = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if path.name == "check_sanitization.py":
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.suffix in SKIP_SUFFIXES:
            continue
        files.append(path)
    return files


def main() -> None:
    findings = []
    for path in iter_files():
        rel = path.relative_to(ROOT)
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for name, pattern in CHECKS.items():
            for match in pattern.finditer(text):
                line_no = text.count("\n", 0, match.start()) + 1
                snippet = text[match.start() : match.end()]
                findings.append({"check": name, "file": str(rel), "line": line_no, "match": snippet})

    result = {
        "status": "pass" if not findings else "fail",
        "checked_files": len(iter_files()),
        "findings": findings,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if findings:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
