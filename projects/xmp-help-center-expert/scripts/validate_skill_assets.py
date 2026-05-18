#!/usr/bin/env python3
"""Lightweight static checks for the xmp-help-center-expert skill package."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ALLOWED_MODES = {"route", "how-to", "api-reference", "release-lookup", "explain"}
REQUIRED_FILES = [
    "SKILL.md",
    "VERSION",
    "CHANGELOG.md",
    "LICENSE",
    "NOTICE",
    "agents/openai.yaml",
    "distill_config.json",
    "test-prompts.json",
    "references/release-checklist.md",
    "references/url_map.md",
    "references/response-review-checklist.md",
    "references/xmp-official-refresh-automation.md",
    "references/source-refresh-candidates.md",
    "references/image_index.jsonl",
    "scripts/search_kb.py",
    "scripts/archive_helplook_docs.py",
    "scripts/distill_captures.py",
    "scripts/validate_distillation.py",
    "scripts/search_kb.py",
    "scripts/build_bundle.py",
    "response-fixtures/create-ad-how-to.answer.md",
    "response-fixtures/open-api-reference.answer.md",
    "response-fixtures/account-state-blocked.answer.md",
]


def fail(message: str) -> None:
    print(f"FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def check_required_files() -> None:
    missing = [path for path in REQUIRED_FILES if not (ROOT / path).exists()]
    if missing:
        fail("Missing required files: " + ", ".join(missing))


def check_release_files() -> None:
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        fail("VERSION must be semantic version format like 1.1.0")
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    if version not in changelog:
        fail(f"CHANGELOG.md missing current version {version}")
    notice = (ROOT / "NOTICE").read_text(encoding="utf-8")
    for phrase in ("third-party content", "respective owners", "private XMP account"):
        if phrase not in notice:
            fail(f"NOTICE missing rights/boundary phrase: {phrase}")
    metadata = (ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")
    for phrase in ("display_name", "short_description", "default_prompt"):
        if phrase not in metadata:
            fail(f"agents/openai.yaml missing {phrase}")


def check_frontmatter() -> None:
    text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        fail("SKILL.md missing YAML frontmatter")
    try:
        frontmatter = text[4 : text.index("\n---\n", 4)]
    except ValueError:
        fail("SKILL.md frontmatter is not closed")
    if "name: xmp-help-center-expert" not in frontmatter:
        fail("SKILL.md frontmatter must set name: xmp-help-center-expert")
    if "description:" not in frontmatter:
        fail("SKILL.md frontmatter missing description")
    for trigger in ("XMP", "Open API", "素材报表", "团队管理", "功能更新公告"):
        if trigger not in frontmatter:
            fail(f"SKILL.md description missing trigger: {trigger}")
    for phrase in ("Fresh Official Source Hook", "Source Refresh Candidate", "references/source-refresh-candidates.md"):
        if phrase not in text:
            fail(f"SKILL.md missing source refresh hook phrase: {phrase}")


def normalize_reference(ref: str) -> str | None:
    if ref.startswith("09-patterns/"):
        return "references/" + ref
    if ref.startswith(("references/", "scripts/")):
        return ref
    return None


def check_skill_references() -> None:
    text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    refs = []
    for ref in re.findall(r"`([^`]+)`", text):
        normalized = normalize_reference(ref)
        if normalized:
            refs.append(normalized)
    missing = sorted({ref for ref in refs if not (ROOT / ref).exists()})
    if missing:
        fail("Missing referenced paths: " + ", ".join(missing))


def check_test_prompts() -> None:
    path = ROOT / "test-prompts.json"
    try:
        cases = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"test-prompts.json is invalid JSON: {exc}")
    if not isinstance(cases, list) or len(cases) < 10:
        fail("test-prompts.json must contain at least 10 cases")
    seen = set()
    for index, case in enumerate(cases, start=1):
        if not isinstance(case, dict):
            fail(f"case #{index} must be an object")
        for key in ("id", "mode", "prompt", "must_check", "must_not_do"):
            if key not in case:
                fail(f"case #{index} missing {key}")
        if case["id"] in seen:
            fail(f"duplicate case id: {case['id']}")
        seen.add(case["id"])
        if case["mode"] not in ALLOWED_MODES:
            fail(f"{case['id']} has invalid mode: {case['mode']}")
        if not isinstance(case["must_check"], list) or len(case["must_check"]) < 3:
            fail(f"{case['id']} must include at least 3 must_check items")
        if not isinstance(case["must_not_do"], list) or not case["must_not_do"]:
            fail(f"{case['id']} must include at least 1 must_not_do item")
        for item in case["must_check"]:
            if not isinstance(item, str):
                fail(f"{case['id']} must_check items must be strings")
            if item.startswith("references/") and item.endswith(".md") and not (ROOT / item).exists():
                fail(f"{case['id']} references missing path: {item}")
    if "official_source_refresh_candidate" not in seen:
        fail("test-prompts.json missing official_source_refresh_candidate regression case")


def check_source_refresh_protocol() -> None:
    text = (ROOT / "references" / "source-refresh-candidates.md").read_text(encoding="utf-8")
    for phrase in (
        "LLM WIKI-style incremental ingestion gate",
        "Candidate Criteria",
        "Reject Criteria",
        "Confirmation needed",
        "references/url_map.md",
    ):
        if phrase not in text:
            fail(f"source-refresh-candidates.md missing phrase: {phrase}")


def check_image_index() -> None:
    index_path = ROOT / "references" / "image_index.jsonl"
    count = 0
    missing = []
    for line_number, line in enumerate(index_path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        count += 1
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            fail(f"references/image_index.jsonl:{line_number} invalid json: {exc}")
        for field in ("image_path", "thumbnail_path"):
            value = row.get(field)
            if not value:
                missing.append(f"line {line_number} missing {field}")
            elif not (ROOT / value).exists():
                missing.append(f"line {line_number} {field} not found: {value}")
    if count != 374:
        fail(f"expected 374 image evidence rows, found {count}")
    if missing:
        fail("Image index failures: " + "; ".join(missing[:10]))


def check_distillation() -> None:
    subprocess.check_output(
        ["python3", str(ROOT / "scripts" / "validate_distillation.py"), "--root", str(ROOT)],
        text=True,
    )


def search_paths(query: str, limit: int = 8) -> list[str]:
    output = subprocess.check_output(
        ["python3", str(ROOT / "scripts" / "search_kb.py"), query, "--root", str(ROOT), "--limit", str(limit)],
        text=True,
    )
    paths = []
    for line in output.splitlines():
        match = re.match(r"^\[\d+\]\s+(.+)$", line)
        if match:
            paths.append(match.group(1).strip())
    return paths


def check_search_companions() -> None:
    expectations = {
        "XMP 怎么创建广告": (
            "references/09-patterns/create-ad.md",
            "references/02-ads-workflow/source-help-xmp-mobvista-com-docs-create-ad-guide.md",
        ),
        "XMP 接口请求协议怎么查": (
            "references/09-patterns/open-api.md",
            "references/07-open-api/source-help-xmp-mobvista-com-docs-request-protocol.md",
        ),
        "XMP 一键上单是什么": (
            "references/09-patterns/ai-assistant.md",
            "references/06-ai-assistant/source-help-xmp-mobvista-com-docs-yi-jian-shang-dan.md",
        ),
        "我的 XMP 账号为什么不能投放": (
            "references/09-patterns/account-state-blocked.md",
        ),
    }
    for query, required in expectations.items():
        paths = search_paths(query)
        for path in required:
            if path not in paths:
                fail(f"search for {query!r} missing {path}; got: {', '.join(paths[:8])}")
        if query != "我的 XMP 账号为什么不能投放":
            if not any("/09-patterns/" not in path and path.startswith("references/") for path in paths):
                fail(f"search for {query!r} did not return a concrete official reference")


def check_response_fixtures() -> None:
    required_sections = ["## Recommendation", "## Official Basis", "## Steps Or Location", "## Verification", "## Limits"]
    for path in (ROOT / "response-fixtures").glob("*.answer.md"):
        text = path.read_text(encoding="utf-8")
        for section in required_sections:
            if section not in text:
                fail(f"{path.relative_to(ROOT)} missing section {section}")
        refs = re.findall(r"\((references/[^)]+\.md)\)", text)
        if not refs:
            fail(f"{path.relative_to(ROOT)} must cite at least one local reference")
        for ref in refs:
            if not (ROOT / ref).exists():
                fail(f"{path.relative_to(ROOT)} cites missing reference: {ref}")


def check_bundle_script() -> None:
    output = ROOT / "dist" / "validator-smoke.zip"
    try:
        subprocess.check_output(
            ["python3", str(ROOT / "scripts" / "build_bundle.py"), "--root", str(ROOT), "--output", str(output)],
            text=True,
        )
        if not output.exists() or output.stat().st_size <= 0:
            fail("build_bundle.py did not create a non-empty zip")
    finally:
        if output.exists():
            output.unlink()


def main() -> int:
    check_required_files()
    check_release_files()
    check_frontmatter()
    check_skill_references()
    check_test_prompts()
    check_source_refresh_protocol()
    check_image_index()
    check_distillation()
    check_search_companions()
    check_response_fixtures()
    check_bundle_script()
    print("OK: xmp-help-center-expert skill assets validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
