#!/usr/bin/env python3
"""Search a distilled Markdown knowledge base."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re


DEFAULT_STOPWORDS = {"the", "a", "an", "and", "or", "of", "for", "to", "in", "xmp", "我的", "知识", "问题", "怎么"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Search a distilled skill knowledge base.")
    parser.add_argument("query", help="Keyword or phrase to search for.")
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="Target skill root.")
    parser.add_argument("--config", type=Path, help="distill_config.json path.")
    parser.add_argument("--limit", type=int, default=12, help="Maximum results.")
    return parser.parse_args()


def load_config(root: Path, config_path: Path | None) -> dict:
    path = config_path or root / "distill_config.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}


def terms_for(query: str, config: dict) -> list[str]:
    lowered = query.lower().strip()
    parts = [part for part in re.split(r"\s+", lowered) if part]
    stopwords = set(config.get("stopwords", DEFAULT_STOPWORDS))
    compact = re.sub(r"\s+", "", lowered)
    terms = [lowered]
    if compact and compact != lowered:
        terms.append(compact)
    for part in parts:
        if part not in terms and part not in stopwords:
            terms.append(part)
    for needle, aliases in config.get("aliases", {}).items():
        if needle.lower() in lowered:
            for alias in aliases:
                alias = alias.lower()
                if alias not in terms:
                    terms.append(alias)
    return terms


def title_for(text: str, fallback: str) -> str:
    match = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
    return match.group(1).strip() if match else fallback


def source_for(text: str) -> str:
    match = re.search(r"^source:\s*(.+)$", text, re.MULTILINE)
    return match.group(1).strip() if match else ""


def count_term(text: str, term: str) -> int:
    if re.fullmatch(r"[a-z0-9]{1,2}", term.lower()):
        return len(re.findall(rf"\b{re.escape(term.lower())}\b", text))
    return text.count(term.lower())


def score(path: Path, text: str, query: str, config: dict) -> int:
    terms = terms_for(query, config)
    lowered = text.lower()
    path_lower = path.as_posix().lower()
    value = 0
    for index, term in enumerate(terms):
        weight = 3 if index == 0 else 1
        value += count_term(lowered, term) * weight
        if term in path_lower:
            value += 8
    pattern_dirs = tuple(config.get("pattern_dirs", ["09-patterns", "patterns"]))
    if value > 0 and any(part in path.parts for part in pattern_dirs):
        value += int(config.get("pattern_boost", 220))
    return value


def companion_references(text: str) -> list[str]:
    refs = []
    for ref in re.findall(r"`(references/[^`]+\.md)`", text):
        if ref not in refs:
            refs.append(ref)
    return refs


def snippets(text: str, query: str, config: dict) -> list[str]:
    lowered = text.lower()
    hits = []
    for term in terms_for(query, config):
        idx = lowered.find(term)
        if idx == -1:
            continue
        left = max(0, idx - 90)
        right = min(len(text), idx + len(term) + 140)
        hits.append(re.sub(r"\s+", " ", text[left:right]).strip())
        if len(hits) >= 2:
            break
    return hits


def image_text(item: dict) -> str:
    values = [
        item.get("title", ""),
        item.get("caption", ""),
        item.get("ocr_text", ""),
        item.get("visual_summary", ""),
        item.get("notes", ""),
        item.get("tags", ""),
        item.get("source_url", ""),
    ]
    return "\n".join(str(value) for value in values if value)


def search_images(root: Path, query: str, config: dict) -> list[tuple[int, dict]]:
    index_path = root / "references" / "image_index.jsonl"
    if not index_path.exists():
        return []
    results = []
    for line in index_path.read_text(encoding="utf-8", errors="ignore").splitlines():
        if not line.strip():
            continue
        item = json.loads(line)
        text = image_text(item)
        item_score = score(Path(item.get("image_path", "image")), text, query, config)
        if item_score <= 0:
            continue
        results.append((item_score + int(config.get("image_boost", 40)), item))
    results.sort(key=lambda row: (-row[0], row[1].get("image_id", "")))
    return results


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    config = load_config(root, args.config)
    references = root / "references"
    text_results = []
    by_relative_path = {}
    for path in references.rglob("*.md"):
        text = path.read_text(encoding="utf-8", errors="ignore")
        item_score = score(path, text, args.query, config)
        if item_score <= 0:
            continue
        row = {"kind": "text", "score": item_score, "path": path, "text": text}
        text_results.append(row)
        by_relative_path[path.relative_to(root).as_posix()] = row

    pattern_dirs = tuple(config.get("pattern_dirs", ["09-patterns", "patterns"]))
    companion_boost = int(config.get("pattern_reference_boost", 20))
    eligible_patterns = [
        row
        for row in text_results
        if any(part in row["path"].parts for part in pattern_dirs)
        and row["path"].name not in set(config.get("no_companion_patterns", []))
    ]
    eligible_patterns.sort(key=lambda row: (-row["score"], row["path"].as_posix()))
    for row in eligible_patterns[: int(config.get("max_companion_patterns", 1))]:
        path = row["path"]
        for ref in companion_references(row["text"]):
            companion = by_relative_path.get(ref)
            if companion is None:
                ref_path = root / ref
                if not ref_path.exists():
                    continue
                text = ref_path.read_text(encoding="utf-8", errors="ignore")
                companion = {"kind": "text", "score": 0, "path": ref_path, "text": text}
                text_results.append(companion)
                by_relative_path[ref] = companion
            companion["score"] = max(companion["score"], row["score"] + companion_boost)
    image_results = search_images(root, args.query, config)
    merged = text_results + [{"kind": "image", "score": item_score, "item": item} for item_score, item in image_results]
    merged.sort(key=lambda row: (-row["score"], row.get("path", Path(row.get("item", {}).get("image_id", ""))).as_posix() if row["kind"] == "text" else row["item"].get("image_id", "")))
    for row in merged[: args.limit]:
        if row["kind"] == "text":
            item_score = row["score"]
            path = row["path"]
            text = row["text"]
            rel = path.relative_to(root)
            print(f"\n[{item_score}] {rel}")
            print(f"Title: {title_for(text, path.stem)}")
            print(f"Category: {rel.parts[1] if len(rel.parts) > 2 else rel.parts[0]}")
            source = source_for(text)
            if source:
                print(f"Source: {source}")
            for hit in snippets(text, args.query, config):
                print(f"- ...{hit}...")
            continue
        item_score = row["score"]
        item = row["item"]
        print(f"\n[{item_score}] references/image_index.jsonl#{item.get('image_id', '')}")
        print(f"Title: {item.get('title') or item.get('image_id')}")
        print("Category: image-evidence")
        source = item.get("source_url") or item.get("source_id")
        if source:
            print(f"Source: {source}")
        print(f"Image: {item.get('image_path', '')}")
        print(f"Thumbnail: {item.get('thumbnail_path', '')}")
        if item.get("row_id"):
            print(f"Row ID: {item.get('row_id')}")
        summary = item.get("visual_summary") or item.get("caption") or item.get("ocr_text")
        if summary:
            compact_summary = re.sub(r"\s+", " ", summary).strip()[:240]
            print(f"- ...{compact_summary}...")

    if not merged:
        print("No matches.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
