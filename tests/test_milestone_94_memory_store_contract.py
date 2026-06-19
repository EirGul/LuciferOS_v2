import pytest

from lucifer_os.memory import SQLiteMemoryStore
from lucifer_os.memory.models import MemoryItem, MemoryScope, MemoryType
from lucifer_os.memory.service import MemoryService
from lucifer_os.memory.store import InMemoryMemoryStore


@pytest.fixture(params=["inmemory", "sqlite"])
def memory_store(request, tmp_path):
    if request.param == "inmemory":
        yield InMemoryMemoryStore()
        return

    store = SQLiteMemoryStore(tmp_path / "contract.sqlite3")
    try:
        yield store
    finally:
        store.close()


def test_memory_stores_share_add_get_list_delete_contract(memory_store):
    item = MemoryItem(
        content="Shared store contract.",
        type=MemoryType.FACT,
        scope=MemoryScope.PROJECT,
        source="contract-test",
        confidence=0.9,
        tags=("contract", "memory"),
        metadata={"milestone": 94},
    )

    assert memory_store.add(item) == item
    assert memory_store.get(item.id) == item
    assert memory_store.list() == [item]
    assert memory_store.list(scope=MemoryScope.PROJECT) == [item]
    assert memory_store.list(type=MemoryType.FACT) == [item]
    assert memory_store.delete(item.id) is True
    assert memory_store.get(item.id) is None
    assert memory_store.delete(item.id) is False


def test_memory_stores_preserve_unicode_tags_and_metadata(memory_store):
    item = MemoryItem(
        content="Husk norsk tekst: kjøkken, sjøkken, læring og Lucifer.",
        type=MemoryType.USER_INSTRUCTION,
        scope=MemoryScope.GLOBAL,
        source="user",
        tags=("norsk", "språk", "lucifer"),
        metadata={
            "project": "LuciferOS_v2",
            "nested": {"æøå": "ÆØÅ"},
            "count": 3,
        },
    )

    memory_store.add(item)
    loaded = memory_store.get(item.id)

    assert loaded == item
    assert loaded is not None
    assert loaded.content == item.content
    assert loaded.tags == item.tags
    assert loaded.metadata == item.metadata


def test_memory_stores_filter_scope_and_type_together(memory_store):
    global_fact = MemoryItem(
        content="Global fact.",
        type=MemoryType.FACT,
        scope=MemoryScope.GLOBAL,
    )
    project_fact = MemoryItem(
        content="Project fact.",
        type=MemoryType.FACT,
        scope=MemoryScope.PROJECT,
    )
    project_preference = MemoryItem(
        content="Project preference.",
        type=MemoryType.PREFERENCE,
        scope=MemoryScope.PROJECT,
    )

    memory_store.add(global_fact)
    memory_store.add(project_fact)
    memory_store.add(project_preference)

    assert memory_store.list(scope=MemoryScope.PROJECT, type=MemoryType.FACT) == [project_fact]
    assert memory_store.list(scope=MemoryScope.GLOBAL, type=MemoryType.PREFERENCE) == []


def test_memory_service_works_with_sqlite_memory_store(tmp_path):
    store = SQLiteMemoryStore(tmp_path / "service.sqlite3")
    service = MemoryService(store=store)

    try:
        result = service.add_memory(
            content="SQLite store works behind MemoryService.",
            type=MemoryType.PROJECT_STATE,
            scope=MemoryScope.PROJECT,
            source="test",
        )

        assert result.allowed is True
        assert result.requires_confirmation is False
        assert result.item is not None
        assert service.get_memory(result.item.id) == result.item
        assert service.list_memories(scope=MemoryScope.PROJECT) == [result.item]

        delete_result = service.delete_memory(result.item.id, confirmed=True, source="test")

        assert delete_result.allowed is True
        assert delete_result.deleted is True
        assert service.get_memory(result.item.id) is None
    finally:
        store.close()


def test_sqlite_memory_store_is_public_memory_export():
    import lucifer_os.memory as memory

    assert memory.SQLiteMemoryStore is SQLiteMemoryStore
