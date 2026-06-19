from lucifer_os.memory.models import MemoryItem, MemoryScope, MemoryType
from lucifer_os.memory.sqlite_store import SQLiteMemoryStore
from lucifer_os.memory.store import MemoryStore


def test_sqlite_memory_store_implements_memory_store_contract(tmp_path):
    store = SQLiteMemoryStore(tmp_path / "memory.sqlite3")

    try:
        assert isinstance(store, MemoryStore)
    finally:
        store.close()


def test_sqlite_memory_store_adds_and_gets_memory_item(tmp_path):
    store = SQLiteMemoryStore(tmp_path / "memory.sqlite3")
    item = MemoryItem(
        content="LuciferOS uses explicit memory writes.",
        type=MemoryType.FACT,
        scope=MemoryScope.PROJECT,
        source="test",
        confidence=0.8,
        tags=("memory", "sqlite"),
        metadata={"project": "luciferos_v2"},
    )

    try:
        returned = store.add(item)
        loaded = store.get(item.id)

        assert returned == item
        assert loaded == item
        assert loaded is not None
        assert loaded.metadata == {"project": "luciferos_v2"}
        assert loaded.tags == ("memory", "sqlite")
        assert loaded.confidence == 0.8
    finally:
        store.close()


def test_sqlite_memory_store_persists_across_instances(tmp_path):
    db_path = tmp_path / "memory.sqlite3"
    first_store = SQLiteMemoryStore(db_path)
    item = MemoryItem(
        content="Persistent memory survives a new store instance.",
        type=MemoryType.PROJECT_STATE,
        scope=MemoryScope.PROJECT,
    )

    first_store.add(item)
    first_store.close()

    second_store = SQLiteMemoryStore(db_path)

    try:
        loaded = second_store.get(item.id)

        assert loaded == item
    finally:
        second_store.close()


def test_sqlite_memory_store_lists_and_filters_items(tmp_path):
    store = SQLiteMemoryStore(tmp_path / "memory.sqlite3")
    global_fact = MemoryItem(
        content="Global fact.",
        type=MemoryType.FACT,
        scope=MemoryScope.GLOBAL,
    )
    project_preference = MemoryItem(
        content="Project preference.",
        type=MemoryType.PREFERENCE,
        scope=MemoryScope.PROJECT,
    )
    project_fact = MemoryItem(
        content="Project fact.",
        type=MemoryType.FACT,
        scope=MemoryScope.PROJECT,
    )

    try:
        store.add(global_fact)
        store.add(project_preference)
        store.add(project_fact)

        assert store.list() == [global_fact, project_preference, project_fact]
        assert store.list(scope=MemoryScope.PROJECT) == [project_preference, project_fact]
        assert store.list(type=MemoryType.FACT) == [global_fact, project_fact]
        assert store.list(scope=MemoryScope.PROJECT, type=MemoryType.FACT) == [project_fact]
    finally:
        store.close()


def test_sqlite_memory_store_deletes_items(tmp_path):
    store = SQLiteMemoryStore(tmp_path / "memory.sqlite3")
    item = MemoryItem(
        content="Delete me.",
        type=MemoryType.TASK_CONTEXT,
        scope=MemoryScope.SESSION,
    )

    try:
        store.add(item)

        assert store.get(item.id) == item
        assert store.delete(item.id) is True
        assert store.get(item.id) is None
        assert store.delete(item.id) is False
    finally:
        store.close()


def test_sqlite_memory_store_does_not_change_inmemory_contract():
    from lucifer_os.memory.store import InMemoryMemoryStore

    store = InMemoryMemoryStore()
    item = MemoryItem(
        content="In-memory store still works.",
        type=MemoryType.FACT,
        scope=MemoryScope.SESSION,
    )

    assert store.add(item) == item
    assert store.get(item.id) == item
    assert store.list(scope=MemoryScope.SESSION) == [item]
    assert store.delete(item.id) is True
