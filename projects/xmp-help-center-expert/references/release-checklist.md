---
title: "XMP Help Center Expert Release Checklist"
source: "local-release-governance"
category: "09-patterns"
captured_at: "2026-05-15"
status: "release-checklist"
source_hash: "manual"
aliases: "release checklist, GitHub publish, public repo"
---

# XMP Help Center Expert Release Checklist

Use this checklist before publishing or updating the public GitHub repository.

## Key Rules

- Keep the source project and global install copy synchronized before release.
- Run both package and distillation validators from the skill root.
- Confirm `NOTICE` is present because the repository includes official third-party help-center evidence.
- Do not claim the package can diagnose private XMP account state.
- Confirm the Fresh Official Source Hook still asks before capture/distillation and only proposes public official XMP sources.

## Use Cases

- Publishing the skill to GitHub.
- Preparing a release update after refresh or optimization.
- Checking whether another user can install and validate the skill.

## Release Steps

1. Run `python3 scripts/validate_skill_assets.py`.
2. Run `python3 scripts/validate_distillation.py --root .`.
3. Run the three representative search checks from the README.
4. Compare source and installed copies with `diff -qr`.
5. Update `VERSION` and `CHANGELOG.md`.
6. Build a distributable bundle with `python3 scripts/build_bundle.py --output /tmp/xmp-help-center-expert.zip`.
7. Confirm `references/source-refresh-candidates.md` and the `official_source_refresh_candidate` regression prompt are present.
8. Commit and push to the public GitHub repository.

## Limitations

- This checklist does not validate live XMP website freshness.
- This checklist does not grant rights to third-party help-center content.

## Source Trace

- Skill root: `SKILL.md`
- Validation script: `scripts/validate_skill_assets.py`
- Bundle script: `scripts/build_bundle.py`
- Distillation config: `distill_config.json`
- Source refresh candidate protocol: `references/source-refresh-candidates.md`
