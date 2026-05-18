"""Adapter contracts for Meta read-only data.

This module intentionally exposes only read methods. Local drafts and blocked
events live in the domain layer and never call Meta write endpoints.
"""

from __future__ import annotations

import json
import re
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from .models import AccountSnapshot, AdItem, AdSetItem, CampaignItem

LEAD_ACTION_TYPES = {
    "lead",
    "onsite_conversion.lead",
    "onsite_conversion.lead_grouped",
    "onsite_web_lead",
    "offsite_complete_registration_add_meta_leads",
}
PURCHASE_ACTION_TYPES = {
    "purchase",
    "omni_purchase",
    "web_in_store_purchase",
    "web_app_in_store_purchase",
    "onsite_web_purchase",
    "onsite_web_app_purchase",
    "offsite_conversion.fb_pixel_purchase",
}
LPV_ACTION_TYPES = {"landing_page_view", "omni_landing_page_view"}


class MetaReadonlyAdapter(ABC):
    """Read-only Meta product adapter interface."""

    @abstractmethod
    def fetch_snapshot(self) -> AccountSnapshot:
        """Return a normalized account snapshot for local diagnosis."""


class MockMetaReadonlyAdapter(MetaReadonlyAdapter):
    """Load a read-only Meta-like snapshot from a local JSON fixture."""

    def __init__(self, fixture_path: str | Path) -> None:
        self.fixture_path = Path(fixture_path)

    def fetch_snapshot(self) -> AccountSnapshot:
        payload = json.loads(self.fixture_path.read_text(encoding="utf-8"))
        return snapshot_from_audit_payload(payload, source=f"fixture:{self.fixture_path.name}")


def snapshot_from_audit_payload(payload: dict[str, Any], *, source: str) -> AccountSnapshot:
    account = payload.get("summary", {}).get("account") or payload.get("endpoints", {}).get("ad_account", {})
    currency = str(account.get("currency") or "USD")
    campaigns = _campaigns(payload, currency)
    adsets = _adsets(payload, currency)
    ads = _ads(payload, currency)

    return AccountSnapshot(
        account_id=str(account.get("id") or "unknown"),
        account_name=str(account.get("name") or "未知 Meta 账户"),
        currency=currency,
        timezone=str(account.get("timezone") or account.get("timezone_name") or "未知时区"),
        updated_at=str(payload.get("meta", {}).get("generated_at") or "未知时间"),
        source=source,
        campaigns=tuple(campaigns),
        adsets=tuple(adsets),
        ads=tuple(ads),
        object_counts=dict(payload.get("summary", {}).get("object_counts") or {}),
        insight_rows=dict(payload.get("summary", {}).get("insight_rows") or {}),
    )


def _endpoint_rows(payload: dict[str, Any], endpoint: str) -> list[dict[str, Any]]:
    data = payload.get("endpoints", {}).get(endpoint, {}).get("data", [])
    return [row for row in data if isinstance(row, dict)]


def _number(value: Any) -> float:
    if value in (None, ""):
        return 0.0
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _int(value: Any) -> int:
    return int(_number(value))


def _action_value(row: dict[str, Any], action_types: set[str]) -> int:
    total = 0.0
    for action in row.get("actions", []) or []:
        if isinstance(action, dict) and action.get("action_type") in action_types:
            total += _number(action.get("value"))
    return int(total)


def _status_lookup(rows: list[dict[str, Any]]) -> dict[str, str]:
    return {
        str(row.get("id")): str(row.get("effective_status") or row.get("status") or "未知")
        for row in rows
        if row.get("id")
    }


def _campaigns(payload: dict[str, Any], currency: str) -> list[CampaignItem]:
    statuses = _status_lookup(_endpoint_rows(payload, "campaigns"))
    rows = sorted(_endpoint_rows(payload, "insights_campaign"), key=lambda item: _number(item.get("spend")), reverse=True)
    return [
        CampaignItem(
            id=str(row.get("campaign_id") or row.get("id") or row.get("campaign_name") or "unknown-campaign"),
            name=str(row.get("campaign_name") or row.get("name") or "未命名 Campaign"),
            status=statuses.get(str(row.get("campaign_id")), str(row.get("effective_status") or row.get("status") or "未知")),
            spend=round(_number(row.get("spend")), 2),
            impressions=_int(row.get("impressions")),
            clicks=_int(row.get("inline_link_clicks") or row.get("clicks")),
            leads=_action_value(row, LEAD_ACTION_TYPES),
            purchases=_action_value(row, PURCHASE_ACTION_TYPES),
            currency=currency,
            landing_page_views=_action_value(row, LPV_ACTION_TYPES),
        )
        for row in rows
    ]


def _adsets(payload: dict[str, Any], currency: str) -> list[AdSetItem]:
    statuses = _status_lookup(_endpoint_rows(payload, "adsets"))
    rows = sorted(_endpoint_rows(payload, "insights_adset"), key=lambda item: _number(item.get("spend")), reverse=True)
    return [
        AdSetItem(
            id=str(row.get("adset_id") or row.get("id") or row.get("adset_name") or "unknown-adset"),
            name=str(row.get("adset_name") or row.get("name") or "未命名 Ad Set"),
            campaign_id=str(row.get("campaign_id") or "unknown-campaign"),
            status=statuses.get(str(row.get("adset_id")), str(row.get("effective_status") or row.get("status") or "未知")),
            spend=round(_number(row.get("spend")), 2),
            impressions=_int(row.get("impressions")),
            clicks=_int(row.get("inline_link_clicks") or row.get("clicks")),
            landing_page_views=_action_value(row, LPV_ACTION_TYPES),
            leads=_action_value(row, LEAD_ACTION_TYPES),
            purchases=_action_value(row, PURCHASE_ACTION_TYPES),
            currency=currency,
            campaign_name=str(row.get("campaign_name") or ""),
        )
        for row in rows
    ]


def _ads(payload: dict[str, Any], currency: str) -> list[AdItem]:
    statuses = _status_lookup(_endpoint_rows(payload, "ads"))
    rows = sorted(_endpoint_rows(payload, "insights_ad"), key=lambda item: _number(item.get("spend")), reverse=True)
    return [
        AdItem(
            id=str(row.get("ad_id") or row.get("id") or row.get("ad_name") or "unknown-ad"),
            name=str(row.get("ad_name") or row.get("name") or "未命名 Ad"),
            campaign_id=str(row.get("campaign_id") or "unknown-campaign"),
            adset_id=str(row.get("adset_id") or "unknown-adset"),
            status=statuses.get(str(row.get("ad_id")), str(row.get("effective_status") or row.get("status") or "未知")),
            spend=round(_number(row.get("spend")), 2),
            impressions=_int(row.get("impressions")),
            clicks=_int(row.get("inline_link_clicks") or row.get("clicks")),
            landing_page_views=_action_value(row, LPV_ACTION_TYPES),
            leads=_action_value(row, LEAD_ACTION_TYPES),
            purchases=_action_value(row, PURCHASE_ACTION_TYPES),
            currency=currency,
            campaign_name=str(row.get("campaign_name") or ""),
            adset_name=str(row.get("adset_name") or ""),
            creative=_safe_creative(row.get("creative")),
        )
        for row in rows
    ]


def _safe_creative(value: Any) -> dict[str, object]:
    if not isinstance(value, dict):
        return {}
    allowed = {
        "id",
        "name",
        "title",
        "body",
        "video_id",
        "object_story_spec",
        "preview_url",
        "preview_status",
    }
    result: dict[str, object] = {}
    for key, item in value.items():
        if key in allowed:
            result[str(key)] = _redact_url_secret(item)
    return result


def _redact_url_secret(value: Any) -> object:
    if isinstance(value, str):
        return re.sub(r"access_token=[^&\s]+", "access_token=REDACTED", value)
    if isinstance(value, dict):
        return {
            str(key): _redact_url_secret(item)
            for key, item in value.items()
            if str(key) not in {"thumbnail_url", "image_url"}
        }
    if isinstance(value, list):
        return [_redact_url_secret(item) for item in value]
    return value
