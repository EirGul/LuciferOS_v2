from dataclasses import FrozenInstanceError

import pytest

from lucifer_os.memory import (
    InMemoryMemoryStore,
    MemoryContextBuilder,
    MemoryQuery,
    MemoryRetrievalOutcome,
    MemoryRetrievalPurpose,
    MemoryRetrievalResult,
    MemoryRetrievalService,
    MemoryScope,
    MemoryService,
    MemoryType,
)


def make_query(**overrides) -> MemoryQuery:
    values = {
        "request_id": "m141-retrieval-request",
        "text": "LuciferOS retrieval",
        "scopes": (MemoryScope.PROJECT,),
        "types": (MemoryType.PROJECT_STATE,),
        "purpose": MemoryRetrievalPurpose.PROJECT_ASSISTANCE,
        "source": "test-milestone-141",
        "limit": 5,
        "max_context_chars": 180,
    }
    values.update(overrides)
    return MemoryQuery(**values)


def build_store() -> InMemoryMemoryStore:
    store = InMemoryMemoryStore()
    service = MemoryService(store)
    service.add_memory(
        content="LuciferOS retrieval is deterministic and bounded.",
        type=MemoryType.PROJECT_STATE,
        scope=MemoryScope.PROJECT,
        tags=("luciferos", "retrieval"),
    )
    service.add_memory(
        content="LuciferOS stores project retrieval contracts explicitly.",
        type=MemoryType.PROJECT_STATE,
        scope=MemoryScope.PROJECT,
        tags=("luciferos", "retrieval"),
    )
    return store


def test_retrieve_returns_explicit_denied_result_without_store_access():
    class StoreThatMustNotBeRead(InMemoryMemoryStore):
        def list(self, *args, **kwargs):
            raise AssertionError("denied retrieval must not read the store")

    retrieval = MemoryRetrievalService(StoreThatMustNotBeRead()).retrieve(
        make_query(types=(MemoryType.USER_INSTRUCTION,))
    )

    assert retrieval.outcome == MemoryRetrievalOutcome.DENIED
    assert retrieval.reason_code == "retrieval_type_not_allowed"
    assert retrieval.request_id == "m141-retrieval-request"
    assert retrieval.source == "test-milestone-141"
    assert retrieval.result_count == 0
    assert retrieval.matches == ()
    assert retrieval.memory_ids == ()


def test_retrieve_returns_explicit_no_match_result_with_request_boundaries():
    retrieval = MemoryRetrievalService(build_store()).retrieve(
        make_query(text="nonexistent")
    )

    assert retrieval.outcome == MemoryRetrievalOutcome.NO_MATCH
    assert retrieval.reason_code == "retrieval_no_match"
    assert retrieval.applied_scopes == (MemoryScope.PROJECT,)
    assert retrieval.applied_types == (MemoryType.PROJECT_STATE,)
    assert retrieval.result_limit == 5
    assert retrieval.max_context_chars == 180
    assert retrieval.result_count == 0
    assert retrieval.matches == ()


def test_retrieve_returns_immutable_bounded_matches_and_identifiers():
    retrieval = MemoryRetrievalService(build_store()).retrieve(
        make_query(limit=1)
    )

    assert retrieval.outcome == MemoryRetrievalOutcome.MATCHED
    assert isinstance(retrieval.matches, tuple)
    assert retrieval.result_count == 1
    assert len(retrieval.matches) == 1
    assert retrieval.memory_ids == (retrieval.matches[0].item.id,)

    with pytest.raises(FrozenInstanceError):
        retrieval.matches = ()


def test_context_builder_uses_retrieval_budget_not_a_constructor_total_budget():
    retrieval = MemoryRetrievalService(build_store()).retrieve(
        make_query(max_context_chars=110)
    )

    context = MemoryContextBuilder(max_chars_per_item=240).build(retrieval)

    assert len(context.text) <= retrieval.max_context_chars
    assert context.truncated is True
    assert context.memory_ids == (retrieval.matches[0].item.id,)

    with pytest.raises(TypeError):
        MemoryContextBuilder(max_total_chars=110)


def test_context_builder_returns_empty_context_for_denied_and_no_match_results():
    denied = MemoryRetrievalService(InMemoryMemoryStore()).retrieve(
        make_query(types=(MemoryType.USER_INSTRUCTION,))
    )
    no_match = MemoryRetrievalService(build_store()).retrieve(
        make_query(text="nonexistent")
    )
    builder = MemoryContextBuilder()

    assert builder.build(denied).is_empty is True
    assert builder.build(denied).truncated is False
    assert builder.build(no_match).is_empty is True
    assert builder.build(no_match).truncated is False


def test_memory_retrieval_result_enforces_outcome_match_invariants():
    with pytest.raises(ValueError):
        MemoryRetrievalResult(
            request_id="m141-invalid",
            source="test-milestone-141",
            purpose=MemoryRetrievalPurpose.PROJECT_ASSISTANCE,
            outcome=MemoryRetrievalOutcome.MATCHED,
            reason_code="retrieval_matched",
            applied_scopes=(MemoryScope.PROJECT,),
            applied_types=(MemoryType.PROJECT_STATE,),
            matches=(),
            result_count=0,
            result_limit=5,
            max_context_chars=180,
        )


def test_memory_retrieval_result_enforces_bounded_identifiers_and_outcome_codes():
    values = {
        "request_id": "m141-valid",
        "source": "test-milestone-141",
        "purpose": MemoryRetrievalPurpose.PROJECT_ASSISTANCE,
        "outcome": MemoryRetrievalOutcome.NO_MATCH,
        "reason_code": "retrieval_no_match",
        "applied_scopes": (MemoryScope.PROJECT,),
        "applied_types": (MemoryType.PROJECT_STATE,),
        "matches": (),
        "result_count": 0,
        "result_limit": 5,
        "max_context_chars": 180,
    }

    with pytest.raises(ValueError):
        MemoryRetrievalResult(**(values | {"request_id": "x" * 129}))

    with pytest.raises(ValueError):
        MemoryRetrievalResult(**(values | {"reason_code": "x" * 129}))

    with pytest.raises(ValueError):
        MemoryRetrievalResult(**(
            values
            | {
                "outcome": MemoryRetrievalOutcome.NO_MATCH,
                "reason_code": "wrong_reason",
            }
        ))
