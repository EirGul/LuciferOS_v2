from pathlib import Path


def test_memory_correction_command_grammar_design_exists():
    assert Path("docs/memory_correction_command_grammar_design.md").exists()


def test_memory_correction_command_grammar_design_is_design_only():
    text = Path("docs/memory_correction_command_grammar_design.md").read_text(encoding="utf-8")

    assert "Milestone 115 is design-only." in text
    assert "It must not modify MemoryCommandParser, MemoryCommandExecutor, IntentRouter, Core, API, HUD, provider prompts, voice, tools, or runtime adapters." in text


def test_memory_correction_command_grammar_design_defines_canonical_commands():
    text = Path("docs/memory_correction_command_grammar_design.md").read_text(encoding="utf-8")

    assert 'korriger minne "<target>" til "<replacement>"' in text
    assert 'correct memory "<target>" to "<replacement>"' in text


def test_memory_correction_command_grammar_design_defines_required_fields():
    text = Path("docs/memory_correction_command_grammar_design.md").read_text(encoding="utf-8")

    assert "type = CORRECT" in text
    assert "query = target text" in text
    assert "content = replacement text" in text
    assert "memory_id = None unless an explicit id syntax is added later" in text


def test_memory_correction_command_grammar_design_preserves_safety_boundaries():
    text = Path("docs/memory_correction_command_grammar_design.md").read_text(encoding="utf-8")

    required = [
        "Parser output must never guess a target memory id.",
        "Parser output must not create a pending action.",
        "Parser output must not update memory.",
        "Resolver and executor remain responsible for target resolution and confirmation.",
        "Normal conversation must remain not_memory_command unless it matches the explicit grammar.",
    ]

    for item in required:
        assert item in text


def test_memory_correction_command_grammar_design_preserves_non_goals():
    text = Path("docs/memory_correction_command_grammar_design.md").read_text(encoding="utf-8")

    required = [
        "parser implementation",
        "executor integration",
        "resolver integration",
        "pending-action creation",
        "Core integration",
        "provider prompt injection",
        "voice integration",
    ]

    for item in required:
        assert item in text
