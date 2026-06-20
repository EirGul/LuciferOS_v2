from lucifer_os.memory import (
    MemoryItem,
    MemoryQuery,
    MemoryRetrievalPurpose,
    MemoryRetrievalService,
    MemoryScope,
    MemoryType,
)
from lucifer_os.memory.store import MemoryStore


def query(
    *,
    text: str = "LuciferOS",
    scopes: tuple[MemoryScope, ...] = (MemoryScope.PROJECT,),
    types: tuple[MemoryType, ...] = (MemoryType.PROJECT_STATE,),
    purpose: MemoryRetrievalPurpose = MemoryRetrievalPurpose.PROJECT_ASSISTANCE,
) -> MemoryQuery:
    return MemoryQuery(
        text=text,
        scopes=scopes,
        types=types,
        purpose=purpose,
        source="test-milestone-140",
        limit=5,
        max_context_chars=300,
    )


class ListForbiddenMemoryStore(MemoryStore):
    def add(self, item: MemoryItem) -> MemoryItem:
        raise AssertionError("add must not be called")

    def get(self, memory_id: str) -> MemoryItem | None:
        raise AssertionError("get must not be called")

    def list(
        self,
        scope: MemoryScope | None = None,
        type: MemoryType | None = None,
    ) -> list[MemoryItem]:
        raise AssertionError("list must not be called for denied retrieval")

    def update(self, item: MemoryItem) -> bool:
        raise AssertionError("update must not be called")

    def delete(self, memory_id: str) -> bool:
        raise AssertionError("delete must not be called")


class OrderedMemoryStore(MemoryStore):
    def __init__(self, items: list[MemoryItem]) -> None:
        self.items = items

    def add(self, item: MemoryItem) -> MemoryItem:
        self.items.append(item)
        return item

    def get(self, memory_id: str) -> MemoryItem | None:
        return next((item for item in self.items if item.id == memory_id), None)

    def list(
        self,
        scope: MemoryScope | None = None,
        type: MemoryType | None = None,
    ) -> list[MemoryItem]:
        items = list(self.items)
        if scope is not None:
            items = [item for item in items if item.scope == scope]
        if type is not None:
            items = [item for item in items if item.type == type]
        return items

    def update(self, item: MemoryItem) -> bool:
        return False

    def delete(self, memory_id: str) -> bool:
        return False


def test_project_assistance_allows_explicit_project_read():
    service = MemoryRetrievalService(ListForbiddenMemoryStore())

    decision = service.evaluate(query())

    assert decision.allowed is True
    assert decision.reason_code == "retrieval_allowed"


def test_conversation_response_denies_global_scope_until_core_context_exists():
    service = MemoryRetrievalService(ListForbiddenMemoryStore())

    decision = service.evaluate(
        query(
            scopes=(MemoryScope.GLOBAL,),
            purpose=MemoryRetrievalPurpose.CONVERSATION_RESPONSE,
        )
    )

    assert decision.allowed is False
    assert decision.reason_code == "conversation_scope_not_allowed"
    assert service.search(
        query(
            scopes=(MemoryScope.GLOBAL,),
            purpose=MemoryRetrievalPurpose.CONVERSATION_RESPONSE,
        )
    ) == []


def test_project_assistance_denies_global_scope_until_trusted_project_context_exists():
    service = MemoryRetrievalService(ListForbiddenMemoryStore())

    decision = service.evaluate(
        query(
            scopes=(MemoryScope.GLOBAL,),
            purpose=MemoryRetrievalPurpose.PROJECT_ASSISTANCE,
        )
    )

    assert decision.allowed is False
    assert decision.reason_code == "project_assistance_scope_not_allowed"


def test_explicit_memory_search_may_read_global_scope_when_other_filters_are_safe():
    service = MemoryRetrievalService(ListForbiddenMemoryStore())

    decision = service.evaluate(
        query(
            scopes=(MemoryScope.GLOBAL,),
            purpose=MemoryRetrievalPurpose.EXPLICIT_MEMORY_SEARCH,
        )
    )

    assert decision.allowed is True
    assert decision.reason_code == "retrieval_allowed"


def test_policy_denies_high_impact_types_before_store_is_read():
    service = MemoryRetrievalService(ListForbiddenMemoryStore())

    denied_query = query(types=(MemoryType.USER_INSTRUCTION,))

    decision = service.evaluate(denied_query)

    assert decision.allowed is False
    assert decision.reason_code == "retrieval_type_not_allowed"
    assert service.search(denied_query) == []


def test_policy_denies_interface_and_tool_scopes_before_store_is_read():
    service = MemoryRetrievalService(ListForbiddenMemoryStore())

    for scope in (
        MemoryScope.INTERFACE_SPECIFIC,
        MemoryScope.TOOL_SPECIFIC,
    ):
        denied_query = query(scopes=(scope,))

        decision = service.evaluate(denied_query)

        assert decision.allowed is False
        assert decision.reason_code == "retrieval_scope_not_allowed"
        assert service.search(denied_query) == []


def test_retrieval_uses_score_then_memory_id_as_stable_tie_break():
    item_z = MemoryItem(
        id="z-memory",
        content="LuciferOS retrieval policy",
        type=MemoryType.PROJECT_STATE,
        scope=MemoryScope.PROJECT,
    )
    item_a = MemoryItem(
        id="a-memory",
        content="LuciferOS retrieval policy",
        type=MemoryType.PROJECT_STATE,
        scope=MemoryScope.PROJECT,
    )
    store = OrderedMemoryStore([item_z, item_a])
    service = MemoryRetrievalService(store)

    results = service.search(query(text="LuciferOS retrieval"))

    assert [result.item.id for result in results] == ["a-memory", "z-memory"]


def test_retrieval_policy_and_search_do_not_mutate_store_records():
    item = MemoryItem(
        id="safe-memory",
        content="LuciferOS retrieval remains read only",
        type=MemoryType.PROJECT_STATE,
        scope=MemoryScope.PROJECT,
    )
    store = OrderedMemoryStore([item])
    service = MemoryRetrievalService(store)

    results = service.search(query(text="retrieval read"))

    assert len(results) == 1
    assert store.items == [item]
    assert results[0].item.id == item.id
