import pytest

from lucifer_os.memory.models import MemoryItem, MemoryScope, MemoryType
from lucifer_os.memory.sqlite_store import SQLiteMemoryStore
from lucifer_os.memory.store import InMemoryMemoryStore


@pytest.fixture(params=["inmemory", "sqlite"])
def memory_store(request, tmp_path):
    if request.param == "inmemory":
        yield InMemoryMemoryStore()
        return

    store = SQLiteMemoryStore(tmp_path / "update-contract.sqlite3")
    try:
        yield store
    finally:
        store.close()


def test_memory_store_updates_existing_item_without_changing_id(memory_store):
    original = MemoryItem(
        id="memory-1",
        content="Original memory.",
        type=MemoryType.FACT,
        scope=MemoryScope.PROJECT,
        source="test",
        confidence=0.7,
        tags=("old",),
        metadata={"version": 1},
        created_at="2026-01-01T00:00:00+00:00",
        updated_at="2026-01-01T00:00:00+00:00",
    )
    corrected = MemoryItem(
        id=original.id,
        content="Corrected memory.",
        type=MemoryType.CORRECTION,
        scope=MemoryScope.PROJECT,
        source="test",
        confidence=0.95,
        tags=("new", "corrected"),
        metadata={"version": 2, "corrected": True},
        created_at=original.created_at,
        updated_at="2026-01-02T00:00:00+00:00",
    )

    memory_store.add(original)

    assert memory_store.update(corrected) is True
    assert memory_store.get(original.id) == corrected
    assert memory_store.list() == [corrected]


def test_memory_store_update_returns_false_for_missing_item(memory_store):
    missing = MemoryItem(
        id="missing-memory",
        content="This item was never stored.",
        type=MemoryType.FACT,
        scope=MemoryScope.PROJECT,
    )

    assert memory_store.update(missing) is False
    assert memory_store.get(missing.id) is None
    assert memory_store.list() == []


def test_memory_store_update_preserves_scope_and_type_filtering(memory_store):
    item = MemoryItem(
        id="memory-2",
        content="Stored as project fact.",
        type=MemoryType.FACT,
        scope=MemoryScope.PROJECT,
        created_at="2026-01-01T00:00:00+00:00",
        updated_at="2026-01-01T00:00:00+00:00",
    )
    updated = MemoryItem(
        id=item.id,
        content="Updated as global preference.",
        type=MemoryType.PREFERENCE,
        scope=MemoryScope.GLOBAL,
        created_at=item.created_at,
        updated_at="2026-01-03T00:00:00+00:00",
    )

    memory_store.add(item)
    assert memory_store.update(updated) is True

    assert memory_store.list(scope=MemoryScope.PROJECT) == []
    assert memory_store.list(type=MemoryType.FACT) == []
    assert memory_store.list(scope=MemoryScope.GLOBAL, type=MemoryType.PREFERENCE) == [updated]


def test_memory_store_update_is_part_of_store_contract():
    store = InMemoryMemoryStore()

    assert hasattr(store, "update")
    assert callable(store.update)
