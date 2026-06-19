from pathlib import Path


def test_memory_architecture_document_exists():
    doc = Path('docs/memory_architecture.md')

    assert doc.is_file()


def test_memory_architecture_document_lists_core_memory_modules():
    doc = Path('docs/memory_architecture.md').read_text(encoding='utf-8')

    assert 'models.py' in doc
    assert 'store.py' in doc
    assert 'service.py' in doc
    assert 'learning.py' in doc
    assert 'policy.py' in doc
    assert 'audit.py' in doc
    assert 'retrieval.py' in doc
    assert 'context.py' in doc


def test_memory_architecture_document_preserves_boundaries():
    doc = Path('docs/memory_architecture.md').read_text(encoding='utf-8')

    assert 'Memory is its own subsystem.' in doc
    assert 'HUD must not write memory directly.' in doc
    assert 'Providers must not receive unbounded memory dumps.' in doc
    assert 'Automatic memory from normal chat is not allowed at this stage.' in doc


def test_memory_architecture_document_lists_not_implemented_items():
    doc = Path('docs/memory_architecture.md').read_text(encoding='utf-8')

    assert 'Persistent database storage' in doc
    assert 'Core integration' in doc
    assert 'Provider prompt-context injection' in doc
    assert 'User-facing memory management commands' in doc
