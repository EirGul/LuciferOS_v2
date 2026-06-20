from pathlib import Path


def read_doc() -> str:
    return Path("docs/memory_candidate_selection_audit_design.md").read_text(
        encoding="utf-8"
    )


def test_selection_audit_design_exists():
    assert Path("docs/memory_candidate_selection_audit_design.md").exists()


def test_selection_audit_design_is_design_only_and_isolated():
    text = read_doc()

    assert "Milestone 126 is design-only." in text
    assert "It must not modify MemoryCommandExecutor" in text
    assert "MemoryAuditSink" in text
    assert "Core, API, HUD, provider prompts, voice, tools, or runtime adapters." in text


def test_selection_audit_design_declares_required_lifecycle_actions():
    text = read_doc()

    required_actions = [
        "selection_request_created",
        "selection_request_rejected",
        "selection_request_cancelled",
        "selection_request_expired",
        "selection_candidate_rejected",
        "selection_candidate_accepted",
        "selection_pending_action_prepared",
    ]

    for action in required_actions:
        assert action in text


def test_selection_audit_design_requires_minimal_traceability_fields():
    text = read_doc()

    required_fields = [
        "event id",
        "timestamp",
        "action",
        "selection request id when available",
        "command type",
        "selected memory id when a candidate was accepted",
        "pending action id when a pending action was prepared",
        "reason or bounded outcome code",
        "source identifier for the owning memory component",
    ]

    for field in required_fields:
        assert field in text


def test_selection_audit_design_excludes_sensitive_or_unbounded_content():
    text = read_doc()

    excluded = [
        "all candidate memory contents",
        "raw user command text by default",
        "proposed correction content by default",
        "provider prompts",
        "full memory-store snapshots",
        "interface-local presentation state",
    ]

    for item in excluded:
        assert item in text


def test_selection_audit_design_maps_selection_lifecycle_without_memory_mutation():
    text = read_doc()

    required = [
        "selection_request_created",
        "selection_request_rejected",
        "selection_candidate_rejected",
        "selection_candidate_accepted",
        "selection_pending_action_prepared",
        "Selection expiry and cancellation must never create a memory update or delete event.",
    ]

    for item in required:
        assert item in text


def test_selection_audit_design_requires_order_before_pending_confirmation():
    text = read_doc()

    assert "selection_candidate_accepted is emitted." in text
    assert "selection_pending_action_prepared is emitted." in text
    assert "No selection audit event may claim that memory changed before confirmation reaches MemoryService." in text


def test_selection_audit_design_preserves_non_goals():
    text = read_doc()

    non_goals = [
        "selection audit implementation",
        "MemoryAuditAction enum changes",
        "MemoryAuditSink changes",
        "executor audit calls",
        "persistent audit storage",
        "global audit integration",
        "Core integration",
        "API endpoints",
        "HUD panels",
        "provider prompt injection",
        "automatic memory extraction",
        "semantic or vector retrieval",
        "OS or tool actions",
        "voice integration",
    ]

    for item in non_goals:
        assert item in text
