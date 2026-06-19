from __future__ import annotations

from lucifer_os.memory.models import MemoryScope, MemoryType
from lucifer_os.memory.service import MemoryService


class LearningService:
    EXPLICIT_PREFIXES = (
        "husk at ",
        "lær at ",
        "remember that ",
        "learn that ",
    )

    def __init__(self, memory_service: MemoryService) -> None:
        self.memory_service = memory_service

    def is_explicit_learning_request(self, text: str) -> bool:
        normalized = text.strip().lower()
        return any(normalized.startswith(prefix) for prefix in self.EXPLICIT_PREFIXES)

    def extract_explicit_memory_content(self, text: str) -> str | None:
        stripped = text.strip()
        normalized = stripped.lower()
        for prefix in self.EXPLICIT_PREFIXES:
            if normalized.startswith(prefix):
                return stripped[len(prefix):].strip() or None
        return None

    def learn_explicit_memory(
        self,
        text: str,
        scope: MemoryScope = MemoryScope.GLOBAL,
        type: MemoryType = MemoryType.USER_INSTRUCTION,
    ):
        content = self.extract_explicit_memory_content(text)
        if content is None:
            return None
        return self.memory_service.add_memory(
            content=content,
            type=type,
            scope=scope,
            source="explicit-learning-request",
        )
