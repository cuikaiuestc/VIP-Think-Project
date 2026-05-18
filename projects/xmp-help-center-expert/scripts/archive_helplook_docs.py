#!/usr/bin/env python3
import argparse
import hashlib
import html
import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path


BASE_URL = "https://help-xmp.mobvista.com"
RUN_ID = "docs-2026-05-12"


def fetch(url: str) -> tuple[str, bytes, str]:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 Codex HelpLook Archiver",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = resp.read()
        content_type = resp.headers.get("content-type", "")
        final_url = resp.geturl()
    return final_url, data, content_type


def safe_slug(value: str) -> str:
    parsed = urllib.parse.urlparse(value)
    raw = parsed.path.strip("/").replace("docs/", "") or "homepage"
    raw = urllib.parse.unquote(raw)
    slug = re.sub(r"[^0-9A-Za-z\u4e00-\u9fff]+", "-", raw).strip("-")
    return slug[:90] or "source"


def extract_doc_links(text: str) -> list[str]:
    links = set()
    for match in re.finditer(r"""href=["']([^"']*/docs/[^"']+)["']""", text):
        href = html.unescape(match.group(1))
        if href.startswith("http"):
            parsed = urllib.parse.urlparse(href)
            if parsed.netloc not in {"help-xmp.mobvista.com", "asy6hz.helplookapp.com"}:
                continue
            path = parsed.path
        else:
            path = urllib.parse.urlparse(href).path
        if path.startswith("/docs/"):
            links.add(BASE_URL + path)
    return sorted(links)


def extract_between_article_div(text: str) -> str:
    markers = ['id="Article_CSS"', 'id="hl-edior3"', "id='Article_CSS'", "id='hl-edior3'"]
    idx = -1
    for marker in markers:
        idx = text.find(marker)
        if idx >= 0:
            break
    if idx < 0:
        return ""
    start = text.rfind("<div", 0, idx)
    if start < 0:
        return ""
    depth = 0
    pos = start
    for token in re.finditer(r"</?div\b[^>]*>", text[start:], re.I | re.S):
        tag = token.group(0)
        if tag.startswith("</"):
            depth -= 1
            if depth == 0:
                end = start + token.end()
                return text[start:end]
        else:
            depth += 1
        pos = start + token.end()
    return text[start:pos]


def first_text(pattern: str, text: str, default: str = "") -> str:
    match = re.search(pattern, text, re.I | re.S)
    if not match:
        return default
    return clean_inline(match.group(1))


def clean_inline(value: str) -> str:
    value = re.sub(r"<[^>]+>", "", value)
    value = html.unescape(value)
    value = re.sub(r"\s+", " ", value).strip()
    return value


def normalize_image_url(tag: str) -> str:
    for attr in ("data-origin", "data-href", "src"):
        match = re.search(attr + r"""=["']([^"']+)["']""", tag, re.I)
        if match:
            url = html.unescape(match.group(1))
            if url.startswith("data:image"):
                continue
            if "load-img." in url:
                continue
            return urllib.parse.urljoin(BASE_URL, url)
    return ""


def html_to_markdown(article_html: str, image_map: dict[str, str]) -> str:
    text = article_html
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.I)
    text = re.sub(r"</p\s*>", "\n\n", text, flags=re.I)
    text = re.sub(r"<h1[^>]*>(.*?)</h1>", lambda m: "\n# " + clean_inline(m.group(1)) + "\n\n", text, flags=re.I | re.S)
    text = re.sub(r"<h2[^>]*>(.*?)</h2>", lambda m: "\n## " + clean_inline(m.group(1)) + "\n\n", text, flags=re.I | re.S)
    text = re.sub(r"<h3[^>]*>(.*?)</h3>", lambda m: "\n### " + clean_inline(m.group(1)) + "\n\n", text, flags=re.I | re.S)
    text = re.sub(r"<blockquote[^>]*>(.*?)</blockquote>", lambda m: "\n> " + clean_inline(m.group(1)) + "\n\n", text, flags=re.I | re.S)
    text = re.sub(r"<li[^>]*>(.*?)</li>", lambda m: "\n- " + clean_inline(m.group(1)), text, flags=re.I | re.S)
    text = re.sub(r"<strong[^>]*>(.*?)</strong>", lambda m: "**" + clean_inline(m.group(1)) + "**", text, flags=re.I | re.S)
    text = re.sub(
        r"<a\b[^>]*href=[\"']([^\"']+)[\"'][^>]*>(.*?)</a>",
        lambda m: f"[{clean_inline(m.group(2))}]({urllib.parse.urljoin(BASE_URL, html.unescape(m.group(1)))})",
        text,
        flags=re.I | re.S,
    )
    def img_replace(match):
        tag = match.group(0)
        remote = normalize_image_url(tag)
        if not remote:
            return ""
        local = image_map.get(remote, remote)
        return f"\n![正文图片]({local})\n"
    text = re.sub(r"<img\b[^>]*>", img_replace, text, flags=re.I | re.S)
    text = re.sub(r"<video\b[^>]*>.*?<source\b[^>]*src=[\"']([^\"']+)[\"'][^>]*>.*?</video>", lambda m: f"\n视频：{html.unescape(m.group(1))}\n", text, flags=re.I | re.S)
    text = re.sub(r"<[^>]+>", "", text)
    text = html.unescape(text)
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def image_extension(url: str, content_type: str) -> str:
    ext = Path(urllib.parse.urlparse(url).path).suffix.lower()
    if ext in {".png", ".jpg", ".jpeg", ".webp", ".gif"}:
        return ".jpg" if ext == ".jpeg" else ext
    if "png" in content_type:
        return ".png"
    if "jpeg" in content_type or "jpg" in content_type:
        return ".jpg"
    if "webp" in content_type:
        return ".webp"
    if "gif" in content_type:
        return ".gif"
    return ".bin"


def download_article_images(article_html: str, root: Path, source_id: str, title: str, source_url: str) -> tuple[dict[str, str], list[dict]]:
    image_urls = []
    for match in re.finditer(r"<img\b[^>]*>", article_html, re.I | re.S):
        url = normalize_image_url(match.group(0))
        if url and "/article/" in url:
            image_urls.append(url)
    image_urls = sorted(set(image_urls))
    image_map = {}
    records = []
    image_dir = root / "raw-sources" / "images" / RUN_ID / safe_slug(source_url)
    thumb_dir = root / "references" / "assets" / "thumbnails" / RUN_ID / safe_slug(source_url)
    image_dir.mkdir(parents=True, exist_ok=True)
    thumb_dir.mkdir(parents=True, exist_ok=True)
    for index, url in enumerate(image_urls, 1):
        try:
            final_url, data, content_type = fetch(url)
        except Exception as exc:
            records.append({"image_url": url, "error": str(exc), "source_id": source_id})
            continue
        digest = hashlib.sha256(data).hexdigest()
        ext = image_extension(final_url, content_type)
        image_id = f"{source_id}-img-{index:02d}-{digest[:8]}"
        filename = f"{image_id}{ext}"
        image_path = image_dir / filename
        thumb_path = thumb_dir / filename
        image_path.write_bytes(data)
        thumb_path.write_bytes(data)
        rel_image = image_path.relative_to(root).as_posix()
        rel_thumb = thumb_path.relative_to(root).as_posix()
        image_map[url] = rel_image
        records.append(
            {
                "image_id": image_id,
                "source_id": source_id,
                "title": title,
                "source_url": source_url,
                "row_id": "",
                "image_path": rel_image,
                "thumbnail_path": rel_thumb,
                "image_url": url,
                "ocr_text": "",
                "visual_summary": "正文配图，需结合原文上下文识别具体界面和字段。",
                "caption": "",
                "notes": "Only article-body images are stored; navigation/logo/decorative homepage images are excluded.",
                "authority_level": "official",
                "confidentiality": "public",
                "captured_at": "2026-05-12",
                "source_hash": digest[:16],
                "bytes": len(data),
                "content_type": content_type,
            }
        )
    return image_map, records


def archive_page(root: Path, url: str) -> dict:
    final_url, data, content_type = fetch(url)
    html_text = data.decode("utf-8", errors="replace")
    article = extract_between_article_div(html_text)
    title = first_text(r'<h1[^>]*class=["\'][^"\']*docs-title[^"\']*["\'][^>]*>(.*?)</h1>', html_text)
    if not title:
        title = first_text(r"<title>(.*?)</title>", html_text, safe_slug(final_url))
    source_id = safe_slug(final_url)
    page_dir = root / "raw-captures" / RUN_ID / source_id
    page_dir.mkdir(parents=True, exist_ok=True)
    (page_dir / "raw.html").write_text(html_text, encoding="utf-8")
    if not article:
        return {
            "id": source_id,
            "title": title,
            "input_url": url,
            "final_url": final_url,
            "path": (page_dir / f"{source_id}.md").relative_to(root).as_posix(),
            "chars": 0,
            "image_files": [],
            "image_urls": [],
            "status": "skipped_no_article",
        }
    image_map, image_records = download_article_images(article, root, source_id, title, final_url)
    markdown_body = html_to_markdown(article, image_map)
    md = "\n".join(
        [
            "---",
            f'title: "{title}"',
            f'source_url: "{final_url}"',
            'authority_level: "official"',
            'confidentiality: "public"',
            'captured_at: "2026-05-12"',
            "---",
            "",
            f"# {title}",
            "",
            markdown_body,
            "",
        ]
    )
    md_path = page_dir / f"{source_id}.md"
    md_path.write_text(md, encoding="utf-8")
    return {
        "id": source_id,
        "title": title,
        "input_url": url,
        "final_url": final_url,
        "path": md_path.relative_to(root).as_posix(),
        "chars": len(markdown_body),
        "source_type": "official_help_center_doc",
        "authority_level": "official",
        "confidentiality": "public",
        "captured_at": "2026-05-12",
        "image_files": [r["image_path"] for r in image_records if "image_path" in r],
        "image_urls": [r["image_url"] for r in image_records if "image_path" in r],
        "image_summary": "Article body images localized when present.",
        "_image_records": image_records,
        "status": "ok",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--limit", type=int, default=120)
    args = parser.parse_args()
    root = Path(args.root).resolve()
    root.mkdir(parents=True, exist_ok=True)
    home_html_path = root / "raw-captures" / "homepage-2026-05-12" / "raw.html"
    if home_html_path.exists():
        home_html = home_html_path.read_text(encoding="utf-8", errors="replace")
    else:
        _, home_data, _ = fetch(BASE_URL + "/")
        home_html = home_data.decode("utf-8", errors="replace")
        home_html_path.parent.mkdir(parents=True, exist_ok=True)
        home_html_path.write_text(home_html, encoding="utf-8")
    urls = extract_doc_links(home_html)
    queue = urls[: args.limit]
    seen = set(queue)
    records = []
    image_records = []
    for i, url in enumerate(queue, 1):
        try:
            record = archive_page(root, url)
        except Exception as exc:
            record = {"id": safe_slug(url), "title": safe_slug(url), "input_url": url, "final_url": url, "path": "", "status": "failed", "error": str(exc)}
        image_records.extend(record.pop("_image_records", []))
        records.append(record)
        print(f"[{i}/{len(queue)}] {record.get('status')} {record.get('title')} {url}")
        time.sleep(0.15)
    manifest_path = root / "raw-captures" / RUN_ID / "manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    image_index_path = root / "references" / "image_index.jsonl"
    image_index_path.parent.mkdir(parents=True, exist_ok=True)
    image_index_path.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in image_records if "image_path" in r) + ("\n" if image_records else ""), encoding="utf-8")
    summary = {
        "run_id": RUN_ID,
        "pages": len(records),
        "ok": sum(1 for r in records if r.get("status") == "ok"),
        "failed": sum(1 for r in records if r.get("status") == "failed"),
        "skipped_no_article": sum(1 for r in records if r.get("status") == "skipped_no_article"),
        "images": sum(1 for r in image_records if "image_path" in r),
        "manifest": manifest_path.relative_to(root).as_posix(),
        "image_index": image_index_path.relative_to(root).as_posix(),
    }
    (root / "reports").mkdir(exist_ok=True)
    (root / "reports" / f"archive-{RUN_ID}.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
