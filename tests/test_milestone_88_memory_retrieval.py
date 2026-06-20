import pytest

from lucifer_os.memory import (
    InMemoryMemoryStore,
    MemoryQuery,
    MemoryRetrievalPurpose,
    MemoryRetrievalService,
    MemoryScope,
    MemoryService,
    MemoryType,
)


ALL_SCOPES = (
    MemoryScope.PROJECT,
    MemoryScope.GLOBAL,
    MemoryScope.SESSION,
)
ALL_TYPES = (
    MemoryType.PROJECT_STATE,
    MemoryType.PREFERENCE,
    MemoryType.TASK_CONTEXT,
)


def query(
    text: str,
    *,
    scopes: tuple[MemoryScope, ...] = ALL_SCOPES,
    types: tuple[MemoryType, ...] = ALL_TYPES,
    limit: int = 5,
) -> MemoryQuery:
    return MemoryQuery(
        text=text,
        scopes=scopes,
        types=types,
        purpose=MemoryRetrievalPurpose.EXPLICIT_MEMORY_SEARCH,
        source="test-milestone-88",
        limit=limit,
    )


def build_store_with_memories():
    store = InMemoryMemoryStore()
    service = MemoryService(store)

    service.add_memory(
        content="LuciferOS uses local Ollama for local AI mode.",
        type=MemoryType.PROJECT_STATE,
        scope=MemoryScope.PROJECT,
        tags=("luciferos", "ollama", "fixture"),
    )
    service.add_memory(
        content="User prefers short technical PowerShell steps.",
        type=MemoryType.PREFERENCE,
        scope=MemoryScope.GLOBAL,
        confirmed=True,
        tags=("powershell", "preference", "fixture"),
    )
    service.add_memory(
        content="Temporary session note about HUD testing.",
        type=MemoryType.TASK_CONTEXT,
        scope=MemoryScope.SESSION,
        tags=("hud", "fixture"),
    )

    return store


def test_memory_query_rejects_invalid_limits():
    with pytest.raises(ValueError):
        query("fixture", limit=0)

    with pytest.raises(ValueError):
        query("fixture", limit=26)


def test_memory_retrieval_filters_by_text():
    retrieval = MemoryRetrievalService(build_store_with_memories())

    results = retrieval.search(query("Ollama local"))

    assert len(results) == 1
    assert results[0].item.content == "LuciferOS uses local Ollama for local AI mode."
    assert results[0].score == 1.0
    assert results[0].matched_terms == ("ollama", "local")


def test_memory_retrieval_filters_by_scope():
    retrieval = MemoryRetrievalService(build_store_with_memories())

    results = retrieval.search(
        query("fixture", scopes=(MemoryScope.PROJECT,))
    )

    assert len(results) == 1
    assert results[0].item.scope == MemoryScope.PROJECT


def test_memory_retrieval_filters_by_type():
    retrieval = MemoryRetrievalService(build_store_with_memories())

    results = retrieval.search(
        query("fixture", types=(MemoryType.PREFERENCE,))
    )

    assert len(results) == 1
    assert results[0].item.type == MemoryType.PREFERENCE


def test_memory_retrieval_respects_limit():
    retrieval = MemoryRetrievalService(build_store_with_memories())

    results = retrieval.search(query("fixture", limit=2))

    assert len(results) == 2


def test_memory_retrieval_returns_empty_when_no_terms_match():
    retrieval = MemoryRetrievalService(build_store_with_memories())

    results = retrieval.search(query("nonexistent"))

    assert results == []
