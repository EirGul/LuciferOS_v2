from pathlib import Path


def test_luciferos_manifest_exists():
    manifest = Path('docs/luciferos_manifest.md')

    assert manifest.is_file()


def test_luciferos_manifest_defines_memory_architecture():
    manifest = Path('docs/luciferos_manifest.md').read_text(encoding='utf-8')

    assert 'Memory & Learning Subsystem' in manifest
    assert 'MemoryService' in manifest
    assert 'MemoryStore' in manifest
    assert 'LearningService' in manifest
    assert 'Permission checks' in manifest
    assert 'Audit logging' in manifest
    assert 'LuciferOS must not store everything the user says.' in manifest
    assert 'The user must be able to delete or correct memories.' in manifest


def test_luciferos_manifest_preserves_core_boundaries():
    manifest = Path('docs/luciferos_manifest.md').read_text(encoding='utf-8')

    assert 'Core must be small, deterministic, testable and interface-independent.' in manifest
    assert 'HUD must not own routing, provider selection, permissions, tools, memory or OS actions.' in manifest
    assert 'Default provider must remain offline unless explicitly overridden.' in manifest
