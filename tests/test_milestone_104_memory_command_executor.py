from lucifer_os.memory import (
    InMemoryMemoryStore,
    MemoryCommand,
    MemoryCommandExecutionStatus,
    MemoryCommandExecutor,
    MemoryCommandParser,
    MemoryCommandType,
    MemoryScope,
    MemoryService,
    MemoryType,
    PendingMemoryActionService,
)


def make_executor(max_results=20):
    memory_service = MemoryService(store=InMemoryMemoryStore())
    pending_service = PendingMemoryActionService()
    return MemoryCommandExecutor(
        memory_service=memory_service,
        pending_service=pending_service,
        default_type=MemoryType.PREFERENCE,
        default_scope=MemoryScope.PROJECT,
        max_results=max_results,
    )


def test_memory_command_executor_stores_low_impact_remember_command():
    executor = make_executor()
    command = MemoryCommandParser().parse("husk at LuciferOS skal svare kort med tale")

    result = executor.execute(command)

    assert result.status == MemoryCommandExecutionStatus.EXECUTED
    assert result.operation_result is not None
    assert result.operation_result.item is not None
    assert result.operation_result.item.content == "LuciferOS skal svare kort med tale"


def test_memory_command_executor_rejects_empty_remember_command():
    executor = make_executor()
    command = MemoryCommand(
        type=MemoryCommandType.REMEMBER,
        raw_text="husk at",
        normalized_text="husk at",
        content="   ",
    )

    result = executor.execute(command)

    assert result.status == MemoryCommandExecutionStatus.REJECTED
    assert result.message == "Remember command has no content."


def test_memory_command_executor_lists_memories_with_bound():
    executor = make_executor(max_results=2)
    parser = MemoryCommandParser()

    executor.execute(parser.parse("husk at first"))
    executor.execute(parser.parse("husk at second"))
    executor.execute(parser.parse("husk at third"))

    result = executor.execute(parser.parse("vis minner"))

    assert result.status == MemoryCommandExecutionStatus.EXECUTED
    assert len(result.memories) == 2


def test_memory_command_executor_searches_memories_with_bound():
    executor = make_executor(max_results=1)
    parser = MemoryCommandParser()

    executor.execute(parser.parse("husk at LuciferOS bruker SQLite"))
    executor.execute(parser.parse("husk at LuciferOS har HUD"))
    executor.execute(parser.parse("husk at annet prosjekt"))

    result = executor.execute(parser.parse("hva husker du om LuciferOS"))

    assert result.status == MemoryCommandExecutionStatus.EXECUTED
    assert len(result.memories) == 1
    assert "LuciferOS" in result.memories[0].content


def test_memory_command_executor_rejects_correct_without_memory_id():
    executor = make_executor()
    command = MemoryCommandParser().parse("korriger minne LuciferOS skal bruke SQLite")

    result = executor.execute(command)

    assert result.status == MemoryCommandExecutionStatus.REJECTED
    assert result.message == "Correct command requires an explicit memory id or a target query."


def test_memory_command_executor_prepares_correct_with_memory_id_as_pending_action():
    executor = make_executor()
    command = MemoryCommand(
        type=MemoryCommandType.CORRECT,
        raw_text="korriger minne memory-1",
        normalized_text="korriger minne memory-1",
        memory_id="memory-1",
        content="Corrected content",
    )

    result = executor.execute(command)

    assert result.status == MemoryCommandExecutionStatus.PENDING_CONFIRMATION
    assert result.pending_action is not None
    assert result.pending_action.memory_id == "memory-1"
    assert result.pending_action.proposed_content == "Corrected content"


def test_memory_command_executor_rejects_delete_without_memory_id():
    executor = make_executor()
    command = MemoryCommandParser().parse("glem at gammelt minne")

    result = executor.execute(command)

    assert result.status == MemoryCommandExecutionStatus.REJECTED
    assert result.message == "No matching memory target was found."


def test_memory_command_executor_prepares_delete_with_memory_id_as_pending_action():
    executor = make_executor()
    command = MemoryCommand(
        type=MemoryCommandType.DELETE,
        raw_text="slett minne memory-1",
        normalized_text="slett minne memory-1",
        memory_id="memory-1",
    )

    result = executor.execute(command)

    assert result.status == MemoryCommandExecutionStatus.PENDING_CONFIRMATION
    assert result.pending_action is not None
    assert result.pending_action.memory_id == "memory-1"


def test_memory_command_executor_confirms_and_cancels_pending_without_runtime_side_effects():
    executor = make_executor()
    delete_command = MemoryCommand(
        type=MemoryCommandType.DELETE,
        raw_text="slett minne memory-1",
        normalized_text="slett minne memory-1",
        memory_id="memory-1",
    )

    executor.execute(delete_command)
    confirm_result = executor.execute(MemoryCommandParser().parse("bekreft"))

    assert confirm_result.status == MemoryCommandExecutionStatus.CONFIRMED_PENDING
    assert confirm_result.pending_action is not None
    assert confirm_result.pending_action.memory_id == "memory-1"

    cancel_result = executor.execute(MemoryCommandParser().parse("avbryt"))

    assert cancel_result.status == MemoryCommandExecutionStatus.REJECTED
    assert cancel_result.confirmation_result is not None
    assert cancel_result.confirmation_result.action is None


def test_memory_command_executor_handles_not_memory_command():
    executor = make_executor()
    command = MemoryCommandParser().parse("dette er vanlig samtale")

    result = executor.execute(command)

    assert result.status == MemoryCommandExecutionStatus.NOT_MEMORY_COMMAND


def test_memory_command_executor_exports_are_public():
    import lucifer_os.memory as memory

    assert memory.MemoryCommandExecutor is MemoryCommandExecutor
    assert memory.MemoryCommandExecutionStatus is MemoryCommandExecutionStatus
