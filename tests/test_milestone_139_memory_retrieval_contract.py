from dataclasses import FrozenInstanceError

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


def make_query(**overrides) -> MemoryQuery:
    values = {
        "text": "LuciferOS",
        "scopes": (MemoryScope.PROJECT,),
        "types": (MemoryType.PROJECT_STATE,),
        "purpose": MemoryRetrievalPurpose.PROJECT_ASSISTANCE,
        "source": "test-milestone-139",
        "limit": 5,
        "max_context_chars": 300,
    }
    values.update(overrides)
    return MemoryQuery(**values)


def build_store() -> InMemoryMemoryStore:
    store = InMemoryMemoryStore()
    service = MemoryService(store)
    service.add_memory(
        content="LuciferOS keeps retrieval deterministic and bounded.",
        type=MemoryType.PROJECT_STATE,
        scope=MemoryScope.PROJECT,
        tags=("luciferos", "retrieval"),
    )
    service.add_memory(
        content="LuciferOS uses explicit project memory boundaries.",
        type=MemoryType.PROJECT_STATE,
        scope=MemoryScope.PROJECT,
        tags=("luciferos", "scope"),
    )
    return store


def test_memory_query_requires_explicit_nonempty_read_boundary_fields():
    with pytest.raises(ValueError):
        make_query(text=" ")

    with pytest.raises(ValueError):
        make_query(scopes=())

    with pytest.raises(ValueError):
        make_query(types=())

    with pytest.raises(ValueError):
        make_query(source=" ")

    with pytest.raises(ValueError):
        make_query(max_context_chars=79)

    with pytest.raises(ValueError):
        make_query(max_context_chars=4001)


def test_memory_query_rejects_duplicate_scope_and_type_filters():
    with pytest.raises(ValueError):
        make_query(scopes=(MemoryScope.PROJECT, MemoryScope.PROJECT))

    with pytest.raises(ValueError):
        make_query(types=(MemoryType.PROJECT_STATE, MemoryType.PROJECT_STATE))


def test_memory_query_requires_supported_retrieval_purpose():
    with pytest.raises(ValueError):
        make_query(purpose="project_assistance")


def test_retrieval_returns_immutable_minimal_memory_snapshots():
    results = MemoryRetrievalService(build_store()).search(make_query())

    assert len(results) == 2
    snapshot = results[0].item
    assert snapshot.content
    assert snapshot.id
    assert snapshot.type == MemoryType.PROJECT_STATE
    assert snapshot.scope == MemoryScope.PROJECT
    assert not hasattr(snapshot, "metadata")
    assert not hasattr(snapshot, "tags")
    assert not hasattr(snapshot, "source")

    with pytest.raises(FrozenInstanceError):
        snapshot.content = "mutated"


def test_retrieval_never_returns_records_outside_explicit_scope_or_type_filters():
    store = build_store()
    service = MemoryService(store)
    service.add_memory(
        content="LuciferOS global preference must not leak into project retrieval.",
        type=MemoryType.PREFERENCE,
        scope=MemoryScope.GLOBAL,
        tags=("luciferos",),
        confirmed=True,
    )

    results = MemoryRetrievalService(store).search(make_query())

    assert results
    assert all(result.item.scope == MemoryScope.PROJECT for result in results)
    assert all(result.item.type == MemoryType.PROJECT_STATE for result in results)


def test_context_builder_enforces_total_budget_with_stable_prefix_selection():
    results = MemoryRetrievalService(build_store()).search(make_query())
    context = MemoryContextBuilder(
        max_items=5,
        max_chars_per_item=240,
        max_total_chars=110,
    ).build(results)

    assert context.truncated is True
    assert len(context.text) <= 110
    assert len(context.memory_ids) == 1
    assert context.memory_ids == (results[0].item.id,)


def test_context_builder_returns_empty_bounded_context_when_first_item_cannot_fit():
    store = InMemoryMemoryStore()
    service = MemoryService(store)
    service.add_memory(
        content="x" * 500,
        type=MemoryType.PROJECT_STATE,
        scope=MemoryScope.PROJECT,
        tags=("oversized",),
    )

    results = MemoryRetrievalService(store).search(
        make_query(text="oversized")
    )
    context = MemoryContextBuilder(
        max_items=1,
        max_chars_per_item=240,
        max_total_chars=80,
    ).build(results)

    assert context.text == ""
    assert context.memory_ids == ()
    assert context.truncated is True

