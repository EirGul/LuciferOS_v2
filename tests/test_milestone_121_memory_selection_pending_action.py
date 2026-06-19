import pytest

from lucifer_os.memory import (
    MemoryCandidateSelectionOutcome,
    MemoryCandidateSelectionPendingActionBuilder,
    MemoryCandidateSelectionPreparationOutcome,
    MemoryCandidateSelectionPreparationResult,
    MemoryCandidateSelectionRequest,
    MemoryCandidateSelector,
    MemoryCommandType,
    MemoryItem,
    MemoryScope,
    MemoryTargetCandidate,
    MemoryType,
    PendingMemoryActionType,
)


def make_candidate(id="memory-1", content="LuciferOS bruker SQLite"):
    memory = MemoryItem(
        id=id,
        content=content,
        type=MemoryType.PREFERENCE,
        scope=MemoryScope.PROJECT,
        source="test",
    )
    return MemoryTargetCandidate(memory=memory, reason="test candidate")


def make_delete_request():
    return MemoryCandidateSelectionRequest(
        command_type=MemoryCommandType.DELETE,
        source_text="glem at SQLite",
        candidates=(make_candidate(),),
    )


def make_correct_request():
    return MemoryCandidateSelectionRequest(
        command_type=MemoryCommandType.CORRECT,
        source_text='korriger minne "SQLite" til "persistent memory"',
        candidates=(make_candidate(),),
        proposed_content="persistent memory",
    )


def test_correct_selection_request_requires_proposed_content():
    with pytest.raises(ValueError, match="proposed content"):
        MemoryCandidateSelectionRequest(
            command_type=MemoryCommandType.CORRECT,
            source_text="korriger minne SQLite",
            candidates=(make_candidate(),),
        )


def test_delete_selection_request_rejects_proposed_content():
    with pytest.raises(ValueError, match="must not include proposed content"):
        MemoryCandidateSelectionRequest(
            command_type=MemoryCommandType.DELETE,
            source_text="glem at SQLite",
            candidates=(make_candidate(),),
            proposed_content="not allowed",
        )


def test_builder_prepares_delete_pending_action_after_valid_selection():
    request = make_delete_request()
    selection = MemoryCandidateSelector().select(request, "memory-1")

    result = MemoryCandidateSelectionPendingActionBuilder().prepare(request, selection)

    assert result.outcome == MemoryCandidateSelectionPreparationOutcome.PREPARED
    assert result.pending_action is not None
    assert result.pending_action.action_type == PendingMemoryActionType.DELETE
    assert result.pending_action.memory_id == "memory-1"
    assert result.pending_action.proposed_content is None
    assert result.pending_action.metadata["selection_request_id"] == request.id


def test_builder_prepares_correct_pending_action_after_valid_selection():
    request = make_correct_request()
    selection = MemoryCandidateSelector().select(request, "memory-1")

    result = MemoryCandidateSelectionPendingActionBuilder().prepare(request, selection)

    assert result.outcome == MemoryCandidateSelectionPreparationOutcome.PREPARED
    assert result.pending_action is not None
    assert result.pending_action.action_type == PendingMemoryActionType.CORRECT
    assert result.pending_action.memory_id == "memory-1"
    assert result.pending_action.proposed_content == "persistent memory"
    assert result.pending_action.metadata["selection_request_id"] == request.id


def test_builder_rejects_selection_from_other_request():
    request = make_delete_request()
    other_request = MemoryCandidateSelectionRequest(
        command_type=MemoryCommandType.DELETE,
        source_text="glem at noe annet",
        candidates=(make_candidate(),),
    )
    selection = MemoryCandidateSelector().select(other_request, "memory-1")

    result = MemoryCandidateSelectionPendingActionBuilder().prepare(request, selection)

    assert result.outcome == MemoryCandidateSelectionPreparationOutcome.REJECTED
    assert result.pending_action is None


def test_builder_rejects_non_selected_result():
    request = make_delete_request()
    selection = MemoryCandidateSelector().select(request, "unknown")

    result = MemoryCandidateSelectionPendingActionBuilder().prepare(request, selection)

    assert result.outcome == MemoryCandidateSelectionPreparationOutcome.REJECTED
    assert result.pending_action is None


def test_prepared_result_requires_pending_action():
    with pytest.raises(ValueError, match="pending_action"):
        MemoryCandidateSelectionPreparationResult(
            outcome=MemoryCandidateSelectionPreparationOutcome.PREPARED,
            explanation="prepared",
        )


def test_builder_does_not_mutate_request_or_candidates():
    request = make_correct_request()
    candidate = request.candidates[0]
    selection = MemoryCandidateSelector().select(request, "memory-1")

    result = MemoryCandidateSelectionPendingActionBuilder().prepare(request, selection)

    assert result.pending_action is not None
    assert request.candidates == (candidate,)
    assert request.proposed_content == "persistent memory"


def test_selection_pending_action_types_are_public_memory_exports():
    import lucifer_os.memory as memory

    assert memory.MemoryCandidateSelectionPendingActionBuilder is MemoryCandidateSelectionPendingActionBuilder
    assert memory.MemoryCandidateSelectionPreparationOutcome is MemoryCandidateSelectionPreparationOutcome
    assert memory.MemoryCandidateSelectionPreparationResult is MemoryCandidateSelectionPreparationResult
