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
    return executor.execute(MemoryCommandParser().parse("glem at SQLite"))


def test_created_selection_request_emits_minimal_audit_event_before_storage():
    sink = InMemoryMemoryCandidateSelectionAuditSink()
    executor = make_executor(sink)

    result = create_ambiguous_delete(executor)

    assert result.status == MemoryCommandExecutionStatus.AWAITING_USER_SELECTION
    assert result.selection_request is not None
    assert executor.selection_service.get_request() == result.selection_request

    events = sink.list_events()
    assert len(events) == 1
    event = events[0]
    assert event.action == MemoryCandidateSelectionAuditAction.REQUEST_CREATED
    assert event.source == "memory-command-executor"
    assert event.selection_request_id == result.selection_request.id
    assert event.command_type.value == "delete"
    assert event.reason == "ambiguous_target"
    assert event.selected_memory_id is None
    assert event.pending_action_id is None


def test_created_correction_selection_audits_command_type_without_content():
    sink = InMemoryMemoryCandidateSelectionAuditSink()
    executor = make_executor(sink)
    add_memory(executor, "LuciferOS bruker SQLite for memory")
    add_memory(executor, "LuciferOS bruker SQLite for audit")

    result = executor.execute(
        MemoryCommandParser().parse(
            'korriger minne "SQLite" til "LuciferOS bruker en persistent store"'
        )
    )

    assert result.status == MemoryCommandExecutionStatus.AWAITING_USER_SELECTION
    event = sink.list_events()[0]
    assert event.command_type.value == "correct"
    assert event.reason == "ambiguous_target"
    assert not hasattr(event, "source_text")
    assert not hasattr(event, "proposed_content")


def test_created_selection_audit_failure_prevents_request_storage():
    executor = make_executor(FailingSelectionAuditSink())

    result = create_ambiguous_delete(executor)

    assert result.status == MemoryCommandExecutionStatus.REJECTED
    assert result.message == "selection_audit_delivery_failed"
    assert result.selection_request is None
    assert executor.selection_service.get_request() is None
    assert executor.pending_service.get_pending() is None


def test_created_selection_audit_failure_does_not_change_memory():
    executor = make_executor(FailingSelectionAuditSink())
    add_memory(executor, "LuciferOS bruker SQLite for memory")
    add_memory(executor, "LuciferOS bruker SQLite for audit")

    result = executor.execute(MemoryCommandParser().parse("glem at SQLite"))

    assert result.status == MemoryCommandExecutionStatus.REJECTED
    assert [item.content for item in executor.memory_service.list_memories()] == [
        "LuciferOS bruker SQLite for memory",
        "LuciferOS bruker SQLite for audit",
    ]


def test_unambiguous_target_does_not_emit_created_selection_audit_event():
    sink = InMemoryMemoryCandidateSelectionAuditSink()
    executor = make_executor(sink)
    add_memory(executor, "LuciferOS bruker SQLite for memory")

    result = executor.execute(MemoryCommandParser().parse("glem at SQLite"))

    assert result.status == MemoryCommandExecutionStatus.PENDING_CONFIRMATION
    assert sink.list_events() == ()


def test_created_selection_audit_types_remain_local_memory_exports():
    import lucifer_os.memory as memory

    assert (
        memory.MemoryCandidateSelectionAuditDeliveryService
        is MemoryCandidateSelectionAuditDeliveryService
    )
    assert memory.MemoryCandidateSelectionAuditAction is MemoryCandidateSelectionAuditAction
