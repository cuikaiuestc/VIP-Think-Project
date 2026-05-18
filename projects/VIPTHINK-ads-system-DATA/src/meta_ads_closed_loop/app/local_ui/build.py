"""Build a local static UI from the read-only closed-loop core."""

from __future__ import annotations

import json
import shutil
from dataclasses import asdict
from pathlib import Path
from typing import Literal

from meta_ads_closed_loop.adapters.meta_readonly import LiveMetaReadonlyAdapter, MockMetaReadonlyAdapter, load_meta_readonly_config
from meta_ads_closed_loop.domain.diagnostics import diagnose_snapshot
from meta_ads_closed_loop.domain.drafts import create_local_draft
from meta_ads_closed_loop.domain.reports import build_closed_loop_report
from meta_ads_closed_loop.domain.safety import MetaWriteBlocker

PROJECT_ROOT = Path(__file__).resolve().parents[4]
DEFAULT_FIXTURE = PROJECT_ROOT / "tests" / "fixtures" / "meta_audit_dataset_minimal.json"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "runtime" / "private" / "local_ui"
DEFAULT_MEDIA_DIR = DEFAULT_OUTPUT_DIR / "media"
STATIC_DIR = Path(__file__).resolve().parent / "static"


def _item_with_metrics(item: object) -> dict[str, object]:
    data = asdict(item)
    for metric in ("ctr", "cpl", "cpa"):
        if hasattr(item, metric):
            data[metric] = getattr(item, metric)
    return data


def _build_drilldown(snapshot: object) -> dict[str, object]:
    ads_by_adset: dict[str, list[dict[str, object]]] = {}
    ads_by_campaign: dict[str, list[dict[str, object]]] = {}
    for ad in snapshot.ads:
        ad_data = _item_with_metrics(ad)
        ads_by_adset.setdefault(ad.adset_id, []).append(ad_data)
        ads_by_campaign.setdefault(ad.campaign_id, []).append(ad_data)

    adsets_by_campaign: dict[str, list[dict[str, object]]] = {}
    for adset in snapshot.adsets:
        ads = ads_by_adset.get(adset.id, [])
        adset_data = {
            **_item_with_metrics(adset),
            "ad_count": len(ads),
            "ads": ads,
        }
        adsets_by_campaign.setdefault(adset.campaign_id, []).append(adset_data)

    campaigns = []
    for campaign in snapshot.campaigns:
        adsets = adsets_by_campaign.get(campaign.id, [])
        campaign_ads = ads_by_campaign.get(campaign.id, [])
        campaigns.append(
            {
                **_item_with_metrics(campaign),
                "adset_count": len(adsets),
                "ad_count": len(campaign_ads),
                "adsets": adsets,
            }
        )

    return {
        "campaigns": campaigns,
        "empty_state": "当前只读快照没有可下钻对象，请检查所选时间窗或 read-only 权限。",
    }


def build_ui_data(
    fixture_path: Path = DEFAULT_FIXTURE,
    *,
    source: Literal["fixture", "live"] = "fixture",
    env_path: Path | None = None,
    account_id: str | None = None,
    date_preset: str = "last_7d",
    max_pages: int = 1,
    media_dir: Path | None = None,
    creative_preview_limit: int = 40,
) -> dict[str, object]:
    if source == "live":
        config = load_meta_readonly_config(env_path)
        adapter = LiveMetaReadonlyAdapter(
            config,
            date_preset=date_preset,
            max_pages=max_pages,
            media_dir=media_dir,
            creative_preview_limit=creative_preview_limit,
        )
        snapshot = adapter.fetch_snapshot(account_id or config.default_account_id)
        accounts = [
            {
                "id": snapshot.account_id,
                "name": snapshot.account_name,
                "currency": snapshot.currency,
                "timezone_name": snapshot.timezone,
                "account_status": "selected",
            }
        ]
    else:
        snapshot = MockMetaReadonlyAdapter(fixture_path).fetch_snapshot()
        accounts = [
            {
                "id": snapshot.account_id,
                "name": snapshot.account_name,
                "currency": snapshot.currency,
                "timezone_name": snapshot.timezone,
                "account_status": "fixture",
            }
        ]
    diagnoses = diagnose_snapshot(snapshot)
    drafts = tuple(create_local_draft(item, created_at="2026-05-17T10:05:00+08:00") for item in diagnoses)
    blocked = (
        MetaWriteBlocker().block("pause", object_type="Campaign", object_id=diagnoses[0].object_id)
        if diagnoses
        else None
    )
    blocked_actions = tuple(item for item in (blocked,) if item is not None)
    report = build_closed_loop_report(snapshot, diagnoses, drafts, blocked_actions)

    return {
        "accounts": accounts,
        "snapshot": {
            **asdict(snapshot),
            "campaigns": [_item_with_metrics(item) for item in snapshot.campaigns],
            "adsets": [_item_with_metrics(item) for item in snapshot.adsets],
            "ads": [_item_with_metrics(item) for item in snapshot.ads],
            "total_spend": snapshot.total_spend,
            "total_leads": snapshot.total_leads,
            "total_purchases": snapshot.total_purchases,
            "total_landing_page_views": snapshot.total_landing_page_views,
        },
        "drilldown": _build_drilldown(snapshot),
        "diagnoses": [asdict(item) for item in diagnoses],
        "drafts": [asdict(item) for item in drafts],
        "blockedActions": [asdict(item) for item in blocked_actions],
        "report": asdict(report),
        "sourceMode": source,
        "workflow": [
            "账户总览",
            "Campaign 下钻",
            "异常诊断",
            "本地优化草稿",
            "安全确认",
            "报表复盘",
        ],
    }


def build_local_ui(
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    fixture_path: Path = DEFAULT_FIXTURE,
    *,
    source: Literal["fixture", "live"] = "fixture",
    env_path: Path | None = None,
    account_id: str | None = None,
    date_preset: str = "last_7d",
    max_pages: int = 1,
    media_dir: Path | None = None,
    creative_preview_limit: int = 40,
) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    for item in STATIC_DIR.iterdir():
        if item.is_file():
            shutil.copy2(item, output_dir / item.name)
    data = build_ui_data(
        fixture_path,
        source=source,
        env_path=env_path,
        account_id=account_id,
        date_preset=date_preset,
        max_pages=max_pages,
        media_dir=media_dir or output_dir / "media",
        creative_preview_limit=creative_preview_limit,
    )
    data_js = "window.META_CLOSED_LOOP_DATA = " + json.dumps(data, ensure_ascii=False, indent=2) + ";\n"
    (output_dir / "data.js").write_text(data_js, encoding="utf-8")
    return output_dir / "index.html"
