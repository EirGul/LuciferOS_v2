from __future__ import annotations

from dataclasses import dataclass

from lucifer_os.memory.retrieval import (
    MemoryRetrievalOutcome,
    MemoryRetrievalResult,
)


@dataclass(frozen=True, slots=True)
class MemoryContext:
    text: str
    memory_ids: tuple[str, ...]
    truncated: bool = False

    @property
    def is_empty(self) -> bool:
        return not self.text.strip()


class MemoryContextBuilder:
    def __init__(
        self,
        max_chars_per_item: int = 240,
    ) -> None:
        if max_chars_per_item < 40:
            raise ValueError("Memory context max_chars_per_item must be at least 40.")
        if max_chars_per_item > 1000:
            raise ValueError("Memory context max_chars_per_item cannot exceed 1000.")

        self.max_chars_per_item = max_chars_per_item

    def build(self, retrieval: MemoryRetrievalResult) -> MemoryContext:
        if retrieval.outcome != MemoryRetrievalOutcome.MATCHED:
            return MemoryContext(text="", memory_ids=())

        header = "Relevant LuciferOS memory:"
        lines = [header]
        memory_ids: list[str] = []
        truncated = False

        for result in retrieval.matches:
            item = result.item
            content = self._trim(item.content)
            line = f"- [{item.type.value}/{item.scope.value}] {content}"
            candidate_text = "\n".join([*lines, line])

            if len(candidate_text) > retrieval.max_context_chars:
                truncated = True
                break

            lines.append(line)
            memory_ids.append(item.id)

        if not memory_ids:
            return MemoryContext(text="", memory_ids=(), truncated=truncated)

        return MemoryContext(
            text="\n".join(lines),
            memory_ids=tuple(memory_ids),
            truncated=truncated,
        )

    def _trim(self, text: str) -> str:
        clean = " ".join(text.split())
        if len(clean) <= self.max_chars_per_item:
            return clean
        return clean[: self.max_chars_per_item - 1].rstrip() + "…"
