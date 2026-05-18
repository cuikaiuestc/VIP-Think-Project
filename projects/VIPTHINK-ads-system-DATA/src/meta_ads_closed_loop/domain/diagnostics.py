"""Simple diagnosis rules for the first closed loop."""

from __future__ import annotations

from dataclasses import dataclass

from meta_ads_closed_loop.adapters.meta_readonly import AccountSnapshot, CampaignItem


@dataclass(frozen=True)
class Diagnosis:
    id: str
    priority: str
    object_type: str
    object_id: str
    object_name: str
    title: str
    evidence: tuple[str, ...]
    suggested_action: str
    confidence: str


def diagnose_snapshot(snapshot: AccountSnapshot) -> tuple[Diagnosis, ...]:
    diagnoses: list[Diagnosis] = []
    for campaign in snapshot.campaigns:
        diagnoses.extend(_diagnose_campaign(campaign))
    return tuple(sorted(diagnoses, key=_priority_rank))


def _diagnose_campaign(campaign: CampaignItem) -> list[Diagnosis]:
    diagnoses: list[Diagnosis] = []
    if campaign.spend > 0 and campaign.leads == 0:
        diagnoses.append(
            Diagnosis(
                id=f"diag-campaign-no-leads-{campaign.id}",
                priority="高",
                object_type="Campaign",
                object_id=campaign.id,
                object_name=campaign.name,
                title="Campaign 有消耗但没有线索",
                evidence=(
                    f"消耗 {campaign.currency} {campaign.spend:,.2f}",
                    "线索 0",
                    f"点击 {campaign.clicks}",
                ),
                suggested_action="生成暂停或复查草稿，先人工核对归因与落地页。",
                confidence="高",
            )
        )
    if campaign.cpl is not None and campaign.cpl >= 30:
        diagnoses.append(
            Diagnosis(
                id=f"diag-campaign-high-cpl-{campaign.id}",
                priority="中",
                object_type="Campaign",
                object_id=campaign.id,
                object_name=campaign.name,
                title="Campaign 线索成本偏高",
                evidence=(
                    f"CPL {campaign.currency} {campaign.cpl:,.2f}",
                    f"线索 {campaign.leads}",
                    f"消耗 {campaign.currency} {campaign.spend:,.2f}",
                ),
                suggested_action="生成预算复查草稿，并标注需要结合内部有效线索判断。",
                confidence="中",
            )
        )
    if campaign.spend > 100 and campaign.ctr < 1:
        diagnoses.append(
            Diagnosis(
                id=f"diag-campaign-low-ctr-{campaign.id}",
                priority="中",
                object_type="Campaign",
                object_id=campaign.id,
                object_name=campaign.name,
                title="Campaign 点击率偏低",
                evidence=(
                    f"CTR {campaign.ctr:.2f}%",
                    f"展示 {campaign.impressions}",
                    f"点击 {campaign.clicks}",
                ),
                suggested_action="生成creative_asset复查草稿，优先检查创意疲劳和受众匹配。",
                confidence="中",
            )
        )
    return diagnoses


def _priority_rank(diagnosis: Diagnosis) -> int:
    return {"高": 0, "中": 1, "低": 2}.get(diagnosis.priority, 9)

