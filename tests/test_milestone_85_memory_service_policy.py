from lucifer_os.memory import InMemoryMemoryStore, MemoryOperationResult, MemoryScope, MemoryService, MemoryType


def test_memory_service_returns_operation_result_for_allowed_project_memory():
    service = MemoryService(InMemoryMemoryStore())

    result = service.add_memory(
        content='Project memory can be stored without confirmation.',
        type=MemoryType.PROJECT_STATE,
        scope=MemoryScope.PROJECT,
    )

    assert isinstance(result, MemoryOperationResult)
    assert result.allowed is True
    assert result.requires_confirmation is False
    assert result.item is not None
    assert result.item.content == 'Project memory can be stored without confirmation.'
    assert service.list_memories() == [result.item]


def test_memory_service_rejects_empty_memory_before_model_creation():
    service = MemoryService(InMemoryMemoryStore())

    result = service.add_memory(
        content='   ',
        type=MemoryType.FACT,
        scope=MemoryScope.PROJECT,
    )

    assert result.allowed is False
    assert result.requires_confirmation is False
    assert result.item is None
    assert service.list_memories() == []
    assert 'empty content' in result.audit_reason


def test_memory_service_requires_confirmation_for_high_impact_write():
    service = MemoryService(InMemoryMemoryStore())

    result = service.add_memory(
        content='Always keep LuciferOS local-first.',
        type=MemoryType.USER_INSTRUCTION,
        scope=MemoryScope.PROJECT,
    )

    assert result.allowed is True
    assert result.requires_confirmation is True
    assert result.item is None
    assert service.list_memories() == []


def test_memory_service_stores_high_impact_write_when_confirmed():
    service = MemoryService(InMemoryMemoryStore())

    result = service.add_memory(
        content='Always keep LuciferOS local-first.',
        type=MemoryType.USER_INSTRUCTION,
        scope=MemoryScope.PROJECT,
        confirmed=True,
    )

    assert result.allowed is True
    assert result.requires_confirmation is False
    assert result.item is not None
    assert service.list_memories() == [result.item]


def test_memory_service_requires_confirmation_before_delete():
    service = MemoryService(InMemoryMemoryStore())
    add_result = service.add_memory(
        content='Temporary project memory.',
        type=MemoryType.PROJECT_STATE,
        scope=MemoryScope.PROJECT,
    )
    item = add_result.item
    assert item is not None

    delete_result = service.delete_memory(item.id)

    assert delete_result.allowed is True
    assert delete_result.requires_confirmation is True
    assert delete_result.deleted is False
    assert service.get_memory(item.id) == item


def test_memory_service_deletes_when_confirmed():
    service = MemoryService(InMemoryMemoryStore())
    add_result = service.add_memory(
        content='Temporary project memory.',
        type=MemoryType.PROJECT_STATE,
        scope=MemoryScope.PROJECT,
    )
    item = add_result.item
    assert item is not None

    delete_result = service.delete_memory(item.id, confirmed=True)

    assert delete_result.allowed is True
    assert delete_result.requires_confirmation is False
    assert delete_result.deleted is True
    assert service.get_memory(item.id) is None
