import pytest

from lucifer_os.memory import InMemoryMemoryStore, MemoryScope, MemoryService, MemoryType
from lucifer_os.memory.learning import LearningService
from lucifer_os.memory.models import MemoryItem


def test_memory_item_requires_content():
    with pytest.raises(ValueError):
        MemoryItem(content='   ', type=MemoryType.FACT, scope=MemoryScope.GLOBAL)


def test_memory_item_validates_confidence():
    with pytest.raises(ValueError):
        MemoryItem(content='test', type=MemoryType.FACT, scope=MemoryScope.GLOBAL, confidence=1.5)


def test_memory_service_can_add_list_get_and_delete_memory():
    store = InMemoryMemoryStore()
    service = MemoryService(store)

    item = service.add_memory(
        content='LuciferOS has a memory subsystem skeleton.',
        type=MemoryType.PROJECT_STATE,
        scope=MemoryScope.PROJECT,
        tags=('luciferos', 'memory'),
    )

    assert service.get_memory(item.id) == item
    assert service.list_memories(scope=MemoryScope.PROJECT) == [item]
    assert service.list_memories(type=MemoryType.PROJECT_STATE) == [item]
    assert service.delete_memory(item.id) is True
    assert service.get_memory(item.id) is None
    assert service.delete_memory(item.id) is False


def test_learning_service_only_accepts_explicit_learning_requests():
    service = MemoryService(InMemoryMemoryStore())
    learning = LearningService(service)

    assert learning.is_explicit_learning_request('husk at jeg liker korte svar') is True
    assert learning.is_explicit_learning_request('lær at status betyr full oversikt') is True
    assert learning.is_explicit_learning_request('hva kan du huske?') is False


def test_learning_service_can_store_explicit_memory():
    service = MemoryService(InMemoryMemoryStore())
    learning = LearningService(service)

    item = learning.learn_explicit_memory('husk at Lucifer skal være lokal først')

    assert item is not None
    assert item.content == 'Lucifer skal være lokal først'
    assert item.type == MemoryType.USER_INSTRUCTION
    assert item.scope == MemoryScope.GLOBAL
    assert item.source == 'explicit-learning-request'
    assert service.list_memories() == [item]
