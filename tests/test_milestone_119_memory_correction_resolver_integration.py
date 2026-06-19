from lucifer_os.memory import (
    InMemoryMemoryAuditSink,
    InMemoryMemoryStore,
    MemoryCommand,
    MemoryCommandExecutionStatus,
    MemoryCommandExecutor,
    MemoryCommandParser,
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


def test_quoted_correction_with_one_safe_match_creates_pending_action():
    executor, service = make_executor()
    memory = add_memory(service, "LuciferOS bruker SQLite for memory")
    command = MemoryCommandParser().parse(
        'korriger minne "SQLite for memory" til "LuciferOS bruker SQLite som persistent memory store"'
    )
    result = executor.execute(command)
    assert result.status == MemoryCommandExecutionStatus.PENDING_CONFIRMATION
    assert result.pending_action is not None
    assert result.pending_action.action_type == PendingMemoryActionType.CORRECT
    assert result.pending_action.memory_id == memory.id
    assert result.pending_action.proposed_content == "LuciferOS bruker SQLite som persistent memory store"


def test_quoted_correction_with_multiple_matches_awaits_user_selection():
    executor, service = make_executor()
    first = add_memory(service, "LuciferOS bruker SQLite for memory")
    second = add_memory(service, "LuciferOS bruker SQLite for audit")
    command = MemoryCommandParser().parse(
        'korriger minne "SQLite" til "LuciferOS bruker en persistent store"'
    )
    result = executor.execute(command)
    assert result.status == MemoryCommandExecutionStatus.AWAITING_USER_SELECTION
    assert result.pending_action is None
    assert result.memories == (first, second)
    assert executor.pending_service.get_pending() is None


def test_quoted_correction_with_no_match_is_rejected_without_pending_action():
    executor, service = make_executor()
    add_memory(service, "LuciferOS bruker SQLite for memory")
    command = MemoryCommandParser().parse(
        'korriger minne "ukjent ting" til "ny tekst"'
    )
    result = executor.execute(command)
    assert result.status == MemoryCommandExecutionStatus.REJECTED
    assert result.pending_action is None
    assert executor.pending_service.get_pending() is None


def test_correct_with_explicit_memory_id_keeps_existing_pending_flow():
    executor, service = make_executor()
    memory = add_memory(service, "LuciferOS bruker SQLite for memory")
    command = MemoryCommand(
        type=MemoryCommandType.CORRECT,
        raw_text="korriger explicit",
        normalized_text="korriger explicit",
        memory_id=memory.id,
        content="LuciferOS bruker SQLite som persistent memory store",
    )
    result = executor.execute(command)
    assert result.status == MemoryCommandExecutionStatus.PENDING_CONFIRMATION
    assert result.pending_action is not None
    assert result.pending_action.memory_id == memory.id


def test_correction_without_proposed_content_is_rejected_before_resolution():
    executor, service = make_executor()
    add_memory(service, "LuciferOS bruker SQLite for memory")
    command = MemoryCommand(
        type=MemoryCommandType.CORRECT,
        raw_text="korriger minne SQLite for memory",
        normalized_text="korriger minne sqlite for memory",
        query="SQLite for memory",
    )
    result = executor.execute(command)
    assert result.status == MemoryCommandExecutionStatus.REJECTED
    assert result.message == "Correct command requires proposed content."
    assert result.pending_action is None


def test_legacy_correction_without_id_or_query_is_rejected():
    executor, _ = make_executor()
    command = MemoryCommandParser().parse("korriger minne gammel tekst")
    result = executor.execute(command)
    assert result.status == MemoryCommandExecutionStatus.REJECTED
    assert result.message == "Correct command requires an explicit memory id or a target query."
    assert result.pending_action is None
