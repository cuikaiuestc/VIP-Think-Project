---
title: "XMP Source Refresh Candidate Protocol"
source: "https://help-xmp.mobvista.com/"
category: "09-patterns"
captured_at: "2026-05-15"
status: "maintenance-pattern"
source_hash: "manual"
aliases: "LLM WIKI hook, source refresh candidate, incremental official source, XMP KB update, 官方帮助页纳入知识库, 新官方来源, 来源刷新候选, 增量知识库"
---

# XMP Source Refresh Candidate Protocol

Use this protocol when a conversation reveals a public official XMP Help Center source that should potentially become part of the local knowledge base.

## Key Rules

- Only propose candidates from public official XMP Help Center or clearly official Mobvista/XMP documentation sources.
- Do not crawl, capture, distill, or write references automatically from the answer flow.
- Always ask for confirmation before running archive or distillation steps.
- Never ingest private account pages, screenshots, tokens, backend errors, or login-only XMP surfaces into the public KB.
- Keep every accepted candidate traceable through URL, capture date, reference path, validation output, and `references/url_map.md`.

## Use Cases

- 用户提供新的 XMP 官方帮助页，询问是否可以纳入知识库。
- A user shares a `help-xmp.mobvista.com` page that is missing from the current local capture.
- A release, API, route, or how-to answer depends on a public official page newer than the current local reference.
- A current local reference is marked partial or incomplete and the conversation reveals a better official source.

## Purpose

This is the skill's LLM WIKI-style incremental ingestion gate. It does not crawl by itself. It makes future KB updates explicit, reviewable, and limited to official public XMP sources.

## Candidate Criteria

A candidate qualifies only when all are true:

- The URL is official or likely official: `help-xmp.mobvista.com` or a public Mobvista/XMP documentation page clearly tied to XMP Help Center content.
- The source would improve future answers for route, how-to, API reference, release lookup, or feature explanation.
- The source is absent from `references/url_map.md`, marked incomplete/partial/queued, or newer than the current local capture.

## Reject Criteria

Do not propose ingestion when the source is:

- A private XMP backend page, account-specific screenshot, token page, error page, or login-only surface.
- A non-official blog, forum, competitor page, copied article, or user interpretation.
- Only loosely related to the user's XMP Help Center question.

## Output Shape

When triggered, append:

```markdown
## Source Refresh Candidate

- Candidate: <title or URL>
- Why it qualifies: <official source + missing/newer/partial + future answer value>
- Proposed update path: capture public page -> distill -> validate retrieval -> update url_map -> sync/install
- Confirmation needed: ask before capture or distillation
```

## Update Path

1. Capture only public official content into `[omitted-raw-capture-path]`.
2. Distill with `python3 scripts/distill_captures.py --root .`.
3. Validate with `python3 scripts/validate_distillation.py --root .`.
4. Run targeted retrieval with `python3 scripts/search_kb.py "<query>"`.
5. Run `python3 scripts/validate_skill_assets.py`.
6. Update `references/url_map.md` with URL, status, category, image count, capture date, and reference path.

## Limits

This protocol does not replace scheduled full refreshes in `references/xmp-official-refresh-automation.md`. It is for small, conversation-discovered official-source candidates.

## Limitations

- This protocol does not validate whether a candidate URL is currently reachable.
- This protocol does not authorize login, CAPTCHA bypass, private account inspection, or token collection.
- This protocol does not prove that the candidate should be merged; merge decisions require capture quality, distillation quality, and retrieval validation.
- This protocol does not update installed global copies or GitHub by itself.

## Source Trace

- Source scope: public XMP Help Center official pages.
- Source URL root: `https://help-xmp.mobvista.com/`
- Current URL map: `references/url_map.md`
- Full refresh protocol: `references/xmp-official-refresh-automation.md`
- Validation script: `scripts/validate_skill_assets.py`
