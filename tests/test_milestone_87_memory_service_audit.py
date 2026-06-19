from lucifer_os.memory import (
    InMemoryMemoryAuditSink,
    InMemoryMemoryStore,
    MemoryAuditAction,
    MemoryScope,
    MemoryService,
    MemoryType,
)


def test_memory_service_audits_allowed_write_request_and_storage():
    audit_sink = InMemoryMemoryAuditSink()
    service = MemoryService(InMemoryMemoryStore(), audit_sink=audit_sink)

    result = service.add_memory(
        content='Audit should record stored project memory.',
        type=MemoryType.PROJECT_STATE,
        scope=MemoryScope.PROJECT,
    )

    assert result.item is not None
    events = audit_sink.list_events()
    assert [event.action for event in events] == [
        MemoryAuditAction.WRITE_REQUESTED,
        MemoryAuditAction.WRITE_STORED,
    ]
    assert events[1].memory_id == result.item.id


def test_memory_service_audits_rejected_write():
    audit_sink = InMemoryMemoryAuditSink()
    service = MemoryService(InMemoryMemoryStore(), audit_sink=audit_sink)

    result = service.add_memory(
        content='   ',
        type=MemoryType.FACT,
        scope=MemoryScope.PROJECT,
    )

    assert result.allowed is False
    events = audit_sink.list_events()
    assert [event.action for event in events] == [
        MemoryAuditAction.WRITE_REQUESTED,
        MemoryAuditAction.WRITE_REJECTED,
    ]
    assert 'empty content' in events[1].reason


def test_memory_service_audits_write_confirmation_requirement():
    audit_sink = InMemoryMemoryAuditSink()
    service = MemoryService(InMemoryMemoryStore(), audit_sink=audit_sink)

    result = service.add_memory(
        content='Always keep LuciferOS local-first.',
        type=MemoryType.USER_INSTRUCTION,
        scope=MemoryScope.PROJECT,
    )

    assert result.requires_confirmation is True
    events = audit_sink.list_events()
    assert [event.action for event in events] == [
        MemoryAuditAction.WRITE_REQUESTED,
        MemoryAuditAction.WRITE_REQUIRES_CONFIRMATION,
    ]


def test_memory_service_audits_delete_confirmation_requirement():
    audit_sink = InMemoryMemoryAuditSink()
    service = MemoryService(InMemoryMemoryStore(), audit_sink=audit_sink)
    add_result = service.add_memory(
        content='Temporary memory.',
        type=MemoryType.PROJECT_STATE,
        scope=MemoryScope.PROJECT,
    )
    item = add_result.item
    assert item is not None
    audit_sink.list_events().clear()

    delete_result = service.delete_memory(item.id)

    assert delete_result.requires_confirmation is True
    events = audit_sink.list_events()
    assert [event.action for event in events][-2:] == [
        MemoryAuditAction.DELETE_REQUESTED,
        MemoryAuditAction.DELETE_REQUIRES_CONFIRMATION,
    ]
    assert service.get_memory(item.id) == item


def test_memory_service_audits_confirmed_delete_completion():
    audit_sink = InMemoryMemoryAuditSink()
    service = MemoryService(InMemoryMemoryStore(), audit_sink=audit_sink)
    add_result = service.add_memory(
        content='Temporary memory.',
        type=MemoryType.PROJECT_STATE,
        scope=MemoryScope.PROJECT,
    )
    item = add_result.item
    assert item is not None

    delete_result = service.delete_memory(item.id, confirmed=True)

    assert delete_result.deleted is True
    events = audit_sink.list_events()
    assert events[-2].action == MemoryAuditAction.DELETE_REQUESTED
    assert events[-1].action == MemoryAuditAction.DELETE_COMPLETED
    assert events[-1].memory_id == item.id
    assert events[-1].metadata['deleted'] is True


def test_memory_service_audits_rejected_delete():
    audit_sink = InMemoryMemoryAuditSink()
    service = MemoryService(InMemoryMemoryStore(), audit_sink=audit_sink)

    result = service.delete_memory('   ', confirmed=True)

    assert result.allowed is False
    events = audit_sink.list_events()
    assert [event.action for event in events] == [
        MemoryAuditAction.DELETE_REQUESTED,
        MemoryAuditAction.DELETE_REJECTED,
    ]
    assert 'empty memory id' in events[1].reason
