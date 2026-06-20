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
    PendingMemoryActionType,
)


def make_executor():
    store = InMemoryMemoryStore()
    audit = InMemoryMemoryAuditSink()
    service = MemoryService(store=store, policy=MemoryPolicy(), audit_sink=audit)
    selection_service = MemoryCandidateSelectionRequestService()
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


def test_delete_multiple_match_creates_active_selection_request():
    executor, service, selection_service = make_executor()
    first = add_memory(service, "LuciferOS bruker SQLite for memory")
    second = add_memory(service, "LuciferOS bruker SQLite for audit")

    result = executor.execute(MemoryCommandParser().parse("glem at SQLite"))

    assert result.status == MemoryCommandExecutionStatus.AWAITING_USER_SELECTION
    assert result.selection_request is not None
    assert result.selection_request.command_type.value == "delete"
    assert result.selection_request.proposed_content is None
    assert result.selection_request.candidates[0].memory == first
    assert result.selection_request.candidates[1].memory == second
    assert selection_service.get_request() == result.selection_request
    assert executor.pending_service.get_pending() is None


def test_valid_delete_selection_creates_pending_action_but_does_not_delete():
    executor, service, selection_service = make_executor()
    first = add_memory(service, "LuciferOS bruker SQLite for memory")
    second = add_memory(service, "LuciferOS bruker SQLite for audit")

    waiting = executor.execute(MemoryCommandParser().parse("glem at SQLite"))
    request = waiting.selection_request
    assert request is not None

    result = executor.select_memory_candidate(request.id, second.id)

    assert result.status == MemoryCommandExecutionStatus.PENDING_CONFIRMATION
    assert result.pending_action is not None
    assert result.pending_action.action_type == PendingMemoryActionType.DELETE
    assert result.pending_action.memory_id == second.id
    assert selection_service.get_request() is None
    assert executor.pending_service.get_pending() == result.pending_action
    assert second in service.list_memories()
    assert first in service.list_memories()


def test_valid_correction_selection_preserves_proposed_content():
    executor, service, selection_service = make_executor()
    first = add_memory(service, "LuciferOS bruker SQLite for memory")
    second = add_memory(service, "LuciferOS bruker SQLite for audit")

    waiting = executor.execute(
        MemoryCommandParser().parse(
            'korriger minne "SQLite" til "LuciferOS bruker en persistent store"'
        )
    )
    request = waiting.selection_request
    assert request is not None
    assert request.proposed_content == "LuciferOS bruker en persistent store"

    result = executor.select_memory_candidate(request.id, first.id)

    assert result.status == MemoryCommandExecutionStatus.PENDING_CONFIRMATION
    assert result.pending_action is not None
    assert result.pending_action.action_type == PendingMemoryActionType.CORRECT
    assert result.pending_action.memory_id == first.id
    assert result.pending_action.proposed_content == "LuciferOS bruker en persistent store"
    assert selection_service.get_request() is None
    assert first in service.list_memories()
    assert second in service.list_memories()


def test_invalid_candidate_selection_keeps_request_and_creates_no_pending_action():
    executor, service, selection_service = make_executor()
    add_memory(service, "LuciferOS bruker SQLite for memory")
    add_memory(service, "LuciferOS bruker SQLite for audit")

    waiting = executor.execute(MemoryCommandParser().parse("glem at SQLite"))
    request = waiting.selection_request
    assert request is not None

    result = executor.select_memory_candidate(request.id, "memory-unknown")

    assert result.status == MemoryCommandExecutionStatus.REJECTED
    assert result.pending_action is None
    assert result.selection_request == request
    assert selection_service.get_request() == request
    assert executor.pending_service.get_pending() is None


def test_wrong_selection_request_id_creates_no_pending_action_and_keeps_active_request():
    executor, service, selection_service = make_executor()
    memory = add_memory(service, "LuciferOS bruker SQLite for memory")
    add_memory(service, "LuciferOS bruker SQLite for audit")

    waiting = executor.execute(MemoryCommandParser().parse("glem at SQLite"))
    request = waiting.selection_request
    assert request is not None

    result = executor.select_memory_candidate("wrong-request-id", memory.id)

    assert result.status == MemoryCommandExecutionStatus.REJECTED
    assert result.pending_action is None
    assert selection_service.get_request() == request
    assert executor.pending_service.get_pending() is None


def test_selection_cannot_create_two_pending_actions():
    executor, service, selection_service = make_executor()
    first = add_memory(service, "LuciferOS bruker SQLite for memory")
    second = add_memory(service, "LuciferOS bruker SQLite for audit")

    waiting = executor.execute(MemoryCommandParser().parse("glem at SQLite"))
    request = waiting.selection_request
    assert request is not None

    first_result = executor.select_memory_candidate(request.id, first.id)
    second_result = executor.select_memory_candidate(request.id, second.id)

    assert first_result.status == MemoryCommandExecutionStatus.PENDING_CONFIRMATION
    assert second_result.status == MemoryCommandExecutionStatus.REJECTED
    assert executor.pending_service.get_pending() == first_result.pending_action
    assert selection_service.get_request() is None


def test_new_selection_request_does_not_silently_replace_previous_active_request():
    executor, service, selection_service = make_executor()
    add_memory(service, "LuciferOS bruker SQLite for memory")
    add_memory(service, "LuciferOS bruker SQLite for audit")

    first_waiting = executor.execute(MemoryCommandParser().parse("glem at SQLite"))
    second_waiting = executor.execute(
        MemoryCommandParser().parse(
            'korriger minne "SQLite" til "LuciferOS bruker en persistent store"'
        )
    )

    assert first_waiting.selection_request is not None
    assert second_waiting.status == MemoryCommandExecutionStatus.REJECTED
    assert second_waiting.selection_request == first_waiting.selection_request
    assert selection_service.get_request() == first_waiting.selection_request
    assert executor.pending_service.get_pending() is None


def test_selection_service_types_are_public_memory_exports():
    import lucifer_os.memory as memory

    assert memory.MemoryCandidateSelectionRequestService is MemoryCandidateSelectionRequestService
