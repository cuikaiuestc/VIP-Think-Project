"""Typed product data returned by read-only Meta adapters."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class CampaignItem:
    id: str
    name: str
    status: str
    spend: float
    impressions: int
    clicks: int
    leads: int
    purchases: int
    currency: str
    landing_page_views: int = 0

    @property
    def cpl(self) -> float | None:
        if self.leads <= 0:
            return None
        return round(self.spend / self.leads, 2)

    @property
    def cpa(self) -> float | None:
        if self.purchases <= 0:
            return None
        return round(self.spend / self.purchases, 2)

    @property
    def ctr(self) -> float:
        if self.impressions <= 0:
            return 0.0
        return round(self.clicks / self.impressions * 100, 2)


@dataclass(frozen=True)
class AdSetItem:
    id: str
    name: str
    campaign_id: str
    status: str
    spend: float
    impressions: int
    clicks: int
    landing_page_views: int
    leads: int
    purchases: int
    currency: str
    campaign_name: str = ""

    @property
    def cpl(self) -> float | None:
        if self.leads <= 0:
            return None
        return round(self.spend / self.leads, 2)

    @property
    def cpa(self) -> float | None:
        if self.purchases <= 0:
            return None
        return round(self.spend / self.purchases, 2)

    @property
    def ctr(self) -> float:
        if self.impressions <= 0:
            return 0.0
        return round(self.clicks / self.impressions * 100, 2)


@dataclass(frozen=True)
class AdItem:
    id: str
    name: str
    campaign_id: str
    adset_id: str
    status: str
    spend: float
    impressions: int
    clicks: int
    landing_page_views: int
    leads: int
    purchases: int
    currency: str
    campaign_name: str = ""
    adset_name: str = ""
    creative: dict[str, object] = field(default_factory=dict)

    @property
    def cpl(self) -> float | None:
        if self.leads <= 0:
            return None
        return round(self.spend / self.leads, 2)

    @property
    def cpa(self) -> float | None:
        if self.purchases <= 0:
            return None
        return round(self.spend / self.purchases, 2)

    @property
    def ctr(self) -> float:
        if self.impressions <= 0:
            return 0.0
        return round(self.clicks / self.impressions * 100, 2)


@dataclass(frozen=True)
class AccountSnapshot:
    account_id: str
    account_name: str
    currency: str
    timezone: str
    updated_at: str
    source: str
    campaigns: tuple[CampaignItem, ...] = field(default_factory=tuple)
    adsets: tuple[AdSetItem, ...] = field(default_factory=tuple)
    ads: tuple[AdItem, ...] = field(default_factory=tuple)
    object_counts: dict[str, Any] = field(default_factory=dict)
    insight_rows: dict[str, Any] = field(default_factory=dict)

    @property
    def total_spend(self) -> float:
        return round(sum(item.spend for item in self.campaigns), 2)

    @property
    def total_leads(self) -> int:
        return sum(item.leads for item in self.campaigns)

    @property
    def total_purchases(self) -> int:
        return sum(item.purchases for item in self.campaigns)

    @property
    def total_landing_page_views(self) -> int:
        return sum(item.landing_page_views for item in self.ads)
