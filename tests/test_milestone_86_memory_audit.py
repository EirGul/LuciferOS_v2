import pytest

from lucifer_os.memory import (
    InMemoryMemoryAuditSink,
    MemoryAuditAction,
    MemoryAuditEvent,
    MemoryAuditSink,
)


def test_memory_audit_event_requires_reason():
    with pytest.raises(ValueError):
        MemoryAuditEvent(
            action=MemoryAuditAction.WRITE_REQUESTED,
            reason='   ',
        )


def test_memory_audit_event_has_action_reason_id_and_timestamp():
    event = MemoryAuditEvent(
        action=MemoryAuditAction.WRITE_STORED,
        reason='Memory was stored after policy evaluation.',
        memory_id='memory-123',
    )

    assert event.action == MemoryAuditAction.WRITE_STORED
    assert event.reason == 'Memory was stored after policy evaluation.'
    assert event.memory_id == 'memory-123'
    assert event.id
    assert event.created_at


def test_in_memory_memory_audit_sink_records_events_in_order():
    sink = InMemoryMemoryAuditSink()

    first = sink.record(
        MemoryAuditEvent(
            action=MemoryAuditAction.WRITE_REQUESTED,
            reason='Memory write was requested.',
        )
    )
    second = sink.record(
        MemoryAuditEvent(
            action=MemoryAuditAction.WRITE_STORED,
            reason='Memory write was stored.',
            memory_id='memory-123',
        )
    )

    assert sink.list_events() == [first, second]


def test_in_memory_memory_audit_sink_returns_copy_of_events():
    sink = InMemoryMemoryAuditSink()
    event = sink.record(
        MemoryAuditEvent(
            action=MemoryAuditAction.DELETE_REQUESTED,
            reason='Memory delete was requested.',
        )
    )

    events = sink.list_events()
    events.clear()

    assert sink.list_events() == [event]


def test_memory_audit_sink_is_abstract():
    with pytest.raises(TypeError):
        MemoryAuditSink()
