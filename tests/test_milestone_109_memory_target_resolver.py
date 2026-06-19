import pytest

from lucifer_os.memory import (
    MemoryItem,
    MemoryScope,
    MemoryTargetCandidate,
    MemoryTargetResolutionOutcome,
    MemoryTargetResolutionResult,
    MemoryTargetResolver,
    MemoryType,
)


def make_memory(content: str, id: str = "memory-1") -> MemoryItem:
    return MemoryItem(
        id=id,
        content=content,
        type=MemoryType.PREFERENCE,
        scope=MemoryScope.PROJECT,
        source="test",
    )


def test_memory_target_candidate_validates_reason_and_score():
    memory = make_memory("LuciferOS bruker SQLite")

    with pytest.raises(ValueError, match="reason"):
        MemoryTargetCandidate(memory=memory, reason="   ")

    with pytest.raises(ValueError, match="score"):
        MemoryTargetCandidate(memory=memory, reason="match", score=1.5)


def test_memory_target_resolution_result_requires_explanation():
    with pytest.raises(ValueError, match="explanation"):
        MemoryTargetResolutionResult(
            outcome=MemoryTargetResolutionOutcome.NO_MATCH,
            explanation="   ",
        )


def test_safe_resolution_requires_selected_memory_id():
    memory = make_memory("LuciferOS bruker SQLite")

    with pytest.raises(ValueError, match="selected_memory_id"):
        MemoryTargetResolutionResult(
            outcome=MemoryTargetResolutionOutcome.SINGLE_SAFE_MATCH,
            explanation="safe",
            candidates=(MemoryTargetCandidate(memory=memory, reason="match"),),
            safe_for_confirmation=True,
        )


def test_resolver_rejects_invalid_max_candidates():
    with pytest.raises(ValueError, match="max_candidates"):
        MemoryTargetResolver(max_candidates=0)


def test_resolver_matches_explicit_memory_id():
    memory = make_memory("LuciferOS bruker SQLite", id="memory-1")
    resolver = MemoryTargetResolver()

    result = resolver.resolve_explicit_id("memory-1", (memory,))

    assert result.outcome == MemoryTargetResolutionOutcome.EXPLICIT_ID_MATCH
    assert result.selected_memory_id == "memory-1"
    assert result.safe_for_confirmation is True
    assert len(result.candidates) == 1


def test_resolver_reports_no_match_for_unknown_explicit_memory_id():
    memory = make_memory("LuciferOS bruker SQLite", id="memory-1")
    resolver = MemoryTargetResolver()

    result = resolver.resolve_explicit_id("missing", (memory,))

    assert result.outcome == MemoryTargetResolutionOutcome.NO_MATCH
    assert result.safe_for_confirmation is False
    assert result.selected_memory_id is None


def test_resolver_finds_single_safe_query_match():
    memory = make_memory("LuciferOS bruker SQLite", id="memory-1")
    resolver = MemoryTargetResolver()

    result = resolver.resolve_query("SQLite", (memory,))

    assert result.outcome == MemoryTargetResolutionOutcome.SINGLE_SAFE_MATCH
    assert result.selected_memory_id == "memory-1"
    assert result.safe_for_confirmation is True


def test_resolver_reports_multiple_candidates_without_safe_selection():
    first = make_memory("LuciferOS bruker SQLite", id="memory-1")
    second = make_memory("SQLite brukes til memory", id="memory-2")
    resolver = MemoryTargetResolver()

    result = resolver.resolve_query("SQLite", (first, second))

    assert result.outcome == MemoryTargetResolutionOutcome.MULTIPLE_CANDIDATES
    assert result.selected_memory_id is None
    assert result.safe_for_confirmation is False
    assert len(result.candidates) == 2


def test_resolver_bounds_candidate_input():
    first = make_memory("SQLite first", id="memory-1")
    second = make_memory("SQLite second", id="memory-2")
    resolver = MemoryTargetResolver(max_candidates=1)

    result = resolver.resolve_query("SQLite", (first, second))

    assert len(result.candidates) == 1
    assert result.candidates[0].memory.id == "memory-1"


def test_resolver_returns_no_match_for_empty_query():
    memory = make_memory("LuciferOS bruker SQLite", id="memory-1")
    resolver = MemoryTargetResolver()

    result = resolver.resolve_query("   ", (memory,))

    assert result.outcome == MemoryTargetResolutionOutcome.NO_MATCH


def test_memory_target_resolver_exports_are_public():
    import lucifer_os.memory as memory

    assert memory.MemoryTargetCandidate is MemoryTargetCandidate
    assert memory.MemoryTargetResolutionOutcome is MemoryTargetResolutionOutcome
    assert memory.MemoryTargetResolutionResult is MemoryTargetResolutionResult
    assert memory.MemoryTargetResolver is MemoryTargetResolver
