from lucifer_os.memory import MemoryScope, MemoryService, MemoryType, SQLiteMemoryStore


def test_memory_service_persists_added_memory_across_sqlite_store_instances(tmp_path):
    db_path = tmp_path / "memory-service.sqlite3"
    first_store = SQLiteMemoryStore(db_path)
    first_service = MemoryService(first_store)

    add_result = first_service.add_memory(
        content="Persistent service memory.",
        type=MemoryType.PROJECT_STATE,
        scope=MemoryScope.PROJECT,
        source="test",
        confidence=0.85,
        tags=("service", "sqlite"),
        metadata={"milestone": 97},
    )
    item = add_result.item
    assert item is not None
    first_store.close()

    second_store = SQLiteMemoryStore(db_path)
    second_service = MemoryService(second_store)

    try:
        loaded = second_service.get_memory(item.id)

        assert loaded == item
        assert loaded is not None
        assert loaded.tags == ("service", "sqlite")
        assert loaded.metadata == {"milestone": 97}
    finally:
        second_store.close()


def test_memory_service_persists_updated_memory_across_sqlite_store_instances(tmp_path):
    db_path = tmp_path / "memory-service-update.sqlite3"
    first_store = SQLiteMemoryStore(db_path)
    first_service = MemoryService(first_store)

    add_result = first_service.add_memory(
        content="Original persistent memory.",
        type=MemoryType.PROJECT_STATE,
        scope=MemoryScope.PROJECT,
    )
    item = add_result.item
    assert item is not None
    first_store.close()

    second_store = SQLiteMemoryStore(db_path)
    second_service = MemoryService(second_store)

    update_result = second_service.update_memory(
        memory_id=item.id,
        content="Updated persistent memory.",
        type=MemoryType.CORRECTION,
        scope=MemoryScope.PROJECT,
        source="test",
        confidence=0.95,
        tags=("updated",),
        metadata={"corrected": True},
    )
    updated_item = update_result.item
    assert updated_item is not None
    second_store.close()

    third_store = SQLiteMemoryStore(db_path)
    third_service = MemoryService(third_store)

    try:
        loaded = third_service.get_memory(item.id)

        assert loaded == updated_item
        assert loaded is not None
        assert loaded.id == item.id
        assert loaded.content == "Updated persistent memory."
        assert loaded.type == MemoryType.CORRECTION
        assert loaded.scope == MemoryScope.PROJECT
        assert loaded.created_at == item.created_at
        assert loaded.updated_at != item.updated_at
    finally:
        third_store.close()


def test_memory_service_persists_confirmed_delete_across_sqlite_store_instances(tmp_path):
    db_path = tmp_path / "memory-service-delete.sqlite3"
    first_store = SQLiteMemoryStore(db_path)
    first_service = MemoryService(first_store)

    add_result = first_service.add_memory(
        content="Memory that will be deleted.",
        type=MemoryType.PROJECT_STATE,
        scope=MemoryScope.PROJECT,
    )
    item = add_result.item
    assert item is not None
    first_store.close()

    second_store = SQLiteMemoryStore(db_path)
    second_service = MemoryService(second_store)

    delete_result = second_service.delete_memory(
        memory_id=item.id,
        confirmed=True,
        source="test",
    )

    assert delete_result.allowed is True
    assert delete_result.requires_confirmation is False
    assert delete_result.deleted is True
    second_store.close()

    third_store = SQLiteMemoryStore(db_path)
    third_service = MemoryService(third_store)

    try:
        assert third_service.get_memory(item.id) is None
        assert third_service.list_memories() == []
    finally:
        third_store.close()


def test_memory_service_persists_confirmed_high_impact_update_with_sqlite(tmp_path):
    db_path = tmp_path / "memory-service-high-impact.sqlite3"
    first_store = SQLiteMemoryStore(db_path)
    first_service = MemoryService(first_store)

    add_result = first_service.add_memory(
        content="Original project state.",
        type=MemoryType.PROJECT_STATE,
        scope=MemoryScope.PROJECT,
    )
    item = add_result.item
    assert item is not None

    update_result = first_service.update_memory(
        memory_id=item.id,
        content="Always keep LuciferOS local-first.",
        type=MemoryType.USER_INSTRUCTION,
        scope=MemoryScope.GLOBAL,
        confirmed=True,
    )
    updated_item = update_result.item
    assert updated_item is not None
    first_store.close()

    second_store = SQLiteMemoryStore(db_path)
    second_service = MemoryService(second_store)

    try:
        loaded = second_service.get_memory(item.id)

        assert loaded == updated_item
        assert loaded is not None
        assert loaded.type == MemoryType.USER_INSTRUCTION
        assert loaded.scope == MemoryScope.GLOBAL
        assert loaded.content == "Always keep LuciferOS local-first."
    finally:
        second_store.close()
