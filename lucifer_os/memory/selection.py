from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from uuid import uuid4

from lucifer_os.memory.commands import MemoryCommandType
from lucifer_os.memory.resolver import MemoryTargetCandidate


class MemoryCandidateSelectionOutcome(str, Enum):
    SELECTED = "selected"
    REJECTED = "rejected"


@dataclass(frozen=True, slots=True)
class MemoryCandidateSelectionRequest:
    command_type: MemoryCommandType
    source_text: str
    candidates: tuple[MemoryTargetCandidate, ...]
    id: str = field(default_factory=lambda: str(uuid4()))

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
