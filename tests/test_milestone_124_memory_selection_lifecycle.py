from datetime import datetime, timedelta, timezone

import pytest

from lucifer_os.memory import (
    InMemoryMemoryCandidateSelectionRequestStore,
    MemoryCandidateSelectionRequest,
    MemoryCandidateSelectionRequestLifecycleResult,
    MemoryCandidateSelectionRequestService,
    MemoryCommandType,
    MemoryItem,
    MemoryScope,
    MemoryTargetCandidate,
    MemoryType,
)
from lucifer_os.memory.pending import InMemoryPendingMemoryActionStore, PendingMemoryAction, PendingMemoryActionService, PendingMemoryActionType


def make_candidate(id="memory-1", content="LuciferOS bruker SQLite"):
    memory = MemoryItem(
        id=id,
        content=content,
        type=MemoryType.PREFERENCE,
        scope=MemoryScope.PROJECT,
        source="test",
    )
    return MemoryTargetCandidate(memory=memory, reason="test candidate")


def make_request(created_at=None):
    kwargs = {}
    if created_at is not None:
        kwargs["created_at"] = created_at

    return MemoryCandidateSelectionRequest(
        command_type=MemoryCommandType.DELETE,
        source_text="glem at SQLite",
        candidates=(make_candidate(),),
        **kwargs,
    )


def test_selection_request_service_requires_positive_stale_timeout():
    with pytest.raises(ValueError, match="greater than zero"):
        MemoryCandidateSelectionRequestService(stale_after_seconds=0)


def test_active_selection_request_remains_available_before_expiry():
    service = MemoryCandidateSelectionRequestService(stale_after_seconds=300)
    request = make_request()

    service.set_request(request)

    result = service.get_request_lifecycle_result()

    assert result.stale is False
    assert result.cancelled is False
    assert result.request == request
    assert service.get_request() == request


def test_stale_selection_request_is_cleared_and_cannot_be_retrieved():
    service = MemoryCandidateSelectionRequestService(stale_after_seconds=1)
    created_at = (datetime.now(timezone.utc) - timedelta(seconds=2)).isoformat()
    request = make_request(created_at=created_at)

    service.set_request(request)

    result = service.get_request_lifecycle_result()

    assert result.stale is True
    assert result.cancelled is False
    assert result.request == request
    assert service.get_request() is None


def test_cancel_selection_request_clears_it_without_pending_action():
    service = MemoryCandidateSelectionRequestService()
    request = make_request()
    service.set_request(request)

    result = service.cancel_request()

    assert result.cancelled is True
    assert result.stale is False
    assert result.request == request
    assert service.get_request() is None


def test_cancel_without_active_selection_request_is_safe():
    service = MemoryCandidateSelectionRequestService()

    result = service.cancel_request()

    assert result.cancelled is False
    assert result.stale is False
    assert result.request is None


def test_selection_expiry_is_independent_from_pending_action_expiry():
    selection_service = MemoryCandidateSelectionRequestService(stale_after_seconds=1)
    pending_store = InMemoryPendingMemoryActionStore()
    pending_service = PendingMemoryActionService(
        store=pending_store,
        stale_after_seconds=300,
    )

    old_request = make_request(
        created_at=(datetime.now(timezone.utc) - timedelta(seconds=2)).isoformat()
    )
    pending = PendingMemoryAction(
        action_type=PendingMemoryActionType.DELETE,
        command_type=MemoryCommandType.DELETE,
        explanation="Delete after confirmation.",
        source_text="glem at SQLite",
        memory_id="memory-1",
    )

    selection_service.set_request(old_request)
    pending_service.set_pending(pending)

    assert selection_service.get_request() is None
    assert pending_service.get_pending() == pending


def test_request_store_keeps_only_one_current_request():
    store = InMemoryMemoryCandidateSelectionRequestStore()
    service = MemoryCandidateSelectionRequestService(store=store)
    first = make_request()
    second = make_request()

    service.set_request(first)
    service.set_request(second)

    assert service.get_request() == second
    assert service.get_request() != first


def test_selection_lifecycle_result_requires_no_extra_mutation():
    request = make_request()
    result = MemoryCandidateSelectionRequestLifecycleResult(
        cancelled=False,
        stale=False,
        request=request,
        reason="active",
    )

    assert result.request is request
    assert request.candidates[0].memory.id == "memory-1"


def test_selection_lifecycle_types_are_public_memory_exports():
    import lucifer_os.memory as memory

    assert memory.MemoryCandidateSelectionRequestService is MemoryCandidateSelectionRequestService
    assert memory.MemoryCandidateSelectionRequestLifecycleResult is MemoryCandidateSelectionRequestLifecycleResult
