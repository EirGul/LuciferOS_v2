from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from uuid import uuid4

from lucifer_os.memory.commands import MemoryCommandType
from lucifer_os.memory.pending import PendingMemoryAction, PendingMemoryActionType
from lucifer_os.memory.resolver import MemoryTargetCandidate
from lucifer_os.memory.selection_audit import (
    InMemoryMemoryCandidateSelectionAuditSink,
    MemoryCandidateSelectionAuditAction,
    MemoryCandidateSelectionAuditDeliveryService,
    MemoryCandidateSelectionAuditEvent,
)


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def parse_utc_iso(value: str) -> datetime:
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed


class MemoryCandidateSelectionOutcome(str, Enum):
    SELECTED = "selected"
    REJECTED = "rejected"


class MemoryCandidateSelectionPreparationOutcome(str, Enum):
    PREPARED = "prepared"
    REJECTED = "rejected"


@dataclass(frozen=True, slots=True)
class MemoryCandidateSelectionRequest:
    command_type: MemoryCommandType
    source_text: str
    candidates: tuple[MemoryTargetCandidate, ...]
    proposed_content: str | None = None
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: str = field(default_factory=utc_now_iso)

    def __post_init__(self) -> None:
        if self.command_type not in {MemoryCommandType.CORRECT, MemoryCommandType.DELETE}:
            raise ValueError("Memory candidate selection supports only correction and delete commands.")
        if not self.source_text.strip():
            raise ValueError("Memory candidate selection source text cannot be empty.")
        if not self.candidates:
            raise ValueError("Memory candidate selection requires at least one candidate.")

        candidate_ids = [candidate.memory.id for candidate in self.candidates]
        if any(not memory_id.strip() for memory_id in candidate_ids):
            raise ValueError("Memory candidate selection candidates require non-empty memory ids.")
        if len(candidate_ids) != len(set(candidate_ids)):
            raise ValueError("Memory candidate selection candidates must have unique memory ids.")

        if self.command_type == MemoryCommandType.CORRECT:
            if self.proposed_content is None or not self.proposed_content.strip():
                raise ValueError("Correction candidate selection requires proposed content.")

        if self.command_type == MemoryCommandType.DELETE:
            if self.proposed_content is not None:
                raise ValueError("Delete candidate selection must not include proposed content.")


@dataclass(frozen=True, slots=True)
class MemoryCandidateSelectionResult:
    outcome: MemoryCandidateSelectionOutcome
    explanation: str
    request_id: str
    selected_memory_id: str | None = None

    def __post_init__(self) -> None:
        if not self.explanation.strip():
            raise ValueError("Memory candidate selection result explanation cannot be empty.")
        if not self.request_id.strip():
            raise ValueError("Memory candidate selection result request_id cannot be empty.")
        if self.outcome == MemoryCandidateSelectionOutcome.SELECTED and not self.selected_memory_id:
            raise ValueError("Selected memory candidate result requires selected_memory_id.")


@dataclass(frozen=True, slots=True)
class MemoryCandidateSelectionPreparationResult:
    outcome: MemoryCandidateSelectionPreparationOutcome
    explanation: str
    pending_action: PendingMemoryAction | None = None

    def __post_init__(self) -> None:
        if not self.explanation.strip():
            raise ValueError("Memory candidate selection preparation explanation cannot be empty.")
        if (
            self.outcome == MemoryCandidateSelectionPreparationOutcome.PREPARED
            and self.pending_action is None
        ):
            raise ValueError("Prepared candidate selection result requires pending_action.")


@dataclass(frozen=True, slots=True)
class MemoryCandidateSelectionRequestLifecycleResult:
    cancelled: bool
    stale: bool
    request: MemoryCandidateSelectionRequest | None = None
    reason: str = ""
    audit_delivery_failed: bool = False

    def __post_init__(self) -> None:
        if self.audit_delivery_failed and not self.reason.strip():
            raise ValueError(
                "Blocked memory candidate selection lifecycle result requires a reason."
            )


class MemoryCandidateSelectionRequestStore(ABC):
    @abstractmethod
    def set(self, request: MemoryCandidateSelectionRequest) -> MemoryCandidateSelectionRequest:
        raise NotImplementedError

    @abstractmethod
    def get(self) -> MemoryCandidateSelectionRequest | None:
        raise NotImplementedError

    @abstractmethod
    def clear(self) -> MemoryCandidateSelectionRequest | None:
        raise NotImplementedError


class InMemoryMemoryCandidateSelectionRequestStore(MemoryCandidateSelectionRequestStore):
    def __init__(self) -> None:
        self._request: MemoryCandidateSelectionRequest | None = None

    def set(self, request: MemoryCandidateSelectionRequest) -> MemoryCandidateSelectionRequest:
        self._request = request
        return request

    def get(self) -> MemoryCandidateSelectionRequest | None:
        return self._request

    def clear(self) -> MemoryCandidateSelectionRequest | None:
        request = self._request
        self._request = None
        return request


class MemoryCandidateSelectionRequestService:
    AUDIT_SOURCE = "memory-candidate-selection-request-service"
    EXPIRY_REASON = "selection_request_stale"

    def __init__(
        self,
        store: MemoryCandidateSelectionRequestStore | None = None,
        stale_after_seconds: int = 300,
        audit_delivery_service: MemoryCandidateSelectionAuditDeliveryService | None = None,
    ) -> None:
        if stale_after_seconds <= 0:
            raise ValueError("stale_after_seconds must be greater than zero.")
        self.store = store or InMemoryMemoryCandidateSelectionRequestStore()
        self.stale_after_seconds = stale_after_seconds
        self.audit_delivery_service = (
            audit_delivery_service
            or MemoryCandidateSelectionAuditDeliveryService(
                InMemoryMemoryCandidateSelectionAuditSink()
            )
        )

    def set_request(
        self,
        request: MemoryCandidateSelectionRequest,
    ) -> MemoryCandidateSelectionRequest:
        return self.store.set(request)

    def get_request(self) -> MemoryCandidateSelectionRequest | None:
        result = self.get_request_lifecycle_result()
        if result.stale or result.audit_delivery_failed:
            return None
        return result.request

    def get_request_lifecycle_result(self) -> MemoryCandidateSelectionRequestLifecycleResult:
        request = self.store.get()
        if request is None:
            return MemoryCandidateSelectionRequestLifecycleResult(
                cancelled=False,
                stale=False,
                request=None,
                reason="No active memory candidate selection request exists.",
            )

        if self.is_stale(request):
            event = MemoryCandidateSelectionAuditEvent(
                action=MemoryCandidateSelectionAuditAction.REQUEST_EXPIRED,
                source=self.AUDIT_SOURCE,
                selection_request_id=request.id,
                command_type=request.command_type,
                reason=self.EXPIRY_REASON,
            )
            delivery = self.audit_delivery_service.deliver(event)
            if delivery.failed:
                return MemoryCandidateSelectionRequestLifecycleResult(
                    cancelled=False,
                    stale=False,
                    request=request,
                    reason=delivery.reason,
                    audit_delivery_failed=True,
                )

            self.store.clear()
            return MemoryCandidateSelectionRequestLifecycleResult(
                cancelled=False,
                stale=True,
                request=request,
                reason="Memory candidate selection request is stale and was cleared.",
            )

        return MemoryCandidateSelectionRequestLifecycleResult(
            cancelled=False,
            stale=False,
            request=request,
            reason="Memory candidate selection request is active.",
        )

    def cancel_request(self) -> MemoryCandidateSelectionRequestLifecycleResult:
        request = self.store.clear()
        if request is None:
            return MemoryCandidateSelectionRequestLifecycleResult(
                cancelled=False,
                stale=False,
                request=None,
                reason="No active memory candidate selection request to cancel.",
            )

        return MemoryCandidateSelectionRequestLifecycleResult(
            cancelled=True,
            stale=False,
            request=request,
            reason="Memory candidate selection request cancelled.",
        )

    def clear_request(self) -> MemoryCandidateSelectionRequest | None:
        return self.store.clear()

    def is_stale(self, request: MemoryCandidateSelectionRequest) -> bool:
        created_at = parse_utc_iso(request.created_at)
        expires_at = created_at + timedelta(seconds=self.stale_after_seconds)
        return datetime.now(timezone.utc) > expires_at


class MemoryCandidateSelector:
    def select(
        self,
        request: MemoryCandidateSelectionRequest,
        memory_id: str,
    ) -> MemoryCandidateSelectionResult:
        clean_memory_id = memory_id.strip()
        if not clean_memory_id:
            return MemoryCandidateSelectionResult(
                outcome=MemoryCandidateSelectionOutcome.REJECTED,
                explanation="No memory candidate id was selected.",
                request_id=request.id,
            )

        for candidate in request.candidates:
            if candidate.memory.id == clean_memory_id:
                return MemoryCandidateSelectionResult(
                    outcome=MemoryCandidateSelectionOutcome.SELECTED,
                    explanation="One memory candidate was selected.",
                    request_id=request.id,
                    selected_memory_id=candidate.memory.id,
                )

        return MemoryCandidateSelectionResult(
            outcome=MemoryCandidateSelectionOutcome.REJECTED,
            explanation="Selected memory candidate does not belong to this request.",
            request_id=request.id,
        )


class MemoryCandidateSelectionPendingActionBuilder:
    def prepare(
        self,
        request: MemoryCandidateSelectionRequest,
        selection: MemoryCandidateSelectionResult,
    ) -> MemoryCandidateSelectionPreparationResult:
        if selection.request_id != request.id:
            return MemoryCandidateSelectionPreparationResult(
                outcome=MemoryCandidateSelectionPreparationOutcome.REJECTED,
                explanation="Selected memory candidate does not belong to this request.",
            )

        if (
            selection.outcome != MemoryCandidateSelectionOutcome.SELECTED
            or selection.selected_memory_id is None
            or not selection.selected_memory_id.strip()
        ):
            return MemoryCandidateSelectionPreparationResult(
                outcome=MemoryCandidateSelectionPreparationOutcome.REJECTED,
                explanation="No valid memory candidate selection is available.",
            )

        candidate_ids = {candidate.memory.id for candidate in request.candidates}
        if selection.selected_memory_id not in candidate_ids:
            return MemoryCandidateSelectionPreparationResult(
                outcome=MemoryCandidateSelectionPreparationOutcome.REJECTED,
                explanation="Selected memory candidate does not belong to this request.",
            )

        if request.command_type == MemoryCommandType.CORRECT:
            action = PendingMemoryAction(
                action_type=PendingMemoryActionType.CORRECT,
                command_type=MemoryCommandType.CORRECT,
                explanation="Correct this memory after confirmation.",
                source_text=request.source_text,
                memory_id=selection.selected_memory_id,
                proposed_content=request.proposed_content,
                metadata={
                    "source": "memory-candidate-selection",
                    "selection_request_id": request.id,
                },
            )
        elif request.command_type == MemoryCommandType.DELETE:
            action = PendingMemoryAction(
                action_type=PendingMemoryActionType.DELETE,
                command_type=MemoryCommandType.DELETE,
                explanation="Delete this memory after confirmation.",
                source_text=request.source_text,
                memory_id=selection.selected_memory_id,
                metadata={
                    "source": "memory-candidate-selection",
                    "selection_request_id": request.id,
                },
            )
        else:
            return MemoryCandidateSelectionPreparationResult(
                outcome=MemoryCandidateSelectionPreparationOutcome.REJECTED,
                explanation="Unsupported memory candidate selection command type.",
            )

        return MemoryCandidateSelectionPreparationResult(
            outcome=MemoryCandidateSelectionPreparationOutcome.PREPARED,
            explanation="Selected memory candidate is ready for pending confirmation.",
            pending_action=action,
        )
