from __future__ import annotations

from dataclasses import dataclass

from lucifer_os.memory.retrieval import MemorySearchResult


@dataclass(frozen=True, slots=True)
class MemoryContext:
    text: str
    memory_ids: tuple[str, ...]

    @property
    def is_empty(self) -> bool:
        return not self.text.strip()


class MemoryContextBuilder:
    def __init__(self, max_items: int = 5, max_chars_per_item: int = 240) -> None:
        if max_items < 1:
            raise ValueError("Memory context max_items must be at least 1.")
        if max_items > 10:
            raise ValueError("Memory context max_items cannot exceed 10.")
        if max_chars_per_item < 40:
            raise ValueError("Memory context max_chars_per_item must be at least 40.")
        if max_chars_per_item > 1000:
            raise ValueError("Memory context max_chars_per_item cannot exceed 1000.")

        self.max_items = max_items
        self.max_chars_per_item = max_chars_per_item

    def build(self, results: list[MemorySearchResult]) -> MemoryContext:
        selected = results[: self.max_items]

        if not selected:
            return MemoryContext(text="", memory_ids=())

        lines = ["Relevant LuciferOS memory:"]
        memory_ids: list[str] = []

        for result in selected:
            item = result.item
            memory_ids.append(item.id)
            content = self._trim(item.content)
            lines.append(f"- [{item.type.value}/{item.scope.value}] {content}")

        return MemoryContext(
            text="\\n".join(lines),
            memory_ids=tuple(memory_ids),
        )

    def _trim(self, text: str) -> str:
        clean = " ".join(text.split())
        if len(clean) <= self.max_chars_per_item:
            return clean
        return clean[: self.max_chars_per_item - 1].rstrip() + "…"
