from __future__ import annotations

from dataclasses import dataclass

from lucifer_os.memory.models import MemoryItem, MemoryScope, MemoryType
from lucifer_os.memory.store import MemoryStore


@dataclass(frozen=True, slots=True)
class MemoryQuery:
    text: str = ""
    scopes: tuple[MemoryScope, ...] = ()
    types: tuple[MemoryType, ...] = ()
    limit: int = 5

    def __post_init__(self) -> None:
        if self.limit < 1:
            raise ValueError("Memory query limit must be at least 1.")
        if self.limit > 25:
            raise ValueError("Memory query limit cannot exceed 25.")


@dataclass(frozen=True, slots=True)
class MemorySearchResult:
    item: MemoryItem
    score: float
    matched_terms: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not 0.0 <= self.score <= 1.0:
            raise ValueError("Memory search score must be between 0.0 and 1.0.")


class MemoryRetrievalService:
    def __init__(self, store: MemoryStore) -> None:
        self.store = store

    def search(self, query: MemoryQuery) -> list[MemorySearchResult]:
        candidates = self.store.list()

        if query.scopes:
            candidates = [item for item in candidates if item.scope in query.scopes]

        if query.types:
            candidates = [item for item in candidates if item.type in query.types]

        terms = self._terms(query.text)
        results: list[MemorySearchResult] = []

        for item in candidates:
            result = self._score_item(item, terms)
            if result is not None:
                results.append(result)

        results.sort(key=lambda result: result.score, reverse=True)
        return results[: query.limit]

    def _score_item(self, item: MemoryItem, terms: tuple[str, ...]) -> MemorySearchResult | None:
        if not terms:
            return MemorySearchResult(item=item, score=0.5)

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
        return MemorySearchResult(item=item, score=score, matched_terms=matched_terms)

    def _terms(self, text: str) -> tuple[str, ...]:
        return tuple(
            term.strip().lower()
            for term in text.split()
            if term.strip()
        )
