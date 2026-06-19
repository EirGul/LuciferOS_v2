from lucifer_os.memory import InMemoryMemoryAuditSink, InMemoryMemoryStore, MemoryAuditAction, MemoryScope, MemoryService, MemoryType


def test_memory_service_updates_existing_memory_without_confirmation_for_low_impact_memory():
    audit_sink = InMemoryMemoryAuditSink()
    service = MemoryService(InMemoryMemoryStore(), audit_sink=audit_sink)
    add_result = service.add_memory(
        content="Original project memory.",
        type=MemoryType.PROJECT_STATE,
        scope=MemoryScope.PROJECT,
    )
    item = add_result.item
    assert item is not None

    update_result = service.update_memory(
        memory_id=item.id,
        content="Corrected project memory.",
        type=MemoryType.PROJECT_STATE,
        scope=MemoryScope.PROJECT,
        source="test",
        confidence=0.95,
        tags=("corrected",),
        metadata={"reason": "test correction"},
    )

    assert update_result.allowed is True
    assert update_result.requires_confirmation is False
    assert update_result.item is not None
    assert update_result.item.id == item.id
    assert update_result.item.content == "Corrected project memory."
    assert update_result.item.created_at == item.created_at
    assert update_result.item.updated_at != item.updated_at
    assert service.get_memory(item.id) == update_result.item

    actions = [event.action for event in audit_sink.list_events()]
    assert MemoryAuditAction.UPDATE_REQUESTED in actions
    assert MemoryAuditAction.UPDATE_COMPLETED in actions


def test_memory_service_rejects_empty_update_content():
    audit_sink = InMemoryMemoryAuditSink()
    service = MemoryService(InMemoryMemoryStore(), audit_sink=audit_sink)
    add_result = service.add_memory(
        content="Original project memory.",
        type=MemoryType.PROJECT_STATE,
        scope=MemoryScope.PROJECT,
    )
    item = add_result.item
    assert item is not None

    update_result = service.update_memory(
        memory_id=item.id,
        content="   ",
        type=MemoryType.PROJECT_STATE,
        scope=MemoryScope.PROJECT,
    )

    assert update_result.allowed is False
    assert update_result.item is None
    assert "empty content" in update_result.audit_reason
    assert service.get_memory(item.id) == item

    actions = [event.action for event in audit_sink.list_events()]
    assert MemoryAuditAction.UPDATE_REJECTED in actions


def test_memory_service_rejects_update_for_missing_memory_id():
    audit_sink = InMemoryMemoryAuditSink()
    service = MemoryService(InMemoryMemoryStore(), audit_sink=audit_sink)

    update_result = service.update_memory(
        memory_id="missing-id",
        content="Corrected memory.",
        type=MemoryType.PROJECT_STATE,
        scope=MemoryScope.PROJECT,
    )

    assert update_result.allowed is False
    assert update_result.requires_confirmation is False
    assert update_result.item is None
    assert "not found" in update_result.audit_reason

    actions = [event.action for event in audit_sink.list_events()]
    assert actions == [
        MemoryAuditAction.UPDATE_REQUESTED,
        MemoryAuditAction.UPDATE_REJECTED,
    ]


def test_memory_service_requires_confirmation_for_high_impact_update():
    audit_sink = InMemoryMemoryAuditSink()
    service = MemoryService(InMemoryMemoryStore(), audit_sink=audit_sink)
    add_result = service.add_memory(
        content="Original project memory.",
        type=MemoryType.PROJECT_STATE,
        scope=MemoryScope.PROJECT,
    )
    item = add_result.item
    assert item is not None

    update_result = service.update_memory(
        memory_id=item.id,
        content="Always keep LuciferOS local-first.",
        type=MemoryType.USER_INSTRUCTION,
        scope=MemoryScope.GLOBAL,
    )

    assert update_result.allowed is True
    assert update_result.requires_confirmation is True
    assert update_result.item is None
    assert service.get_memory(item.id) == item

    actions = [event.action for event in audit_sink.list_events()]
    assert MemoryAuditAction.UPDATE_REQUIRES_CONFIRMATION in actions


def test_memory_service_updates_high_impact_memory_when_confirmed():
    service = MemoryService(InMemoryMemoryStore())
    add_result = service.add_memory(
        content="Original project memory.",
        type=MemoryType.PROJECT_STATE,
        scope=MemoryScope.PROJECT,
    )
    item = add_result.item
    assert item is not None

    update_result = service.update_memory(
        memory_id=item.id,
        content="Always keep LuciferOS local-first.",
        type=MemoryType.USER_INSTRUCTION,
        scope=MemoryScope.GLOBAL,
        confirmed=True,
    )

    assert update_result.allowed is True
    assert update_result.requires_confirmation is False
    assert update_result.item is not None
    assert update_result.item.id == item.id
    assert update_result.item.type == MemoryType.USER_INSTRUCTION
    assert update_result.item.scope == MemoryScope.GLOBAL
    assert service.get_memory(item.id) == update_result.item
