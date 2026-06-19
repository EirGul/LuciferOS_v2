from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
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


def parse_utc_iso(value: str) -> datetime:
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed


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


@dataclass(frozen=True, slots=True)
class PendingMemoryActionConfirmationResult:
    confirmed: bool
    cancelled: bool
    stale: bool
    action: PendingMemoryAction | None = None
    reason: str = ""


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


class PendingMemoryActionService:
    def __init__(
        self,
        store: PendingMemoryActionStore | None = None,
        stale_after_seconds: int = 300,
    ) -> None:
        if stale_after_seconds <= 0:
            raise ValueError("stale_after_seconds must be greater than zero.")
        self.store = store or InMemoryPendingMemoryActionStore()
        self.stale_after_seconds = stale_after_seconds

    def set_pending(self, action: PendingMemoryAction) -> PendingMemoryAction:
        return self.store.set(action)

    def get_pending(self) -> PendingMemoryAction | None:
        action = self.store.get()
        if action is None:
            return None
        if self.is_stale(action):
            self.store.clear()
            return None
        return action

    def confirm_pending(self) -> PendingMemoryActionConfirmationResult:
        action = self.store.get()
        if action is None:
            return PendingMemoryActionConfirmationResult(
                confirmed=False,
                cancelled=False,
                stale=False,
                action=None,
                reason="No pending memory action to confirm.",
            )

        self.store.clear()

        if self.is_stale(action):
            return PendingMemoryActionConfirmationResult(
                confirmed=False,
                cancelled=False,
                stale=True,
                action=action,
                reason="Pending memory action is stale and was cleared.",
            )

        return PendingMemoryActionConfirmationResult(
            confirmed=True,
            cancelled=False,
            stale=False,
            action=action,
            reason="Pending memory action confirmed.",
        )

    def cancel_pending(self) -> PendingMemoryActionConfirmationResult:
        action = self.store.clear()
        if action is None:
            return PendingMemoryActionConfirmationResult(
                confirmed=False,
                cancelled=False,
                stale=False,
                action=None,
                reason="No pending memory action to cancel.",
            )

        return PendingMemoryActionConfirmationResult(
            confirmed=False,
            cancelled=True,
            stale=False,
            action=action,
            reason="Pending memory action cancelled.",
        )

    def is_stale(self, action: PendingMemoryAction) -> bool:
        created_at = parse_utc_iso(action.created_at)
        expires_at = created_at + timedelta(seconds=self.stale_after_seconds)
        return datetime.now(timezone.utc) > expires_at
