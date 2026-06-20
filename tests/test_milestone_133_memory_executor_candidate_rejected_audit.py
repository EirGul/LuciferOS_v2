from lucifer_os.memory import (
    InMemoryMemoryCandidateSelectionAuditSink,
    InMemoryMemoryAuditSink,
    InMemoryMemoryStore,
    MemoryCandidateSelectionAuditAction,
    MemoryCandidateSelectionAuditDeliveryService,
    MemoryCandidateSelectionAuditSink,
    MemoryCandidateSelectionRequestService,
    MemoryCommandExecutionStatus,
    MemoryCommandExecutor,
    MemoryCommandParser,
    MemoryPolicy,
    MemoryScope,
    MemoryService,
    MemoryType,
)


class FailingSelectionAuditSink(MemoryCandidateSelectionAuditSink):
    def record(self, event) -> None:
        raise RuntimeError("audit transport unavailable")


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


def test_wrong_request_id_emits_candidate_rejected_audit_event_and_preserves_request():
    sink = InMemoryMemoryCandidateSelectionAuditSink()
    executor = make_executor(sink)
    request = create_ambiguous_delete(executor)

    result = executor.select_memory_candidate(
        "wrong-request-id",
        request.candidates[0].memory.id,
    )

    assert result.status == MemoryCommandExecutionStatus.REJECTED
    assert result.message == "Memory candidate selection request does not match the active request."
    assert result.selection_request == request
    assert executor.selection_service.get_request() == request
    assert executor.pending_service.get_pending() is None

    events = sink.list_events()
    assert len(events) == 2
    event = events[1]
    assert event.action == MemoryCandidateSelectionAuditAction.CANDIDATE_REJECTED
    assert event.selection_request_id == request.id
    assert event.command_type.value == "delete"
    assert event.reason == "selection_request_id_mismatch"
    assert event.selected_memory_id is None
    assert event.pending_action_id is None


def test_wrong_candidate_id_emits_candidate_rejected_audit_event_and_preserves_request():
    sink = InMemoryMemoryCandidateSelectionAuditSink()
    executor = make_executor(sink)
    request = create_ambiguous_delete(executor)

    result = executor.select_memory_candidate(request.id, "memory-unknown")

    assert result.status == MemoryCommandExecutionStatus.REJECTED
    assert result.message == "Selected memory candidate does not belong to this request."
    assert result.selection_request == request
    assert executor.selection_service.get_request() == request
    assert executor.pending_service.get_pending() is None

    events = sink.list_events()
    assert len(events) == 2
    event = events[1]
    assert event.action == MemoryCandidateSelectionAuditAction.CANDIDATE_REJECTED
    assert event.selection_request_id == request.id
    assert event.command_type.value == "delete"
    assert event.reason == "selection_candidate_id_invalid"
    assert event.selected_memory_id is None
    assert event.pending_action_id is None


def test_candidate_rejection_audit_failure_preserves_request_and_returns_delivery_failure():
    executor = make_executor(InMemoryMemoryCandidateSelectionAuditSink())
    request = create_ambiguous_delete(executor)
    executor.selection_audit_delivery_service = MemoryCandidateSelectionAuditDeliveryService(
        FailingSelectionAuditSink()
    )

    result = executor.select_memory_candidate(request.id, "memory-unknown")

    assert result.status == MemoryCommandExecutionStatus.REJECTED
    assert result.message == "selection_audit_delivery_failed"
    assert result.selection_request == request
    assert executor.selection_service.get_request() == request
    assert executor.pending_service.get_pending() is None


def test_request_mismatch_audit_failure_preserves_request_and_returns_delivery_failure():
    executor = make_executor(InMemoryMemoryCandidateSelectionAuditSink())
    request = create_ambiguous_delete(executor)
    executor.selection_audit_delivery_service = MemoryCandidateSelectionAuditDeliveryService(
        FailingSelectionAuditSink()
    )

    result = executor.select_memory_candidate(
        "wrong-request-id",
        request.candidates[0].memory.id,
    )

    assert result.status == MemoryCommandExecutionStatus.REJECTED
    assert result.message == "selection_audit_delivery_failed"
    assert result.selection_request == request
    assert executor.selection_service.get_request() == request
    assert executor.pending_service.get_pending() is None


def test_valid_candidate_selection_does_not_emit_candidate_rejected_event():
    sink = InMemoryMemoryCandidateSelectionAuditSink()
    executor = make_executor(sink)
    request = create_ambiguous_delete(executor)

    result = executor.select_memory_candidate(
        request.id,
        request.candidates[0].memory.id,
    )

    assert result.status == MemoryCommandExecutionStatus.PENDING_CONFIRMATION
    assert all(
        event.action != MemoryCandidateSelectionAuditAction.CANDIDATE_REJECTED
        for event in sink.list_events()
    )


def test_rejection_audit_event_does_not_include_memory_content_or_user_text():
    sink = InMemoryMemoryCandidateSelectionAuditSink()
    executor = make_executor(sink)
    request = create_ambiguous_delete(executor)

    executor.select_memory_candidate(request.id, "memory-unknown")

    event = sink.list_events()[1]
    assert not hasattr(event, "source_text")
    assert not hasattr(event, "proposed_content")
    assert not hasattr(event, "candidate_content")
