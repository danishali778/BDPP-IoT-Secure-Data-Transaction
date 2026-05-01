from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Ledger:
    user_versions: dict[str, int] = field(default_factory=dict)
    cid_registry: dict[str, str] = field(default_factory=dict)
    reliability_logs: list[dict[str, Any]] = field(default_factory=list)
    transaction_logs: list[dict[str, Any]] = field(default_factory=list)

    def register_user(self, user_id: str) -> None:
        self.user_versions.setdefault(user_id, 1)

    def get_version(self, user_id: str) -> int:
        return self.user_versions.get(user_id, 1)

    def revoke_user(self, user_id: str) -> int:
        self.register_user(user_id)
        self.user_versions[user_id] += 1
        return self.user_versions[user_id]

    def store_cid(self, record_id: str, cid: str) -> None:
        self.cid_registry[record_id] = cid

    def log_reliability(self, event: dict[str, Any]) -> None:
        self.reliability_logs.append(event)

    def log_transaction(self, event: dict[str, Any]) -> None:
        self.transaction_logs.append(event)

