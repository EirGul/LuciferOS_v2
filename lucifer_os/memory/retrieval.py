from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from lucifer_os.memory.models import MemoryItem, MemoryScope, MemoryType
from lucifer_os.memory.store import MemoryStore


class MemoryRetrievalPurpose(str, Enum):
    CONVERSATION_RESPONSE = "conversation_response"
    PROJECT_ASSISTANCE = "project_assistance"
    EXPLICIT_MEMORY_SEARCH = "explicit_memory_search"


class MemoryRetrievalOutcome(str, Enum):
    DENIED = "denied"
    NO_MATCH = "no_match"
    MATCHED = "matched"


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
    request_id: str
    text: str
    scopes: tuple[MemoryScope, ...]
    types: tuple[MemoryType, ...]
    purpose: MemoryRetrievalPurpose
    source: str
    limit: int = 5
    max_context_chars: int = 1200

    def __post_init__(self) -> None:
        if not self.request_id.strip():
            raise ValueError("Memory query request_id cannot be empty.")
        if len(self.request_id) > 128:
            raise ValueError("Memory query request_id cannot exceed 128 characters.")
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


@dataclass(frozen=True, slots=True)
class MemoryRetrievalResult:
    request_id: str
    source: str
    purpose: MemoryRetrievalPurpose
    outcome: MemoryRetrievalOutcome
    reason_code: str
    applied_scopes: tuple[MemoryScope, ...]
    applied_types: tuple[MemoryType, ...]
    matches: tuple[MemorySearchResult, ...]
    result_count: int
    result_limit: int
    max_context_chars: int

    def __post_init__(self) -> None:
        if not self.request_id.strip():
            raise ValueError("Memory retrieval result request_id cannot be empty.")
        if len(self.request_id) > 128:
            raise ValueError(
                "Memory retrieval result request_id cannot exceed 128 characters."
            )
        if not self.source.strip():
            raise ValueError("Memory retrieval result source cannot be empty.")
        if not isinstance(self.purpose, MemoryRetrievalPurpose):
            raise ValueError(
                "Memory retrieval result purpose must be a MemoryRetrievalPurpose."
            )
        if not isinstance(self.outcome, MemoryRetrievalOutcome):
            raise ValueError(
                "Memory retrieval result outcome must be a MemoryRetrievalOutcome."
            )
        if not self.reason_code.strip():
            raise ValueError("Memory retrieval result reason_code cannot be empty.")
        if len(self.reason_code) > 128:
            raise ValueError(
                "Memory retrieval result reason_code cannot exceed 128 characters."
            )
        if not self.applied_scopes:
            raise ValueError(
                "Memory retrieval result must include at least one applied scope."
            )
        if not self.applied_types:
            raise ValueError(
                "Memory retrieval result must include at least one applied memory type."
            )
        if len(set(self.applied_scopes)) != len(self.applied_scopes):
            raise ValueError(
                "Memory retrieval result applied_scopes must not contain duplicates."
            )
        if len(set(self.applied_types)) != len(self.applied_types):
            raise ValueError(
                "Memory retrieval result applied_types must not contain duplicates."
            )
        if self.result_count != len(self.matches):
            raise ValueError(
                "Memory retrieval result result_count must equal match count."
            )
        if self.result_limit < 1 or self.result_limit > 25:
            raise ValueError(
                "Memory retrieval result result_limit must be between 1 and 25."
            )
        if self.result_count > self.result_limit:
            raise ValueError(
                "Memory retrieval result result_count cannot exceed result_limit."
            )
        if self.max_context_chars < 80 or self.max_context_chars > 4000:
            raise ValueError(
                "Memory retrieval result max_context_chars must be between 80 and 4000."
            )
        if self.outcome == MemoryRetrievalOutcome.MATCHED:
            if self.reason_code != "retrieval_matched":
                raise ValueError(
                    "Matched memory retrieval result must use retrieval_matched."
                )
            if not self.matches:
                raise ValueError(
                    "Matched memory retrieval result must include at least one match."
                )
        elif self.outcome == MemoryRetrievalOutcome.NO_MATCH:
            if self.reason_code != "retrieval_no_match":
                raise ValueError(
                    "No-match memory retrieval result must use retrieval_no_match."
                )
            if self.matches or self.result_count:
                raise ValueError(
                    "No-match memory retrieval results cannot include matches."
                )
        elif self.matches or self.result_count:
            raise ValueError(
                "Denied memory retrieval results cannot include matches."
            )

    @property
    def memory_ids(self) -> tuple[str, ...]:
        return tuple(match.item.id for match in self.matches)


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

    def retrieve(self, query: MemoryQuery) -> MemoryRetrievalResult:
        decision = self.evaluate(query)
        if not decision.allowed:
            return self._result(
                query=query,
                outcome=MemoryRetrievalOutcome.DENIED,
                reason_code=decision.reason_code,
                matches=(),
            )

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
        matches = tuple(results[: query.limit])

        if not matches:
            return self._result(
                query=query,
                outcome=MemoryRetrievalOutcome.NO_MATCH,
                reason_code="retrieval_no_match",
                matches=(),
            )

        return self._result(
            query=query,
            outcome=MemoryRetrievalOutcome.MATCHED,
            reason_code="retrieval_matched",
            matches=matches,
        )

    def _result(
        self,
        *,
        query: MemoryQuery,
        outcome: MemoryRetrievalOutcome,
        reason_code: str,
        matches: tuple[MemorySearchResult, ...],
    ) -> MemoryRetrievalResult:
        return MemoryRetrievalResult(
            request_id=query.request_id,
            source=query.source,
            purpose=query.purpose,
            outcome=outcome,
            reason_code=reason_code,
            applied_scopes=query.scopes,
            applied_types=query.types,
            matches=matches,
            result_count=len(matches),
            result_limit=query.limit,
            max_context_chars=query.max_context_chars,
        )

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
