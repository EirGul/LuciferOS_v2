from pathlib import Path


def read_doc() -> str:
    return Path("docs/memory_core_retrieval_design.md").read_text(
        encoding="utf-8"
    )


def test_memory_core_retrieval_design_exists():
    assert Path("docs/memory_core_retrieval_design.md").exists()


def test_memory_core_retrieval_design_is_design_only_and_isolated():
    text = read_doc()

    assert "Milestone 138 is design-only." in text
    assert "It must not modify LuciferCore" in text
    assert "provider prompts, API, HUD, voice, tools, memory write flows" in text


def test_memory_core_retrieval_design_requires_narrow_core_boundary():
    text = read_doc()

    required = [
        "The Core must request a bounded memory retrieval result through a narrow interface.",
        "access SQLite directly",
        "receive the entire memory database",
        "decide memory policy itself",
        "mutate memory as part of retrieval",
        "pass raw memory records directly to a provider prompt",
    ]

    for item in required:
        assert item in text


def test_memory_core_retrieval_design_defines_safe_future_flow():
    text = read_doc()

    required = [
        "CoreRequest",
        "MemoryRetrievalService",
        "retrieval policy evaluation",
        "type and scope filtering",
        "ranked MemoryRetrievalResult",
        "later provider context builder",
        "No provider-context injection is part of this milestone.",
    ]

    for item in required:
        assert item in text


def test_memory_core_retrieval_design_requires_bounded_request_fields():
    text = read_doc()

    required = [
        "request id",
        "query text or normalized query",
        "approved retrieval purpose",
        "allowed scopes",
        "allowed memory types",
        "bounded maximum result count",
        "bounded maximum context character budget",
        "source identifier",
    ]

    for item in required:
        assert item in text


def test_memory_core_retrieval_design_limits_initial_purposes_and_relevance():
    text = read_doc()

    required = [
        "conversation_response",
        "project_assistance",
        "explicit_memory_search",
        "normalized exact match",
        "bounded substring matching",
        "controlled keyword overlap",
        "embeddings",
        "vector database retrieval",
        "LLM relevance scoring",
        "semantic expansion",
    ]

    for item in required:
        assert item in text


def test_memory_core_retrieval_design_requires_policy_filter_budget_and_audit_boundaries():
    text = read_doc()

    required = [
        "policy allow",
        "scope filter",
        "type filter",
        "deterministic relevance filter",
        "bounded ranking",
        "context budget truncation",
        "strict character budget",
        "Retrieval use must become auditable before it is exposed to provider prompts",
    ]

    for item in required:
        assert item in text


def test_memory_core_retrieval_design_preserves_no_mutation_and_non_goals():
    text = read_doc()

    required = [
        "A conversational retrieval must never create a pending action or mutate memory.",
        "MemoryRetrievalRequest implementation",
        "MemoryRetrievalService implementation",
        "Core integration",
        "provider context injection",
        "semantic or vector retrieval",
        "auto-store or learning",
        "changes to selection or confirmation behavior",
    ]

    for item in required:
        assert item in text
