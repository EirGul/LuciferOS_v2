from unittest.mock import patch

from lucifer_os.interfaces.cli import run_cli
from lucifer_os.providers.offline import OfflineProvider


def test_cli_returns_error_when_no_text_is_provided(capsys):
    exit_code = run_cli([])

    captured = capsys.readouterr()

    assert exit_code == 1
    assert 'Bruk:' in captured.out


def test_cli_prints_status_response(capsys):
    exit_code = run_cli(['status'])

    captured = capsys.readouterr()

    assert exit_code == 0
    assert 'LuciferOS kjører. Aktiv provider er offline.' in captured.out
    assert 'LuciferOS status' in captured.out
    assert 'Active provider: offline' in captured.out


def test_cli_prints_conversation_response(capsys):
    exit_code = run_cli(['hei', 'lucifer'])

    captured = capsys.readouterr()

    assert exit_code == 0
    assert 'offline-modus' in captured.out


def test_cli_rejects_unknown_provider(capsys):
    exit_code = run_cli(['--provider', 'unknown', 'hei'])

    captured = capsys.readouterr()

    assert exit_code == 2
    assert 'Ukjent provider: unknown' in captured.out


def test_cli_accepts_ollama_provider_without_real_http(capsys):
    with patch('lucifer_os.interfaces.cli.OllamaProvider', return_value=OfflineProvider()):
        exit_code = run_cli(['--provider', 'ollama', 'hei', 'lucifer'])

    captured = capsys.readouterr()

    assert exit_code == 0
    assert 'offline-modus' in captured.out
