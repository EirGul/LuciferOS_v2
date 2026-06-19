from pathlib import Path


def test_memory_persistence_design_doc_exists():
    doc = Path("docs/memory_persistence_design.md")

    assert doc.exists()


def test_memory_persistence_design_is_design_only():
    text = Path("docs/memory_persistence_design.md").read_text(encoding="utf-8")

    assert "Milestone 92 is design-only." in text
    assert "It must not connect memory to Core, API, HUD, provider prompts, voice, tools, or runtime adapters." in text


def test_memory_persistence_prefers_sqlite_not_json_as_primary_store():
    text = Path("docs/memory_persistence_design.md").read_text(encoding="utf-8")

    assert "The preferred durable backend is SQLite." in text
    assert "JSON must not become the primary durable memory backend." in text


def test_memory_persistence_preserves_existing_store_contract():
    text = Path("docs/memory_persistence_design.md").read_text(encoding="utf-8")

    assert "Persistent stores must implement the existing MemoryStore interface." in text
    assert "The existing InMemoryMemoryStore must remain valid" in text


def test_memory_persistence_boundaries_are_explicit():
    text = Path("docs/memory_persistence_design.md").read_text(encoding="utf-8")

    forbidden_future_work = [
        "provider prompt injection",
        "automatic memory extraction",
        "API memory endpoints",
        "HUD memory editing",
        "Core memory retrieval hooks",
        "voice memory commands",
        "semantic or vector retrieval",
        "PC-control memory integration",
    ]

    for item in forbidden_future_work:
        assert item in text
