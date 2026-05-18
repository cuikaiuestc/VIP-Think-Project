# Migration Notes

Date: 2026-05-16

## Source Repositories

The following public repositories from `https://github.com/cuikaiuestc` were consolidated:

| Source | New location |
| --- | --- |
| `https://github.com/cuikaiuestc/xmp-help-center-expert` | `projects/xmp-help-center-expert/` |
| `https://github.com/cuikaiuestc/ai-video-segment-director` | `projects/ai-video-segment-director/` |
| `https://github.com/cuikaiuestc/ai-weekly-progress-report` | `projects/ai-weekly-progress-report/` |
| `https://github.com/cuikaiuestc/xhs-skill-architecture-report` | `projects/xhs-skill-architecture-report/` |

## Structure Decision

Each original repository was moved into a stable subdirectory under `projects/`. This keeps the original project boundaries visible while giving the company one scannable repository URL.

The original `.git` directories were intentionally excluded, so this repository has one clean history from the consolidation point forward.

## Public-Release Check

Quick checks performed before initial commit:

- Confirmed the GitHub profile currently exposes exactly these four public repositories.
- Copied source contents without nested `.git` directories.
- Checked for unusually large files over 50 MB and 10 MB.
- Ran a broad sensitive-keyword scan.
- The 2026-05-18 clean public rebuild excludes raw captures, raw sources, generated archives, generated HTML reports, and unreviewed image assets from the public release surface.

## Follow-Up Actions

- Keep this repository public only when the current HEAD matches the publication rules.
- Before every future GitHub upload, confirm whether the target is this public work repository or a private/other path.
- If a past public commit is suspected to contain real credentials, private customer data, or other incident-level material, pause normal cleanup and follow incident handling: revoke/rotate secrets, notify the owner, and decide whether to make the repository private or replace it with a fresh clean repository.
