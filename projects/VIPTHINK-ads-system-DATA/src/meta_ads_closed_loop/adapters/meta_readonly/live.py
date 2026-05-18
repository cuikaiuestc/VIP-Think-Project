"""Live read-only Meta Marketing API adapter.

The adapter only performs Graph API GET requests. It has no methods for
publishing, pausing, budget changes, bid changes, creative replacement, or
deletion.
"""

from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Protocol

from .adapter import MetaReadonlyAdapter, snapshot_from_audit_payload
from .models import AccountSnapshot

DEFAULT_API_VERSION = "v25.0"


class MetaConfigError(RuntimeError):
    """Raised when local Meta read-only credentials are missing or incomplete."""


class JsonTransport(Protocol):
    def __call__(self, url: str, timeout: int) -> dict[str, Any]:
        ...


@dataclass(frozen=True)
class MetaReadonlyConfig:
    access_token: str
    api_version: str = DEFAULT_API_VERSION
    default_account_id: str | None = None


def load_env_text(text: str) -> dict[str, str]:
    env: dict[str, str] = {}
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        value = value.strip()
        if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
            value = value[1:-1]
        env[key.strip()] = value
    return env


def load_env_file(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    return load_env_text(path.read_text(encoding="utf-8"))


def load_meta_readonly_config(env_path: Path | None = None) -> MetaReadonlyConfig:
    env = dict(os.environ)
    if env_path is not None:
        env.update(load_env_file(env_path))
    token = env.get("META_ACCESS_TOKEN", "").strip()
    if not token:
        raise MetaConfigError("Missing META_ACCESS_TOKEN. Put it in runtime/private/meta/.env or environment variables.")
    account_id = env.get("META_AD_ACCOUNT_ID", "").strip() or None
    return MetaReadonlyConfig(
        access_token=token,
        api_version=env.get("META_API_VERSION", DEFAULT_API_VERSION).strip() or DEFAULT_API_VERSION,
        default_account_id=normalize_account_id(account_id) if account_id else None,
    )


def normalize_account_id(account_id: str) -> str:
    account_id = account_id.strip()
    if account_id.startswith("act_"):
        return account_id
    return f"act_{account_id}"


def redact_token(token: str) -> str:
    if len(token) < 12:
        return "****"
    return f"{token[:4]}...{token[-4:]}"


def fetch_url_json(url: str, timeout: int = 30) -> dict[str, Any]:
    with urllib.request.urlopen(url, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


class MetaGraphReadonlyClient:
    def __init__(
        self,
        config: MetaReadonlyConfig,
        *,
        transport: JsonTransport = fetch_url_json,
        timeout: int = 30,
    ) -> None:
        self.config = config
        self.transport = transport
        self.timeout = timeout

    def get(self, object_id: str, edge: str | None = None, params: dict[str, str] | None = None) -> dict[str, Any]:
        query = dict(params or {})
        query["access_token"] = self.config.access_token
        base = f"https://graph.facebook.com/{self.config.api_version}/{object_id}"
        if edge:
            base = f"{base}/{edge}"
        url = f"{base}?{urllib.parse.urlencode(query)}"
        return self.transport(url, self.timeout)

    def get_paged(
        self,
        object_id: str,
        edge: str | None,
        params: dict[str, str],
        *,
        max_pages: int,
    ) -> dict[str, Any]:
        first_payload = self.get(object_id, edge, params)
        if "data" not in first_payload:
            return first_payload
        rows = list(first_payload.get("data") or [])
        pages_fetched = 1
        next_url = first_payload.get("paging", {}).get("next")
        while next_url and pages_fetched < max_pages:
            payload = self.transport(next_url, self.timeout)
            rows.extend(payload.get("data") or [])
            pages_fetched += 1
            next_url = payload.get("paging", {}).get("next")
        return {
            **{key: value for key, value in first_payload.items() if key != "paging"},
            "data": rows,
            "paging_summary": {
                "pages_fetched": pages_fetched,
                "rows_returned": len(rows),
                "has_next_page": bool(next_url),
            },
        }

    def list_ad_accounts(self, *, max_pages: int = 10) -> list[dict[str, Any]]:
        payload = self.get_paged(
            "me",
            "adaccounts",
            {
                "fields": "id,name,currency,timezone_name,account_status,amount_spent,balance,spend_cap,business",
                "limit": "100",
            },
            max_pages=max_pages,
        )
        return [row for row in payload.get("data", []) if isinstance(row, dict)]


class LiveMetaReadonlyAdapter(MetaReadonlyAdapter):
    def __init__(
        self,
        config: MetaReadonlyConfig,
        *,
        date_preset: str = "last_7d",
        max_pages: int = 1,
        media_dir: Path | None = None,
        creative_preview_limit: int = 40,
        client: MetaGraphReadonlyClient | None = None,
    ) -> None:
        self.config = config
        self.date_preset = date_preset
        self.max_pages = max_pages
        self.media_dir = media_dir
        self.creative_preview_limit = creative_preview_limit
        self.client = client or MetaGraphReadonlyClient(config)

    def fetch_accounts(self) -> list[dict[str, Any]]:
        accounts = self.client.list_ad_accounts(max_pages=self.max_pages)
        return [_safe_account(row) for row in accounts]

    def fetch_snapshot(self, account_id: str | None = None) -> AccountSnapshot:
        resolved_account_id = normalize_account_id(account_id or self.config.default_account_id or "")
        if resolved_account_id == "act_":
            raise MetaConfigError("Missing META_AD_ACCOUNT_ID or explicit account_id for snapshot fetch.")
        payload = self.fetch_audit_payload(resolved_account_id)
        return snapshot_from_audit_payload(payload, source=f"meta-readonly:{resolved_account_id}")

    def fetch_audit_payload(self, account_id: str) -> dict[str, Any]:
        errors: list[dict[str, str]] = []
        campaigns_payload = self._fetch_campaigns_payload(account_id, errors)
        adsets_payload = self._fetch_adsets_payload(account_id, errors)
        ads_payload = self._fetch_ads_payload(account_id, errors)
        endpoints = {
            "ad_account": self.client.get(
                account_id,
                None,
                {"fields": "id,name,currency,timezone_name,account_status,amount_spent,balance,spend_cap,business"},
            ),
            "campaigns": campaigns_payload,
            "adsets": adsets_payload,
            "ads": ads_payload,
            "insights_campaign": self.client.get_paged(
                account_id,
                "insights",
                {
                    "fields": "date_start,date_stop,campaign_id,campaign_name,spend,impressions,reach,frequency,clicks,inline_link_clicks,ctr,cpc,cpm,actions,cost_per_action_type",
                    "level": "campaign",
                    "date_preset": self.date_preset,
                    "limit": "100",
                },
                max_pages=self.max_pages,
            ),
            "insights_adset": self.client.get_paged(
                account_id,
                "insights",
                {
                    "fields": "date_start,date_stop,campaign_id,campaign_name,adset_id,adset_name,spend,impressions,reach,frequency,clicks,inline_link_clicks,ctr,cpc,cpm,actions,cost_per_action_type",
                    "level": "adset",
                    "date_preset": self.date_preset,
                    "limit": "200",
                },
                max_pages=self.max_pages,
            ),
            "insights_ad": self.client.get_paged(
                account_id,
                "insights",
                {
                    "fields": "date_start,date_stop,campaign_id,campaign_name,adset_id,adset_name,ad_id,ad_name,spend,impressions,reach,frequency,clicks,inline_link_clicks,ctr,cpc,cpm,actions,cost_per_action_type",
                    "level": "ad",
                    "date_preset": self.date_preset,
                    "limit": "300",
                },
                max_pages=self.max_pages,
            ),
        }
        preview_ad_ids = _top_insight_ad_ids(
            endpoints.get("insights_ad", {}).get("data", []),
            limit=self.creative_preview_limit,
        )
        self._enrich_insight_ad_creatives(endpoints, errors, preview_ad_ids=preview_ad_ids)
        endpoints["insights_ad"]["data"] = _attach_ads_creative(
            endpoints["insights_ad"].get("data", []),
            endpoints["ads"].get("data", []),
            media_dir=self.media_dir,
            preview_ad_ids=preview_ad_ids,
        )
        dataset = {
            "meta": {
                "platform": "meta",
                "api_version": self.config.api_version,
                "account_id": account_id,
                "date_preset": self.date_preset,
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "read_only": True,
            },
            "endpoints": endpoints,
            "errors": errors,
        }
        dataset["summary"] = _summarize_dataset(dataset)
        return dataset

    def _fetch_campaigns_payload(self, account_id: str, errors: list[dict[str, str]]) -> dict[str, Any]:
        try:
            return self.client.get_paged(
                account_id,
                "campaigns",
                {
                    "fields": "id,name,objective,status,effective_status,buying_type,bid_strategy,daily_budget,lifetime_budget,created_time,updated_time",
                    "limit": "100",
                },
                max_pages=self.max_pages,
            )
        except urllib.error.HTTPError:
            errors.append(
                {
                    "endpoint": "campaigns",
                    "message": "Campaign extended fields unavailable; used basic object fields.",
                }
            )
            try:
                return self.client.get_paged(
                    account_id,
                    "campaigns",
                    {"fields": "id,name,status,effective_status,created_time,updated_time", "limit": "100"},
                    max_pages=self.max_pages,
                )
            except urllib.error.HTTPError:
                errors.append(
                    {
                        "endpoint": "campaigns",
                        "message": "Campaign object tree unavailable; using insights rows for campaign metrics.",
                    }
                )
                return _empty_endpoint_payload()

    def _fetch_adsets_payload(self, account_id: str, errors: list[dict[str, str]]) -> dict[str, Any]:
        try:
            return self.client.get_paged(
                account_id,
                "adsets",
                {
                    "fields": "id,name,campaign_id,optimization_goal,billing_event,bid_strategy,daily_budget,lifetime_budget,status,effective_status,created_time,updated_time",
                    "limit": "200",
                },
                max_pages=self.max_pages,
            )
        except urllib.error.HTTPError:
            errors.append(
                {
                    "endpoint": "adsets",
                    "message": "Ad Set extended fields unavailable; used basic object fields.",
                }
            )
            try:
                return self.client.get_paged(
                    account_id,
                    "adsets",
                    {"fields": "id,name,campaign_id,status,effective_status,created_time,updated_time", "limit": "200"},
                    max_pages=self.max_pages,
                )
            except urllib.error.HTTPError:
                errors.append(
                    {
                        "endpoint": "adsets",
                        "message": "Ad Set object tree unavailable; using insights rows for ad set metrics.",
                    }
                )
                return _empty_endpoint_payload()

    def _fetch_ads_payload(self, account_id: str, errors: list[dict[str, str]]) -> dict[str, Any]:
        rich_fields = "id,name,campaign_id,adset_id,creative{id,name,title,body,thumbnail_url,image_url,video_id,object_story_spec},status,effective_status,created_time,updated_time"
        basic_fields = "id,name,campaign_id,adset_id,creative,status,effective_status,created_time,updated_time"
        try:
            return self.client.get_paged(
                account_id,
                "ads",
                {"fields": rich_fields, "limit": "300"},
                max_pages=self.max_pages,
            )
        except urllib.error.HTTPError:
            errors.append(
                {
                    "endpoint": "ads",
                    "message": "Ad creative detail fields unavailable; used basic creative reference.",
                }
            )
            try:
                return self.client.get_paged(
                    account_id,
                    "ads",
                    {"fields": basic_fields, "limit": "300"},
                    max_pages=self.max_pages,
                )
            except urllib.error.HTTPError:
                errors.append(
                    {
                        "endpoint": "ads",
                        "message": "Ad object tree unavailable; using insights rows for ad metrics without creative preview.",
                    }
                )
                return _empty_endpoint_payload()

    def _enrich_insight_ad_creatives(
        self,
        endpoints: dict[str, Any],
        errors: list[dict[str, str]],
        *,
        preview_ad_ids: set[str],
    ) -> None:
        if not preview_ad_ids:
            return
        ad_rows = [row for row in endpoints.get("ads", {}).get("data", []) if isinstance(row, dict)]
        missing_detail_rows = [
            row
            for row in ad_rows
            if str(row.get("id")) in preview_ad_ids and not _creative_has_preview_candidate(row.get("creative"))
        ]
        for row in missing_detail_rows:
            creative = row.get("creative")
            creative_id = creative.get("id") if isinstance(creative, dict) else None
            if not creative_id:
                continue
            try:
                row["creative"] = self.client.get(
                    str(creative_id),
                    None,
                    {"fields": "id,name,title,body,thumbnail_url,image_url,video_id,object_story_spec"},
                )
            except urllib.error.HTTPError:
                errors.append(
                    {
                        "endpoint": "creative",
                        "message": "Creative preview fields unavailable for one ad; preview left empty.",
                    }
                )


def _attach_ads_creative(
    insight_rows: Any,
    ads_rows: Any,
    *,
    media_dir: Path | None = None,
    preview_ad_ids: set[str] | None = None,
) -> list[dict[str, Any]]:
    insight_ad_ids = {
        str(row.get("ad_id"))
        for row in insight_rows or []
        if isinstance(row, dict) and row.get("ad_id")
    }
    creative_by_ad_id = {
        str(row.get("id")): _safe_creative(
            row.get("creative"),
            ad_id=str(row.get("id")),
            media_dir=media_dir if str(row.get("id")) in (preview_ad_ids or insight_ad_ids) else None,
        )
        for row in ads_rows
        if isinstance(row, dict) and row.get("id")
    }
    result: list[dict[str, Any]] = []
    for row in insight_rows or []:
        if not isinstance(row, dict):
            continue
        copied = dict(row)
        copied["creative"] = creative_by_ad_id.get(str(row.get("ad_id")), {})
        result.append(copied)
    return result


def _empty_endpoint_payload() -> dict[str, Any]:
    return {
        "data": [],
        "paging_summary": {
            "pages_fetched": 0,
            "rows_returned": 0,
            "has_next_page": False,
        },
    }


def _safe_account(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": row.get("id"),
        "name": row.get("name"),
        "currency": row.get("currency"),
        "timezone_name": row.get("timezone_name"),
        "account_status": row.get("account_status"),
        "business": row.get("business"),
    }


def _safe_creative(value: Any, *, ad_id: str | None = None, media_dir: Path | None = None) -> dict[str, object]:
    if not isinstance(value, dict):
        return {}
    allowed = {"id", "name", "title", "body", "video_id", "object_story_spec"}
    result = {key: _redact_secret_shape(value[key]) for key in allowed if key in value}
    preview_path = _cache_creative_preview(value, ad_id=ad_id, media_dir=media_dir)
    if preview_path:
        result["preview_url"] = preview_path
        result["preview_status"] = "cached"
    elif media_dir is not None:
        result["preview_status"] = "unavailable"
    return result


def _creative_has_preview_candidate(value: Any) -> bool:
    return isinstance(value, dict) and any(isinstance(value.get(key), str) for key in ("thumbnail_url", "image_url"))


def _top_insight_ad_ids(rows: Any, *, limit: int) -> set[str]:
    if limit <= 0:
        return set()
    valid_rows = [row for row in rows or [] if isinstance(row, dict) and row.get("ad_id")]
    valid_rows.sort(key=lambda row: _float(row.get("spend")), reverse=True)
    return {str(row.get("ad_id")) for row in valid_rows[:limit]}


def _float(value: Any) -> float:
    if value in (None, ""):
        return 0.0
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _cache_creative_preview(value: dict[str, Any], *, ad_id: str | None, media_dir: Path | None) -> str | None:
    if media_dir is None or not ad_id:
        return None
    source_url = _first_image_url(value)
    if not source_url:
        return None
    parsed = urllib.parse.urlparse(source_url)
    if parsed.scheme != "https":
        return None
    media_dir.mkdir(parents=True, exist_ok=True)
    safe_ad_id = re.sub(r"[^A-Za-z0-9_.-]+", "_", ad_id)[:80] or "ad"
    suffix = _image_suffix(parsed.path)
    output_path = media_dir / f"{safe_ad_id}{suffix}"
    if output_path.exists() and output_path.stat().st_size > 0:
        return f"media/{output_path.name}"
    request = urllib.request.Request(source_url, headers={"User-Agent": "meta-readonly-local-preview/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=8) as response:
            content_type = response.headers.get("Content-Type", "")
            data = response.read()
    except (OSError, urllib.error.URLError):
        return None
    if not content_type.startswith("image/") or not data:
        return None
    output_path.write_bytes(data)
    return f"media/{output_path.name}"


def _first_image_url(value: dict[str, Any]) -> str | None:
    for key in ("thumbnail_url", "image_url"):
        item = value.get(key)
        if isinstance(item, str) and item.startswith("https://"):
            return item
    return None


def _image_suffix(path: str) -> str:
    suffix = Path(path).suffix.lower()
    if suffix in {".jpg", ".jpeg", ".png", ".webp", ".gif"}:
        return suffix
    return ".jpg"


def _redact_secret_shape(value: Any) -> object:
    if isinstance(value, str):
        return re.sub(r"access_token=[^&\s]+", "access_token=REDACTED", value)
    if isinstance(value, dict):
        return {
            str(key): _redact_secret_shape(item)
            for key, item in value.items()
            if str(key) not in {"thumbnail_url", "image_url"}
        }
    if isinstance(value, list):
        return [_redact_secret_shape(item) for item in value]
    return value


def _rows(payload: dict[str, Any], endpoint: str) -> list[dict[str, Any]]:
    data = payload.get("endpoints", {}).get(endpoint, {}).get("data", [])
    return [row for row in data if isinstance(row, dict)]


def _summarize_dataset(dataset: dict[str, Any]) -> dict[str, Any]:
    account = dataset["endpoints"].get("ad_account", {})
    return {
        "account": {
            "id": account.get("id"),
            "name": account.get("name"),
            "currency": account.get("currency"),
            "timezone": account.get("timezone_name"),
            "account_status": account.get("account_status"),
        },
        "object_counts": {
            "campaigns": len(_rows(dataset, "campaigns")),
            "adsets": len(_rows(dataset, "adsets")),
            "ads": len(_rows(dataset, "ads")),
        },
        "insight_rows": {
            "campaign": len(_rows(dataset, "insights_campaign")),
            "adset": len(_rows(dataset, "insights_adset")),
            "ad": len(_rows(dataset, "insights_ad")),
        },
    }
