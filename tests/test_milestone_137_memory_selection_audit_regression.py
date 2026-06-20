from datetime import datetime, timedelta, timezone
from pathlib import Path

from lucifer_os.memory import (
    InMemoryMemoryCandidateSelectionAuditSink,
    InMemoryMemoryAuditSink,
    InMemoryMemoryStore,
    MemoryCandidateSelectionAuditAction,
    MemoryCandidateSelectionAuditDeliveryService,
    MemoryCandidateSelectionRequest,
    MemoryCandidateSelectionRequestService,
    MemoryCommandExecutionStatus,
    MemoryCommandExecutor,
    MemoryCommandParser,
    MemoryItem,
    MemoryPolicy,
    MemoryScope,
    MemoryService,
    MemoryTargetCandidate,
    MemoryType,
)


def make_executor(audit_sink):
    memory_service = MemoryService(
        store=InMemoryMemoryStore(),
        policy=MemoryPolicy(),
        audit_sink=InMemoryMemoryAuditSink(),
    )
    return MemoryCommandExecutor(
        memory_service=memory_service,
        selection_service=MemoryCandidateSelectionRequestService(),
        selection_audit_delivery_service=MemoryCandidateSelectionAuditDeliveryService(
            audit_sink
        ),
    )


def add_memory(executor, content):
    result = executor.memory_service.add_memory(
        content=content,
        type=MemoryType.PREFERENCE,
        scope=MemoryScope.PROJECT,
        source="test",
        confirmed=True,
    )
    assert result.allowed is True


def create_ambiguous_delete(executor):
    add_memory(executor, "LuciferOS bruker SQLite for memory")
    add_memory(executor, "LuciferOS bruker SQLite for audit")

    result = executor.execute(MemoryCommandParser().parse("glem at SQLite"))

    assert result.status == MemoryCommandExecutionStatus.AWAITING_USER_SELECTION
    assert result.selection_request is not None
    return result.selection_request


def make_expired_request():
    candidate = MemoryTargetCandidate(
        memory=MemoryItem(
            id="memory-1",
            content="LuciferOS bruker SQLite",
            type=MemoryType.PREFERENCE,
            scope=MemoryScope.PROJECT,
            source="test",
        ),
        reason="test candidate",
    )
    return MemoryCandidateSelectionRequest(
        command_type=MemoryCommandParser().parse("glem at SQLite").type,
        source_text="glem at SQLite",
        candidates=(candidate,),
        created_at=(datetime.now(timezone.utc) - timedelta(seconds=2)).isoformat(),
    )


def test_selection_audit_contract_document_exists():
    assert Path("docs/memory_candidate_selection_audit_contract.md").exists()


def test_successful_selection_emits_created_accepted_prepared_in_order():
    sink = InMemoryMemoryCandidateSelectionAuditSink()
    executor = make_executor(sink)
    request = create_ambiguous_delete(executor)

    result = executor.select_memory_candidate(
        request.id,
        request.candidates[0].memory.id,
    )

    assert result.status == MemoryCommandExecutionStatus.PENDING_CONFIRMATION
    assert result.pending_action is not None
    assert [event.action for event in sink.list_events()] == [
        MemoryCandidateSelectionAuditAction.REQUEST_CREATED,
        MemoryCandidateSelectionAuditAction.CANDIDATE_ACCEPTED,
        MemoryCandidateSelectionAuditAction.PENDING_ACTION_PREPARED,
    ]
    assert executor.selection_service.get_request() is None
    assert executor.pending_service.get_pending() == result.pending_action


def test_invalid_candidate_emits_rejected_event_and_retains_request():
    sink = InMemoryMemoryCandidateSelectionAuditSink()
    executor = make_executor(sink)
    request = create_ambiguous_delete(executor)

    result = executor.select_memory_candidate(request.id, "memory-unknown")

    assert result.status == MemoryCommandExecutionStatus.REJECTED
    assert executor.selection_service.get_request() == request
    assert executor.pending_service.get_pending() is None
    assert sink.list_events()[-1].action == (
        MemoryCandidateSelectionAuditAction.CANDIDATE_REJECTED
    )


def test_active_request_blocks_new_ambiguous_request_and_audits_rejection():
    sink = InMemoryMemoryCandidateSelectionAuditSink()
    executor = make_executor(sink)
    request = create_ambiguous_delete(executor)

    result = executor.execute(
        MemoryCommandParser().parse(
            'korriger minne "SQLite" til "LuciferOS bruker persistent storage"'
        )
    )

    assert result.status == MemoryCommandExecutionStatus.REJECTED
    assert executor.selection_service.get_request() == request
    assert sink.list_events()[-1].action == (
        MemoryCandidateSelectionAuditAction.REQUEST_REJECTED
    )


def test_cancel_audits_then_clears_without_memory_mutation():
    sink = InMemoryMemoryCandidateSelectionAuditSink()
    executor = make_executor(sink)
    request = create_ambiguous_delete(executor)
    contents_before = tuple(item.content for item in executor.memory_service.list_memories())

    result = executor.cancel_memory_candidate_selection()

    assert result.status == MemoryCommandExecutionStatus.CANCELLED_USER_SELECTION
    assert executor.selection_service.get_request() is None
    assert tuple(item.content for item in executor.memory_service.list_memories()) == contents_before
    assert sink.list_events()[-1].action == (
        MemoryCandidateSelectionAuditAction.REQUEST_CANCELLED
    )
    assert request.id == result.selection_request.id


def test_expiry_audits_then_clears_without_pending_action():
    sink = InMemoryMemoryCandidateSelectionAuditSink()
    service = MemoryCandidateSelectionRequestService(
        stale_after_seconds=1,
        audit_delivery_service=MemoryCandidateSelectionAuditDeliveryService(sink),
    )
    request = make_expired_request()
    service.set_request(request)

    result = service.get_request_lifecycle_result()

    assert result.stale is True
    assert service.store.get() is None
    events = sink.list_events()
    assert len(events) == 1
    assert events[0].action == MemoryCandidateSelectionAuditAction.REQUEST_EXPIRED


def test_all_selection_events_exclude_content_and_raw_user_text():
    sink = InMemoryMemoryCandidateSelectionAuditSink()
    executor = make_executor(sink)
    request = create_ambiguous_delete(executor)
    executor.select_memory_candidate(request.id, "memory-unknown")

    for event in sink.list_events():
        assert not hasattr(event, "source_text")
        assert not hasattr(event, "raw_text")
        assert not hasattr(event, "proposed_content")
        assert not hasattr(event, "candidate_content")


def test_selection_audit_events_never_claim_memory_mutation():
    sink = InMemoryMemoryCandidateSelectionAuditSink()
    executor = make_executor(sink)
    request = create_ambiguous_delete(executor)
    executor.select_memory_candidate(request.id, request.candidates[0].memory.id)

    assert all(event.is_memory_mutation_event is False for event in sink.list_events())
