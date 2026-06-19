from pathlib import Path


def read_doc() -> str:
    return Path("docs/memory_candidate_selection_lifecycle_design.md").read_text(
        encoding="utf-8"
    )


def test_selection_lifecycle_design_exists():
    assert Path("docs/memory_candidate_selection_lifecycle_design.md").exists()


def test_selection_lifecycle_design_is_design_only():
    text = read_doc()

    assert "Milestone 123 is design-only." in text
    assert (
        "It must not modify MemoryCommandExecutor, MemoryCandidateSelectionRequestService, "
        "PendingMemoryActionService, IntentRouter, Core, API, HUD, provider prompts, voice, "
        "tools, or runtime adapters."
    ) in text


def test_selection_lifecycle_design_defines_required_states():
    text = read_doc()

    required = [
        "created",
        "awaiting_user_selection",
        "selected",
        "prepared_for_confirmation",
        "cancelled",
        "expired",
        "replaced",
    ]

    for item in required:
        assert item in text


def test_selection_lifecycle_design_requires_request_and_memory_identity():
    text = read_doc()

    assert "the active selection request id" in text
    assert "one concrete memory id from that request" in text
    assert "a request id that does not match the active request" in text
    assert "a memory id not present in the active request" in text
    assert 'Ordinal selections such as "1" or "2" are not part of this milestone.' in text


def test_selection_lifecycle_design_requires_expiry_before_runtime_integration():
    text = read_doc()

    assert "Selection requests must be short-lived." in text
    assert "Expired selection requests must be cleared and must not prepare a PendingMemoryAction." in text
    assert "Selection expiry must be independent from pending-action expiry." in text


def test_selection_lifecycle_design_prevents_silent_user_facing_replacement():
    text = read_doc()

    assert "A new ambiguous memory command must not silently replace an active selection request in a user-facing flow." in text
    assert "require explicit cancellation before replacement" in text
    assert "Cancellation must clear the selection request without changing memory and without creating a pending action." in text


def test_selection_lifecycle_design_preserves_selection_to_pending_safety():
    text = read_doc()

    required = [
        "A valid selection may prepare exactly one PendingMemoryAction.",
        "clear the active selection request",
        "preserve proposed correction content for CORRECT",
        "preserve the separate PendingMemoryActionService confirmation gate",
        "Selection must not call MemoryService.update_memory or MemoryService.delete_memory.",
    ]

    for item in required:
        assert item in text


def test_selection_lifecycle_design_preserves_interface_and_non_goal_boundaries():
    text = read_doc()

    required = [
        "create PendingMemoryAction objects directly",
        "bypass MemoryCandidateSelector",
        "bypass MemoryCandidateSelectionPendingActionBuilder",
        "inject candidate lists into provider prompts",
        "selection lifecycle implementation",
        "selection expiry implementation",
        "selection cancellation implementation",
        "runtime selection commands",
        "Core integration",
        "voice integration",
    ]

    for item in required:
        assert item in text
