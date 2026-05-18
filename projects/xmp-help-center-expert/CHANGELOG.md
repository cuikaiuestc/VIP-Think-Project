# Changelog

## 1.2.0 - 2026-05-15

- Added an LLM WIKI-style Fresh Official Source Hook to propose incremental XMP official-source ingestion when conversations reveal useful new official help-center URLs.
- Added `references/source-refresh-candidates.md` as the reviewable protocol for source candidates, reject criteria, and update path.
- Added a regression prompt for official-source refresh candidates.
- Strengthened package validation so the hook, candidate protocol, and regression case must stay present.

## 1.1.0 - 2026-05-15

- Hardened retrieval so scenario patterns can pull concrete official references into search results.
- Added three response fixtures covering `firm`, `api-reference`, and `blocked` answer behavior.
- Strengthened `scripts/validate_skill_assets.py` to check fixtures, referenced paths, image paths, and companion retrieval.
- Added public-release governance files for GitHub publication.
- Added a portable zip bundle builder for public distribution.

## 1.0.0 - 2026-05-13

- Created the `xmp-help-center-expert` Codex skill from the XMP Help Center archive.
- Archived 41/41 public detail pages from `https://help-xmp.mobvista.com/`.
- Localized 374 image evidence items.
- Distilled official references and scenario routing notes.
- Added skill-level validation and regression prompts.
