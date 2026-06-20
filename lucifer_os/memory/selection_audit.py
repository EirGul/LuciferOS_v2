from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4

from lucifer_os.memory.commands import MemoryCommandType


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class MemoryCandidateSelectionAuditAction(str, Enum):
    REQUEST_CREATED = "selection_request_created"
    REQUEST_REJECTED = "selection_request_rejected"
    REQUEST_CANCELLED = "selection_request_cancelled"
    REQUEST_EXPIRED = "selection_request_expired"
    CANDIDATE_REJECTED = "selection_candidate_rejected"
    CANDIDATE_ACCEPTED = "selection_candidate_accepted"
    PENDING_ACTION_PREPARED = "selection_pending_action_prepared"


_ACTIONS_REQUIRING_REQUEST_CONTEXT = {
    MemoryCandidateSelectionAuditAction.REQUEST_CREATED,
    MemoryCandidateSelectionAuditAction.REQUEST_CANCELLED,
    MemoryCandidateSelectionAuditAction.REQUEST_EXPIRED,
    MemoryCandidateSelectionAuditAction.CANDIDATE_REJECTED,
    MemoryCandidateSelectionAuditAction.CANDIDATE_ACCEPTED,
    MemoryCandidateSelectionAuditAction.PENDING_ACTION_PREPARED,
}


@dataclass(frozen=True, slots=True)
class MemoryCandidateSelectionAuditEvent:
    action: MemoryCandidateSelectionAuditAction
    source: str
    selection_request_id: str | None = None
    command_type: MemoryCommandType | None = None
    selected_memory_id: str | None = None
    pending_action_id: str | None = None
    reason: str = ""
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: str = field(default_factory=utc_now_iso)

    def __post_init__(self) -> None:
        if not self.source.strip():
            raise ValueError("Memory candidate selection audit event source cannot be empty.")
        if not self.id.strip():
            raise ValueError("Memory candidate selection audit event id cannot be empty.")
        if not self.created_at.strip():
            raise ValueError("Memory candidate selection audit event created_at cannot be empty.")

        if self.selection_request_id is not None and not self.selection_request_id.strip():
            raise ValueError(
                "Memory candidate selection audit event selection_request_id cannot be blank."
            )
        if self.selected_memory_id is not None and not self.selected_memory_id.strip():
            raise ValueError(
                "Memory candidate selection audit event selected_memory_id cannot be blank."
            )
        if self.pending_action_id is not None and not self.pending_action_id.strip():
            raise ValueError(
                "Memory candidate selection audit event pending_action_id cannot be blank."
            )

        if self.action in _ACTIONS_REQUIRING_REQUEST_CONTEXT:
            if self.selection_request_id is None:
                raise ValueError(
                    "Memory candidate selection audit event action requires selection_request_id."
                )
            if self.command_type is None:
                raise ValueError(
                    "Memory candidate selection audit event action requires command_type."
                )

        if self.action == MemoryCandidateSelectionAuditAction.CANDIDATE_ACCEPTED:
            if self.selected_memory_id is None:
                raise ValueError(
                    "Accepted memory candidate audit event requires selected_memory_id."
                )

        if self.action == MemoryCandidateSelectionAuditAction.PENDING_ACTION_PREPARED:
            if self.selected_memory_id is None:
                raise ValueError(
                    "Prepared pending action audit event requires selected_memory_id."
                )
            if self.pending_action_id is None:
                raise ValueError(
                    "Prepared pending action audit event requires pending_action_id."
                )

    @property
    def is_memory_mutation_event(self) -> bool:
        return False


class MemoryCandidateSelectionAuditSink(ABC):
    @abstractmethod
    def record(self, event: MemoryCandidateSelectionAuditEvent) -> None:
        raise NotImplementedError


class InMemoryMemoryCandidateSelectionAuditSink(MemoryCandidateSelectionAuditSink):
    def __init__(self) -> None:
        self._events: list[MemoryCandidateSelectionAuditEvent] = []

    def record(self, event: MemoryCandidateSelectionAuditEvent) -> None:
        self._events.append(event)

    def list_events(self) -> tuple[MemoryCandidateSelectionAuditEvent, ...]:
        return tuple(self._events)

    def clear(self) -> tuple[MemoryCandidateSelectionAuditEvent, ...]:
        events = tuple(self._events)
        self._events.clear()
        return events
