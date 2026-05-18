# XMP Help Center Expert

`xmp-help-center-expert` is a Codex skill that turns the public XMP Help Center into a traceable, validated expert assistant for XMP feature routing, how-to questions, Open API lookup, release-note lookup, and support-boundary decisions.

When installed globally, this directory is copied to `/Users/takuya/.codex/skills/xmp-help-center-expert` and used as a Codex skill.

## Value For External Reporting

This project converts a scattered official help center into a reusable AI operating asset:

- **Faster support and onboarding**: users can ask natural-language XMP questions and get routed to the correct official document instead of manually browsing the help center.
- **Traceable answers**: every substantive answer is grounded in local official references, URL maps, image evidence, and validation reports.
- **Reusable support boundary**: the skill explicitly separates public documentation facts from private account state, preventing unsupported claims about permissions, delivery, API tokens, or backend errors.
- **LLM WIKI-style growth loop**: when a conversation exposes a useful new official XMP Help Center URL, the skill can propose a `Source Refresh Candidate` instead of silently ignoring it or crawling without approval.
- **Repeatable maintenance**: archive, distillation, search, and validation scripts make future refreshes auditable instead of one-off manual work.
- **Product knowledge leverage**: 41 official pages, 35 distilled source notes, 11 scenario patterns, 374 image evidence items, 11 regression prompts, and 3 answer fixtures are packaged as one validated Codex skill.

In practical terms, the skill reduces repeated documentation lookup, improves answer consistency, and gives support/product/operations teams a controlled way to reuse official XMP knowledge inside Codex.

## Source Scope

- Source URL: https://help-xmp.mobvista.com/
- Homepage capture: `[omitted-raw-capture-path]`
- Detail-page manifest: `[omitted-raw-capture-path]`
- Authority: official public help center
- Current scope: homepage/navigation capture plus 41 linked detail pages.

## Current Status

- Version: 1.2.0
- Detail pages archived: 41/41
- Localized images: 374
- Reference Markdown files: 35
- Skill support files: `SKILL.md`, `test-prompts.json`, `references/url_map.md`, `references/response-review-checklist.md`, `references/xmp-official-refresh-automation.md`
- Scenario patterns: 11
- Response fixtures: 3
- Regression prompts: 11
- Retrieval checks: 4/4 passed

## Quick Install

Copy this directory to your Codex skills folder:

```bash
mkdir -p ~/.codex/skills
rsync -a xmp-help-center-expert/ ~/.codex/skills/xmp-help-center-expert/
```

Then ask Codex a question such as:

```text
Use $xmp-help-center-expert: XMP Open API 有哪些入口？
```

## Validation

Run these checks from the skill root:

```bash
python3 scripts/validate_skill_assets.py
python3 scripts/validate_distillation.py --root .
python3 scripts/search_kb.py "XMP 接口请求协议怎么查" --limit 8
python3 scripts/search_kb.py "XMP 一键上单是什么" --limit 8
python3 scripts/search_kb.py "我的 XMP 账号为什么不能投放" --limit 8
```

Expected result:

- skill assets validated
- structure failures: 0
- image evidence failures: 0
- retrieval checks: 4/4 passed
- representative searches include both scenario patterns and concrete official references

## Build A Bundle

To create a portable zip bundle:

```bash
python3 scripts/build_bundle.py --output /tmp/xmp-help-center-expert.zip
```

The bundle includes the skill package and local evidence assets, excluding `.git`, caches, virtual environments, and generated zip files.

## LLM WIKI-Style Source Refresh

The skill includes a Fresh Official Source Hook modeled after the `facebook-ads-expert` source-refresh pattern. After answering, it checks whether the conversation revealed a useful public official XMP source that is missing, partial, or newer than the local capture.

When triggered, the skill should append a `Source Refresh Candidate` section that:

- names the candidate official URL or title;
- explains why it qualifies;
- proposes the capture -> distill -> validate -> `url_map` update path;
- asks for confirmation before any capture or distillation.

The detailed protocol is in `references/source-refresh-candidates.md`; the full refresh operating contract remains in `references/xmp-official-refresh-automation.md`.

## Folder Contract

- Raw captures and localized source images are omitted from this clean public release.
- `references/`: distilled source notes and hand-written scenario patterns.
- `references/source-refresh-candidates.md`: LLM WIKI-style incremental official-source ingestion protocol.
- `references/image_index.jsonl`: image evidence index, omitted unless separately reviewed.
- `reports/`: archive, distillation, and validation reports, omitted unless separately reviewed.
- `scripts/`: copied distillation/search/validation scripts from `knowledge-base-distiller`.
- `scripts/build_bundle.py`: builds a portable zip bundle for distribution.
- `distill_config.json`: routing, aliases, and validation queries for XMP help-center questions.
- `test-prompts.json`: regression prompt cases for answer behavior.
- `response-fixtures/`: expected answer-shape fixtures for firm/API/blocked cases.
- `agents/openai.yaml`: Codex UI metadata.

## Public Content Notice

The repository includes archived public XMP Help Center evidence for traceability. Skill code and glue files are provided under the repository license; XMP, Mobvista, HelpLook, source help-center text, screenshots, images, product names, and trademarks remain the property of their respective owners. See `NOTICE`.
