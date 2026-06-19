from lucifer_os.memory import (
    InMemoryMemoryAuditSink,
    InMemoryMemoryStore,
    MemoryCommand,
    MemoryCommandExecutionStatus,
    MemoryCommandExecutor,
    MemoryCommandType,
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
    return MemoryCommandExecutor(memory_service=service, max_results=10), service


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


def test_delete_query_with_one_safe_match_creates_pending_action():
    executor, service = make_executor()
    memory = add_memory(service, "LuciferOS bruker SQLite for memory")
    command = MemoryCommand(
        type=MemoryCommandType.DELETE,
        raw_text="glem at SQLite for memory",
        normalized_text="glem at sqlite for memory",
        query="SQLite for memory",
    )
    result = executor.execute(command)
    assert result.status == MemoryCommandExecutionStatus.PENDING_CONFIRMATION
    assert result.pending_action is not None
    assert result.pending_action.action_type == PendingMemoryActionType.DELETE
    assert result.pending_action.memory_id == memory.id


def test_delete_query_with_multiple_matches_awaits_user_selection():
    executor, service = make_executor()
    first = add_memory(service, "LuciferOS bruker SQLite for memory")
    second = add_memory(service, "LuciferOS bruker SQLite for audit")
    command = MemoryCommand(
        type=MemoryCommandType.DELETE,
        raw_text="glem at SQLite",
        normalized_text="glem at sqlite",
        query="SQLite",
    )
    result = executor.execute(command)
    assert result.status == MemoryCommandExecutionStatus.AWAITING_USER_SELECTION
    assert result.pending_action is None
    assert result.memories == (first, second)
    assert executor.pending_service.get_pending() is None


def test_delete_query_with_no_match_is_rejected_without_pending_action():
    executor, service = make_executor()
    add_memory(service, "LuciferOS bruker SQLite for memory")
    command = MemoryCommand(
        type=MemoryCommandType.DELETE,
        raw_text="glem at ukjent ting",
        normalized_text="glem at ukjent ting",
        query="ukjent ting",
    )
    result = executor.execute(command)
    assert result.status == MemoryCommandExecutionStatus.REJECTED
    assert result.pending_action is None
    assert executor.pending_service.get_pending() is None


def test_delete_with_explicit_memory_id_keeps_existing_pending_flow():
    executor, service = make_executor()
    memory = add_memory(service, "LuciferOS bruker SQLite for memory")
    command = MemoryCommand(
        type=MemoryCommandType.DELETE,
        raw_text="slett minne explicit",
        normalized_text="slett minne explicit",
        memory_id=memory.id,
    )
    result = executor.execute(command)
    assert result.status == MemoryCommandExecutionStatus.PENDING_CONFIRMATION
    assert result.pending_action is not None
    assert result.pending_action.memory_id == memory.id


def test_delete_without_id_or_query_is_rejected():
    executor, _ = make_executor()
    command = MemoryCommand(
        type=MemoryCommandType.DELETE,
        raw_text="slett minne",
        normalized_text="slett minne",
    )
    result = executor.execute(command)
    assert result.status == MemoryCommandExecutionStatus.REJECTED
    assert result.pending_action is None
