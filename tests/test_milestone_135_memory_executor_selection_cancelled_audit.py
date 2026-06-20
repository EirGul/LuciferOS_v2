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


def test_cancel_active_selection_audits_before_clearing_request():
    sink = InMemoryMemoryCandidateSelectionAuditSink()
    executor = make_executor(sink)
    request = create_ambiguous_delete(executor)

    result = executor.cancel_memory_candidate_selection()

    assert result.status == MemoryCommandExecutionStatus.CANCELLED_USER_SELECTION
    assert result.selection_request == request
    assert executor.selection_service.get_request() is None
    assert executor.pending_service.get_pending() is None

    events = sink.list_events()
    assert [event.action for event in events] == [
        MemoryCandidateSelectionAuditAction.REQUEST_CREATED,
        MemoryCandidateSelectionAuditAction.REQUEST_CANCELLED,
    ]

    cancelled = events[1]
    assert cancelled.source == "memory-command-executor"
    assert cancelled.selection_request_id == request.id
    assert cancelled.command_type.value == "delete"
    assert cancelled.reason == "selection_request_cancelled"
    assert cancelled.selected_memory_id is None
    assert cancelled.pending_action_id is None


def test_cancel_audit_failure_preserves_active_request_and_creates_no_pending_action():
    executor = make_executor(InMemoryMemoryCandidateSelectionAuditSink())
    request = create_ambiguous_delete(executor)
    executor.selection_audit_delivery_service = MemoryCandidateSelectionAuditDeliveryService(
        FailingSelectionAuditSink()
    )

    result = executor.cancel_memory_candidate_selection()

    assert result.status == MemoryCommandExecutionStatus.REJECTED
    assert result.message == "selection_audit_delivery_failed"
    assert result.selection_request == request
    assert executor.selection_service.get_request() == request
    assert executor.pending_service.get_pending() is None


def test_cancel_without_active_selection_emits_no_cancel_audit_event():
    sink = InMemoryMemoryCandidateSelectionAuditSink()
    executor = make_executor(sink)

    result = executor.cancel_memory_candidate_selection()

    assert result.status == MemoryCommandExecutionStatus.REJECTED
    assert result.message == "No active memory candidate selection request to cancel."
    assert sink.list_events() == ()


def test_cancel_audit_event_does_not_include_memory_content_or_user_text():
    sink = InMemoryMemoryCandidateSelectionAuditSink()
    executor = make_executor(sink)
    create_ambiguous_delete(executor)

    executor.cancel_memory_candidate_selection()

    event = sink.list_events()[1]
    assert not hasattr(event, "source_text")
    assert not hasattr(event, "proposed_content")
    assert not hasattr(event, "candidate_content")
    assert not hasattr(event, "raw_text")


def test_cancel_does_not_change_memory_items():
    sink = InMemoryMemoryCandidateSelectionAuditSink()
    executor = make_executor(sink)
    first = "LuciferOS bruker SQLite for memory"
    second = "LuciferOS bruker SQLite for audit"
    add_memory(executor, first)
    add_memory(executor, second)

    waiting = executor.execute(MemoryCommandParser().parse("glem at SQLite"))
    assert waiting.status == MemoryCommandExecutionStatus.AWAITING_USER_SELECTION

    result = executor.cancel_memory_candidate_selection()

    assert result.status == MemoryCommandExecutionStatus.CANCELLED_USER_SELECTION
    assert [item.content for item in executor.memory_service.list_memories()] == [
        first,
        second,
    ]
