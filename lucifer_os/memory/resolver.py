from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from lucifer_os.memory.models import MemoryItem


class MemoryTargetResolutionOutcome(str, Enum):
    NO_MATCH = "no_match"
    SINGLE_SAFE_MATCH = "single_safe_match"
    MULTIPLE_CANDIDATES = "multiple_candidates"
    UNSAFE_AMBIGUOUS_MATCH = "unsafe_ambiguous_match"
    EXPLICIT_ID_MATCH = "explicit_id_match"


@dataclass(frozen=True, slots=True)
class MemoryTargetCandidate:
    memory: MemoryItem
    reason: str
    score: float = 1.0

    def __post_init__(self) -> None:
        if not self.reason.strip():
            raise ValueError("Memory target candidate reason cannot be empty.")
        if self.score < 0.0 or self.score > 1.0:
            raise ValueError("Memory target candidate score must be between 0.0 and 1.0.")


@dataclass(frozen=True, slots=True)
class MemoryTargetResolutionResult:
    outcome: MemoryTargetResolutionOutcome
    explanation: str
    candidates: tuple[MemoryTargetCandidate, ...] = field(default_factory=tuple)
    selected_memory_id: str | None = None
    safe_for_confirmation: bool = False

    def __post_init__(self) -> None:
        if not self.explanation.strip():
            raise ValueError("Memory target resolution explanation cannot be empty.")
        if self.safe_for_confirmation and not self.selected_memory_id:
            raise ValueError("Safe memory target resolution requires selected_memory_id.")


class MemoryTargetResolver:
    def __init__(self, max_candidates: int = 10) -> None:
        if max_candidates <= 0:
            raise ValueError("max_candidates must be greater than zero.")
        self.max_candidates = max_candidates

    def resolve_explicit_id(
        self,
        memory_id: str,
        candidates: tuple[MemoryItem, ...],
    ) -> MemoryTargetResolutionResult:
        clean_memory_id = memory_id.strip()
        if not clean_memory_id:
            return MemoryTargetResolutionResult(
                outcome=MemoryTargetResolutionOutcome.NO_MATCH,
                explanation="No explicit memory id was provided.",
            )

        for memory in candidates[: self.max_candidates]:
            if memory.id == clean_memory_id:
                return MemoryTargetResolutionResult(
                    outcome=MemoryTargetResolutionOutcome.EXPLICIT_ID_MATCH,
                    explanation="Explicit memory id matched one candidate.",
                    candidates=(
                        MemoryTargetCandidate(
                            memory=memory,
                            reason="explicit memory id match",
                            score=1.0,
                        ),
                    ),
                    selected_memory_id=memory.id,
                    safe_for_confirmation=True,
                )

        return MemoryTargetResolutionResult(
            outcome=MemoryTargetResolutionOutcome.NO_MATCH,
            explanation="Explicit memory id did not match any bounded candidate.",
        )

    def resolve_query(
        self,
        query: str,
        candidates: tuple[MemoryItem, ...],
    ) -> MemoryTargetResolutionResult:
        clean_query = query.strip().lower()
        if not clean_query:
            return MemoryTargetResolutionResult(
                outcome=MemoryTargetResolutionOutcome.NO_MATCH,
                explanation="No memory target query was provided.",
            )

        matches = tuple(
            MemoryTargetCandidate(
                memory=memory,
                reason="normalized content substring match",
                score=1.0,
            )
            for memory in candidates[: self.max_candidates]
            if clean_query in memory.content.lower()
        )

        if not matches:
            return MemoryTargetResolutionResult(
                outcome=MemoryTargetResolutionOutcome.NO_MATCH,
                explanation="No matching memory candidate was found.",
            )

        if len(matches) == 1:
            return MemoryTargetResolutionResult(
                outcome=MemoryTargetResolutionOutcome.SINGLE_SAFE_MATCH,
                explanation="One safe memory candidate was found.",
                candidates=matches,
                selected_memory_id=matches[0].memory.id,
                safe_for_confirmation=True,
            )

        return MemoryTargetResolutionResult(
            outcome=MemoryTargetResolutionOutcome.MULTIPLE_CANDIDATES,
            explanation="Multiple memory candidates were found; user selection is required.",
            candidates=matches,
            safe_for_confirmation=False,
        )
