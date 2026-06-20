from pathlib import Path


def read_doc() -> str:
    return Path("docs/memory_candidate_selection_audit_delivery_design.md").read_text(
        encoding="utf-8"
    )


def test_selection_audit_delivery_design_exists():
    assert Path("docs/memory_candidate_selection_audit_delivery_design.md").exists()


def test_selection_audit_delivery_design_is_design_only_and_isolated():
    text = read_doc()

    assert "Milestone 129 is design-only." in text
    assert "It must not modify MemoryCommandExecutor" in text
    assert "Core, API, HUD, provider prompts, voice, tools, or runtime adapters." in text


def test_selection_audit_delivery_design_selects_fail_closed_for_state_changes():
    text = read_doc()

    assert "Decision: fail closed for state-changing selection transitions" in text
    assert "A failed audit delivery must prevent the related state transition from completing." in text
    assert "The system must return or surface an explicit audit-delivery failure." in text


def test_selection_audit_delivery_design_distinguishes_rejection_events():
    text = read_doc()

    required = [
        "the user-facing operation remains rejected",
        "the audit event should still be attempted",
        "an audit-delivery failure must be surfaced explicitly",
        "the active selection request must remain unchanged",
    ]

    for item in required:
        assert item in text


def test_selection_audit_delivery_design_assigns_expiry_to_selection_service():
    text = read_doc()

    assert "MemoryCandidateSelectionRequestService owns" in text
    assert "selection_request_expired" in text
    assert "The service owns expiry because it determines staleness and clears the request." in text


def test_selection_audit_delivery_design_assigns_remaining_events_to_executor():
    text = read_doc()

    required = [
        "MemoryCommandExecutor owns",
        "selection_request_created",
        "selection_request_rejected",
        "selection_request_cancelled",
        "selection_candidate_rejected",
        "selection_candidate_accepted",
        "selection_pending_action_prepared",
    ]

    for item in required:
        assert item in text


def test_selection_audit_delivery_design_requires_safe_ordering():
    text = read_doc()

    required = [
        "If step 2 fails, no active request is stored.",
        "If step 3 fails, the stale request remains stored and no expiry result is reported as completed.",
        "If step 2 fails, the active request remains stored.",
        "If either audit delivery fails, the active selection request remains stored and no pending action is stored.",
    ]

    for item in required:
        assert item in text


def test_selection_audit_delivery_design_preserves_minimal_failure_data_and_non_goals():
    text = read_doc()

    required = [
        "a bounded reason code",
        "no raw candidate content",
        "no raw source text",
        "no proposed correction content",
        "no provider prompt data",
        "audit delivery implementation",
        "executor audit calls",
        "selection-service audit calls",
        "global audit integration",
        "Core integration",
        "voice integration",
    ]

    for item in required:
        assert item in text
