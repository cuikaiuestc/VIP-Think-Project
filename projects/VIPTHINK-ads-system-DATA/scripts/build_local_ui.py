#!/usr/bin/env python3
"""Build the local static product UI under runtime/private/local_ui."""

import argparse
from pathlib import Path

from meta_ads_closed_loop.app.local_ui.build import DEFAULT_OUTPUT_DIR, build_local_ui


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build the local Meta closed-loop UI.")
    parser.add_argument("--source", choices=["fixture", "live"], default="fixture")
    parser.add_argument("--fixture", default="tests/fixtures/meta_audit_dataset_minimal.json")
    parser.add_argument("--env", default="runtime/private/meta/.env")
    parser.add_argument("--account-id", default=None)
    parser.add_argument("--date-preset", default="last_7d")
    parser.add_argument("--max-pages", type=int, default=1)
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--media-dir", default=None)
    parser.add_argument("--creative-preview-limit", type=int, default=40)
    args = parser.parse_args()

    html_path = build_local_ui(
        output_dir=Path(args.output_dir),
        fixture_path=Path(args.fixture),
        source=args.source,
        env_path=Path(args.env),
        account_id=args.account_id,
        date_preset=args.date_preset,
        max_pages=args.max_pages,
        media_dir=Path(args.media_dir) if args.media_dir else None,
        creative_preview_limit=args.creative_preview_limit,
    )
    print(Path(html_path).resolve())
    print(f"Output directory: {Path(args.output_dir).resolve()}")
