import pytest

from lucifer_os.memory import (
    InMemoryMemoryStore,
    MemoryContextBuilder,
    MemoryQuery,
    MemoryRetrievalOutcome,
    MemoryRetrievalPurpose,
    MemoryRetrievalService,
    MemoryScope,
    MemoryService,
    MemoryType,
)


def build_retrieval_result(
    *,
    text: str = "LuciferOS PowerShell",
    limit: int = 5,
    max_context_chars: int = 1200,
):
    store = InMemoryMemoryStore()
    service = MemoryService(store)

    first = service.add_memory(
        content="LuciferOS uses local Ollama through explicit runtime mode.",
        type=MemoryType.PROJECT_STATE,
        scope=MemoryScope.PROJECT,
    ).item
    second = service.add_memory(
        content="User prefers short PowerShell steps with A/B troubleshooting.",
        type=MemoryType.PREFERENCE,
        scope=MemoryScope.PROJECT,
    ).item

    assert first is not None
    assert second is not None

    retrieval = MemoryRetrievalService(store)
    return retrieval.retrieve(
        MemoryQuery(
            request_id="test-milestone-89",
            text=text,
            scopes=(MemoryScope.PROJECT,),
            types=(MemoryType.PROJECT_STATE, MemoryType.PREFERENCE),
            purpose=MemoryRetrievalPurpose.PROJECT_ASSISTANCE,
            source="test-milestone-89",
            limit=limit,
            max_context_chars=max_context_chars,
        )
    )


def test_memory_context_builder_rejects_invalid_limits():
    with pytest.raises(ValueError):
        MemoryContextBuilder(max_chars_per_item=39)

    with pytest.raises(ValueError):
        MemoryContextBuilder(max_chars_per_item=1001)

    with pytest.raises(TypeError):
        MemoryContextBuilder(max_items=1)

    with pytest.raises(TypeError):
        MemoryContextBuilder(max_total_chars=1200)


def test_memory_context_builder_returns_empty_context_without_matches():
    retrieval = build_retrieval_result(text="nonexistent")
    context = MemoryContextBuilder().build(retrieval)

    assert retrieval.outcome == MemoryRetrievalOutcome.NO_MATCH
    assert context.text == ""
    assert context.memory_ids == ()
    assert context.truncated is False
    assert context.is_empty is True


def test_memory_context_builder_builds_limited_context_text():
    retrieval = build_retrieval_result(limit=1)
    context = MemoryContextBuilder().build(retrieval)

    assert context.is_empty is False
    assert context.text.startswith("Relevant LuciferOS memory:")
    assert context.text.count("- [") == 1
    assert len(context.memory_ids) == 1
    assert context.truncated is False


def test_memory_context_builder_includes_type_scope_and_content_only():
    retrieval = build_retrieval_result()
    context = MemoryContextBuilder().build(retrieval)

    assert "[project_state/project]" in context.text
    assert "[preference/project]" in context.text
    assert "LuciferOS uses local Ollama" in context.text
    assert "User prefers short PowerShell steps" in context.text
    assert "metadata" not in context.text.lower()
    assert "audit" not in context.text.lower()


def test_memory_context_builder_trims_long_memory_content():
    store = InMemoryMemoryStore()
    service = MemoryService(store)
    item = service.add_memory(
        content="x" * 200,
        type=MemoryType.PROJECT_STATE,
        scope=MemoryScope.PROJECT,
        tags=("long",),
    ).item
    assert item is not None

    retrieval = MemoryRetrievalService(store).retrieve(
        MemoryQuery(
            request_id="test-milestone-89-long",
            text="long",
            scopes=(MemoryScope.PROJECT,),
            types=(MemoryType.PROJECT_STATE,),
            purpose=MemoryRetrievalPurpose.PROJECT_ASSISTANCE,
            source="test-milestone-89",
            limit=1,
            max_context_chars=120,
        )
    )
    context = MemoryContextBuilder(
        max_chars_per_item=50,
    ).build(retrieval)

    assert "…" in context.text
    assert len(context.text) <= 120
