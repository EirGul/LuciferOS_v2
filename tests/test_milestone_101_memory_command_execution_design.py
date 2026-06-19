from pathlib import Path


def test_memory_command_execution_design_doc_exists():
    doc = Path("docs/memory_command_execution_design.md")

    assert doc.exists()


def test_memory_command_execution_design_is_design_only():
    text = Path("docs/memory_command_execution_design.md").read_text(encoding="utf-8")

    assert "Milestone 101 is design-only." in text
    assert "It must not connect memory command execution to IntentRouter, Core, API, HUD, provider prompts, voice, tools, or runtime adapters." in text


def test_memory_command_execution_design_requires_memory_service_boundary():
    text = Path("docs/memory_command_execution_design.md").read_text(encoding="utf-8")

    assert "The executor must not bypass MemoryService, MemoryPolicy or MemoryAuditSink." in text
    assert "Executor logic must call MemoryService." in text
    assert "Executor logic must preserve policy decisions." in text
    assert "Executor logic must preserve audit events." in text


def test_memory_command_execution_design_requires_pending_actions_for_risky_operations():
    text = Path("docs/memory_command_execution_design.md").read_text(encoding="utf-8")

    assert "Pending actions are required for:" in text
    assert "high-impact remember commands" in text
    assert "high-impact correction commands" in text
    assert "all delete commands" in text
    assert "ambiguous correction targets" in text
    assert "ambiguous delete targets" in text


def test_memory_command_execution_design_prevents_unsafe_confirmation():
    text = Path("docs/memory_command_execution_design.md").read_text(encoding="utf-8")

    assert "Confirmation must be bound to one concrete pending action." in text
    assert "Generic confirmation phrases such as ja, bekreft or confirm must not execute unrelated actions." in text
    assert "Stale pending actions must not execute." in text


def test_memory_command_execution_design_prevents_guessing_correct_or_delete_targets():
    text = Path("docs/memory_command_execution_design.md").read_text(encoding="utf-8")

    assert "Correct and delete commands must not guess the target memory item." in text
    assert "the command contains an explicit memory id" in text
    assert "the user has selected one memory from a bounded result list" in text
    assert "If multiple candidates exist, the system must ask the user to choose." in text


def test_memory_command_execution_design_preserves_non_goals():
    text = Path("docs/memory_command_execution_design.md").read_text(encoding="utf-8")

    non_goals = [
        "runtime execution",
        "Core integration",
        "API endpoints",
        "HUD memory panels",
        "provider prompt injection",
        "automatic memory extraction",
        "semantic/vector search",
        "OS/tool actions",
    ]

    for non_goal in non_goals:
        assert non_goal in text
