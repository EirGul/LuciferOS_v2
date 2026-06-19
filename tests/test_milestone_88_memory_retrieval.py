import pytest

from lucifer_os.memory import (
    InMemoryMemoryStore,
    MemoryQuery,
    MemoryRetrievalService,
    MemoryScope,
    MemoryService,
    MemoryType,
)


def build_store_with_memories():
    store = InMemoryMemoryStore()
    service = MemoryService(store)

    service.add_memory(
        content='LuciferOS uses local Ollama for local AI mode.',
        type=MemoryType.PROJECT_STATE,
        scope=MemoryScope.PROJECT,
        tags=('luciferos', 'ollama'),
    )
    service.add_memory(
        content='User prefers short technical PowerShell steps.',
        type=MemoryType.PREFERENCE,
        scope=MemoryScope.GLOBAL,
        confirmed=True,
        tags=('powershell', 'preference'),
    )
    service.add_memory(
        content='Temporary session note about HUD testing.',
        type=MemoryType.TASK_CONTEXT,
        scope=MemoryScope.SESSION,
        tags=('hud',),
    )

    return store


def test_memory_query_rejects_invalid_limits():
    with pytest.raises(ValueError):
        MemoryQuery(limit=0)

    with pytest.raises(ValueError):
        MemoryQuery(limit=26)


def test_memory_retrieval_filters_by_text():
    retrieval = MemoryRetrievalService(build_store_with_memories())

    results = retrieval.search(MemoryQuery(text='Ollama local'))

    assert len(results) == 1
    assert results[0].item.content == 'LuciferOS uses local Ollama for local AI mode.'
    assert results[0].score == 1.0
    assert results[0].matched_terms == ('ollama', 'local')


def test_memory_retrieval_filters_by_scope():
    retrieval = MemoryRetrievalService(build_store_with_memories())

    results = retrieval.search(MemoryQuery(scopes=(MemoryScope.PROJECT,)))

    assert len(results) == 1
    assert results[0].item.scope == MemoryScope.PROJECT


def test_memory_retrieval_filters_by_type():
    retrieval = MemoryRetrievalService(build_store_with_memories())

    results = retrieval.search(MemoryQuery(types=(MemoryType.PREFERENCE,)))

    assert len(results) == 1
    assert results[0].item.type == MemoryType.PREFERENCE


def test_memory_retrieval_respects_limit():
    retrieval = MemoryRetrievalService(build_store_with_memories())

    results = retrieval.search(MemoryQuery(limit=2))

    assert len(results) == 2


def test_memory_retrieval_returns_empty_when_no_terms_match():
    retrieval = MemoryRetrievalService(build_store_with_memories())

    results = retrieval.search(MemoryQuery(text='nonexistent'))

    assert results == []
