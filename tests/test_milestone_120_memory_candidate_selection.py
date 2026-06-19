import pytest

from lucifer_os.memory import (
    MemoryCandidateSelectionOutcome,
    MemoryCandidateSelectionRequest,
    MemoryCandidateSelectionResult,
    MemoryCandidateSelector,
    MemoryCommandType,
    MemoryItem,
    MemoryScope,
    MemoryTargetCandidate,
    MemoryType,
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


def make_request(candidates=None):
    return MemoryCandidateSelectionRequest(
        command_type=MemoryCommandType.DELETE,
        source_text="glem at SQLite",
        candidates=candidates or (make_candidate(),),
    )


def test_selection_request_supports_only_correct_and_delete():
    with pytest.raises(ValueError, match="only correction and delete"):
        MemoryCandidateSelectionRequest(
            command_type=MemoryCommandType.REMEMBER,
            source_text="husk at noe",
            candidates=(make_candidate(),),
        )


def test_selection_request_requires_source_text_and_candidates():
    with pytest.raises(ValueError, match="source text"):
        MemoryCandidateSelectionRequest(
            command_type=MemoryCommandType.DELETE,
            source_text="   ",
            candidates=(make_candidate(),),
        )

    with pytest.raises(ValueError, match="at least one candidate"):
        MemoryCandidateSelectionRequest(
            command_type=MemoryCommandType.DELETE,
            source_text="glem at SQLite",
            candidates=(),
        )


def test_selection_request_rejects_duplicate_candidate_ids():
    duplicate = make_candidate(id="memory-1", content="Annet minne")

    with pytest.raises(ValueError, match="unique memory ids"):
        MemoryCandidateSelectionRequest(
            command_type=MemoryCommandType.DELETE,
            source_text="glem at SQLite",
            candidates=(make_candidate(), duplicate),
        )


def test_selector_selects_only_candidate_belonging_to_request():
    selector = MemoryCandidateSelector()
    request = make_request()

    result = selector.select(request, "memory-1")

    assert result.outcome == MemoryCandidateSelectionOutcome.SELECTED
    assert result.request_id == request.id
    assert result.selected_memory_id == "memory-1"


def test_selector_rejects_blank_or_unknown_candidate_id():
    selector = MemoryCandidateSelector()
    request = make_request()

    blank = selector.select(request, "   ")
    unknown = selector.select(request, "memory-404")

    assert blank.outcome == MemoryCandidateSelectionOutcome.REJECTED
    assert blank.selected_memory_id is None
    assert unknown.outcome == MemoryCandidateSelectionOutcome.REJECTED
    assert unknown.selected_memory_id is None


def test_selected_result_requires_selected_memory_id():
    with pytest.raises(ValueError, match="selected_memory_id"):
        MemoryCandidateSelectionResult(
            outcome=MemoryCandidateSelectionOutcome.SELECTED,
            explanation="selected",
            request_id="request-1",
        )


def test_selector_does_not_mutate_request_or_candidates():
    selector = MemoryCandidateSelector()
    candidate = make_candidate()
    request = make_request(candidates=(candidate,))

    result = selector.select(request, "memory-1")

    assert result.selected_memory_id == "memory-1"
    assert request.candidates == (candidate,)
    assert request.candidates[0] is candidate


def test_selection_types_are_public_memory_exports():
    import lucifer_os.memory as memory

    assert memory.MemoryCandidateSelectionRequest is MemoryCandidateSelectionRequest
    assert memory.MemoryCandidateSelectionResult is MemoryCandidateSelectionResult
    assert memory.MemoryCandidateSelectionOutcome is MemoryCandidateSelectionOutcome
    assert memory.MemoryCandidateSelector is MemoryCandidateSelector
