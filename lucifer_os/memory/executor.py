from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from lucifer_os.memory.commands import MemoryCommand, MemoryCommandType
from lucifer_os.memory.models import MemoryItem, MemoryScope, MemoryType
from lucifer_os.memory.pending import (
    PendingMemoryAction,
    PendingMemoryActionConfirmationResult,
    PendingMemoryActionService,
    PendingMemoryActionType,
)
from lucifer_os.memory.resolution_plan import MemoryResolutionPlanAction, MemoryResolutionPlanner
from lucifer_os.memory.resolver import MemoryTargetCandidate, MemoryTargetResolver
from lucifer_os.memory.selection_audit import (
    InMemoryMemoryCandidateSelectionAuditSink,
    MemoryCandidateSelectionAuditAction,
    MemoryCandidateSelectionAuditDeliveryService,
    MemoryCandidateSelectionAuditEvent,
)
from lucifer_os.memory.selection import (
    MemoryCandidateSelectionOutcome,
    MemoryCandidateSelectionPendingActionBuilder,
    MemoryCandidateSelectionRequest,
    MemoryCandidateSelectionRequestService,
    MemoryCandidateSelector,
)
from lucifer_os.memory.service import MemoryOperationResult, MemoryService


class MemoryCommandExecutionStatus(str, Enum):
    EXECUTED = "executed"
    PENDING_CONFIRMATION = "pending_confirmation"
    AWAITING_USER_SELECTION = "awaiting_user_selection"
    CANCELLED_USER_SELECTION = "cancelled_user_selection"
    CONFIRMED_PENDING = "confirmed_pending"
    CANCELLED_PENDING = "cancelled_pending"
    REJECTED = "rejected"
    NOT_MEMORY_COMMAND = "not_memory_command"

@dataclass(frozen=True, slots=True)
class MemoryCommandExecutionResult:
    status: MemoryCommandExecutionStatus
    message: str
    command: MemoryCommand
    operation_result: MemoryOperationResult | None = None
    pending_action: PendingMemoryAction | None = None
    confirmation_result: PendingMemoryActionConfirmationResult | None = None
    memories: tuple[MemoryItem, ...] = field(default_factory=tuple)
    selection_request: MemoryCandidateSelectionRequest | None = None


class MemoryCommandExecutor:
    def __init__(
        self,
        memory_service: MemoryService,
        pending_service: PendingMemoryActionService | None = None,
        default_type: MemoryType = MemoryType.USER_INSTRUCTION,
        default_scope: MemoryScope = MemoryScope.GLOBAL,
        max_results: int = 20,
        target_resolver: MemoryTargetResolver | None = None,
        resolution_planner: MemoryResolutionPlanner | None = None,
        selection_service: MemoryCandidateSelectionRequestService | None = None,
        candidate_selector: MemoryCandidateSelector | None = None,
        selection_pending_action_builder: MemoryCandidateSelectionPendingActionBuilder | None = None,
        selection_audit_delivery_service: MemoryCandidateSelectionAuditDeliveryService | None = None,
    ) -> None:
        if max_results <= 0:
            raise ValueError("max_results must be greater than zero.")
        self.memory_service = memory_service
        self.pending_service = pending_service or PendingMemoryActionService()
        self.default_type = default_type
        self.default_scope = default_scope
        self.max_results = max_results
        self.target_resolver = target_resolver or MemoryTargetResolver(max_candidates=max_results)
        self.resolution_planner = resolution_planner or MemoryResolutionPlanner()
        self.selection_service = selection_service or MemoryCandidateSelectionRequestService()
        self.candidate_selector = candidate_selector or MemoryCandidateSelector()
        self.selection_pending_action_builder = (
            selection_pending_action_builder
            or MemoryCandidateSelectionPendingActionBuilder()
        )
        self.selection_audit_delivery_service = (
            selection_audit_delivery_service
            or MemoryCandidateSelectionAuditDeliveryService(
                InMemoryMemoryCandidateSelectionAuditSink()
            )
        )

    def execute(self, command: MemoryCommand) -> MemoryCommandExecutionResult:
        if command.type == MemoryCommandType.REMEMBER:
            return self._execute_remember(command)
        if command.type == MemoryCommandType.LIST:
            return self._execute_list(command)
        if command.type == MemoryCommandType.SEARCH:
            return self._execute_search(command)
        if command.type == MemoryCommandType.CORRECT:
            return self._prepare_correct(command)
        if command.type == MemoryCommandType.DELETE:
            return self._prepare_delete(command)
        if command.type == MemoryCommandType.EXPLAIN_POLICY:
            return self._explain_policy(command)
        if command.type == MemoryCommandType.CONFIRM_PENDING:
            return self._confirm_pending(command)
        if command.type == MemoryCommandType.CANCEL_PENDING:
            return self._cancel_pending(command)

        return MemoryCommandExecutionResult(
            status=MemoryCommandExecutionStatus.NOT_MEMORY_COMMAND,
            message="Not a memory command.",
            command=command,
        )

    def _execute_remember(self, command: MemoryCommand) -> MemoryCommandExecutionResult:
        if command.content is None or not command.content.strip():
            return MemoryCommandExecutionResult(
                status=MemoryCommandExecutionStatus.REJECTED,
                message="Remember command has no content.",
                command=command,
            )

        result = self.memory_service.add_memory(
            content=command.content,
            type=self.default_type,
            scope=self.default_scope,
            source="memory-command-executor",
            confirmed=False,
        )

        if result.requires_confirmation:
            pending_action = PendingMemoryAction(
                action_type=PendingMemoryActionType.REMEMBER,
                command_type=command.type,
                explanation="Store this memory after confirmation.",
                source_text=command.raw_text,
                proposed_content=command.content,
                metadata={
                    "type": self.default_type.value,
                    "scope": self.default_scope.value,
                    "source": "memory-command-executor",
                },
            )
            self.pending_service.set_pending(pending_action)
            return MemoryCommandExecutionResult(
                status=MemoryCommandExecutionStatus.PENDING_CONFIRMATION,
                message="Memory write requires confirmation.",
                command=command,
                operation_result=result,
                pending_action=pending_action,
            )

        if not result.allowed:
            return MemoryCommandExecutionResult(
                status=MemoryCommandExecutionStatus.REJECTED,
                message=result.audit_reason,
                command=command,
                operation_result=result,
            )

        return MemoryCommandExecutionResult(
            status=MemoryCommandExecutionStatus.EXECUTED,
            message="Memory stored.",
            command=command,
            operation_result=result,
        )

    def _execute_list(self, command: MemoryCommand) -> MemoryCommandExecutionResult:
        memories = tuple(self.memory_service.list_memories()[: self.max_results])
        return MemoryCommandExecutionResult(
            status=MemoryCommandExecutionStatus.EXECUTED,
            message="Memory list returned.",
            command=command,
            memories=memories,
        )

    def _execute_search(self, command: MemoryCommand) -> MemoryCommandExecutionResult:
        if command.query is None or not command.query.strip():
            return MemoryCommandExecutionResult(
                status=MemoryCommandExecutionStatus.REJECTED,
                message="Search command has no query.",
                command=command,
            )

        query = command.query.strip().lower()
        matches = [
            item
            for item in self.memory_service.list_memories()
            if query in item.content.lower()
        ]
        return MemoryCommandExecutionResult(
            status=MemoryCommandExecutionStatus.EXECUTED,
            message="Memory search returned.",
            command=command,
            memories=tuple(matches[: self.max_results]),
        )

    def _prepare_correct(self, command: MemoryCommand) -> MemoryCommandExecutionResult:
        if command.content is None or not command.content.strip():
            return MemoryCommandExecutionResult(
                status=MemoryCommandExecutionStatus.REJECTED,
                message="Correct command requires proposed content.",
                command=command,
            )

        memory_id = command.memory_id

        if memory_id is None or not memory_id.strip():
            if command.query is None or not command.query.strip():
                return MemoryCommandExecutionResult(
                    status=MemoryCommandExecutionStatus.REJECTED,
                    message="Correct command requires an explicit memory id or a target query.",
                    command=command,
                )

            candidates = tuple(self.memory_service.list_memories()[: self.max_results])
            resolution = self.target_resolver.resolve_query(command.query, candidates)
            plan = self.resolution_planner.plan(command.type, resolution)

            if plan.action == MemoryResolutionPlanAction.PREPARE_PENDING_ACTION:
                memory_id = plan.selected_memory_id
            elif plan.action == MemoryResolutionPlanAction.ASK_USER_TO_CHOOSE:
                return self._await_user_selection(
                    command=command,
                    candidates=plan.candidates,
                )
            else:
                return MemoryCommandExecutionResult(
                    status=MemoryCommandExecutionStatus.REJECTED,
                    message=plan.explanation,
                    command=command,
                    memories=tuple(candidate.memory for candidate in plan.candidates),
                )

        pending_action = PendingMemoryAction(
            action_type=PendingMemoryActionType.CORRECT,
            command_type=command.type,
            explanation="Correct this memory after confirmation.",
            source_text=command.raw_text,
            memory_id=memory_id,
            proposed_content=command.content,
            metadata={
                "type": self.default_type.value,
                "scope": self.default_scope.value,
                "source": "memory-command-executor",
            },
        )
        self.pending_service.set_pending(pending_action)
        return MemoryCommandExecutionResult(
            status=MemoryCommandExecutionStatus.PENDING_CONFIRMATION,
            message="Memory correction requires confirmation.",
            command=command,
            pending_action=pending_action,
        )

    def _prepare_delete(self, command: MemoryCommand) -> MemoryCommandExecutionResult:
        memory_id = command.memory_id

        if memory_id is None or not memory_id.strip():
            if command.query is None or not command.query.strip():
                return MemoryCommandExecutionResult(
                    status=MemoryCommandExecutionStatus.REJECTED,
                    message="Delete command requires an explicit memory id or a target query.",
                    command=command,
                )

            candidates = tuple(self.memory_service.list_memories()[: self.max_results])
            resolution = self.target_resolver.resolve_query(command.query, candidates)
            plan = self.resolution_planner.plan(command.type, resolution)

            if plan.action == MemoryResolutionPlanAction.PREPARE_PENDING_ACTION:
                memory_id = plan.selected_memory_id
            elif plan.action == MemoryResolutionPlanAction.ASK_USER_TO_CHOOSE:
                return self._await_user_selection(
                    command=command,
                    candidates=plan.candidates,
                )
            else:
                return MemoryCommandExecutionResult(
                    status=MemoryCommandExecutionStatus.REJECTED,
                    message=plan.explanation,
                    command=command,
                    memories=tuple(candidate.memory for candidate in plan.candidates),
                )

        pending_action = PendingMemoryAction(
            action_type=PendingMemoryActionType.DELETE,
            command_type=command.type,
            explanation="Delete this memory after confirmation.",
            source_text=command.raw_text,
            memory_id=memory_id,
            metadata={
                "source": "memory-command-executor",
            },
        )
        self.pending_service.set_pending(pending_action)
        return MemoryCommandExecutionResult(
            status=MemoryCommandExecutionStatus.PENDING_CONFIRMATION,
            message="Memory delete requires confirmation.",
            command=command,
            pending_action=pending_action,
        )

    def _await_user_selection(
        self,
        command: MemoryCommand,
        candidates: tuple[MemoryTargetCandidate, ...],
    ) -> MemoryCommandExecutionResult:
        active_lifecycle = self.selection_service.get_request_lifecycle_result()
        if active_lifecycle.audit_delivery_failed:
            return MemoryCommandExecutionResult(
                status=MemoryCommandExecutionStatus.REJECTED,
                message=active_lifecycle.reason,
                command=command,
                memories=tuple(
                    candidate.memory for candidate in active_lifecycle.request.candidates
                ) if active_lifecycle.request is not None else (),
                selection_request=active_lifecycle.request,
            )

        if active_lifecycle.request is not None and not active_lifecycle.stale:
            return MemoryCommandExecutionResult(
                status=MemoryCommandExecutionStatus.REJECTED,
                message=(
                    "An active memory candidate selection request must be cancelled "
                    "or completed before a new selection request is created."
                ),
                command=command,
                memories=tuple(
                    candidate.memory for candidate in active_lifecycle.request.candidates
                ),
                selection_request=active_lifecycle.request,
            )

        request = MemoryCandidateSelectionRequest(
            command_type=command.type,
            source_text=command.raw_text,
            candidates=candidates,
            proposed_content=(
                command.content
                if command.type == MemoryCommandType.CORRECT
                else None
            ),
        )
        event = MemoryCandidateSelectionAuditEvent(
            action=MemoryCandidateSelectionAuditAction.REQUEST_CREATED,
            source="memory-command-executor",
            selection_request_id=request.id,
            command_type=request.command_type,
            reason="ambiguous_target",
        )
        delivery = self.selection_audit_delivery_service.deliver(event)
        if delivery.failed:
            return MemoryCommandExecutionResult(
                status=MemoryCommandExecutionStatus.REJECTED,
                message=delivery.reason,
                command=command,
                memories=tuple(candidate.memory for candidate in candidates),
            )

        self.selection_service.set_request(request)

        return MemoryCommandExecutionResult(
            status=MemoryCommandExecutionStatus.AWAITING_USER_SELECTION,
            message="Multiple matching memories found; user selection is required.",
            command=command,
            memories=tuple(candidate.memory for candidate in candidates),
            selection_request=request,
        )

    def select_memory_candidate(
        self,
        request_id: str,
        memory_id: str,
    ) -> MemoryCommandExecutionResult:
        lifecycle = self.selection_service.get_request_lifecycle_result()
        if lifecycle.audit_delivery_failed:
            return MemoryCommandExecutionResult(
                status=MemoryCommandExecutionStatus.REJECTED,
                message=lifecycle.reason,
                command=self._selection_command(lifecycle.request),
                selection_request=lifecycle.request,
            )

        if lifecycle.stale:
            return MemoryCommandExecutionResult(
                status=MemoryCommandExecutionStatus.REJECTED,
                message=lifecycle.reason,
                command=self._selection_command(lifecycle.request),
            )

        request = lifecycle.request
        if request is None:
            return MemoryCommandExecutionResult(
                status=MemoryCommandExecutionStatus.REJECTED,
                message="No active memory candidate selection request exists.",
                command=self._selection_command(None),
            )

        if request.id != request_id:
            return MemoryCommandExecutionResult(
                status=MemoryCommandExecutionStatus.REJECTED,
                message="Memory candidate selection request does not match the active request.",
                command=self._selection_command(request),
            )

        selection = self.candidate_selector.select(request, memory_id)
        if selection.outcome != MemoryCandidateSelectionOutcome.SELECTED:
            return MemoryCommandExecutionResult(
                status=MemoryCommandExecutionStatus.REJECTED,
                message=selection.explanation,
                command=self._selection_command(request),
                memories=tuple(candidate.memory for candidate in request.candidates),
                selection_request=request,
            )

        preparation = self.selection_pending_action_builder.prepare(request, selection)
        if preparation.pending_action is None:
            return MemoryCommandExecutionResult(
                status=MemoryCommandExecutionStatus.REJECTED,
                message=preparation.explanation,
                command=self._selection_command(request),
                memories=tuple(candidate.memory for candidate in request.candidates),
                selection_request=request,
            )

        self.selection_service.clear_request()
        self.pending_service.set_pending(preparation.pending_action)

        return MemoryCommandExecutionResult(
            status=MemoryCommandExecutionStatus.PENDING_CONFIRMATION,
            message="Selected memory target requires confirmation.",
            command=self._selection_command(request),
            pending_action=preparation.pending_action,
        )

    def cancel_memory_candidate_selection(self) -> MemoryCommandExecutionResult:
        lifecycle = self.selection_service.get_request_lifecycle_result()
        if lifecycle.audit_delivery_failed:
            return MemoryCommandExecutionResult(
                status=MemoryCommandExecutionStatus.REJECTED,
                message=lifecycle.reason,
                command=self._selection_command(lifecycle.request),
                selection_request=lifecycle.request,
            )

        if lifecycle.stale:
            return MemoryCommandExecutionResult(
                status=MemoryCommandExecutionStatus.REJECTED,
                message=lifecycle.reason,
                command=self._selection_command(lifecycle.request),
            )

        request = lifecycle.request
        if request is None:
            return MemoryCommandExecutionResult(
                status=MemoryCommandExecutionStatus.REJECTED,
                message="No active memory candidate selection request to cancel.",
                command=self._selection_command(None),
            )

        result = self.selection_service.cancel_request()
        return MemoryCommandExecutionResult(
            status=MemoryCommandExecutionStatus.CANCELLED_USER_SELECTION,
            message=result.reason,
            command=self._selection_command(request),
            selection_request=result.request,
        )

    @staticmethod
    def _selection_command(
        request: MemoryCandidateSelectionRequest | None,
    ) -> MemoryCommand:
        if request is None:
            return MemoryCommand(
                type=MemoryCommandType.NOT_MEMORY_COMMAND,
                raw_text="memory candidate selection",
                normalized_text="memory candidate selection",
            )

        return MemoryCommand(
            type=request.command_type,
            raw_text=request.source_text,
            normalized_text=request.source_text.strip().lower(),
            content=request.proposed_content,
        )

    def _explain_policy(self, command: MemoryCommand) -> MemoryCommandExecutionResult:
        return MemoryCommandExecutionResult(
            status=MemoryCommandExecutionStatus.EXECUTED,
            message="Memory writes, corrections and deletes are policy-gated and may require confirmation.",
            command=command,
        )

    def _confirm_pending(self, command: MemoryCommand) -> MemoryCommandExecutionResult:
        result = self.pending_service.confirm_pending()
        if not result.confirmed or result.action is None:
            return MemoryCommandExecutionResult(
                status=MemoryCommandExecutionStatus.REJECTED,
                message=result.reason,
                command=command,
                confirmation_result=result,
                pending_action=result.action,
            )

        operation_result = self._execute_confirmed_action(result.action)
        status = MemoryCommandExecutionStatus.CONFIRMED_PENDING if operation_result.allowed else MemoryCommandExecutionStatus.REJECTED
        return MemoryCommandExecutionResult(
            status=status,
            message=result.reason,
            command=command,
            operation_result=operation_result,
            confirmation_result=result,
            pending_action=result.action,
        )

    def _execute_confirmed_action(self, action: PendingMemoryAction) -> MemoryOperationResult:
        if action.action_type == PendingMemoryActionType.REMEMBER:
            if action.proposed_content is None or not action.proposed_content.strip():
                return MemoryOperationResult(
                    allowed=False,
                    requires_confirmation=False,
                    audit_reason="Confirmed remember action has no proposed content.",
                )
            return self.memory_service.add_memory(
                content=action.proposed_content,
                type=self.default_type,
                scope=self.default_scope,
                source="memory-command-executor",
                confirmed=True,
            )

        if action.action_type == PendingMemoryActionType.CORRECT:
            if action.memory_id is None or not action.memory_id.strip():
                return MemoryOperationResult(
                    allowed=False,
                    requires_confirmation=False,
                    audit_reason="Confirmed correction action has no memory id.",
                )
            if action.proposed_content is None or not action.proposed_content.strip():
                return MemoryOperationResult(
                    allowed=False,
                    requires_confirmation=False,
                    audit_reason="Confirmed correction action has no proposed content.",
                )
            return self.memory_service.update_memory(
                memory_id=action.memory_id,
                content=action.proposed_content,
                type=self.default_type,
                scope=self.default_scope,
                source="memory-command-executor",
                confirmed=True,
            )

        if action.action_type == PendingMemoryActionType.DELETE:
            if action.memory_id is None or not action.memory_id.strip():
                return MemoryOperationResult(
                    allowed=False,
                    requires_confirmation=False,
                    audit_reason="Confirmed delete action has no memory id.",
                )
            return self.memory_service.delete_memory(
                memory_id=action.memory_id,
                source="memory-command-executor",
                confirmed=True,
            )

        return MemoryOperationResult(
            allowed=False,
            requires_confirmation=False,
            audit_reason="Unsupported pending memory action type.",
        )

    def _cancel_pending(self, command: MemoryCommand) -> MemoryCommandExecutionResult:
        result = self.pending_service.cancel_pending()
        status = MemoryCommandExecutionStatus.CANCELLED_PENDING if result.cancelled else MemoryCommandExecutionStatus.REJECTED
        return MemoryCommandExecutionResult(
            status=status,
            message=result.reason,
            command=command,
            confirmation_result=result,
            pending_action=result.action,
        )
