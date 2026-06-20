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
    PendingMemoryActionType,
)


class FailingSelectionAuditSink(MemoryCandidateSelectionAuditSink):
    def record(self, event) -> None:
        raise RuntimeError("audit transport unavailable")


class FailOnActionSelectionAuditSink(MemoryCandidateSelectionAuditSink):
    def __init__(self, failing_action):
        self.failing_action = failing_action
        self.events = []

    def record(self, event) -> None:
        if event.action == self.failing_action:
            raise RuntimeError("audit transport unavailable")
        self.events.append(event)

    def list_events(self):
        return tuple(self.events)


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


def create_ambiguous_correct(executor):
    add_memory(executor, "LuciferOS bruker SQLite for memory")
    add_memory(executor, "LuciferOS bruker SQLite for audit")
    result = executor.execute(
        MemoryCommandParser().parse(
            'korriger minne "SQLite" til "LuciferOS bruker en persistent store"'
        )
    )
    assert result.status == MemoryCommandExecutionStatus.AWAITING_USER_SELECTION
    assert result.selection_request is not None
    return result.selection_request


def test_valid_delete_selection_audits_accepted_then_pending_prepared_before_state_change():
    sink = InMemoryMemoryCandidateSelectionAuditSink()
    executor = make_executor(sink)
    request = create_ambiguous_delete(executor)
    selected_id = request.candidates[1].memory.id

    result = executor.select_memory_candidate(request.id, selected_id)

    assert result.status == MemoryCommandExecutionStatus.PENDING_CONFIRMATION
    assert result.pending_action is not None
    assert result.pending_action.action_type == PendingMemoryActionType.DELETE
    assert result.pending_action.memory_id == selected_id
    assert executor.selection_service.get_request() is None
    assert executor.pending_service.get_pending() == result.pending_action

    events = sink.list_events()
    assert [event.action for event in events] == [
        MemoryCandidateSelectionAuditAction.REQUEST_CREATED,
        MemoryCandidateSelectionAuditAction.CANDIDATE_ACCEPTED,
        MemoryCandidateSelectionAuditAction.PENDING_ACTION_PREPARED,
    ]

    accepted = events[1]
    prepared = events[2]
    assert accepted.selection_request_id == request.id
    assert accepted.selected_memory_id == selected_id
    assert accepted.pending_action_id is None
    assert accepted.reason == "selection_candidate_valid"
    assert prepared.selection_request_id == request.id
    assert prepared.selected_memory_id == selected_id
    assert prepared.pending_action_id == result.pending_action.id
    assert prepared.reason == "selection_pending_action_prepared"


def test_valid_correct_selection_preserves_content_without_auditing_content():
    sink = InMemoryMemoryCandidateSelectionAuditSink()
    executor = make_executor(sink)
    request = create_ambiguous_correct(executor)
    selected_id = request.candidates[0].memory.id

    result = executor.select_memory_candidate(request.id, selected_id)

    assert result.status == MemoryCommandExecutionStatus.PENDING_CONFIRMATION
    assert result.pending_action is not None
    assert result.pending_action.action_type == PendingMemoryActionType.CORRECT
    assert result.pending_action.proposed_content == "LuciferOS bruker en persistent store"

    for event in sink.list_events():
        assert not hasattr(event, "source_text")
        assert not hasattr(event, "proposed_content")
        assert not hasattr(event, "candidate_content")


def test_accepted_audit_failure_preserves_request_and_creates_no_pending_action():
    executor = make_executor(InMemoryMemoryCandidateSelectionAuditSink())
    request = create_ambiguous_delete(executor)
    executor.selection_audit_delivery_service = MemoryCandidateSelectionAuditDeliveryService(
        FailingSelectionAuditSink()
    )

    result = executor.select_memory_candidate(
        request.id,
        request.candidates[0].memory.id,
    )

    assert result.status == MemoryCommandExecutionStatus.REJECTED
    assert result.message == "selection_audit_delivery_failed"
    assert result.selection_request == request
    assert executor.selection_service.get_request() == request
    assert executor.pending_service.get_pending() is None


def test_prepared_audit_failure_preserves_request_and_creates_no_pending_action():
    executor = make_executor(InMemoryMemoryCandidateSelectionAuditSink())
    request = create_ambiguous_delete(executor)
    selective_sink = FailOnActionSelectionAuditSink(
        MemoryCandidateSelectionAuditAction.PENDING_ACTION_PREPARED
    )
    executor.selection_audit_delivery_service = MemoryCandidateSelectionAuditDeliveryService(
        selective_sink
    )

    result = executor.select_memory_candidate(
        request.id,
        request.candidates[0].memory.id,
    )

    assert result.status == MemoryCommandExecutionStatus.REJECTED
    assert result.message == "selection_audit_delivery_failed"
    assert result.selection_request == request
    assert executor.selection_service.get_request() == request
    assert executor.pending_service.get_pending() is None
    assert [event.action for event in selective_sink.list_events()] == [
        MemoryCandidateSelectionAuditAction.CANDIDATE_ACCEPTED,
    ]


def test_valid_selection_never_emits_candidate_rejected_event():
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


def test_accepted_and_prepared_events_use_only_minimal_identifiers():
    sink = InMemoryMemoryCandidateSelectionAuditSink()
    executor = make_executor(sink)
    request = create_ambiguous_delete(executor)

    result = executor.select_memory_candidate(
        request.id,
        request.candidates[0].memory.id,
    )
    assert result.pending_action is not None

    accepted, prepared = sink.list_events()[1:]

    assert accepted.source == "memory-command-executor"
    assert prepared.source == "memory-command-executor"
    assert accepted.command_type.value == "delete"
    assert prepared.command_type.value == "delete"
    assert not hasattr(accepted, "raw_text")
    assert not hasattr(prepared, "raw_text")
