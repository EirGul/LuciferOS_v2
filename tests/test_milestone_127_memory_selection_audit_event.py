import pytest

from lucifer_os.memory import (
    MemoryCandidateSelectionAuditAction,
    MemoryCandidateSelectionAuditEvent,
    MemoryCommandType,
)


def make_event(**overrides):
    values = {
        "action": MemoryCandidateSelectionAuditAction.REQUEST_CREATED,
        "source": "memory-selection-service",
        "selection_request_id": "request-1",
        "command_type": MemoryCommandType.DELETE,
        "reason": "ambiguous_target",
    }
    values.update(overrides)
    return MemoryCandidateSelectionAuditEvent(**values)


def test_selection_audit_actions_match_the_contract():
    assert {
        action.value for action in MemoryCandidateSelectionAuditAction
    } == {
        "selection_request_created",
        "selection_request_rejected",
        "selection_request_cancelled",
        "selection_request_expired",
        "selection_candidate_rejected",
        "selection_candidate_accepted",
        "selection_pending_action_prepared",
    }


def test_selection_audit_event_is_immutable_and_has_minimal_fields():
    event = make_event()

    assert event.action == MemoryCandidateSelectionAuditAction.REQUEST_CREATED
    assert event.source == "memory-selection-service"
    assert event.selection_request_id == "request-1"
    assert event.command_type == MemoryCommandType.DELETE
    assert event.selected_memory_id is None
    assert event.pending_action_id is None
    assert event.reason == "ambiguous_target"
    assert event.id
    assert event.created_at


def test_selection_audit_event_never_claims_memory_mutation():
    event = make_event(
        action=MemoryCandidateSelectionAuditAction.PENDING_ACTION_PREPARED,
        selected_memory_id="memory-1",
        pending_action_id="pending-1",
    )

    assert event.is_memory_mutation_event is False


def test_request_rejection_can_be_audited_without_new_request_context():
    event = make_event(
        action=MemoryCandidateSelectionAuditAction.REQUEST_REJECTED,
        selection_request_id=None,
        command_type=None,
        reason="active_selection_exists",
    )

    assert event.selection_request_id is None
    assert event.command_type is None
    assert event.reason == "active_selection_exists"


@pytest.mark.parametrize(
    "action",
    [
        MemoryCandidateSelectionAuditAction.REQUEST_CREATED,
        MemoryCandidateSelectionAuditAction.REQUEST_CANCELLED,
        MemoryCandidateSelectionAuditAction.REQUEST_EXPIRED,
        MemoryCandidateSelectionAuditAction.CANDIDATE_REJECTED,
        MemoryCandidateSelectionAuditAction.CANDIDATE_ACCEPTED,
        MemoryCandidateSelectionAuditAction.PENDING_ACTION_PREPARED,
    ],
)
def test_contextual_actions_require_request_id_and_command_type(action):
    with pytest.raises(ValueError, match="requires selection_request_id"):
        make_event(action=action, selection_request_id=None)

    with pytest.raises(ValueError, match="requires command_type"):
        make_event(action=action, command_type=None)


def test_candidate_accepted_requires_selected_memory_id():
    with pytest.raises(ValueError, match="requires selected_memory_id"):
        make_event(
            action=MemoryCandidateSelectionAuditAction.CANDIDATE_ACCEPTED,
            selected_memory_id=None,
        )


def test_pending_action_prepared_requires_selected_memory_and_pending_action_ids():
    with pytest.raises(ValueError, match="requires selected_memory_id"):
        make_event(
            action=MemoryCandidateSelectionAuditAction.PENDING_ACTION_PREPARED,
            selected_memory_id=None,
            pending_action_id="pending-1",
        )

    with pytest.raises(ValueError, match="requires pending_action_id"):
        make_event(
            action=MemoryCandidateSelectionAuditAction.PENDING_ACTION_PREPARED,
            selected_memory_id="memory-1",
            pending_action_id=None,
        )


@pytest.mark.parametrize(
    "field_name",
    ["source", "id", "created_at", "selection_request_id", "selected_memory_id", "pending_action_id"],
)
def test_selection_audit_event_rejects_blank_identifier_fields(field_name):
    values = {
        "action": MemoryCandidateSelectionAuditAction.PENDING_ACTION_PREPARED,
        "source": "memory-selection-service",
        "selection_request_id": "request-1",
        "command_type": MemoryCommandType.CORRECT,
        "selected_memory_id": "memory-1",
        "pending_action_id": "pending-1",
    }
    values[field_name] = "   "

    with pytest.raises(ValueError):
        MemoryCandidateSelectionAuditEvent(**values)


def test_selection_audit_types_are_public_memory_exports():
    import lucifer_os.memory as memory

    assert memory.MemoryCandidateSelectionAuditAction is MemoryCandidateSelectionAuditAction
    assert memory.MemoryCandidateSelectionAuditEvent is MemoryCandidateSelectionAuditEvent
