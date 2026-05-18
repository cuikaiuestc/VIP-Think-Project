---
title: "XMP Help Center Response Review Checklist"
source: "local-skill-quality"
category: "09-patterns"
captured_at: "2026-05-13"
status: "review-checklist"
source_hash: "manual"
aliases: "answer review, regression review, response checklist"
---

# XMP Help Center Response Review Checklist

Use this checklist when reviewing answers to `test-prompts.json` or when judging whether an answer stayed within the XMP Help Center evidence.

## Key Rules

- Review answer claims against local official-source references.
- Treat account-specific claims as blocked unless the user supplied live XMP evidence.
- Require image evidence to be traceable through `references/image_index.jsonl`.

## Use Cases

- Reviewing regression answers for `test-prompts.json`.
- Checking whether an answer overclaims from public documentation.
- Deciding whether a response needs a blocked/tentative confidence label.

## Required Checks

- The answer selects a confidence level: `firm`, `tentative`, or `blocked`.
- The answer includes `Official Basis` with local reference paths and what each source supports.
- The answer separates official help-center facts from inference or user-provided account evidence.
- The answer uses `references/09-patterns/` for routing questions before concrete reference files.
- API answers cite `references/07-open-api/`.
- Release answers cite `references/08-release-notes/`.
- Image references come from `references/image_index.jsonl` and are not treated as OCR evidence.

## Must Not Do

- Do not claim to know live XMP backend state without user-provided surface evidence.
- Do not treat homepage/category routing as full operation steps.
- Do not guarantee feature access, delivery, approval, API permission, data accuracy, or campaign outcome.
- Do not answer account-specific errors from public KB alone.
- Do not cite raw images as proof of text unless the matching Markdown reference supports the claim.

## Acceptance Standard

An answer passes when a user can trace every substantive claim to a local official-source reference or to clearly labeled user-provided evidence.

## Limitations

- This checklist does not validate factual freshness against the live XMP website.
- It reviews answer behavior, not the completeness of the underlying official captures.

## Source Trace

- Test cases: `test-prompts.json`
- Skill instructions: `SKILL.md`
