from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4

from lucifer_os.memory.commands import MemoryCommandType


class PendingMemoryActionType(str, Enum):
    REMEMBER = "remember"
    CORRECT = "correct"
    DELETE = "delete"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True, slots=True)
class PendingMemoryAction:
    action_type: PendingMemoryActionType
    command_type: MemoryCommandType
    explanation: str
    source_text: str
    memory_id: str | None = None
    proposed_content: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    requires_confirmation: bool = True
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: str = field(default_factory=utc_now_iso)

    def __post_init__(self) -> None:
        if not self.explanation.strip():
            raise ValueError("Pending memory action explanation cannot be empty.")
        if not self.source_text.strip():
            raise ValueError("Pending memory action source text cannot be empty.")


class PendingMemoryActionStore(ABC):
    @abstractmethod
    def set(self, action: PendingMemoryAction) -> PendingMemoryAction:
        raise NotImplementedError

    @abstractmethod
    def get(self) -> PendingMemoryAction | None:
        raise NotImplementedError

    @abstractmethod
    def clear(self) -> PendingMemoryAction | None:
        raise NotImplementedError


class InMemoryPendingMemoryActionStore(PendingMemoryActionStore):
    def __init__(self) -> None:
        self._action: PendingMemoryAction | None = None

    def set(self, action: PendingMemoryAction) -> PendingMemoryAction:
        self._action = action
        return action

    def get(self) -> PendingMemoryAction | None:
        return self._action

    def clear(self) -> PendingMemoryAction | None:
        action = self._action
        self._action = None
        return action
