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


def test_active_selection_rejection_emits_audit_and_preserves_original_request():
    sink = InMemoryMemoryCandidateSelectionAuditSink()
    executor = make_executor(sink)
    active_request = create_ambiguous_delete(executor)

    result = executor.execute(
        MemoryCommandParser().parse(
            'korriger minne "SQLite" til "LuciferOS bruker en persistent store"'
        )
    )

    assert result.status == MemoryCommandExecutionStatus.REJECTED
    assert result.message == (
        "An active memory candidate selection request must be cancelled "
        "or completed before a new selection request is created."
    )
    assert result.selection_request == active_request
    assert executor.selection_service.get_request() == active_request
    assert executor.pending_service.get_pending() is None

    events = sink.list_events()
    assert [event.action for event in events] == [
        MemoryCandidateSelectionAuditAction.REQUEST_CREATED,
        MemoryCandidateSelectionAuditAction.REQUEST_REJECTED,
    ]

    rejected = events[1]
    assert rejected.source == "memory-command-executor"
    assert rejected.selection_request_id == active_request.id
    assert rejected.command_type.value == "correct"
    assert rejected.reason == "active_selection_exists"
    assert rejected.selected_memory_id is None
    assert rejected.pending_action_id is None


def test_active_selection_rejection_audit_failure_preserves_request_and_returns_delivery_failure():
    executor = make_executor(InMemoryMemoryCandidateSelectionAuditSink())
    active_request = create_ambiguous_delete(executor)
    executor.selection_audit_delivery_service = MemoryCandidateSelectionAuditDeliveryService(
        FailingSelectionAuditSink()
    )

    result = executor.execute(
        MemoryCommandParser().parse(
            'korriger minne "SQLite" til "LuciferOS bruker en persistent store"'
        )
    )

    assert result.status == MemoryCommandExecutionStatus.REJECTED
    assert result.message == "selection_audit_delivery_failed"
    assert result.selection_request == active_request
    assert executor.selection_service.get_request() == active_request
    assert executor.pending_service.get_pending() is None


def test_request_rejected_audit_uses_attempted_command_type_not_active_command_type():
    sink = InMemoryMemoryCandidateSelectionAuditSink()
    executor = make_executor(sink)
    active_request = create_ambiguous_delete(executor)

    result = executor.execute(
        MemoryCommandParser().parse(
            'korriger minne "SQLite" til "LuciferOS bruker en persistent store"'
        )
    )

    assert result.status == MemoryCommandExecutionStatus.REJECTED
    event = sink.list_events()[1]
    assert active_request.command_type.value == "delete"
    assert event.command_type.value == "correct"


def test_active_selection_rejection_does_not_change_memory_or_create_new_request():
    sink = InMemoryMemoryCandidateSelectionAuditSink()
    executor = make_executor(sink)
    first = "LuciferOS bruker SQLite for memory"
    second = "LuciferOS bruker SQLite for audit"
    add_memory(executor, first)
    add_memory(executor, second)

    first_result = executor.execute(MemoryCommandParser().parse("glem at SQLite"))
    active_request = first_result.selection_request
    assert active_request is not None

    second_result = executor.execute(
        MemoryCommandParser().parse(
            'korriger minne "SQLite" til "LuciferOS bruker en persistent store"'
        )
    )

    assert second_result.status == MemoryCommandExecutionStatus.REJECTED
    assert second_result.selection_request == active_request
    assert executor.selection_service.get_request() == active_request
    assert [item.content for item in executor.memory_service.list_memories()] == [
        first,
        second,
    ]
    assert executor.pending_service.get_pending() is None


def test_request_rejected_audit_event_does_not_include_content_or_raw_user_text():
    sink = InMemoryMemoryCandidateSelectionAuditSink()
    executor = make_executor(sink)
    create_ambiguous_delete(executor)

    executor.execute(
        MemoryCommandParser().parse(
            'korriger minne "SQLite" til "LuciferOS bruker en persistent store"'
        )
    )

    event = sink.list_events()[1]
    assert not hasattr(event, "source_text")
    assert not hasattr(event, "proposed_content")
    assert not hasattr(event, "candidate_content")
    assert not hasattr(event, "raw_text")
