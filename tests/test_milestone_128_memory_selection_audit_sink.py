import pytest

from lucifer_os.memory import (
    InMemoryMemoryCandidateSelectionAuditSink,
    MemoryCandidateSelectionAuditAction,
    MemoryCandidateSelectionAuditEvent,
    MemoryCandidateSelectionAuditSink,
    MemoryCommandType,
)


def make_event(action=MemoryCandidateSelectionAuditAction.REQUEST_CREATED):
    return MemoryCandidateSelectionAuditEvent(
        action=action,
        source="memory-selection-service",
        selection_request_id="request-1",
        command_type=MemoryCommandType.DELETE,
        reason="ambiguous_target",
    )


def test_selection_audit_sink_is_abstract_contract():
    with pytest.raises(TypeError):
        MemoryCandidateSelectionAuditSink()


def test_in_memory_selection_audit_sink_starts_empty():
    sink = InMemoryMemoryCandidateSelectionAuditSink()

    assert sink.list_events() == ()


def test_in_memory_selection_audit_sink_records_event_in_order():
    sink = InMemoryMemoryCandidateSelectionAuditSink()
    first = make_event()
    second = MemoryCandidateSelectionAuditEvent(
        action=MemoryCandidateSelectionAuditAction.CANDIDATE_ACCEPTED,
        source="memory-selection-service",
        selection_request_id="request-1",
        command_type=MemoryCommandType.DELETE,
        selected_memory_id="memory-2",
        reason="selected",
    )

    sink.record(first)
    sink.record(second)

    assert sink.list_events() == (first, second)


def test_in_memory_selection_audit_sink_preserves_event_identity():
    sink = InMemoryMemoryCandidateSelectionAuditSink()
    event = make_event()

    sink.record(event)

    assert sink.list_events()[0] is event


def test_in_memory_selection_audit_sink_returns_immutable_snapshot():
    sink = InMemoryMemoryCandidateSelectionAuditSink()
    sink.record(make_event())

    events = sink.list_events()

    assert isinstance(events, tuple)
    with pytest.raises(AttributeError):
        events.append(make_event())


def test_in_memory_selection_audit_sink_clear_returns_then_removes_events():
    sink = InMemoryMemoryCandidateSelectionAuditSink()
    first = make_event()
    second = make_event()
    sink.record(first)
    sink.record(second)

    cleared = sink.clear()

    assert cleared == (first, second)
    assert sink.list_events() == ()


def test_in_memory_selection_audit_sink_clear_is_safe_when_empty():
    sink = InMemoryMemoryCandidateSelectionAuditSink()

    assert sink.clear() == ()
    assert sink.list_events() == ()


def test_selection_audit_sink_types_are_public_memory_exports():
    import lucifer_os.memory as memory

    assert memory.MemoryCandidateSelectionAuditSink is MemoryCandidateSelectionAuditSink
    assert (
        memory.InMemoryMemoryCandidateSelectionAuditSink
        is InMemoryMemoryCandidateSelectionAuditSink
    )
