from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4


class MemoryAuditAction(str, Enum):
    WRITE_REQUESTED = "write_requested"
    WRITE_REJECTED = "write_rejected"
    WRITE_REQUIRES_CONFIRMATION = "write_requires_confirmation"
    WRITE_STORED = "write_stored"
    UPDATE_REQUESTED = "update_requested"
    UPDATE_REJECTED = "update_rejected"
    UPDATE_REQUIRES_CONFIRMATION = "update_requires_confirmation"
    UPDATE_COMPLETED = "update_completed"
    DELETE_REQUESTED = "delete_requested"
    DELETE_REJECTED = "delete_rejected"
    DELETE_REQUIRES_CONFIRMATION = "delete_requires_confirmation"
    DELETE_COMPLETED = "delete_completed"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True, slots=True)
class MemoryAuditEvent:
    action: MemoryAuditAction
    reason: str
    memory_id: str | None = None
    source: str = "memory-service"
    metadata: dict[str, Any] = field(default_factory=dict)
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: str = field(default_factory=utc_now_iso)

    def __post_init__(self) -> None:
        if not self.reason.strip():
            raise ValueError("Memory audit event reason cannot be empty.")


class MemoryAuditSink(ABC):
    @abstractmethod
    def record(self, event: MemoryAuditEvent) -> MemoryAuditEvent:
        raise NotImplementedError

    @abstractmethod
    def list_events(self) -> list[MemoryAuditEvent]:
        raise NotImplementedError


class InMemoryMemoryAuditSink(MemoryAuditSink):
    def __init__(self) -> None:
        self._events: list[MemoryAuditEvent] = []

    def record(self, event: MemoryAuditEvent) -> MemoryAuditEvent:
        self._events.append(event)
        return event

    def list_events(self) -> list[MemoryAuditEvent]:
        return list(self._events)
