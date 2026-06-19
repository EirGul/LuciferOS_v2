from pathlib import Path


def test_memory_architecture_documents_sqlite_persistence_status():
    text = Path("docs/memory_architecture.md").read_text(encoding="utf-8")

    assert "SQLite persistent store" in text
    assert "Persistent memory storage is implemented through SQLiteMemoryStore." in text
    assert "Persistence is still not connected to Core, API, HUD, providers, voice or tools." in text


def test_memory_architecture_documents_update_and_correction_policy():
    text = Path("docs/memory_architecture.md").read_text(encoding="utf-8")

    assert "MemoryUpdateRequest" in text
    assert "update_memory" in text
    assert "Memory updates and corrections must pass through policy." in text


def test_memory_persistence_design_matches_current_implementation():
    text = Path("docs/memory_persistence_design.md").read_text(encoding="utf-8")

    assert "Current status after Milestone 97" in text
    assert "SQLiteMemoryStore" in text
    assert "policy-gated update/correction flow" in text
    assert "persistence across new SQLite store instances" in text


def test_memory_persistence_design_preserves_integration_boundaries():
    text = Path("docs/memory_persistence_design.md").read_text(encoding="utf-8")

    forbidden_integrations = [
        "provider prompt injection",
        "automatic memory extraction",
        "API memory endpoints",
        "HUD memory editing",
        "Core memory retrieval hooks",
        "voice memory commands",
        "semantic or vector retrieval",
        "PC-control memory integration",
    ]

    for integration in forbidden_integrations:
        assert integration in text
