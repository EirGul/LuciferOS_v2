from datetime import datetime, timedelta, timezone

from lucifer_os.memory import (
    InMemoryMemoryCandidateSelectionAuditSink,
    InMemoryMemoryAuditSink,
    InMemoryMemoryStore,
    MemoryCandidateSelectionAuditAction,
    MemoryCandidateSelectionAuditDeliveryService,
    MemoryCandidateSelectionAuditSink,
    MemoryCandidateSelectionRequest,
    MemoryCandidateSelectionRequestService,
    MemoryCommandExecutionStatus,
    MemoryCommandExecutor,
    MemoryCommandParser,
    MemoryCommandType,
    MemoryItem,
    MemoryPolicy,
    MemoryScope,
    MemoryService,
    MemoryTargetCandidate,
    MemoryType,
)


class FailingSelectionAuditSink(MemoryCandidateSelectionAuditSink):
    def record(self, event) -> None:
        raise RuntimeError("audit transport unavailable")


def make_candidate(id="memory-1"):
    return MemoryTargetCandidate(
        memory=MemoryItem(
            id=id,
            content="LuciferOS bruker SQLite",
            type=MemoryType.PREFERENCE,
            scope=MemoryScope.PROJECT,
            source="test",
        ),
        reason="test",
    )


def make_expired_request():
    return MemoryCandidateSelectionRequest(
        command_type=MemoryCommandType.DELETE,
        source_text="glem at SQLite",
        candidates=(make_candidate(),),
        created_at=(datetime.now(timezone.utc) - timedelta(seconds=2)).isoformat(),
    )


def make_service(sink, stale_after_seconds=1):
    return MemoryCandidateSelectionRequestService(
        stale_after_seconds=stale_after_seconds,
        audit_delivery_service=MemoryCandidateSelectionAuditDeliveryService(sink),
    )


def make_executor(selection_service):
    memory_service = MemoryService(
        store=InMemoryMemoryStore(),
        policy=MemoryPolicy(),
        audit_sink=InMemoryMemoryAuditSink(),
    )
    return MemoryCommandExecutor(
        memory_service=memory_service,
        selection_service=selection_service,
    )


def test_expiry_delivers_minimal_audit_event_before_clearing_request():
    sink = InMemoryMemoryCandidateSelectionAuditSink()
    service = make_service(sink)
    request = make_expired_request()
    service.set_request(request)

    result = service.get_request_lifecycle_result()

    assert result.stale is True
    assert result.audit_delivery_failed is False
    assert service.store.get() is None
    events = sink.list_events()
    assert len(events) == 1
    event = events[0]
    assert event.action == MemoryCandidateSelectionAuditAction.REQUEST_EXPIRED
    assert event.selection_request_id == request.id
    assert event.command_type == MemoryCommandType.DELETE
    assert event.reason == "selection_request_stale"
    assert event.selected_memory_id is None
    assert event.pending_action_id is None


def test_expiry_audit_failure_keeps_request_and_reports_blocked_result():
    service = make_service(FailingSelectionAuditSink())
    request = make_expired_request()
    service.set_request(request)

    result = service.get_request_lifecycle_result()

    assert result.stale is False
    assert result.audit_delivery_failed is True
    assert result.request == request
    assert result.reason == "selection_audit_delivery_failed"
    assert service.store.get() == request
    assert service.get_request() is None


def test_repeated_expiry_audit_failure_never_clears_request():
    service = make_service(FailingSelectionAuditSink())
    request = make_expired_request()
    service.set_request(request)

    first = service.get_request_lifecycle_result()
    second = service.get_request_lifecycle_result()

    assert first.audit_delivery_failed is True
    assert second.audit_delivery_failed is True
    assert service.store.get() == request


def test_audit_failure_blocks_candidate_selection_and_creates_no_pending_action():
    selection_service = make_service(FailingSelectionAuditSink())
    request = make_expired_request()
    selection_service.set_request(request)
    executor = make_executor(selection_service)

    result = executor.select_memory_candidate(
        request.id,
        request.candidates[0].memory.id,
    )

    assert result.status == MemoryCommandExecutionStatus.REJECTED
    assert result.message == "selection_audit_delivery_failed"
    assert result.selection_request == request
    assert executor.pending_service.get_pending() is None
    assert selection_service.store.get() == request


def test_audit_failure_blocks_cancel_and_preserves_request():
    selection_service = make_service(FailingSelectionAuditSink())
    request = make_expired_request()
    selection_service.set_request(request)
    executor = make_executor(selection_service)

    result = executor.cancel_memory_candidate_selection()

    assert result.status == MemoryCommandExecutionStatus.REJECTED
    assert result.message == "selection_audit_delivery_failed"
    assert result.selection_request == request
    assert selection_service.store.get() == request


def test_audit_failure_blocks_new_ambiguous_selection_and_preserves_request():
    selection_service = make_service(FailingSelectionAuditSink())
    request = make_expired_request()
    selection_service.set_request(request)
    executor = make_executor(selection_service)

    for content in (
        "LuciferOS bruker SQLite for memory",
        "LuciferOS bruker SQLite for audit",
    ):
        added = executor.memory_service.add_memory(
            content=content,
            type=MemoryType.PREFERENCE,
            scope=MemoryScope.PROJECT,
            source="test",
            confirmed=True,
        )
        assert added.allowed is True

    result = executor.execute(
        MemoryCommandParser().parse('korriger minne "SQLite" til "persistent store"')
    )

    assert result.status == MemoryCommandExecutionStatus.REJECTED
    assert result.message == "selection_audit_delivery_failed"
    assert result.selection_request == request
    assert selection_service.store.get() == request
    assert executor.pending_service.get_pending() is None


def test_lifecycle_result_requires_reason_when_audit_delivery_failed():
    try:
        from lucifer_os.memory import MemoryCandidateSelectionRequestLifecycleResult

        MemoryCandidateSelectionRequestLifecycleResult(
            cancelled=False,
            stale=False,
            audit_delivery_failed=True,
        )
    except ValueError as error:
        assert "requires a reason" in str(error)
    else:
        raise AssertionError("Expected ValueError for blocked lifecycle result without reason.")


def test_expiry_audit_types_remain_local_memory_exports():
    import lucifer_os.memory as memory

    assert (
        memory.MemoryCandidateSelectionAuditDeliveryService
        is MemoryCandidateSelectionAuditDeliveryService
    )
    assert (
        memory.MemoryCandidateSelectionRequestService
        is MemoryCandidateSelectionRequestService
    )
