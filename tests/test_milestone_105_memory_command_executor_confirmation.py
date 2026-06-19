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
    PendingMemoryAction,
    PendingMemoryActionService,
    PendingMemoryActionType,
)


def make_executor():
    memory_service = MemoryService(store=InMemoryMemoryStore())
    pending_service = PendingMemoryActionService()
    executor = MemoryCommandExecutor(
        memory_service=memory_service,
        pending_service=pending_service,
        default_type=MemoryType.USER_INSTRUCTION,
        default_scope=MemoryScope.GLOBAL,
    )
    return executor, memory_service, pending_service


def test_confirmed_pending_remember_executes_memory_write():
    executor, memory_service, pending_service = make_executor()
    action = PendingMemoryAction(
        action_type=PendingMemoryActionType.REMEMBER,
        command_type=MemoryCommandType.REMEMBER,
        explanation="Store this memory after confirmation.",
        source_text="husk at LuciferOS skal bekrefte high impact minner",
        proposed_content="LuciferOS skal bekrefte high impact minner",
    )
    pending_service.set_pending(action)

    result = executor.execute(MemoryCommandParser().parse("bekreft"))

    assert result.status == MemoryCommandExecutionStatus.CONFIRMED_PENDING
    assert result.operation_result is not None
    assert result.operation_result.item is not None
    assert result.operation_result.item.content == "LuciferOS skal bekrefte high impact minner"
    assert memory_service.list_memories()[0].content == "LuciferOS skal bekrefte high impact minner"


def test_confirmed_pending_correct_executes_memory_update():
    executor, memory_service, pending_service = make_executor()
    stored = memory_service.add_memory(
        content="old content",
        type=MemoryType.PREFERENCE,
        scope=MemoryScope.PROJECT,
        source="test",
        confirmed=True,
    ).item
    assert stored is not None
    action = PendingMemoryAction(
        action_type=PendingMemoryActionType.CORRECT,
        command_type=MemoryCommandType.CORRECT,
        explanation="Correct this memory after confirmation.",
        source_text="korriger minne",
        memory_id=stored.id,
        proposed_content="new content",
    )
    pending_service.set_pending(action)

    result = executor.execute(MemoryCommandParser().parse("bekreft"))

    assert result.status == MemoryCommandExecutionStatus.CONFIRMED_PENDING
    assert result.operation_result is not None
    assert result.operation_result.item is not None
    assert result.operation_result.item.content == "new content"
    assert memory_service.get_memory(stored.id).content == "new content"


def test_confirmed_pending_delete_executes_memory_delete():
    executor, memory_service, pending_service = make_executor()
    stored = memory_service.add_memory(
        content="delete me",
        type=MemoryType.PREFERENCE,
        scope=MemoryScope.PROJECT,
        source="test",
        confirmed=True,
    ).item
    assert stored is not None
    action = PendingMemoryAction(
        action_type=PendingMemoryActionType.DELETE,
        command_type=MemoryCommandType.DELETE,
        explanation="Delete this memory after confirmation.",
        source_text="slett minne",
        memory_id=stored.id,
    )
    pending_service.set_pending(action)

    result = executor.execute(MemoryCommandParser().parse("bekreft"))

    assert result.status == MemoryCommandExecutionStatus.CONFIRMED_PENDING
    assert result.operation_result is not None
    assert result.operation_result.deleted is True
    assert memory_service.get_memory(stored.id) is None


def test_confirm_pending_without_pending_action_does_nothing():
    executor, memory_service, _pending_service = make_executor()

    result = executor.execute(MemoryCommandParser().parse("bekreft"))

    assert result.status == MemoryCommandExecutionStatus.REJECTED
    assert result.operation_result is None
    assert memory_service.list_memories() == []


def test_confirmed_pending_remember_without_content_is_rejected():
    executor, memory_service, pending_service = make_executor()
    action = PendingMemoryAction(
        action_type=PendingMemoryActionType.REMEMBER,
        command_type=MemoryCommandType.REMEMBER,
        explanation="Store this memory after confirmation.",
        source_text="husk at empty",
        proposed_content="   ",
    )
    pending_service.set_pending(action)

    result = executor.execute(MemoryCommandParser().parse("bekreft"))

    assert result.status == MemoryCommandExecutionStatus.REJECTED
    assert result.operation_result is not None
    assert result.operation_result.audit_reason == "Confirmed remember action has no proposed content."
    assert memory_service.list_memories() == []


def test_confirmed_pending_correct_without_memory_id_is_rejected():
    executor, _memory_service, pending_service = make_executor()
    action = PendingMemoryAction(
        action_type=PendingMemoryActionType.CORRECT,
        command_type=MemoryCommandType.CORRECT,
        explanation="Correct this memory after confirmation.",
        source_text="korriger minne",
        proposed_content="new content",
    )
    pending_service.set_pending(action)

    result = executor.execute(MemoryCommandParser().parse("bekreft"))

    assert result.status == MemoryCommandExecutionStatus.REJECTED
    assert result.operation_result is not None
    assert result.operation_result.audit_reason == "Confirmed correction action has no memory id."


def test_confirmed_pending_delete_without_memory_id_is_rejected():
    executor, _memory_service, pending_service = make_executor()
    action = PendingMemoryAction(
        action_type=PendingMemoryActionType.DELETE,
        command_type=MemoryCommandType.DELETE,
        explanation="Delete this memory after confirmation.",
        source_text="slett minne",
    )
    pending_service.set_pending(action)

    result = executor.execute(MemoryCommandParser().parse("bekreft"))

    assert result.status == MemoryCommandExecutionStatus.REJECTED
    assert result.operation_result is not None
    assert result.operation_result.audit_reason == "Confirmed delete action has no memory id."


def test_cancel_pending_still_does_not_execute_memory_operation():
    executor, memory_service, pending_service = make_executor()
    action = PendingMemoryAction(
        action_type=PendingMemoryActionType.REMEMBER,
        command_type=MemoryCommandType.REMEMBER,
        explanation="Store this memory after confirmation.",
        source_text="husk at cancelled",
        proposed_content="cancelled",
    )
    pending_service.set_pending(action)

    result = executor.execute(MemoryCommandParser().parse("avbryt"))

    assert result.status == MemoryCommandExecutionStatus.CANCELLED_PENDING
    assert result.operation_result is None
    assert memory_service.list_memories() == []
