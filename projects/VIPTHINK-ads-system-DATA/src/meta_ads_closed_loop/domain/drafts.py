"""Local optimization drafts. These are never Meta write operations."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from .diagnostics import Diagnosis


@dataclass(frozen=True)
class OptimizationDraft:
    id: str
    diagnosis_id: str
    object_type: str
    object_id: str
    object_name: str
    title: str
    body: str
    status: str
    created_at: str


def create_local_draft(diagnosis: Diagnosis, *, created_at: str | None = None) -> OptimizationDraft:
    timestamp = created_at or datetime.now(timezone.utc).isoformat()
    return OptimizationDraft(
        id=f"draft-{diagnosis.id}",
        diagnosis_id=diagnosis.id,
        object_type=diagnosis.object_type,
        object_id=diagnosis.object_id,
        object_name=diagnosis.object_name,
        title=f"{diagnosis.object_name}：{diagnosis.title}",
        body=(
            f"建议动作：{diagnosis.suggested_action}\n"
            f"证据：{'；'.join(diagnosis.evidence)}\n"
            "安全边界：本草稿只保存在本地，不会调用 Meta 写接口。"
        ),
        status="本地草稿",
        created_at=timestamp,
    )

