"""Build the first closed-loop report from read-only data and local drafts."""

from __future__ import annotations

from dataclasses import dataclass

from meta_ads_closed_loop.adapters.meta_readonly import AccountSnapshot

from .diagnostics import Diagnosis
from .drafts import OptimizationDraft
from .safety import BlockedWriteAction


@dataclass(frozen=True)
class ClosedLoopReport:
    account_name: str
    source: str
    updated_at: str
    total_spend: float
    total_leads: int
    total_purchases: int
    total_landing_page_views: int
    diagnosis_count: int
    draft_count: int
    blocked_action_count: int
    summary: str


def build_closed_loop_report(
    snapshot: AccountSnapshot,
    diagnoses: tuple[Diagnosis, ...],
    drafts: tuple[OptimizationDraft, ...],
    blocked_actions: tuple[BlockedWriteAction, ...],
) -> ClosedLoopReport:
    return ClosedLoopReport(
        account_name=snapshot.account_name,
        source=snapshot.source,
        updated_at=snapshot.updated_at,
        total_spend=snapshot.total_spend,
        total_leads=snapshot.total_leads,
        total_purchases=snapshot.total_purchases,
        total_landing_page_views=snapshot.total_landing_page_views,
        diagnosis_count=len(diagnoses),
        draft_count=len(drafts),
        blocked_action_count=len(blocked_actions),
        summary=(
            f"已读取 {snapshot.account_name} 的只读数据，发现 {len(diagnoses)} 条诊断，"
            f"生成 {len(drafts)} 份本地草稿，阻断 {len(blocked_actions)} 次危险写动作。"
        ),
    )

