from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class MemoryCommandType(str, Enum):
    REMEMBER = "remember"
    LIST = "list"
    SEARCH = "search"
    CORRECT = "correct"
    DELETE = "delete"
    EXPLAIN_POLICY = "explain_policy"
    CONFIRM_PENDING = "confirm_pending"
    CANCEL_PENDING = "cancel_pending"
    NOT_MEMORY_COMMAND = "not_memory_command"


@dataclass(frozen=True, slots=True)
class MemoryCommand:
    type: MemoryCommandType
    raw_text: str
    normalized_text: str
    content: str | None = None
    query: str | None = None
    memory_id: str | None = None
    confidence: float = 1.0


class MemoryCommandParser:
    REMEMBER_PREFIXES = (
        "husk at ",
        "l\u00e6r at ",
        "remember that ",
        "learn that ",
    )

    LIST_PHRASES = frozenset({
        "hva husker du",
        "vis minner",
        "list memories",
        "show memories",
    })

    SEARCH_PREFIXES = (
        "hva husker du om ",
        "s\u00f8k i minner etter ",
        "search memories for ",
        "search memory for ",
    )

    CORRECT_PREFIXES = (
        "korriger minne ",
        "rett minne ",
        "endre minne ",
        "correct memory ",
    )

    DELETE_PREFIXES = (
        "slett minne ",
        "delete memory ",
        "glem at ",
        "forget that ",
    )

    EXPLAIN_POLICY_PHRASES = frozenset({
        "forklar minnepolicy",
        "forklar memory policy",
        "explain memory policy",
    })

    CONFIRM_PHRASES = frozenset({
        "ja",
        "bekreft",
        "ja utf\u00f8r",
        "confirm",
    })

    CANCEL_PHRASES = frozenset({
        "nei",
        "avbryt",
        "stopp",
        "cancel",
    })

    def parse(self, text: str) -> MemoryCommand:
        raw_text = text
        normalized_text = text.strip().lower()

        if not normalized_text:
            return self._not_memory_command(raw_text, normalized_text)

        remember_content = self._extract_prefix_content(text, self.REMEMBER_PREFIXES)
        if remember_content is not None:
            return MemoryCommand(
                type=MemoryCommandType.REMEMBER,
                raw_text=raw_text,
                normalized_text=normalized_text,
                content=remember_content,
            )

        if normalized_text in self.LIST_PHRASES:
            return MemoryCommand(
                type=MemoryCommandType.LIST,
                raw_text=raw_text,
                normalized_text=normalized_text,
            )

        search_query = self._extract_prefix_content(text, self.SEARCH_PREFIXES)
        if search_query is not None:
            return MemoryCommand(
                type=MemoryCommandType.SEARCH,
                raw_text=raw_text,
                normalized_text=normalized_text,
                query=search_query,
            )

        correction = self._extract_prefix_content(text, self.CORRECT_PREFIXES)
        if correction is not None:
            return MemoryCommand(
                type=MemoryCommandType.CORRECT,
                raw_text=raw_text,
                normalized_text=normalized_text,
                content=correction,
            )

        deletion_target = self._extract_prefix_content(text, self.DELETE_PREFIXES)
        if deletion_target is not None:
            return MemoryCommand(
                type=MemoryCommandType.DELETE,
                raw_text=raw_text,
                normalized_text=normalized_text,
                query=deletion_target,
            )

        if normalized_text in self.EXPLAIN_POLICY_PHRASES:
            return MemoryCommand(
                type=MemoryCommandType.EXPLAIN_POLICY,
                raw_text=raw_text,
                normalized_text=normalized_text,
            )

        if normalized_text in self.CONFIRM_PHRASES:
            return MemoryCommand(
                type=MemoryCommandType.CONFIRM_PENDING,
                raw_text=raw_text,
                normalized_text=normalized_text,
            )

        if normalized_text in self.CANCEL_PHRASES:
            return MemoryCommand(
                type=MemoryCommandType.CANCEL_PENDING,
                raw_text=raw_text,
                normalized_text=normalized_text,
            )

        return self._not_memory_command(raw_text, normalized_text)

    @staticmethod
    def _extract_prefix_content(text: str, prefixes: tuple[str, ...]) -> str | None:
        stripped = text.strip()
        normalized = stripped.lower()

        for prefix in prefixes:
            if normalized.startswith(prefix):
                content = stripped[len(prefix):].strip()
                return content or None

        return None

    @staticmethod
    def _not_memory_command(raw_text: str, normalized_text: str) -> MemoryCommand:
        return MemoryCommand(
            type=MemoryCommandType.NOT_MEMORY_COMMAND,
            raw_text=raw_text,
            normalized_text=normalized_text,
            confidence=1.0,
        )
