from pathlib import Path


def test_memory_command_design_doc_exists():
    doc = Path("docs/memory_command_design.md")

    assert doc.exists()


def test_memory_command_design_is_design_only():
    text = Path("docs/memory_command_design.md").read_text(encoding="utf-8")

    assert "Milestone 99 is design-only." in text
    assert "It must not connect memory commands to IntentRouter, Core, API, HUD, provider prompts, voice, tools, or runtime adapters." in text


def test_memory_command_design_defines_command_categories():
    text = Path("docs/memory_command_design.md").read_text(encoding="utf-8")

    required_categories = [
        "remember",
        "list memories",
        "search memories",
        "correct memory",
        "delete memory",
        "explain memory policy",
        "cancel pending memory action",
        "confirm pending memory action",
    ]

    for category in required_categories:
        assert category in text


def test_memory_command_design_preserves_policy_and_audit_rules():
    text = Path("docs/memory_command_design.md").read_text(encoding="utf-8")

    assert "policy-gated writes, updates and deletes" in text
    assert "confirmation for high-impact operations" in text
    assert "audit events for meaningful memory operations" in text
    assert "Deletes must require confirmation." in text
    assert "High-impact corrections must require confirmation." in text


def test_memory_command_design_protects_routing_boundaries():
    text = Path("docs/memory_command_design.md").read_text(encoding="utf-8")

    assert "Milestone 99 must not modify IntentRouter." in text
    assert "Future memory command routing should be explicit and must not use aggressive fuzzy matching." in text
    assert "Words like lære, lært, husk or glem must not automatically hijack ordinary conversation." in text


def test_memory_command_design_protects_provider_boundary():
    text = Path("docs/memory_command_design.md").read_text(encoding="utf-8")

    assert "Memory commands must not inject memory into provider prompts." in text
    assert "Provider context injection is a separate future milestone" in text
