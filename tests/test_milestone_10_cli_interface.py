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
    with patch('lucifer_os.providers.factory.OllamaProvider', return_value=OfflineProvider()):
        exit_code = run_cli(['--provider', 'ollama', 'hei', 'lucifer'])

    captured = capsys.readouterr()

    assert exit_code == 0
    assert 'offline-modus' in captured.out


def test_cli_uses_config_default_provider_when_no_provider_argument(capsys):
    exit_code = run_cli(['hei', 'lucifer'])

    captured = capsys.readouterr()

    assert exit_code == 0
    assert 'offline-modus' in captured.out


def test_cli_provider_argument_overrides_config_default(capsys):
    with patch('lucifer_os.providers.factory.OllamaProvider', return_value=OfflineProvider()):
        exit_code = run_cli(['--provider', 'ollama', 'hei'])

    captured = capsys.readouterr()

    assert exit_code == 0
    assert 'offline-modus' in captured.out


def test_cli_uses_config_ollama_model_when_creating_ollama_provider(capsys):
    captured_configs = []

    def fake_ollama_provider(config):
        captured_configs.append(config)
        return OfflineProvider()

    with patch('lucifer_os.providers.factory.OllamaProvider', side_effect=fake_ollama_provider):
        exit_code = run_cli(['--provider', 'ollama', 'hei'])

    captured = capsys.readouterr()

    assert exit_code == 0
    assert 'offline-modus' in captured.out
    assert captured_configs
    assert captured_configs[0].model == 'eirik-qwen3:latest'


def test_cli_api_mode_uses_api_client(capsys, monkeypatch):
    from lucifer_os.interfaces.api_schema import ApiChatResponse
    from lucifer_os.interfaces.cli import run_cli

    class FakeClient:
        def chat(self, text):
            assert text == 'Hei Lucifer'
            return ApiChatResponse(
                voice_summary='api kort svar',
                visual_text='api langt svar',
                visual_channel='api',
                trace_id='trace-api',
                metadata={},
            )

    monkeypatch.setattr('lucifer_os.interfaces.cli.LuciferApiClient', FakeClient)

    exit_code = run_cli(['--api', 'Hei', 'Lucifer'])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert 'api kort svar' in captured.out
    assert 'api langt svar' in captured.out


def test_cli_api_mode_returns_error_when_api_is_unavailable(capsys, monkeypatch):
    from lucifer_os.interfaces.cli import run_cli

    class FakeClient:
        def chat(self, text):
            raise ConnectionError('Kunne ikke kontakte LuciferOS API')

    monkeypatch.setattr('lucifer_os.interfaces.cli.LuciferApiClient', FakeClient)

    exit_code = run_cli(['--api', 'Hei', 'Lucifer'])

    captured = capsys.readouterr()
    assert exit_code == 2
    assert 'Kunne ikke kontakte LuciferOS API' in captured.out


def test_cli_api_mode_keeps_empty_text_validation(capsys):
    from lucifer_os.interfaces.cli import run_cli

    exit_code = run_cli(['--api'])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert '--api' in captured.out


def test_cli_api_health_prints_health_response(capsys, monkeypatch):
    from lucifer_os.interfaces.api_schema import ApiHealthResponse
    from lucifer_os.interfaces.cli import run_cli

    class FakeClient:
        def health(self):
            return ApiHealthResponse(
                app_ready=True,
                project_root='.',
                interface_name='api',
                provider_name=None,
                adapter_name='api',
            )

    monkeypatch.setattr('lucifer_os.interfaces.cli.LuciferApiClient', FakeClient)

    exit_code = run_cli(['--api-health'])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert 'app_ready: True' in captured.out
    assert 'interface_name: api' in captured.out
    assert 'adapter_name: api' in captured.out


def test_cli_api_health_returns_error_when_api_is_unavailable(capsys, monkeypatch):
    from lucifer_os.interfaces.cli import run_cli

    class FakeClient:
        def health(self):
            raise ConnectionError('Kunne ikke kontakte LuciferOS API')

    monkeypatch.setattr('lucifer_os.interfaces.cli.LuciferApiClient', FakeClient)

    exit_code = run_cli(['--api-health'])

    captured = capsys.readouterr()
    assert exit_code == 2
    assert 'Kunne ikke kontakte LuciferOS API' in captured.out


def test_cli_help_mentions_api_health(capsys):
    from lucifer_os.interfaces.cli import run_cli

    exit_code = run_cli([])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert '--api-health' in captured.out
