import pytest

from lucifer_os.memory import (
    InMemoryPendingMemoryActionStore,
    MemoryCommandType,
    PendingMemoryAction,
    PendingMemoryActionStore,
    PendingMemoryActionType,
)


def test_pending_memory_action_requires_explanation_and_source_text():
    with pytest.raises(ValueError, match="explanation"):
        PendingMemoryAction(
            action_type=PendingMemoryActionType.REMEMBER,
            command_type=MemoryCommandType.REMEMBER,
            explanation="   ",
            source_text="husk at LuciferOS er local-first",
        )

    with pytest.raises(ValueError, match="source text"):
        PendingMemoryAction(
            action_type=PendingMemoryActionType.REMEMBER,
            command_type=MemoryCommandType.REMEMBER,
            explanation="Store this memory after confirmation.",
            source_text="   ",
        )


def test_pending_memory_action_captures_confirmation_payload():
    action = PendingMemoryAction(
        action_type=PendingMemoryActionType.CORRECT,
        command_type=MemoryCommandType.CORRECT,
        explanation="Correct selected memory after confirmation.",
        source_text="korriger minne LuciferOS skal bruke SQLite",
        memory_id="memory-1",
        proposed_content="LuciferOS skal bruke SQLite",
        metadata={"scope": "project"},
    )

    assert action.action_type == PendingMemoryActionType.CORRECT
    assert action.command_type == MemoryCommandType.CORRECT
    assert action.memory_id == "memory-1"
    assert action.proposed_content == "LuciferOS skal bruke SQLite"
    assert action.requires_confirmation is True
    assert action.metadata == {"scope": "project"}
    assert action.id
    assert action.created_at


def test_inmemory_pending_memory_action_store_sets_gets_and_clears_action():
    store = InMemoryPendingMemoryActionStore()
    action = PendingMemoryAction(
        action_type=PendingMemoryActionType.DELETE,
        command_type=MemoryCommandType.DELETE,
        explanation="Delete selected memory after confirmation.",
        source_text="slett minne memory-1",
        memory_id="memory-1",
    )

    assert isinstance(store, PendingMemoryActionStore)
    assert store.get() is None
    assert store.set(action) == action
    assert store.get() == action
    assert store.clear() == action
    assert store.get() is None
    assert store.clear() is None


def test_inmemory_pending_memory_action_store_replaces_existing_action():
    store = InMemoryPendingMemoryActionStore()
    first = PendingMemoryAction(
        action_type=PendingMemoryActionType.REMEMBER,
        command_type=MemoryCommandType.REMEMBER,
        explanation="Store first memory after confirmation.",
        source_text="husk at first",
        proposed_content="first",
    )
    second = PendingMemoryAction(
        action_type=PendingMemoryActionType.REMEMBER,
        command_type=MemoryCommandType.REMEMBER,
        explanation="Store second memory after confirmation.",
        source_text="husk at second",
        proposed_content="second",
    )

    store.set(first)
    store.set(second)

    assert store.get() == second


def test_pending_memory_action_exports_are_public():
    import lucifer_os.memory as memory

    assert memory.PendingMemoryAction is PendingMemoryAction
    assert memory.PendingMemoryActionType is PendingMemoryActionType
    assert memory.PendingMemoryActionStore is PendingMemoryActionStore
    assert memory.InMemoryPendingMemoryActionStore is InMemoryPendingMemoryActionStore
