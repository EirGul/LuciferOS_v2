from lucifer_os.memory import (
    MemoryItem,
    MemoryScope,
    MemoryTargetResolutionOutcome,
    MemoryTargetResolutionResult,
    MemoryTargetResolver,
    MemoryType,
)


def make_memory(
    content: str,
    id: str,
    tags: tuple[str, ...] = (),
    metadata: dict | None = None,
) -> MemoryItem:
    return MemoryItem(
        id=id,
        content=content,
        type=MemoryType.PREFERENCE,
        scope=MemoryScope.PROJECT,
        source="test",
        tags=tags,
        metadata=metadata or {},
    )


def test_resolver_empty_memory_id_returns_no_match():
    resolver = MemoryTargetResolver()
    memory = make_memory("LuciferOS bruker SQLite", id="memory-1")

    result = resolver.resolve_explicit_id("   ", (memory,))

    assert result.outcome == MemoryTargetResolutionOutcome.NO_MATCH
    assert result.selected_memory_id is None
    assert result.safe_for_confirmation is False


def test_resolver_empty_candidate_list_returns_no_match_for_explicit_id():
    resolver = MemoryTargetResolver()

    result = resolver.resolve_explicit_id("memory-1", ())

    assert result.outcome == MemoryTargetResolutionOutcome.NO_MATCH
    assert result.selected_memory_id is None
    assert result.candidates == ()


def test_resolver_empty_candidate_list_returns_no_match_for_query():
    resolver = MemoryTargetResolver()

    result = resolver.resolve_query("SQLite", ())

    assert result.outcome == MemoryTargetResolutionOutcome.NO_MATCH
    assert result.selected_memory_id is None
    assert result.candidates == ()


def test_resolver_does_not_match_metadata_before_metadata_matching_is_implemented():
    resolver = MemoryTargetResolver()
    memory = make_memory(
        "LuciferOS bruker vanlig innhold",
        id="memory-1",
        metadata={"topic": "SQLite"},
    )

    result = resolver.resolve_query("SQLite", (memory,))

    assert result.outcome == MemoryTargetResolutionOutcome.NO_MATCH
    assert result.selected_memory_id is None


def test_resolver_does_not_match_tags_before_tag_matching_is_implemented():
    resolver = MemoryTargetResolver()
    memory = make_memory(
        "LuciferOS bruker vanlig innhold",
        id="memory-1",
        tags=("SQLite",),
    )

    result = resolver.resolve_query("SQLite", (memory,))

    assert result.outcome == MemoryTargetResolutionOutcome.NO_MATCH
    assert result.selected_memory_id is None


def test_multiple_candidates_are_never_safe_for_confirmation():
    resolver = MemoryTargetResolver()
    first = make_memory("SQLite first", id="memory-1")
    second = make_memory("SQLite second", id="memory-2")

    result = resolver.resolve_query("SQLite", (first, second))

    assert result.outcome == MemoryTargetResolutionOutcome.MULTIPLE_CANDIDATES
    assert result.safe_for_confirmation is False
    assert result.selected_memory_id is None


def test_explicit_id_resolution_respects_max_candidates_bound():
    resolver = MemoryTargetResolver(max_candidates=1)
    first = make_memory("first", id="memory-1")
    second = make_memory("second", id="memory-2")

    result = resolver.resolve_explicit_id("memory-2", (first, second))

    assert result.outcome == MemoryTargetResolutionOutcome.NO_MATCH
    assert result.selected_memory_id is None


def test_query_resolution_respects_max_candidates_bound():
    resolver = MemoryTargetResolver(max_candidates=1)
    first = make_memory("no match", id="memory-1")
    second = make_memory("SQLite second", id="memory-2")

    result = resolver.resolve_query("SQLite", (first, second))

    assert result.outcome == MemoryTargetResolutionOutcome.NO_MATCH
    assert result.selected_memory_id is None


def test_safe_result_invariant_requires_selected_memory_id():
    try:
        MemoryTargetResolutionResult(
            outcome=MemoryTargetResolutionOutcome.SINGLE_SAFE_MATCH,
            explanation="invalid safe result",
            safe_for_confirmation=True,
        )
    except ValueError as exc:
        assert "selected_memory_id" in str(exc)
    else:
        raise AssertionError("Expected safe result without selected_memory_id to fail.")


def test_resolver_does_not_mutate_memory_items():
    resolver = MemoryTargetResolver()
    memory = make_memory("LuciferOS bruker SQLite", id="memory-1")
    before = memory

    result = resolver.resolve_query("SQLite", (memory,))

    assert result.outcome == MemoryTargetResolutionOutcome.SINGLE_SAFE_MATCH
    assert memory == before
    assert result.candidates[0].memory == before
