import pytest

from lucifer_os.memory import (
    InMemoryMemoryCandidateSelectionAuditSink,
    MemoryCandidateSelectionAuditAction,
    MemoryCandidateSelectionAuditDeliveryResult,
    MemoryCandidateSelectionAuditDeliveryService,
    MemoryCandidateSelectionAuditDeliveryStatus,
    MemoryCandidateSelectionAuditEvent,
    MemoryCandidateSelectionAuditSink,
    MemoryCommandType,
)


class FailingSelectionAuditSink(MemoryCandidateSelectionAuditSink):
    def record(self, event: MemoryCandidateSelectionAuditEvent) -> None:
        raise RuntimeError("transport unavailable")


def make_event():
    return MemoryCandidateSelectionAuditEvent(
        action=MemoryCandidateSelectionAuditAction.REQUEST_CREATED,
        source="memory-selection-service",
        selection_request_id="request-1",
        command_type=MemoryCommandType.DELETE,
        reason="ambiguous_target",
    )


def test_successful_audit_delivery_returns_explicit_delivered_result():
    sink = InMemoryMemoryCandidateSelectionAuditSink()
    service = MemoryCandidateSelectionAuditDeliveryService(sink)
    event = make_event()

    result = service.deliver(event)

    assert result.status == MemoryCandidateSelectionAuditDeliveryStatus.DELIVERED
    assert result.delivered is True
    assert result.failed is False
    assert result.event is event
    assert result.reason == ""
    assert sink.list_events() == (event,)


def test_failed_audit_delivery_returns_bounded_failure_without_raising():
    service = MemoryCandidateSelectionAuditDeliveryService(FailingSelectionAuditSink())
    event = make_event()

    result = service.deliver(event)

    assert result.status == MemoryCandidateSelectionAuditDeliveryStatus.FAILED
    assert result.delivered is False
    assert result.failed is True
    assert result.event is event
    assert result.reason == "selection_audit_delivery_failed"


def test_failure_result_does_not_expose_sink_exception_text():
    service = MemoryCandidateSelectionAuditDeliveryService(FailingSelectionAuditSink())

    result = service.deliver(make_event())

    assert "transport unavailable" not in result.reason
    assert result.reason == "selection_audit_delivery_failed"


def test_failed_delivery_result_requires_bounded_reason():
    with pytest.raises(ValueError, match="requires a bounded reason"):
        MemoryCandidateSelectionAuditDeliveryResult(
            status=MemoryCandidateSelectionAuditDeliveryStatus.FAILED,
            event=make_event(),
        )


def test_delivered_result_rejects_failure_reason():
    with pytest.raises(ValueError, match="must not include a failure reason"):
        MemoryCandidateSelectionAuditDeliveryResult(
            status=MemoryCandidateSelectionAuditDeliveryStatus.DELIVERED,
            event=make_event(),
            reason="not allowed",
        )


def test_delivery_service_does_not_mutate_event_or_claim_memory_mutation():
    sink = InMemoryMemoryCandidateSelectionAuditSink()
    service = MemoryCandidateSelectionAuditDeliveryService(sink)
    event = make_event()

    result = service.deliver(event)

    assert result.event == event
    assert event.is_memory_mutation_event is False
    assert sink.list_events()[0] == event


def test_delivery_types_are_public_memory_exports():
    import lucifer_os.memory as memory

    assert (
        memory.MemoryCandidateSelectionAuditDeliveryService
        is MemoryCandidateSelectionAuditDeliveryService
    )
    assert (
        memory.MemoryCandidateSelectionAuditDeliveryStatus
        is MemoryCandidateSelectionAuditDeliveryStatus
    )
    assert (
        memory.MemoryCandidateSelectionAuditDeliveryResult
        is MemoryCandidateSelectionAuditDeliveryResult
    )
