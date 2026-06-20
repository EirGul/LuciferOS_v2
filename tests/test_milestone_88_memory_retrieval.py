import pytest

from lucifer_os.memory import (
    InMemoryMemoryStore,
    MemoryQuery,
    MemoryRetrievalOutcome,
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
        request_id=f"test-milestone-88-{text}",
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

    result = retrieval.retrieve(query("Ollama local"))

    assert result.outcome == MemoryRetrievalOutcome.MATCHED
    assert result.result_count == 1
    assert result.matches[0].item.content == "LuciferOS uses local Ollama for local AI mode."
    assert result.matches[0].score == 1.0
    assert result.matches[0].matched_terms == ("ollama", "local")


def test_memory_retrieval_filters_by_scope():
    retrieval = MemoryRetrievalService(build_store_with_memories())

    result = retrieval.retrieve(
        query("fixture", scopes=(MemoryScope.PROJECT,))
    )

    assert result.outcome == MemoryRetrievalOutcome.MATCHED
    assert result.result_count == 1
    assert result.matches[0].item.scope == MemoryScope.PROJECT


def test_memory_retrieval_filters_by_type():
    retrieval = MemoryRetrievalService(build_store_with_memories())

    result = retrieval.retrieve(
        query("fixture", types=(MemoryType.PREFERENCE,))
    )

    assert result.outcome == MemoryRetrievalOutcome.MATCHED
    assert result.result_count == 1
    assert result.matches[0].item.type == MemoryType.PREFERENCE


def test_memory_retrieval_respects_limit():
    retrieval = MemoryRetrievalService(build_store_with_memories())

    result = retrieval.retrieve(query("fixture", limit=2))

    assert result.outcome == MemoryRetrievalOutcome.MATCHED
    assert result.result_count == 2
    assert len(result.matches) == 2


def test_memory_retrieval_returns_no_match_when_no_terms_match():
    retrieval = MemoryRetrievalService(build_store_with_memories())

    result = retrieval.retrieve(query("nonexistent"))

    assert result.outcome == MemoryRetrievalOutcome.NO_MATCH
    assert result.reason_code == "retrieval_no_match"
    assert result.matches == ()
