# Publish Checklist

Use this checklist before any public update.

## Repository Boundary

- [ ] Target repository confirmed.
- [ ] Repository visibility confirmed.
- [ ] Work is on a branch, not direct `main`.
- [ ] README explains the public/private boundary.
- [ ] `.gitignore` blocks private files, raw exports, generated packages, and unreviewed captures.

## File Review

- [ ] Changed-file list reviewed.
- [ ] No `.env`, token, cookie, key, certificate, or private credential.
- [ ] No raw business export, private spreadsheet, PDF, screenshot, or log.
- [ ] No raw captures or raw source mirrors.
- [ ] No generated archives such as `dist/*.zip`.
- [ ] No unreviewed generated HTML or image assets.
- [ ] Examples are fake, public, or de-identified.

## Scans

- [ ] Sensitive keyword scan completed.
- [ ] Business-sensitive keyword scan completed.
- [ ] File type and large-file scan completed.
- [ ] Scan findings are explained or remediated.

## Review

- [ ] PR description includes what changed.
- [ ] PR description includes verification commands and scan results.
- [ ] PR description lists excluded assets and unresolved decisions.
- [ ] Repository owner has approved any risky publication decision.
