from __future__ import annotations

from typing import Any

from lucifer_os.memory.models import MemoryItem, MemoryScope, MemoryType
from lucifer_os.memory.store import MemoryStore


class MemoryService:
    def __init__(self, store: MemoryStore) -> None:
        self.store = store

    def add_memory(
        self,
        content: str,
        type: MemoryType,
        scope: MemoryScope,
        source: str = "user",
        confidence: float = 1.0,
        tags: tuple[str, ...] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> MemoryItem:
        item = MemoryItem(
            content=content,
            type=type,
            scope=scope,
            source=source,
            confidence=confidence,
            tags=tags or (),
            metadata=metadata or {},
        )
        return self.store.add(item)

    def get_memory(self, memory_id: str) -> MemoryItem | None:
        return self.store.get(memory_id)

    def list_memories(
        self,
        scope: MemoryScope | None = None,
        type: MemoryType | None = None,
    ) -> list[MemoryItem]:
        return self.store.list(scope=scope, type=type)

    def delete_memory(self, memory_id: str) -> bool:
        return self.store.delete(memory_id)
