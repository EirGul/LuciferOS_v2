from pathlib import Path


def test_memory_command_execution_docs_reflect_current_executor_status():
    text = Path("docs/memory_command_execution_design.md").read_text(encoding="utf-8")

    assert "MemoryCommandExecutor now exists as an isolated memory-layer component." in text
    assert "Memory command execution translates parsed MemoryCommand objects into safe MemoryService operations." in text
    assert "The executor must not bypass MemoryService, MemoryPolicy or MemoryAuditSink." in text


def test_memory_command_execution_docs_preserve_integration_boundaries():
    text = Path("docs/memory_command_execution_design.md").read_text(encoding="utf-8")

    assert "It must not connect memory command execution to IntentRouter, Core, API, HUD, provider prompts, voice, tools, or runtime adapters." in text
    assert "MemoryCommandExecutor belongs to the memory layer only." in text
    assert "It is not a runtime router." in text
    assert "It is not a provider prompt builder." in text


def test_memory_command_execution_docs_describe_implemented_behavior():
    text = Path("docs/memory_command_execution_design.md").read_text(encoding="utf-8")

    required_behaviors = [
        "execute remember commands through MemoryService.add_memory",
        "create pending remember actions when MemoryService requires confirmation",
        "list memories with max_results bounds",
        "search memories with bounded substring matching",
        "prepare correction commands as pending actions when an explicit memory id exists",
        "prepare delete commands as pending actions when an explicit memory id exists",
        "execute confirmed pending remember actions",
        "execute confirmed pending correction actions",
        "execute confirmed pending delete actions",
    ]

    for behavior in required_behaviors:
        assert behavior in text


def test_memory_command_execution_docs_describe_confirmation_safety():
    text = Path("docs/memory_command_execution_design.md").read_text(encoding="utf-8")

    assert "Confirmation is bound to one concrete pending action." in text
    assert "Stale pending actions must not execute." in text
    assert "Confirming a pending action clears it before execution." in text
    assert "The same pending action must not execute twice." in text
    assert "Confirm after cancel must not execute anything." in text


def test_memory_command_execution_docs_describe_target_resolution_limits():
    text = Path("docs/memory_command_execution_design.md").read_text(encoding="utf-8")

    assert "Correct and delete commands must not guess the target memory item." in text
    assert "They may prepare execution only when the command contains an explicit memory id." in text
    assert "If multiple candidates exist, the system must ask the user to choose." in text


def test_memory_command_execution_docs_preserve_non_goals():
    text = Path("docs/memory_command_execution_design.md").read_text(encoding="utf-8")

    non_goals = [
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
