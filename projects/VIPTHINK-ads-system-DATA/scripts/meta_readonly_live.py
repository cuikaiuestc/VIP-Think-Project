#!/usr/bin/env python3
"""Run read-only Meta account discovery or local UI generation."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from meta_ads_closed_loop.adapters.meta_readonly import (
    LiveMetaReadonlyAdapter,
    MetaConfigError,
    load_meta_readonly_config,
)
from meta_ads_closed_loop.adapters.meta_readonly.live import redact_token


def main() -> int:
    parser = argparse.ArgumentParser(description="Meta read-only live helper.")
    parser.add_argument("--env", default="runtime/private/meta/.env")
    parser.add_argument("--mode", choices=["list-accounts", "snapshot"], default="list-accounts")
    parser.add_argument("--account-id", default=None)
    parser.add_argument("--date-preset", default="last_7d")
    parser.add_argument("--max-pages", type=int, default=1)
    parser.add_argument("--output", default="runtime/private/meta/live_snapshot.json")
    args = parser.parse_args()

    try:
        config = load_meta_readonly_config(Path(args.env))
        adapter = LiveMetaReadonlyAdapter(config, date_preset=args.date_preset, max_pages=args.max_pages)
        print(f"Meta API version: {config.api_version}")
        print(f"Token: {redact_token(config.access_token)}")
        if args.mode == "list-accounts":
            accounts = adapter.fetch_accounts()
            print(json.dumps({"account_count": len(accounts), "accounts": accounts}, ensure_ascii=False, indent=2))
            return 0

        snapshot = adapter.fetch_audit_payload(args.account_id or config.default_account_id or "")
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Output: {output_path.resolve()}")
        print(json.dumps(snapshot["summary"], ensure_ascii=False, indent=2))
        return 0
    except MetaConfigError as exc:
        print(str(exc))
        return 2


if __name__ == "__main__":
    sys.exit(main())
