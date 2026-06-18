from lucifer_os.interfaces.hud_models import HudChatView, HudHealthView
from lucifer_os.interfaces.hud_preview import run_hud_preview


class FakeHudController:
    def health_view(self):
        return HudHealthView(
            online=True,
            status_text='LuciferOS API online',
            provider_name='offline',
            adapter_name='api',
        )

    def send_text_view(self, text):
        assert text == 'Hei Lucifer'
        return HudChatView(
            voice_summary='hud kort svar',
            visual_text='hud langt svar',
            trace_id='trace-preview',
            metadata={},
        )


class FailingHudController:
    def health_view(self):
        raise ConnectionError('Kunne ikke kontakte LuciferOS API')


def test_hud_preview_health_prints_health_view(capsys, monkeypatch):
    monkeypatch.setattr('lucifer_os.interfaces.hud_preview.HudController', FakeHudController)

    exit_code = run_hud_preview(['health'])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert 'online: True' in captured.out
    assert 'status: LuciferOS API online' in captured.out
    assert 'provider: offline' in captured.out
    assert 'adapter: api' in captured.out


def test_hud_preview_chat_prints_chat_view(capsys, monkeypatch):
    monkeypatch.setattr('lucifer_os.interfaces.hud_preview.HudController', FakeHudController)

    exit_code = run_hud_preview(['chat', 'Hei', 'Lucifer'])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert 'voice: hud kort svar' in captured.out
    assert 'visual: hud langt svar' in captured.out
    assert 'trace_id: trace-preview' in captured.out


def test_hud_preview_requires_command(capsys):
    exit_code = run_hud_preview([])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert 'hud_preview health|chat' in captured.out


def test_hud_preview_chat_requires_text(capsys, monkeypatch):
    monkeypatch.setattr('lucifer_os.interfaces.hud_preview.HudController', FakeHudController)

    exit_code = run_hud_preview(['chat'])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert 'chat <tekst>' in captured.out


def test_hud_preview_unknown_command_returns_error(capsys, monkeypatch):
    monkeypatch.setattr('lucifer_os.interfaces.hud_preview.HudController', FakeHudController)

    exit_code = run_hud_preview(['unknown'])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert 'Ukjent HUD-preview kommando: unknown' in captured.out


def test_hud_preview_returns_error_when_api_unavailable(capsys, monkeypatch):
    monkeypatch.setattr('lucifer_os.interfaces.hud_preview.HudController', FailingHudController)

    exit_code = run_hud_preview(['health'])

    captured = capsys.readouterr()
    assert exit_code == 2
    assert 'Kunne ikke kontakte LuciferOS API' in captured.out
