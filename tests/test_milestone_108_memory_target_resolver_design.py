from pathlib import Path


def test_memory_target_resolver_design_doc_exists():
    doc = Path("docs/memory_target_resolver_design.md")

    assert doc.exists()


def test_memory_target_resolver_design_is_design_only():
    text = Path("docs/memory_target_resolver_design.md").read_text(encoding="utf-8")

    assert "Milestone 108 is design-only." in text
    assert "It must not connect target resolution to IntentRouter, Core, API, HUD, provider prompts, voice, tools, or runtime adapters." in text


def test_memory_target_resolver_design_prevents_guessing():
    text = Path("docs/memory_target_resolver_design.md").read_text(encoding="utf-8")

    assert "The resolver must prevent guessing." in text
    assert "The resolver must protect against changing or deleting the wrong memory." in text
    assert "Correction and deletion may be prepared only when one concrete memory id is selected." in text


def test_memory_target_resolver_design_defines_resolution_outcomes():
    text = Path("docs/memory_target_resolver_design.md").read_text(encoding="utf-8")

    outcomes = [
        "no_match",
        "single_safe_match",
        "multiple_candidates",
        "unsafe_ambiguous_match",
        "explicit_id_match",
    ]

    for outcome in outcomes:
        assert outcome in text


def test_memory_target_resolver_design_requires_bounded_resolution():
    text = Path("docs/memory_target_resolver_design.md").read_text(encoding="utf-8")

    assert "Resolver input must be bounded." in text
    assert "Resolver output must be bounded." in text
    assert "The resolver must never dump the entire memory store into a provider prompt." in text


def test_memory_target_resolver_design_keeps_matching_deterministic_first():
    text = Path("docs/memory_target_resolver_design.md").read_text(encoding="utf-8")

    assert "Initial resolver implementation should use deterministic matching only:" in text
    assert "exact memory id match" in text
    assert "normalized content substring match" in text
    assert "Semantic or vector matching is out of scope for the first resolver implementation." in text


def test_memory_target_resolver_design_preserves_user_selection_and_confirmation():
    text = Path("docs/memory_target_resolver_design.md").read_text(encoding="utf-8")

    assert "When multiple candidates exist, the user must select one candidate explicitly." in text
    assert "Selection must bind to a concrete memory id." in text
    assert "Selection must create or update a pending action, not execute immediately." in text
    assert "The pending action must still require confirmation for correction or deletion." in text


def test_memory_target_resolver_design_preserves_non_goals():
    text = Path("docs/memory_target_resolver_design.md").read_text(encoding="utf-8")

    non_goals = [
        "resolver implementation",
        "executor integration",
        "IntentRouter integration",
        "Core integration",
        "API endpoints",
        "HUD memory panels",
        "provider prompt injection",
        "automatic memory extraction",
        "semantic/vector search",
        "OS/tool actions",
        "voice integration",
    ]

    for non_goal in non_goals:
        assert non_goal in text
