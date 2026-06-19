from __future__ import annotations

from abc import ABC, abstractmethod

from lucifer_os.memory.models import MemoryItem, MemoryScope, MemoryType


class MemoryStore(ABC):
    @abstractmethod
    def add(self, item: MemoryItem) -> MemoryItem:
        raise NotImplementedError

    @abstractmethod
    def get(self, memory_id: str) -> MemoryItem | None:
        raise NotImplementedError

    @abstractmethod
    def list(self, scope: MemoryScope | None = None, type: MemoryType | None = None) -> list[MemoryItem]:
        raise NotImplementedError

    @abstractmethod
    def delete(self, memory_id: str) -> bool:
        raise NotImplementedError


class InMemoryMemoryStore(MemoryStore):
    def __init__(self) -> None:
        self._items: dict[str, MemoryItem] = {}

    def add(self, item: MemoryItem) -> MemoryItem:
        self._items[item.id] = item
        return item

    def get(self, memory_id: str) -> MemoryItem | None:
        return self._items.get(memory_id)

    def list(self, scope: MemoryScope | None = None, type: MemoryType | None = None) -> list[MemoryItem]:
        items = list(self._items.values())
        if scope is not None:
            items = [item for item in items if item.scope == scope]
        if type is not None:
            items = [item for item in items if item.type == type]
        return items

    def delete(self, memory_id: str) -> bool:
        if memory_id not in self._items:
            return False
        del self._items[memory_id]
        return True
