from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from lucifer_os.memory.audit import InMemoryMemoryAuditSink, MemoryAuditAction, MemoryAuditEvent, MemoryAuditSink
from lucifer_os.memory.models import MemoryItem, MemoryScope, MemoryType, utc_now_iso
from lucifer_os.memory.policy import MemoryDeleteRequest, MemoryPolicy, MemoryUpdateRequest, MemoryWriteRequest
from lucifer_os.memory.store import MemoryStore


@dataclass(frozen=True, slots=True)
class MemoryOperationResult:
    allowed: bool
    requires_confirmation: bool
    audit_reason: str
    item: MemoryItem | None = None
    deleted: bool = False


class MemoryService:
    def __init__(
        self,
        store: MemoryStore,
        policy: MemoryPolicy | None = None,
        audit_sink: MemoryAuditSink | None = None,
    ) -> None:
        self.store = store
        self.policy = policy or MemoryPolicy()
        self.audit_sink = audit_sink or InMemoryMemoryAuditSink()

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
        self.audit_sink.record(
            MemoryAuditEvent(
                action=MemoryAuditAction.WRITE_REQUESTED,
                reason="Memory write requested.",
                source=source,
                metadata={
                    "type": type.value,
                    "scope": scope.value,
                    "confirmed": confirmed,
                },
            )
        )

        decision = self.policy.evaluate_write(
            MemoryWriteRequest(
                content=content,
                type=type,
                scope=scope,
                source=source,
            )
        )

        if not decision.allowed:
            self.audit_sink.record(
                MemoryAuditEvent(
                    action=MemoryAuditAction.WRITE_REJECTED,
                    reason=decision.audit_reason,
                    source=source,
                    metadata={
                        "type": type.value,
                        "scope": scope.value,
                    },
                )
            )
            return MemoryOperationResult(
                allowed=False,
                requires_confirmation=decision.requires_confirmation,
                audit_reason=decision.audit_reason,
            )

        if decision.requires_confirmation and not confirmed:
            self.audit_sink.record(
                MemoryAuditEvent(
                    action=MemoryAuditAction.WRITE_REQUIRES_CONFIRMATION,
                    reason=decision.audit_reason,
                    source=source,
                    metadata={
                        "type": type.value,
                        "scope": scope.value,
                    },
                )
            )
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

        self.audit_sink.record(
            MemoryAuditEvent(
                action=MemoryAuditAction.WRITE_STORED,
                reason=decision.audit_reason,
                memory_id=stored_item.id,
                source=source,
                metadata={
                    "type": type.value,
                    "scope": scope.value,
                },
            )
        )

        return MemoryOperationResult(
            allowed=True,
            requires_confirmation=False,
            audit_reason=decision.audit_reason,
            item=stored_item,
        )

    def update_memory(
        self,
        memory_id: str,
        content: str,
        type: MemoryType,
        scope: MemoryScope,
        source: str = "user",
        confidence: float = 1.0,
        tags: tuple[str, ...] | None = None,
        metadata: dict[str, Any] | None = None,
        confirmed: bool = False,
    ) -> MemoryOperationResult:
        clean_memory_id = memory_id.strip()

        self.audit_sink.record(
            MemoryAuditEvent(
                action=MemoryAuditAction.UPDATE_REQUESTED,
                reason="Memory update requested.",
                memory_id=clean_memory_id or None,
                source=source,
                metadata={
                    "type": type.value,
                    "scope": scope.value,
                    "confirmed": confirmed,
                },
            )
        )

        decision = self.policy.evaluate_update(
            MemoryUpdateRequest(
                memory_id=memory_id,
                content=content,
                type=type,
                scope=scope,
                source=source,
            )
        )

        if not decision.allowed:
            self.audit_sink.record(
                MemoryAuditEvent(
                    action=MemoryAuditAction.UPDATE_REJECTED,
                    reason=decision.audit_reason,
                    memory_id=clean_memory_id or None,
                    source=source,
                    metadata={
                        "type": type.value,
                        "scope": scope.value,
                    },
                )
            )
            return MemoryOperationResult(
                allowed=False,
                requires_confirmation=decision.requires_confirmation,
                audit_reason=decision.audit_reason,
            )

        if decision.requires_confirmation and not confirmed:
            self.audit_sink.record(
                MemoryAuditEvent(
                    action=MemoryAuditAction.UPDATE_REQUIRES_CONFIRMATION,
                    reason=decision.audit_reason,
                    memory_id=clean_memory_id,
                    source=source,
                    metadata={
                        "type": type.value,
                        "scope": scope.value,
                    },
                )
            )
            return MemoryOperationResult(
                allowed=True,
                requires_confirmation=True,
                audit_reason=decision.audit_reason,
            )

        existing = self.store.get(clean_memory_id)
        if existing is None:
            reason = "Memory update rejected: memory id not found."
            self.audit_sink.record(
                MemoryAuditEvent(
                    action=MemoryAuditAction.UPDATE_REJECTED,
                    reason=reason,
                    memory_id=clean_memory_id or None,
                    source=source,
                    metadata={
                        "type": type.value,
                        "scope": scope.value,
                    },
                )
            )
            return MemoryOperationResult(
                allowed=False,
                requires_confirmation=False,
                audit_reason=reason,
            )

        updated_item = MemoryItem(
            id=existing.id,
            content=content,
            type=type,
            scope=scope,
            source=source,
            confidence=confidence,
            tags=tags or (),
            metadata=metadata or {},
            created_at=existing.created_at,
            updated_at=utc_now_iso(),
        )

        updated = self.store.update(updated_item)

        self.audit_sink.record(
            MemoryAuditEvent(
                action=MemoryAuditAction.UPDATE_COMPLETED,
                reason=decision.audit_reason,
                memory_id=updated_item.id,
                source=source,
                metadata={
                    "type": type.value,
                    "scope": scope.value,
                    "updated": updated,
                },
            )
        )

        return MemoryOperationResult(
            allowed=True,
            requires_confirmation=False,
            audit_reason=decision.audit_reason,
            item=updated_item if updated else None,
        )

    def get_memory(self, memory_id: str) -> MemoryItem | None:
        return self.store.get(memory_id)

    def list_memories(
        self,
        scope: MemoryScope | None = None,
        type: MemoryType | None = None,
    ) -> list[MemoryItem]:
        return self.store.list(scope=scope, type=type)

    def delete_memory(self, memory_id: str, confirmed: bool = False, source: str = "user") -> MemoryOperationResult:
        self.audit_sink.record(
            MemoryAuditEvent(
                action=MemoryAuditAction.DELETE_REQUESTED,
                reason="Memory delete requested.",
                memory_id=memory_id.strip() or None,
                source=source,
                metadata={
                    "confirmed": confirmed,
                },
            )
        )

        decision = self.policy.evaluate_delete(
            MemoryDeleteRequest(memory_id=memory_id, source=source)
        )

        if not decision.allowed:
            self.audit_sink.record(
                MemoryAuditEvent(
                    action=MemoryAuditAction.DELETE_REJECTED,
                    reason=decision.audit_reason,
                    memory_id=memory_id.strip() or None,
                    source=source,
                )
            )
            return MemoryOperationResult(
                allowed=False,
                requires_confirmation=decision.requires_confirmation,
                audit_reason=decision.audit_reason,
            )

        if decision.requires_confirmation and not confirmed:
            self.audit_sink.record(
                MemoryAuditEvent(
                    action=MemoryAuditAction.DELETE_REQUIRES_CONFIRMATION,
                    reason=decision.audit_reason,
                    memory_id=memory_id,
                    source=source,
                )
            )
            return MemoryOperationResult(
                allowed=True,
                requires_confirmation=True,
                audit_reason=decision.audit_reason,
                deleted=False,
            )

        deleted = self.store.delete(memory_id)

        self.audit_sink.record(
            MemoryAuditEvent(
                action=MemoryAuditAction.DELETE_COMPLETED,
                reason=decision.audit_reason,
                memory_id=memory_id,
                source=source,
                metadata={
                    "deleted": deleted,
                },
            )
        )

        return MemoryOperationResult(
            allowed=True,
            requires_confirmation=False,
            audit_reason=decision.audit_reason,
            deleted=deleted,
        )
