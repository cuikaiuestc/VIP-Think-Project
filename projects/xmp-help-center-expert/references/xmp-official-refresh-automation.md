---
title: "XMP Official Help Center Refresh Automation"
source: "https://help-xmp.mobvista.com/"
category: "09-patterns"
captured_at: "2026-05-13"
status: "refresh-protocol"
source_hash: "manual"
aliases: "XMP refresh, help center refresh, official source update"
---

# XMP Official Help Center Refresh Automation

Use this protocol when refreshing the official XMP Help Center knowledge base.

## Key Rules

- Refresh from the public official XMP Help Center only.
- Preserve archive reports before changing distilled references.
- Validate retrieval and image paths before installing the refreshed skill globally.

## Use Cases

- Re-capturing XMP Help Center pages after official documentation changes.
- Adding newly published pages to the local KB.
- Re-validating route/how-to/API/release retrieval after a refresh.
- Processing confirmed `Source Refresh Candidate` items proposed by the LLM WIKI-style hook in `references/source-refresh-candidates.md`.

## Operating Contract

- Run from the skill root.
- Source of truth is `https://help-xmp.mobvista.com/`.
- Preserve public official provenance: URL, capture date, status, title, image paths, and source hash.
- Do not overwrite existing references until archive and distillation reports look sane.

## Refresh Steps

1. Capture the help center and detail pages with `python3 scripts/archive_helplook_docs.py`.
2. Distill captured pages with `python3 scripts/distill_captures.py --root .`.
3. Run `python3 scripts/validate_distillation.py --root .`.
4. Run `python3 scripts/search_kb.py "<representative query>"` for route, how-to, API, release, and blocked/account-state scenarios.
5. Run `python3 scripts/validate_skill_assets.py`.
6. Update `references/url_map.md` with page status, category, image count, and reference path.

## Stop Conditions

- Stop before distillation if capture returns mostly empty pages, login walls, redirects, or low-content category shells.
- Stop before writing references if routing searches no longer hit expected pattern files.
- Stop before installing globally if `validate_skill_assets.py` fails.

## Refresh Report

Record the run id, source URL, page count, image count, reference count, validation result, and notable new/removed pages in `reports/`.

## Limitations

- This protocol does not bypass login-only content.
- It does not update private account state or customer-specific backend data.

## Source Trace

- Current manifest: `[omitted-raw-capture-path]`
- Current distillation config: `distill_config.json`
- Source URL: https://help-xmp.mobvista.com/
- Incremental candidate protocol: `references/source-refresh-candidates.md`
