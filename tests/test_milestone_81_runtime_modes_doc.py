from pathlib import Path


def test_runtime_modes_document_exists():
    doc = Path('docs/runtime_modes.md')

    assert doc.is_file()


def test_runtime_modes_document_defines_offline_and_ollama_modes():
    doc = Path('docs/runtime_modes.md').read_text(encoding='utf-8')

    assert 'Safe / Offline Mode' in doc
    assert 'Local AI / Ollama Mode' in doc
    assert 'start_lucifer_api.bat' in doc
    assert 'start_lucifer_api_ollama.bat' in doc
    assert 'provider_name : offline' in doc
    assert 'provider_name : ollama' in doc


def test_runtime_modes_document_preserves_boundaries():
    doc = Path('docs/runtime_modes.md').read_text(encoding='utf-8')

    assert 'HUD may display runtime status, but must not choose providers.' in doc
    assert 'Provider selection belongs to API/runtime configuration.' in doc
    assert 'Core must remain interface-independent.' in doc
    assert 'Offline mode must remain available.' in doc
    assert 'Ollama mode must remain explicit.' in doc
