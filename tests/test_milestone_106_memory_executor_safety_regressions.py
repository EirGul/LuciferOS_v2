from datetime import datetime, timedelta, timezone

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


def make_executor(stale_after_seconds=300):
    memory_service = MemoryService(store=InMemoryMemoryStore())
    pending_service = PendingMemoryActionService(stale_after_seconds=stale_after_seconds)
    executor = MemoryCommandExecutor(
        memory_service=memory_service,
        pending_service=pending_service,
        default_type=MemoryType.USER_INSTRUCTION,
        default_scope=MemoryScope.GLOBAL,
    )
    return executor, memory_service, pending_service


def test_confirm_cannot_execute_same_pending_action_twice():
    executor, memory_service, pending_service = make_executor()
    action = PendingMemoryAction(
        action_type=PendingMemoryActionType.REMEMBER,
        command_type=MemoryCommandType.REMEMBER,
        explanation="Store this memory after confirmation.",
        source_text="husk at only once",
        proposed_content="only once",
    )
    pending_service.set_pending(action)

    first = executor.execute(MemoryCommandParser().parse("bekreft"))
    second = executor.execute(MemoryCommandParser().parse("bekreft"))

    assert first.status == MemoryCommandExecutionStatus.CONFIRMED_PENDING
    assert second.status == MemoryCommandExecutionStatus.REJECTED
    assert len(memory_service.list_memories()) == 1
    assert memory_service.list_memories()[0].content == "only once"


def test_stale_pending_action_executes_nothing():
    executor, memory_service, pending_service = make_executor(stale_after_seconds=1)
    old_time = datetime.now(timezone.utc) - timedelta(seconds=10)
    action = PendingMemoryAction(
        action_type=PendingMemoryActionType.REMEMBER,
        command_type=MemoryCommandType.REMEMBER,
        explanation="Store stale memory after confirmation.",
        source_text="husk at stale",
        proposed_content="stale",
        created_at=old_time.isoformat(),
    )
    pending_service.set_pending(action)

    result = executor.execute(MemoryCommandParser().parse("bekreft"))

    assert result.status == MemoryCommandExecutionStatus.REJECTED
    assert result.confirmation_result is not None
    assert result.confirmation_result.stale is True
    assert result.operation_result is None
    assert memory_service.list_memories() == []


def test_cancel_after_confirm_executes_nothing():
    executor, memory_service, pending_service = make_executor()
    action = PendingMemoryAction(
        action_type=PendingMemoryActionType.REMEMBER,
        command_type=MemoryCommandType.REMEMBER,
        explanation="Store memory after confirmation.",
        source_text="husk at confirmed",
        proposed_content="confirmed",
    )
    pending_service.set_pending(action)

    confirm_result = executor.execute(MemoryCommandParser().parse("bekreft"))
    cancel_result = executor.execute(MemoryCommandParser().parse("avbryt"))

    assert confirm_result.status == MemoryCommandExecutionStatus.CONFIRMED_PENDING
    assert cancel_result.status == MemoryCommandExecutionStatus.REJECTED
    assert cancel_result.operation_result is None
    assert len(memory_service.list_memories()) == 1


def test_confirm_after_cancel_executes_nothing():
    executor, memory_service, pending_service = make_executor()
    action = PendingMemoryAction(
        action_type=PendingMemoryActionType.REMEMBER,
        command_type=MemoryCommandType.REMEMBER,
        explanation="Store memory after confirmation.",
        source_text="husk at cancelled",
        proposed_content="cancelled",
    )
    pending_service.set_pending(action)

    cancel_result = executor.execute(MemoryCommandParser().parse("avbryt"))
    confirm_result = executor.execute(MemoryCommandParser().parse("bekreft"))

    assert cancel_result.status == MemoryCommandExecutionStatus.CANCELLED_PENDING
    assert confirm_result.status == MemoryCommandExecutionStatus.REJECTED
    assert confirm_result.operation_result is None
    assert memory_service.list_memories() == []


def test_delete_unknown_memory_id_does_not_report_deleted_success():
    executor, memory_service, pending_service = make_executor()
    action = PendingMemoryAction(
        action_type=PendingMemoryActionType.DELETE,
        command_type=MemoryCommandType.DELETE,
        explanation="Delete unknown memory after confirmation.",
        source_text="slett minne unknown-memory",
        memory_id="unknown-memory",
    )
    pending_service.set_pending(action)

    result = executor.execute(MemoryCommandParser().parse("bekreft"))

    assert result.status == MemoryCommandExecutionStatus.CONFIRMED_PENDING
    assert result.operation_result is not None
    assert result.operation_result.deleted is False
    assert memory_service.get_memory("unknown-memory") is None


def test_correct_unknown_memory_id_is_rejected_by_memory_service():
    executor, _memory_service, pending_service = make_executor()
    action = PendingMemoryAction(
        action_type=PendingMemoryActionType.CORRECT,
        command_type=MemoryCommandType.CORRECT,
        explanation="Correct unknown memory after confirmation.",
        source_text="korriger minne unknown-memory",
        memory_id="unknown-memory",
        proposed_content="new content",
    )
    pending_service.set_pending(action)

    result = executor.execute(MemoryCommandParser().parse("bekreft"))

    assert result.status == MemoryCommandExecutionStatus.REJECTED
    assert result.operation_result is not None
    assert result.operation_result.allowed is False
    assert result.operation_result.audit_reason == "Memory update rejected: memory id not found."


def test_normal_conversation_still_does_not_execute_memory_command():
    executor, memory_service, _pending_service = make_executor()
    command = MemoryCommandParser().parse("hva vil du lære etter hvert")

    result = executor.execute(command)

    assert result.status == MemoryCommandExecutionStatus.NOT_MEMORY_COMMAND
    assert result.operation_result is None
    assert memory_service.list_memories() == []


def test_executor_rejects_direct_empty_search_command():
    executor, _memory_service, _pending_service = make_executor()
    command = MemoryCommand(
        type=MemoryCommandType.SEARCH,
        raw_text="search memories for",
        normalized_text="search memories for",
        query="   ",
    )

    result = executor.execute(command)

    assert result.status == MemoryCommandExecutionStatus.REJECTED
    assert result.message == "Search command has no query."
