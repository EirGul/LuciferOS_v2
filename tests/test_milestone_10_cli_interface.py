from lucifer_os.interfaces.cli import run_cli


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
