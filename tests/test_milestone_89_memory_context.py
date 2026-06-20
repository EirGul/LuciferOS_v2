import pytest

from lucifer_os.memory import (
    InMemoryMemoryStore,
    MemoryContextBuilder,
    MemoryQuery,
    MemoryRetrievalPurpose,
    MemoryRetrievalService,
    MemoryScope,
    MemoryService,
    MemoryType,
)


def build_search_results():
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
    return retrieval.search(
        MemoryQuery(
            text="LuciferOS PowerShell",
            scopes=(MemoryScope.PROJECT,),
            types=(MemoryType.PROJECT_STATE, MemoryType.PREFERENCE),
            purpose=MemoryRetrievalPurpose.PROJECT_ASSISTANCE,
            source="test-milestone-89",
            limit=5,
        )
    )


def test_memory_context_builder_rejects_invalid_limits():
    with pytest.raises(ValueError):
        MemoryContextBuilder(max_items=0)

    with pytest.raises(ValueError):
        MemoryContextBuilder(max_items=11)

    with pytest.raises(ValueError):
        MemoryContextBuilder(max_chars_per_item=39)

    with pytest.raises(ValueError):
        MemoryContextBuilder(max_chars_per_item=1001)

    with pytest.raises(ValueError):
        MemoryContextBuilder(max_total_chars=79)

    with pytest.raises(ValueError):
        MemoryContextBuilder(max_total_chars=4001)


def test_memory_context_builder_returns_empty_context_without_results():
    context = MemoryContextBuilder().build([])

    assert context.text == ""
    assert context.memory_ids == ()
    assert context.truncated is False
    assert context.is_empty is True


def test_memory_context_builder_builds_limited_context_text():
    results = build_search_results()
    context = MemoryContextBuilder(max_items=1).build(results)

    assert context.is_empty is False
    assert context.text.startswith("Relevant LuciferOS memory:")
    assert context.text.count("- [") == 1
    assert len(context.memory_ids) == 1
    assert context.truncated is False


def test_memory_context_builder_includes_type_scope_and_content_only():
    results = build_search_results()
    context = MemoryContextBuilder(max_items=2).build(results)

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

    results = MemoryRetrievalService(store).search(
        MemoryQuery(
            text="long",
            scopes=(MemoryScope.PROJECT,),
            types=(MemoryType.PROJECT_STATE,),
            purpose=MemoryRetrievalPurpose.PROJECT_ASSISTANCE,
            source="test-milestone-89",
            limit=1,
        )
    )
    context = MemoryContextBuilder(
        max_chars_per_item=50,
        max_total_chars=120,
    ).build(results)

    assert "…" in context.text
    assert len(context.text) < 120
