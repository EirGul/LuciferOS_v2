from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from lucifer_os.memory.models import MemoryItem, MemoryScope, MemoryType
from lucifer_os.memory.policy import MemoryDeleteRequest, MemoryPolicy, MemoryWriteRequest
from lucifer_os.memory.store import MemoryStore


@dataclass(frozen=True, slots=True)
class MemoryOperationResult:
    allowed: bool
    requires_confirmation: bool
    audit_reason: str
    item: MemoryItem | None = None
    deleted: bool = False


class MemoryService:
    def __init__(self, store: MemoryStore, policy: MemoryPolicy | None = None) -> None:
        self.store = store
        self.policy = policy or MemoryPolicy()

    def add_memory(
        self,
        content: str,
        type: MemoryType,
        scope: MemoryScope,
        source: str = "user",
        confidence: float = 1.0,
        tags: tuple[str, ...] | None = None,
        metadata: dict[str, Any] | None = None,
        confirmed: bool = False,
    ) -> MemoryOperationResult:
        decision = self.policy.evaluate_write(
            MemoryWriteRequest(
                content=content,
                type=type,
                scope=scope,
                source=source,
            )
        )

        if not decision.allowed:
            return MemoryOperationResult(
                allowed=False,
                requires_confirmation=decision.requires_confirmation,
                audit_reason=decision.audit_reason,
            )

        if decision.requires_confirmation and not confirmed:
            return MemoryOperationResult(
                allowed=True,
                requires_confirmation=True,
                audit_reason=decision.audit_reason,
            )

        item = MemoryItem(
            content=content,
            type=type,
            scope=scope,
            source=source,
            confidence=confidence,
            tags=tags or (),
            metadata=metadata or {},
        )
        stored_item = self.store.add(item)

        return MemoryOperationResult(
            allowed=True,
            requires_confirmation=False,
            audit_reason=decision.audit_reason,
            item=stored_item,
        )

    def get_memory(self, memory_id: str) -> MemoryItem | None:
        return self.store.get(memory_id)

    def list_memories(
        self,
        scope: MemoryScope | None = None,
        type: MemoryType | None = None,
    ) -> list[MemoryItem]:
        return self.store.list(scope=scope, type=type)

    def delete_memory(self, memory_id: str, confirmed: bool = False) -> MemoryOperationResult:
        decision = self.policy.evaluate_delete(
            request=__import__("lucifer_os.memory.policy", fromlist=["MemoryDeleteRequest"]).MemoryDeleteRequest(
                memory_id=memory_id,
            )
        )

        if not decision.allowed:
            return MemoryOperationResult(
                allowed=False,
                requires_confirmation=decision.requires_confirmation,
                audit_reason=decision.audit_reason,
            )

        if decision.requires_confirmation and not confirmed:
            return MemoryOperationResult(
                allowed=True,
                requires_confirmation=True,
                audit_reason=decision.audit_reason,
                deleted=False,
            )

        deleted = self.store.delete(memory_id)

        return MemoryOperationResult(
            allowed=True,
            requires_confirmation=False,
            audit_reason=decision.audit_reason,
            deleted=deleted,
        )
