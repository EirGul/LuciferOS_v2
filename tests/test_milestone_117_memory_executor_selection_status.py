from lucifer_os.memory import MemoryCommandExecutionStatus


def test_memory_executor_has_awaiting_user_selection_status():
    assert MemoryCommandExecutionStatus.AWAITING_USER_SELECTION.value == "awaiting_user_selection"


def test_awaiting_user_selection_is_distinct_from_execution_and_confirmation_statuses():
    status = MemoryCommandExecutionStatus.AWAITING_USER_SELECTION

    assert status != MemoryCommandExecutionStatus.EXECUTED
    assert status != MemoryCommandExecutionStatus.PENDING_CONFIRMATION
    assert status != MemoryCommandExecutionStatus.CONFIRMED_PENDING
    assert status != MemoryCommandExecutionStatus.REJECTED


def test_memory_executor_selection_status_is_public_memory_export():
    import lucifer_os.memory as memory

    assert memory.MemoryCommandExecutionStatus.AWAITING_USER_SELECTION == MemoryCommandExecutionStatus.AWAITING_USER_SELECTION
