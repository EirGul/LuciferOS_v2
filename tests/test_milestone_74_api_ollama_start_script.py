from pathlib import Path


def test_ollama_api_start_script_exists_and_sets_provider():
    script = Path('start_lucifer_api_ollama.bat')

    assert script.is_file()

    content = script.read_text(encoding='utf-8')

    assert 'set LUCIFER_PROVIDER=ollama' in content
    assert 'py -m lucifer_os.interfaces.api_server' in content
    assert 'http://127.0.0.1:8787' in content
    assert 'Ctrl+C' in content
