"""Safety blocker for every real Meta write action."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone


WRITE_ACTIONS = {
    "publish",
    "pause",
    "enable",
    "update_budget",
    "update_bid",
    "replace_creative",
    "duplicate_and_launch",
    "delete",
}


@dataclass(frozen=True)
class BlockedWriteAction:
    action: str
    object_type: str
    object_id: str
    reason: str
    created_at: str


class MetaWriteBlocker:
    """Convert every dangerous action into a local blocked event."""

    def block(self, action: str, *, object_type: str, object_id: str) -> BlockedWriteAction:
        if action not in WRITE_ACTIONS:
            reason = "未知写动作也按危险动作处理，禁止调用 Meta 写接口。"
        else:
            reason = "Meta/Facebook API 在本项目中只允许 read-only；该真实写操作已被阻断。"
        return BlockedWriteAction(
            action=action,
            object_type=object_type,
            object_id=object_id,
            reason=reason,
            created_at=datetime.now(timezone.utc).isoformat(),
        )

