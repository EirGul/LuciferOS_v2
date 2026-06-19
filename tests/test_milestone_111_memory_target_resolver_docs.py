from pathlib import Path


def test_memory_target_resolver_docs_reflect_current_status():
    text = Path("docs/memory_target_resolver_design.md").read_text(encoding="utf-8")

    assert "MemoryTargetResolver now exists as an isolated memory-layer model." in text
    assert "The current MemoryTargetResolver can:" in text
    assert "resolve explicit memory ids against a bounded candidate list" in text
    assert "resolve query text through normalized content substring matching" in text


def test_memory_target_resolver_docs_preserve_boundaries():
    text = Path("docs/memory_target_resolver_design.md").read_text(encoding="utf-8")

    assert "It must not connect target resolution to IntentRouter, Core, API, HUD, provider prompts, voice, tools, runtime adapters, or MemoryCommandExecutor." in text
    assert "It does not execute memory changes." in text
    assert "It does not call MemoryService.update_memory." in text
    assert "It does not call MemoryService.delete_memory." in text
    assert "It does not call MemoryCommandExecutor." in text


def test_memory_target_resolver_docs_describe_current_matching_limits():
    text = Path("docs/memory_target_resolver_design.md").read_text(encoding="utf-8")

    assert "Current resolver implementation uses deterministic matching only:" in text
    assert "explicit memory id match" in text
    assert "normalized content substring match" in text
    assert "The current resolver does not match tags." in text
    assert "The current resolver does not match metadata." in text


def test_memory_target_resolver_docs_describe_safety_regressions():
    text = Path("docs/memory_target_resolver_design.md").read_text(encoding="utf-8")

    required = [
        "empty memory id returns no_match",
        "empty candidate list returns no_match",
        "metadata is not matched before metadata matching is implemented",
        "tags are not matched before tag matching is implemented",
        "multiple candidates are never safe_for_confirmation",
        "explicit-id resolution respects max_candidates",
        "query resolution respects max_candidates",
        "safe result invariant requires selected_memory_id",
        "resolver does not mutate memory items",
    ]

    for item in required:
        assert item in text


def test_memory_target_resolver_docs_preserve_non_goals():
    text = Path("docs/memory_target_resolver_design.md").read_text(encoding="utf-8")

    non_goals = [
        "executor integration",
        "IntentRouter integration",
        "Core integration",
        "API endpoints",
        "HUD memory panels",
        "provider prompt injection",
        "automatic memory extraction",
        "semantic/vector search",
        "tag matching",
        "metadata matching",
        "OS/tool actions",
        "voice integration",
    ]

    for non_goal in non_goals:
        assert non_goal in text


def test_memory_target_resolver_docs_keep_historical_milestone_108_contracts():
    text = Path("docs/memory_target_resolver_design.md").read_text(encoding="utf-8")

    assert "Milestone 108 is design-only." in text
    assert "Initial resolver implementation should use deterministic matching only:" in text
    assert "Milestone 108 must not add:" in text
