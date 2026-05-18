# Publication Rules

This repository is public. Treat every committed file as externally visible.

## Default Policy

- Public release must use a whitelist mindset: publish only reviewed source assets.
- Keep private work, uncertain work, raw captures, and exports outside this repository.
- Do not use GitHub as a file backup location.
- Do not commit credentials, tokens, cookies, account exports, private screenshots, raw business data, logs, or generated archives.

## Allowed By Default

- README and project documentation intended for public readers.
- `SKILL.md`, `test-prompts.json`, `VERSION`, `CHANGELOG.md`, `LICENSE`, and `NOTICE`.
- Reusable scripts that do not contain local private paths, credentials, or account-specific values.
- Templates and fake or de-identified examples.
- Public-source references after review.

## Blocked By Default

- `.env`, tokens, cookies, keys, certificates, and private credentials.
- Raw web captures and raw source mirrors such as `raw-captures/` and `raw-sources/`.
- Generated archives such as `dist/*.zip`.
- Raw business exports, spreadsheets, PDFs, screenshots, logs, and private reports.
- Unreviewed generated HTML reports and image assets.
- Customer, student, parent, supplier, order, revenue, cost, contract, or internal strategy data.

## Required Before Publishing

1. Confirm the target repository and visibility.
2. Review the full changed-file list.
3. Run a sensitive keyword scan.
4. Run a file type and large-file scan.
5. Confirm that examples are fake, public, or de-identified.
6. Record any excluded or unresolved items in the PR description.
7. Use a branch and PR review before updating `main`.

## Incident Boundary

If a real secret, credential, private customer record, or business-sensitive export may have been exposed, do not treat it as a normal cleanup. Pause and escalate to the repository owner for secret rotation, visibility changes, or history cleanup decisions.
