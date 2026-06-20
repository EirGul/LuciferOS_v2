from datetime import datetime, timedelta, timezone

from lucifer_os.memory import (
    InMemoryMemoryAuditSink,
    InMemoryMemoryStore,
    MemoryCandidateSelectionRequestService,
    MemoryCommandExecutionStatus,
    MemoryCommandExecutor,
    MemoryCommandParser,
    MemoryPolicy,
    MemoryScope,
    MemoryService,
    MemoryType,
)


def make_executor(selection_service=None):
    store = InMemoryMemoryStore()
    audit = InMemoryMemoryAuditSink()
    service = MemoryService(store=store, policy=MemoryPolicy(), audit_sink=audit)
    selection_service = selection_service or MemoryCandidateSelectionRequestService()
    executor = MemoryCommandExecutor(
        memory_service=service,
        selection_service=selection_service,
        max_results=10,
    )
    return executor, service, selection_service


def add_memory(service, content):
    result = service.add_memory(
        content=content,
        type=MemoryType.PREFERENCE,
        scope=MemoryScope.PROJECT,
        source="test",
        confirmed=True,
    )
    assert result.allowed is True
    return next(item for item in service.list_memories() if item.content == content)


def create_ambiguous_delete(executor, service):
    add_memory(service, "LuciferOS bruker SQLite for memory")
    add_memory(service, "LuciferOS bruker SQLite for audit")
    return executor.execute(MemoryCommandParser().parse("glem at SQLite"))


def test_executor_has_cancelled_user_selection_status():
    assert (
        MemoryCommandExecutionStatus.CANCELLED_USER_SELECTION.value
        == "cancelled_user_selection"
    )


def test_new_ambiguous_command_does_not_silently_replace_active_selection_request():
    executor, service, selection_service = make_executor()

    first = create_ambiguous_delete(executor, service)
    first_request = first.selection_request
    assert first_request is not None

    second = executor.execute(
        MemoryCommandParser().parse(
            'korriger minne "SQLite" til "LuciferOS bruker en persistent store"'
        )
    )

    assert second.status == MemoryCommandExecutionStatus.REJECTED
    assert second.selection_request == first_request
    assert selection_service.get_request() == first_request
    assert executor.pending_service.get_pending() is None


def test_cancel_active_selection_clears_request_without_pending_action():
    executor, service, selection_service = make_executor()
    waiting = create_ambiguous_delete(executor, service)
    request = waiting.selection_request
    assert request is not None

    result = executor.cancel_memory_candidate_selection()

    assert result.status == MemoryCommandExecutionStatus.CANCELLED_USER_SELECTION
    assert result.selection_request == request
    assert selection_service.get_request() is None
    assert executor.pending_service.get_pending() is None


def test_cancel_without_active_selection_is_rejected():
    executor, _, _ = make_executor()

    result = executor.cancel_memory_candidate_selection()

    assert result.status == MemoryCommandExecutionStatus.REJECTED
    assert result.message == "No active memory candidate selection request to cancel."


def test_stale_selection_cannot_be_selected_or_prepare_pending_action():
    selection_service = MemoryCandidateSelectionRequestService(stale_after_seconds=1)
    executor, service, _ = make_executor(selection_service=selection_service)
    waiting = create_ambiguous_delete(executor, service)
    request = waiting.selection_request
    assert request is not None

    expired_request = type(request)(
        command_type=request.command_type,
        source_text=request.source_text,
        candidates=request.candidates,
        proposed_content=request.proposed_content,
        id=request.id,
        created_at=(datetime.now(timezone.utc) - timedelta(seconds=2)).isoformat(),
    )
    selection_service.set_request(expired_request)

    result = executor.select_memory_candidate(request.id, request.candidates[0].memory.id)

    assert result.status == MemoryCommandExecutionStatus.REJECTED
    assert result.message == "Memory candidate selection request is stale and was cleared."
    assert selection_service.get_request() is None
    assert executor.pending_service.get_pending() is None


def test_cancelled_selection_allows_new_ambiguous_selection_request():
    executor, service, selection_service = make_executor()
    first = create_ambiguous_delete(executor, service)
    first_request = first.selection_request
    assert first_request is not None

    cancelled = executor.cancel_memory_candidate_selection()
    assert cancelled.status == MemoryCommandExecutionStatus.CANCELLED_USER_SELECTION

    second = executor.execute(
        MemoryCommandParser().parse(
            'korriger minne "SQLite" til "LuciferOS bruker en persistent store"'
        )
    )

    assert second.status == MemoryCommandExecutionStatus.AWAITING_USER_SELECTION
    assert second.selection_request is not None
    assert second.selection_request.id != first_request.id
    assert selection_service.get_request() == second.selection_request


def test_stale_selection_allows_new_ambiguous_selection_request():
    selection_service = MemoryCandidateSelectionRequestService(stale_after_seconds=1)
    executor, service, _ = make_executor(selection_service=selection_service)
    first = create_ambiguous_delete(executor, service)
    request = first.selection_request
    assert request is not None

    expired_request = type(request)(
        command_type=request.command_type,
        source_text=request.source_text,
        candidates=request.candidates,
        proposed_content=request.proposed_content,
        id=request.id,
        created_at=(datetime.now(timezone.utc) - timedelta(seconds=2)).isoformat(),
    )
    selection_service.set_request(expired_request)

    second = executor.execute(
        MemoryCommandParser().parse(
            'korriger minne "SQLite" til "LuciferOS bruker en persistent store"'
        )
    )

    assert second.status == MemoryCommandExecutionStatus.AWAITING_USER_SELECTION
    assert second.selection_request is not None
    assert second.selection_request.id != request.id
    assert executor.pending_service.get_pending() is None


def test_cancel_or_expiry_never_changes_memory():
    selection_service = MemoryCandidateSelectionRequestService(stale_after_seconds=1)
    executor, service, _ = make_executor(selection_service=selection_service)
    first = add_memory(service, "LuciferOS bruker SQLite for memory")
    second = add_memory(service, "LuciferOS bruker SQLite for audit")

    waiting = executor.execute(MemoryCommandParser().parse("glem at SQLite"))
    request = waiting.selection_request
    assert request is not None

    cancelled = executor.cancel_memory_candidate_selection()
    assert cancelled.status == MemoryCommandExecutionStatus.CANCELLED_USER_SELECTION
    assert first in service.list_memories()
    assert second in service.list_memories()
