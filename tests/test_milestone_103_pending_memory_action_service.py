from datetime import datetime, timedelta, timezone

import pytest

from lucifer_os.memory import (
    InMemoryPendingMemoryActionStore,
    MemoryCommandType,
    PendingMemoryAction,
    PendingMemoryActionConfirmationResult,
    PendingMemoryActionService,
    PendingMemoryActionType,
)


def make_action(**overrides):
    values = {
        "action_type": PendingMemoryActionType.REMEMBER,
        "command_type": MemoryCommandType.REMEMBER,
        "explanation": "Store memory after confirmation.",
        "source_text": "husk at LuciferOS er local-first",
        "proposed_content": "LuciferOS er local-first",
    }
    values.update(overrides)
    return PendingMemoryAction(**values)


def test_pending_memory_action_service_sets_and_gets_pending_action():
    service = PendingMemoryActionService()
    action = make_action()

    assert service.get_pending() is None
    assert service.set_pending(action) == action
    assert service.get_pending() == action


def test_pending_memory_action_service_confirms_and_clears_pending_action():
    service = PendingMemoryActionService()
    action = make_action()
    service.set_pending(action)

    result = service.confirm_pending()

    assert isinstance(result, PendingMemoryActionConfirmationResult)
    assert result.confirmed is True
    assert result.cancelled is False
    assert result.stale is False
    assert result.action == action
    assert service.get_pending() is None


def test_pending_memory_action_service_cancel_clears_without_confirming():
    service = PendingMemoryActionService()
    action = make_action()
    service.set_pending(action)

    result = service.cancel_pending()

    assert result.confirmed is False
    assert result.cancelled is True
    assert result.stale is False
    assert result.action == action
    assert service.get_pending() is None


def test_pending_memory_action_service_handles_missing_pending_action():
    service = PendingMemoryActionService()

    confirm_result = service.confirm_pending()
    cancel_result = service.cancel_pending()

    assert confirm_result.confirmed is False
    assert confirm_result.action is None
    assert "No pending memory action to confirm." == confirm_result.reason
    assert cancel_result.cancelled is False
    assert cancel_result.action is None
    assert "No pending memory action to cancel." == cancel_result.reason


def test_pending_memory_action_service_clears_stale_action_on_get():
    old_time = datetime.now(timezone.utc) - timedelta(seconds=10)
    action = make_action(created_at=old_time.isoformat())
    service = PendingMemoryActionService(stale_after_seconds=1)

    service.set_pending(action)

    assert service.get_pending() is None


def test_pending_memory_action_service_does_not_confirm_stale_action():
    old_time = datetime.now(timezone.utc) - timedelta(seconds=10)
    action = make_action(created_at=old_time.isoformat())
    service = PendingMemoryActionService(stale_after_seconds=1)

    service.set_pending(action)
    result = service.confirm_pending()

    assert result.confirmed is False
    assert result.cancelled is False
    assert result.stale is True
    assert result.action == action
    assert service.get_pending() is None


def test_pending_memory_action_service_rejects_invalid_stale_timeout():
    with pytest.raises(ValueError, match="stale_after_seconds"):
        PendingMemoryActionService(stale_after_seconds=0)


def test_pending_memory_action_service_accepts_external_store():
    store = InMemoryPendingMemoryActionStore()
    service = PendingMemoryActionService(store=store)
    action = make_action()

    service.set_pending(action)

    assert store.get() == action


def test_pending_memory_action_service_exports_are_public():
    import lucifer_os.memory as memory

    assert memory.PendingMemoryActionService is PendingMemoryActionService
    assert memory.PendingMemoryActionConfirmationResult is PendingMemoryActionConfirmationResult
