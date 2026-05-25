# Validation Report

Validated on 2026-05-25 in the local sanitized package directory.

## Commands

```bash
python3 scripts/generate_fb_weekly_report.py
python3 scripts/check_sanitization.py
rg -n "(/Users/takuya|report_id|act_[0-9]{6,}|sk-[A-Za-z0-9_-]{16,}|ghp_[A-Za-z0-9_]{16,}|AKIA[0-9A-Z]{16}|1[3-9][0-9]{9}|[0-9]{1,3}(\.[0-9]{1,3}){3})" . --glob '!outputs/generated/*.xlsx' --glob '!scripts/check_sanitization.py' --glob '!.git/**' || true
rg -n "(?i)(token|cookie|password|secret)" . --glob '!scripts/check_sanitization.py' --glob '!.git/**' || true
```

## Results

- Report generation: pass.
- Generated readiness: `ready_with_caveat`.
- Sanitization checker: pass.
- Private home path / raw report identifier / ad account identifier / credential-like shape / phone / IP grep: no findings.
- Credential keyword grep excluding the checker implementation: no findings.

## Generated Sample Outputs

- `outputs/generated/FB_weekly_report_sanitized_2026-05-25.md`
- `outputs/generated/FB_weekly_report_sanitized_2026-05-25.xlsx`
- `outputs/generated/FB_weekly_report_sanitized_2026-05-25.html`
- `outputs/generated/FB_weekly_report_sanitized_2026-05-25_manifest.json`

The generated outputs are ignored by git and can be regenerated from committed sample data.

## GitHub Push Gate

Target repository: `https://github.com/cuikaiuestc/VIP-Think-Project`.

Observed visibility: `PUBLIC`.

Push status: blocked until explicit owner confirmation.

