from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from lucifer_os.memory.models import MemoryItem, MemoryScope, MemoryType
from lucifer_os.memory.store import MemoryStore


class MemoryRetrievalPurpose(str, Enum):
    CONVERSATION_RESPONSE = "conversation_response"
    PROJECT_ASSISTANCE = "project_assistance"
    EXPLICIT_MEMORY_SEARCH = "explicit_memory_search"


@dataclass(frozen=True, slots=True)
class MemoryRetrievalDecision:
    allowed: bool
    reason_code: str


class MemoryRetrievalPolicy:
    """Conservative read-policy for deterministic memory retrieval.

    This policy is intentionally independent from write/update/delete policy.
    It does not perform retrieval and does not mutate memory.
    """

    _BLOCKED_TYPES = frozenset({
        MemoryType.COMMAND_ALIAS,
        MemoryType.RELATIONSHIP,
        MemoryType.USER_INSTRUCTION,
    })

    _BLOCKED_SCOPES = frozenset({
        MemoryScope.INTERFACE_SPECIFIC,
        MemoryScope.TOOL_SPECIFIC,
    })

    _CONVERSATION_ALLOWED_SCOPES = frozenset({
        MemoryScope.PROJECT,
        MemoryScope.SESSION,
    })

    _PROJECT_ASSISTANCE_ALLOWED_SCOPES = frozenset({
        MemoryScope.PROJECT,
        MemoryScope.SESSION,
    })

    def evaluate(self, query: "MemoryQuery") -> MemoryRetrievalDecision:
        if any(memory_type in self._BLOCKED_TYPES for memory_type in query.types):
            return MemoryRetrievalDecision(
                allowed=False,
                reason_code="retrieval_type_not_allowed",
            )

        if any(scope in self._BLOCKED_SCOPES for scope in query.scopes):
            return MemoryRetrievalDecision(
                allowed=False,
                reason_code="retrieval_scope_not_allowed",
            )

        if query.purpose == MemoryRetrievalPurpose.CONVERSATION_RESPONSE:
            if not set(query.scopes).issubset(self._CONVERSATION_ALLOWED_SCOPES):
                return MemoryRetrievalDecision(
                    allowed=False,
                    reason_code="conversation_scope_not_allowed",
                )

        if query.purpose == MemoryRetrievalPurpose.PROJECT_ASSISTANCE:
            if not set(query.scopes).issubset(self._PROJECT_ASSISTANCE_ALLOWED_SCOPES):
                return MemoryRetrievalDecision(
                    allowed=False,
                    reason_code="project_assistance_scope_not_allowed",
                )

        return MemoryRetrievalDecision(
            allowed=True,
            reason_code="retrieval_allowed",
        )


@dataclass(frozen=True, slots=True)
class MemoryQuery:
    text: str
    scopes: tuple[MemoryScope, ...]
    types: tuple[MemoryType, ...]
    purpose: MemoryRetrievalPurpose
    source: str
    limit: int = 5
    max_context_chars: int = 1200

    def __post_init__(self) -> None:
        if not self.text.strip():
            raise ValueError("Memory query text cannot be empty.")
        if not isinstance(self.purpose, MemoryRetrievalPurpose):
            raise ValueError("Memory query purpose must be a MemoryRetrievalPurpose.")
        if not self.source.strip():
            raise ValueError("Memory query source cannot be empty.")
        if not self.scopes:
            raise ValueError("Memory query must include at least one allowed scope.")
        if not self.types:
            raise ValueError("Memory query must include at least one allowed memory type.")
        if len(set(self.scopes)) != len(self.scopes):
            raise ValueError("Memory query scopes must not contain duplicates.")
        if len(set(self.types)) != len(self.types):
            raise ValueError("Memory query types must not contain duplicates.")
        if self.limit < 1:
            raise ValueError("Memory query limit must be at least 1.")
        if self.limit > 25:
            raise ValueError("Memory query limit cannot exceed 25.")
        if self.max_context_chars < 80:
            raise ValueError("Memory query max_context_chars must be at least 80.")
        if self.max_context_chars > 4000:
            raise ValueError("Memory query max_context_chars cannot exceed 4000.")


@dataclass(frozen=True, slots=True)
class MemorySnapshot:
    id: str
    content: str
    type: MemoryType
    scope: MemoryScope


@dataclass(frozen=True, slots=True)
class MemorySearchResult:
    item: MemorySnapshot
    score: float
    matched_terms: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not 0.0 <= self.score <= 1.0:
            raise ValueError("Memory search score must be between 0.0 and 1.0.")


class MemoryRetrievalService:
    def __init__(
        self,
        store: MemoryStore,
        policy: MemoryRetrievalPolicy | None = None,
    ) -> None:
        self.store = store
        self.policy = policy or MemoryRetrievalPolicy()

    def evaluate(self, query: MemoryQuery) -> MemoryRetrievalDecision:
        return self.policy.evaluate(query)

    def search(self, query: MemoryQuery) -> list[MemorySearchResult]:
        decision = self.evaluate(query)
        if not decision.allowed:
            return []

        candidates = self.store.list()

        candidates = [item for item in candidates if item.scope in query.scopes]
        candidates = [item for item in candidates if item.type in query.types]

        terms = self._terms(query.text)
        results: list[MemorySearchResult] = []

        for item in candidates:
            result = self._score_item(item, terms)
            if result is not None:
                results.append(result)

        results.sort(key=lambda result: (-result.score, result.item.id))
        return results[: query.limit]

    def _score_item(
        self,
        item: MemoryItem,
        terms: tuple[str, ...],
    ) -> MemorySearchResult | None:
        haystack = " ".join((
            item.content,
            item.type.value,
            item.scope.value,
            " ".join(item.tags),
        )).lower()

        matched_terms = tuple(term for term in terms if term in haystack)

        if not matched_terms:
            return None

        score = min(1.0, len(matched_terms) / len(terms))
        return MemorySearchResult(
            item=MemorySnapshot(
                id=item.id,
                content=item.content,
                type=item.type,
                scope=item.scope,
            ),
            score=score,
            matched_terms=matched_terms,
        )

    def _terms(self, text: str) -> tuple[str, ...]:
        return tuple(
            term.strip().lower()
            for term in text.split()
            if term.strip()
        )
