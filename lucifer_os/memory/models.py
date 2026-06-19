from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4


class MemoryType(str, Enum):
    FACT = "fact"
    PREFERENCE = "preference"
    PROJECT_STATE = "project_state"
    CORRECTION = "correction"
    COMMAND_ALIAS = "command_alias"
    RELATIONSHIP = "relationship"
    TASK_CONTEXT = "task_context"
    USER_INSTRUCTION = "user_instruction"


class MemoryScope(str, Enum):
    GLOBAL = "global"
    PROJECT = "project"
    SESSION = "session"
    INTERFACE_SPECIFIC = "interface-specific"
    TOOL_SPECIFIC = "tool-specific"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(slots=True)
class MemoryItem:
    content: str
    type: MemoryType
    scope: MemoryScope
    source: str = "user"
    confidence: float = 1.0
    tags: tuple[str, ...] = field(default_factory=tuple)
    metadata: dict[str, Any] = field(default_factory=dict)
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: str = field(default_factory=utc_now_iso)
    updated_at: str = field(default_factory=utc_now_iso)

    def __post_init__(self) -> None:
        if not self.content.strip():
            raise ValueError("Memory content cannot be empty.")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("Memory confidence must be between 0.0 and 1.0.")
