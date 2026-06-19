from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from lucifer_os.memory.commands import MemoryCommandType
from lucifer_os.memory.resolver import MemoryTargetCandidate, MemoryTargetResolutionOutcome, MemoryTargetResolutionResult


class MemoryResolutionPlanAction(str, Enum):
    REJECT = "reject"
    ASK_USER_TO_CHOOSE = "ask_user_to_choose"
    PREPARE_PENDING_ACTION = "prepare_pending_action"


@dataclass(frozen=True, slots=True)
class MemoryResolutionPlan:
    action: MemoryResolutionPlanAction
    command_type: MemoryCommandType
    explanation: str
    selected_memory_id: str | None = None
    candidates: tuple[MemoryTargetCandidate, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not self.explanation.strip():
            raise ValueError("Memory resolution plan explanation cannot be empty.")
        if self.action == MemoryResolutionPlanAction.PREPARE_PENDING_ACTION and not self.selected_memory_id:
            raise ValueError("Preparing a pending memory action requires selected_memory_id.")


class MemoryResolutionPlanner:
    def plan(
        self,
        command_type: MemoryCommandType,
        resolution: MemoryTargetResolutionResult,
    ) -> MemoryResolutionPlan:
        if command_type not in {MemoryCommandType.CORRECT, MemoryCommandType.DELETE}:
            return MemoryResolutionPlan(
                action=MemoryResolutionPlanAction.REJECT,
                command_type=command_type,
                explanation="Only correction and delete commands can use memory target resolution.",
            )

        if resolution.outcome == MemoryTargetResolutionOutcome.NO_MATCH:
            return MemoryResolutionPlan(
                action=MemoryResolutionPlanAction.REJECT,
                command_type=command_type,
                explanation="No matching memory target was found.",
            )

        if resolution.outcome in {
            MemoryTargetResolutionOutcome.MULTIPLE_CANDIDATES,
            MemoryTargetResolutionOutcome.UNSAFE_AMBIGUOUS_MATCH,
        }:
            return MemoryResolutionPlan(
                action=MemoryResolutionPlanAction.ASK_USER_TO_CHOOSE,
                command_type=command_type,
                explanation="User must choose one memory target before execution can be prepared.",
                candidates=resolution.candidates,
            )

        if resolution.outcome in {
            MemoryTargetResolutionOutcome.SINGLE_SAFE_MATCH,
            MemoryTargetResolutionOutcome.EXPLICIT_ID_MATCH,
        }:
            if not resolution.safe_for_confirmation or not resolution.selected_memory_id:
                return MemoryResolutionPlan(
                    action=MemoryResolutionPlanAction.REJECT,
                    command_type=command_type,
                    explanation="Resolution was not safe for confirmation.",
                    candidates=resolution.candidates,
                )

            return MemoryResolutionPlan(
                action=MemoryResolutionPlanAction.PREPARE_PENDING_ACTION,
                command_type=command_type,
                explanation="One safe memory target was selected for pending confirmation.",
                selected_memory_id=resolution.selected_memory_id,
                candidates=resolution.candidates,
            )

        return MemoryResolutionPlan(
            action=MemoryResolutionPlanAction.REJECT,
            command_type=command_type,
            explanation="Unsupported memory target resolution outcome.",
            candidates=resolution.candidates,
        )
