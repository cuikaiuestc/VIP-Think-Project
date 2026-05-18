#!/usr/bin/env python3
"""Distill text captures into compact Markdown reference notes.

The script is intentionally domain-neutral. Domain choices belong in
distill_config.json, not in this implementation.
"""

from __future__ import annotations

import argparse
import shutil
import hashlib
import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path
import re
from textwrap import shorten
from urllib.parse import urlparse


DEFAULT_STOP_LINES = {
    "Home",
    "Login",
    "Sign up",
    "Get Started",
    "Overview",
    "Support",
    "Reference",
    "Cookie",
    "Privacy",
    "Terms",
    "首页",
    "登录",
    "注册",
    "概览",
    "支持",
    "隐私政策",
    "条款",
}

DEFAULT_KEY_TERMS = (
    "must",
    "should",
    "recommend",
    "required",
    "best practice",
    "avoid",
    "ensure",
    "important",
    "必须",
    "需要",
    "建议",
    "不得",
    "不能",
    "避免",
    "确保",
    "重要",
)

DEFAULT_LIMIT_TERMS = (
    "cannot",
    "do not",
    "may not",
    "policy",
    "privacy",
    "limit",
    "restriction",
    "不能",
    "不得",
    "不保证",
    "限制",
    "政策",
    "隐私",
)


@dataclass
class Capture:
    source_id: str
    input_url: str
    final_url: str
    chars: int
    path: Path
    run: str
    row_id: str = ""
    title: str = ""
    author: str = ""
    published_at: str = ""
    tags: str = ""
    source_type: str = ""
    authority_level: str = ""
    confidentiality: str = ""
    notes: str = ""
    image_files: list[str] | None = None
    image_urls: list[str] | None = None
    image_caption: str = ""
    image_notes: str = ""
    image_ocr: str = ""
    image_summary: str = ""


@dataclass
class Analysis:
    title: str
    category: str
    slug: str
    key_rules: list[str]
    use_cases: list[str]
    limits: list[str]
    related_patterns: list[str]
    aliases: list[str]
    source_hash: str


@dataclass
class ImageEvidence:
    image_id: str
    source_id: str
    title: str
    source_url: str
    row_id: str
    image_path: str
    thumbnail_path: str
    image_url: str
    ocr_text: str
    visual_summary: str
    caption: str
    notes: str
    tags: str
    source_type: str
    authority_level: str
    confidentiality: str
    captured_at: str
    source_hash: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Distill captured text into reference notes.")
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="Target skill root.")
    parser.add_argument("--manifest", action="append", type=Path, help="Manifest path. Can be passed multiple times.")
    parser.add_argument("--config", type=Path, help="distill_config.json path.")
    parser.add_argument("--raw-dir", action="append", type=Path, help="Directory of .txt/.md raw sources when no manifest exists.")
    parser.add_argument("--image-dir", action="append", type=Path, help="Directory of image files to index when no manifest image fields exist.")
    parser.add_argument("--write", action="store_true", help="Write generated notes and report.")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing generated files.")
    parser.add_argument("--limit", type=int, help="Limit number of valid captures.")
    parser.add_argument("--report", type=Path, help="Report path.")
    return parser.parse_args()


def load_config(root: Path, config_path: Path | None) -> dict:
    path = config_path or root / "distill_config.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}


def safe_slug(value: str, fallback: str = "source") -> str:
    parsed = urlparse(value)
    raw = (parsed.netloc + parsed.path).strip("/") if parsed.netloc else value
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", raw).strip("-").lower()
    return (slug[:90].strip("-") or fallback)


def manifest_captures(root: Path, manifest: Path) -> list[Capture]:
    path = manifest if manifest.is_absolute() else root / manifest
    items = json.loads(path.read_text(encoding="utf-8"))
    captures = []
    for item in items:
        raw_path = Path(item["path"])
        if not raw_path.is_absolute():
            raw_path = (path.parent / raw_path).resolve()
            if not raw_path.exists():
                raw_path = (root / item["path"]).resolve()
        if not raw_path.exists():
            continue
        final_url = item.get("final_url") or item.get("source") or item.get("input_url") or raw_path.name
        captures.append(
            Capture(
                source_id=str(item.get("id") or final_url),
                input_url=str(item.get("input_url") or final_url),
                final_url=str(final_url),
                chars=int(item.get("chars") or raw_path.stat().st_size),
                path=raw_path,
                run=path.parent.name,
                row_id=str(item.get("row_id") or item.get("record_id") or item.get("row") or ""),
                title=str(item.get("title") or ""),
                author=str(item.get("author") or ""),
                published_at=str(item.get("published_at") or ""),
                tags=normalize_list_field(item.get("tags")),
                source_type=str(item.get("source_type") or ""),
                authority_level=str(item.get("authority_level") or ""),
                confidentiality=str(item.get("confidentiality") or ""),
                notes=str(item.get("notes") or ""),
                image_files=normalize_list(item.get("image_files")),
                image_urls=normalize_list(item.get("image_urls")),
                image_caption=str(item.get("image_caption") or ""),
                image_notes=str(item.get("image_notes") or ""),
                image_ocr=str(item.get("image_ocr") or item.get("ocr_text") or ""),
                image_summary=str(item.get("image_summary") or item.get("visual_summary") or ""),
            )
        )
    return captures


def normalize_list(value: object) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str):
        return [part.strip() for part in re.split(r"[,;\n]", value) if part.strip()]
    return [str(value).strip()]


def normalize_list_field(value: object) -> str:
    return ", ".join(normalize_list(value))


def raw_dir_captures(root: Path, raw_dir: Path) -> list[Capture]:
    source_dir = raw_dir if raw_dir.is_absolute() else root / raw_dir
    captures = []
    for path in sorted([*source_dir.rglob("*.txt"), *source_dir.rglob("*.md")]):
        text_len = path.stat().st_size
        source_id = path.relative_to(root).as_posix() if root in path.resolve().parents else path.name
        captures.append(
            Capture(
                source_id=source_id,
                input_url=source_id,
                final_url=source_id,
                chars=text_len,
                path=path,
                run=source_dir.name,
            )
        )
    return captures


def read_captures(root: Path, manifests: list[Path] | None, raw_dirs: list[Path] | None, config: dict) -> list[Capture]:
    captures = []
    for manifest in manifests or [Path(p) for p in config.get("manifests", [])]:
        captures.extend(manifest_captures(root, manifest))
    for raw_dir in raw_dirs or [Path(p) for p in config.get("raw_dirs", [])]:
        captures.extend(raw_dir_captures(root, raw_dir))
    if not captures:
        default_raw = root / "raw-captures"
        if default_raw.exists():
            captures.extend(raw_dir_captures(root, default_raw))

    seen = set()
    valid = []
    min_chars = int(config.get("min_chars", 700))
    for capture in captures:
        key = capture.final_url or capture.source_id
        if key in seen:
            continue
        seen.add(key)
        text = capture.path.read_text(encoding="utf-8", errors="ignore")
        if capture.chars >= min_chars and usable_text(text, config):
            valid.append(capture)
    return valid


def resolve_relative(root: Path, base: Path, value: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    candidate = (base / path).resolve()
    if candidate.exists():
        return candidate
    return (root / path).resolve()


def image_files_from_dirs(root: Path, image_dirs: list[Path] | None, config: dict) -> list[Path]:
    dirs = image_dirs or [Path(p) for p in config.get("image_dirs", [])]
    suffixes = tuple(config.get("image_suffixes", [".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp", ".tiff"]))
    files: list[Path] = []
    for directory in dirs:
        source_dir = directory if directory.is_absolute() else root / directory
        if not source_dir.exists():
            continue
        files.extend(path for path in source_dir.rglob("*") if path.is_file() and path.suffix.lower() in suffixes)
    return sorted(files)


def usable_text(text: str, config: dict) -> bool:
    lines = clean_lines(text, config)
    unique_ratio = len(set(lines)) / max(len(lines), 1)
    substantial_chars = sum(len(line) for line in lines if len(line) >= 24)
    min_substantial_chars = int(config.get("min_substantial_chars", 700))
    min_unique_ratio = float(config.get("min_unique_line_ratio", 0.42))
    block_phrases = config.get("block_phrases", ["access denied", "enable cookies", "login required", "请登录"])
    lowered = text.lower()
    if any(phrase.lower() in lowered for phrase in block_phrases):
        return False
    return (substantial_chars >= min_substantial_chars and unique_ratio >= min_unique_ratio) or substantial_chars >= 2500


def clean_lines(text: str, config: dict) -> list[str]:
    stop_lines = set(config.get("stop_lines", [])) | DEFAULT_STOP_LINES
    lines = []
    for raw in text.splitlines():
        line = re.sub(r"\s+", " ", raw).strip()
        if not line or line in stop_lines or len(line) <= 2:
            continue
        if is_noise(line, config):
            continue
        lines.append(line)
    return lines


def is_noise(value: str, config: dict) -> bool:
    if any(phrase in value for phrase in config.get("noise_phrases", [])):
        return True
    language_terms = config.get("language_terms", ["English", "Español", "Français", "Deutsch", "日本語", "한국어", "中文"])
    return sum(1 for term in language_terms if term in value) >= 4


def title_for(lines: list[str], source: str, config: dict) -> str:
    min_title_len = int(config.get("min_title_len", 4))
    for line in lines[: int(config.get("title_scan_lines", 16))]:
        if len(line) >= min_title_len and not line.startswith("http"):
            return line[:120]
    return safe_slug(source).replace("-", " ").title()


def categorize(source: str, title: str, text: str, config: dict) -> str:
    haystacks = {
        "source": source.lower(),
        "title": title.lower(),
        "text": text[: int(config.get("category_text_chars", 5000))].lower(),
    }
    for route in config.get("routes", []):
        category = route["category"]
        needles = [needle.lower() for needle in route.get("needles", [])]
        fields = route.get("fields", ["source", "title", "text"])
        if any(needle in haystacks[field] for field in fields for needle in needles):
            return category

    category_rules = config.get("categories", {})
    joined = f"{haystacks['source']} {haystacks['title']} {haystacks['text']}"
    for category, needles in category_rules.items():
        if any(str(needle).lower() in joined for needle in needles):
            return category
    return config.get("default_category") or next(iter(category_rules.keys()), "01-general")


def split_sentences(text: str, config: dict) -> list[str]:
    normalized = re.sub(r"\s+", " ", text)
    pieces = re.split(r"(?<=[。！？.!?])\s+|(?<=；)\s*|(?<=;)\s+", normalized)
    max_len = int(config.get("max_sentence_chars", 900))
    return [p.strip(" -•\t") for p in pieces if 24 <= len(p.strip()) <= max_len and not is_noise(p, config)]


def score_sentence(sentence: str, title: str, category: str, config: dict) -> int:
    lowered = sentence.lower()
    value = 0
    for term in config.get("key_terms", DEFAULT_KEY_TERMS):
        if term.lower() in lowered:
            value += 6
    for term in config.get("category_terms", {}).get(category, []):
        if term.lower() in lowered:
            value += 3
    for word in re.findall(r"[A-Za-z0-9+]{4,}", title):
        if word.lower() in lowered:
            value += 2
    if 50 <= len(sentence) <= 240:
        value += 2
    if len(sentence) > 360:
        value -= 3
    return value


def choose_sentences(sentences: list[str], title: str, category: str, config: dict, limit: int) -> list[str]:
    ranked = sorted(
        ((score_sentence(sentence, title, category, config), index, sentence) for index, sentence in enumerate(sentences)),
        key=lambda item: (-item[0], item[1]),
    )
    chosen = []
    seen = set()
    for score, _, sentence in ranked:
        if score <= 0 and len(chosen) >= max(2, limit // 2):
            continue
        compact = re.sub(r"\W+", "", sentence.lower())[:90]
        if compact in seen:
            continue
        seen.add(compact)
        chosen.append(shorten(sentence, width=int(config.get("note_sentence_width", 260)), placeholder="..."))
        if len(chosen) >= limit:
            break
    return chosen or [shorten(s, width=260, placeholder="...") for s in sentences[:limit]]


def use_cases(category: str, title: str, text: str, config: dict) -> list[str]:
    configured = config.get("use_cases", {}).get(category)
    if configured:
        return configured[:4]
    return [
        f"Use when the user asks about {category.replace('-', ' ')} concepts related to {title}.",
        "Load this note as supporting evidence, then inspect raw source if exact wording or freshness matters.",
    ]


def limits_for(sentences: list[str], category: str, config: dict) -> list[str]:
    limits = []
    terms = config.get("limit_terms", DEFAULT_LIMIT_TERMS)
    for sentence in sentences:
        lowered = sentence.lower()
        if any(term.lower() in lowered for term in terms):
            limits.append(shorten(sentence, width=230, placeholder="..."))
        if len(limits) >= 3:
            break
    defaults = config.get(
        "default_limitations",
        [
            "Do not treat this distilled note as the source of truth when exact wording, compliance, or freshness matters.",
            "Verify against the raw source before making high-stakes recommendations.",
        ],
    )
    for item in defaults:
        if item not in limits:
            limits.append(item)
    return limits[:5]


def related_patterns(text: str, category: str, root: Path, config: dict) -> list[str]:
    pattern_dir = root / "references" / config.get("pattern_dir", "09-patterns")
    if not pattern_dir.exists():
        return []
    lowered = text.lower()
    hints = config.get("pattern_hints", {})
    scored = []
    for path in pattern_dir.glob("*.md"):
        needles = hints.get(path.name, [path.stem.replace("-", " ")])
        score = sum(1 for needle in needles if needle.lower() in lowered)
        if score:
            scored.append((score, path))
    return [p.relative_to(root).as_posix() for _, p in sorted(scored, key=lambda item: (-item[0], item[1].name))[:5]]


def aliases_for(title: str, text: str, config: dict) -> list[str]:
    haystack = f"{title}\n{text}".lower()
    candidates = config.get("alias_candidates", [])
    return [candidate for candidate in candidates if candidate.lower() in haystack][:12]


def analyze_capture(capture: Capture, root: Path, config: dict) -> Analysis:
    raw_text = capture.path.read_text(encoding="utf-8", errors="ignore")
    lines = clean_lines(raw_text, config)
    compact_text = "\n".join(lines)
    title = capture.title or title_for(lines, capture.final_url, config)
    category = categorize(capture.final_url, title, compact_text, config)
    sentences = split_sentences(compact_text, config)
    key_rules = choose_sentences(sentences, title, category, config, int(config.get("key_rule_limit", 7)))
    source_hash = hashlib.sha256(raw_text.encode("utf-8")).hexdigest()[:16]
    slug_prefix = config.get("slug_prefix", "source")
    slug = f"{slug_prefix}-{safe_slug(capture.final_url or capture.source_id)}"
    return Analysis(
        title=title,
        category=category,
        slug=slug,
        key_rules=key_rules,
        use_cases=use_cases(category, title, compact_text, config),
        limits=limits_for(sentences, category, config),
        related_patterns=related_patterns(compact_text, category, root, config),
        aliases=aliases_for(title, compact_text, config),
        source_hash=source_hash,
    )


def yaml_scalar(value: str) -> str:
    return '"' + value.replace('"', '\\"') + '"'


def render_note(capture: Capture, analysis: Analysis, root: Path, captured_at: str) -> str:
    key_rules = "\n".join(f"- {rule}" for rule in analysis.key_rules)
    use_case_lines = "\n".join(f"- {item}" for item in analysis.use_cases)
    limits = "\n".join(f"- {item}" for item in analysis.limits)
    patterns = "\n".join(f"- `{pattern}`" for pattern in analysis.related_patterns) or "- None mapped yet."
    raw_path = capture.path.relative_to(root).as_posix() if root in capture.path.resolve().parents else str(capture.path)
    alias_line = ", ".join(analysis.aliases)
    return "\n".join(
        [
            "---",
            f"title: {yaml_scalar(analysis.title)}",
            f"source: {capture.final_url}",
            f"category: {analysis.category}",
            f"captured_at: {captured_at}",
            "status: distilled-source",
            f"source_hash: {analysis.source_hash}",
            f"aliases: {alias_line}",
            f"source_type: {capture.source_type}",
            f"authority_level: {capture.authority_level}",
            f"confidentiality: {capture.confidentiality}",
            "---",
            "",
            f"# {analysis.title}",
            "",
            "This is a compact distilled note. Use the raw source for audit, exact wording, or re-distillation.",
            "",
            "## Key Rules",
            "",
            key_rules or "- No strong rule sentence was extracted; inspect the raw source before relying on this note.",
            "",
            "## Use Cases",
            "",
            use_case_lines,
            "",
            "## Limitations",
            "",
            limits,
            "",
            "## Related Patterns",
            "",
            patterns,
            "",
            "## Source Trace",
            "",
            f"- Input URL: {capture.input_url}",
            f"- Final URL: {capture.final_url}",
            f"- Row ID: `{capture.row_id}`",
            f"- Raw source: `{raw_path}`",
            f"- Capture run: `{capture.run}`",
            f"- Raw chars: {capture.chars}",
            f"- Author: {capture.author}",
            f"- Published at: {capture.published_at}",
            f"- Tags: {capture.tags}",
            "",
        ]
    )


def target_path(root: Path, analysis: Analysis) -> Path:
    return root / "references" / analysis.category / f"{analysis.slug}.md"


def render_report(rows: list[dict], captured_at: str) -> str:
    categories: dict[str, int] = {}
    for row in rows:
        categories[row["category"]] = categories.get(row["category"], 0) + 1
    image_count = sum(int(row.get("images", 0)) for row in rows)
    table = ["| Action | Category | Chars | Images | Target | Source |", "|---|---|---:|---:|---|---|"]
    for row in rows:
        table.append(f"| {row['action']} | `{row['category']}` | {row['chars']} | {row.get('images', 0)} | `{row['target']}` | {row['source']} |")
    return "\n".join(
        [
            "# Knowledge Base Distillation Report",
            "",
            f"Distilled: {captured_at}",
            "",
            "## Summary",
            "",
            f"- Valid captures considered: {len(rows)}",
            f"- Reference notes written: {sum(1 for row in rows if row['action'] == 'write')}",
            f"- Reference notes skipped: {sum(1 for row in rows if row['action'].startswith('skip'))}",
            f"- Image evidence items indexed: {image_count}",
            "",
            "## Category Distribution",
            "",
            *[f"- `{category}`: {count}" for category, count in sorted(categories.items())],
            "",
            "## Rows",
            "",
            *table,
            "",
        ]
    )


def image_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()[:16]


def make_thumbnail(source: Path, target: Path, max_size: int = 640) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    try:
        from PIL import Image

        with Image.open(source) as image:
            image.thumbnail((max_size, max_size))
            if image.mode not in ("RGB", "RGBA"):
                image = image.convert("RGB")
            image.save(target)
    except Exception:
        shutil.copy2(source, target)


def conservative_image_summary(path: Path, capture: Capture, config: dict) -> str:
    if capture.image_summary:
        return capture.image_summary
    if capture.image_caption:
        return capture.image_caption
    image_kind = config.get("default_image_kind", "screenshot/chart/flowchart")
    return f"Unverified {image_kind} image associated with {capture.title or capture.final_url}; inspect the image before relying on visual details."


def build_image_evidence_for_capture(capture: Capture, root: Path, config: dict, captured_at: str, write: bool) -> list[ImageEvidence]:
    evidence = []
    image_files = capture.image_files or []
    for index, raw_value in enumerate(image_files, start=1):
        source = resolve_relative(root, capture.path.parent, raw_value)
        if not source.exists():
            continue
        source_hash = image_hash(source)
        image_id = f"{safe_slug(capture.source_id, 'source')}-img-{index}"
        stored_rel = Path("raw-sources/images") / f"{image_id}{source.suffix.lower()}"
        thumb_rel = Path("references/assets/thumbnails") / f"{image_id}{source.suffix.lower()}"
        stored = root / stored_rel
        thumb = root / thumb_rel
        if write:
            stored.parent.mkdir(parents=True, exist_ok=True)
            if source.resolve() != stored.resolve():
                shutil.copy2(source, stored)
            make_thumbnail(stored, thumb, int(config.get("thumbnail_max_size", 640)))
        evidence.append(
            ImageEvidence(
                image_id=image_id,
                source_id=capture.source_id,
                title=capture.title,
                source_url=capture.final_url,
                row_id=capture.row_id,
                image_path=stored_rel.as_posix(),
                thumbnail_path=thumb_rel.as_posix(),
                image_url=(capture.image_urls or [""])[index - 1] if index - 1 < len(capture.image_urls or []) else "",
                ocr_text=capture.image_ocr,
                visual_summary=conservative_image_summary(source, capture, config),
                caption=capture.image_caption,
                notes=capture.image_notes,
                tags=capture.tags,
                source_type=capture.source_type,
                authority_level=capture.authority_level,
                confidentiality=capture.confidentiality,
                captured_at=captured_at,
                source_hash=source_hash,
            )
        )
    return evidence


def build_standalone_image_evidence(root: Path, paths: list[Path], config: dict, captured_at: str, write: bool) -> list[ImageEvidence]:
    evidence = []
    for index, source in enumerate(paths, start=1):
        source_hash = image_hash(source)
        image_id = f"standalone-{safe_slug(source.stem)}-{index}"
        stored_rel = Path("raw-sources/images") / f"{image_id}{source.suffix.lower()}"
        thumb_rel = Path("references/assets/thumbnails") / f"{image_id}{source.suffix.lower()}"
        stored = root / stored_rel
        thumb = root / thumb_rel
        if write:
            stored.parent.mkdir(parents=True, exist_ok=True)
            if source.resolve() != stored.resolve():
                shutil.copy2(source, stored)
            make_thumbnail(stored, thumb, int(config.get("thumbnail_max_size", 640)))
        rel_source = source.relative_to(root).as_posix() if root in source.resolve().parents else str(source)
        evidence.append(
            ImageEvidence(
                image_id=image_id,
                source_id=rel_source,
                title=source.stem,
                source_url=rel_source,
                row_id="",
                image_path=stored_rel.as_posix(),
                thumbnail_path=thumb_rel.as_posix(),
                image_url="",
                ocr_text="",
                visual_summary=f"Unverified standalone image from {rel_source}; inspect the image before relying on visual details.",
                caption="",
                notes="",
                tags="",
                source_type="image",
                authority_level=str(config.get("default_image_authority_level", "reference")),
                confidentiality=str(config.get("default_confidentiality", "internal")),
                captured_at=captured_at,
                source_hash=source_hash,
            )
        )
    return evidence


def write_image_index(root: Path, existing: list[ImageEvidence], write: bool) -> None:
    if not write or not existing:
        return
    index_path = root / "references" / "image_index.jsonl"
    index_path.parent.mkdir(parents=True, exist_ok=True)
    with index_path.open("w", encoding="utf-8") as handle:
        for item in existing:
            handle.write(json.dumps(item.__dict__, ensure_ascii=False, sort_keys=True) + "\n")


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    config = load_config(root, args.config)
    captures = read_captures(root, args.manifest, args.raw_dir, config)
    if args.limit:
        captures = captures[: args.limit]

    captured_at = date.today().isoformat()
    rows = []
    all_image_evidence: list[ImageEvidence] = []
    for capture in captures:
        analysis = analyze_capture(capture, root, config)
        target = target_path(root, analysis)
        image_evidence = build_image_evidence_for_capture(capture, root, config, captured_at, args.write)
        all_image_evidence.extend(image_evidence)
        action = "write"
        if target.exists() and not args.overwrite:
            action = "skip-existing"
        rows.append(
            {
                "action": action,
                "category": analysis.category,
                "chars": capture.chars,
                "images": len(image_evidence),
                "target": target.relative_to(root).as_posix(),
                "source": capture.final_url,
            }
        )
        if args.write and action == "write":
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(render_note(capture, analysis, root, captured_at), encoding="utf-8")

    standalone_images = build_standalone_image_evidence(
        root,
        image_files_from_dirs(root, args.image_dir, config),
        config,
        captured_at,
        args.write,
    )
    all_image_evidence.extend(standalone_images)
    if standalone_images:
        rows.append(
            {
                "action": "write-images" if args.write else "dry-run-images",
                "category": "image-evidence",
                "chars": 0,
                "images": len(standalone_images),
                "target": "references/image_index.jsonl",
                "source": "standalone image dirs",
            }
        )
    write_image_index(root, all_image_evidence, args.write)

    report = render_report(rows, captured_at)
    print(report)
    if args.write:
        report_path = args.report or root / "distill_report.md"
        report_path.write_text(report, encoding="utf-8")
    else:
        print("Dry run only. Re-run with --write to create reference notes and report.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
