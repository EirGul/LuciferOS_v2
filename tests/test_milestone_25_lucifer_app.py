from unittest.mock import patch

import pytest

from lucifer_os.interfaces.base import InterfaceOutput
from lucifer_os.providers.offline import OfflineProvider
from lucifer_os.runtime.app import LuciferApp


def test_lucifer_app_defaults_to_cli_interface():
    app = LuciferApp()

    assert app.interface_name == 'cli'
    assert app.adapter.name == 'cli'


def test_lucifer_app_handles_text_and_returns_interface_output():
    app = LuciferApp(interface_name='cli')

    output = app.handle_text('Hei Lucifer')

    assert isinstance(output, InterfaceOutput)
    assert output.visual_channel == 'cli'
    assert output.trace_id
    assert 'offline-modus' in output.voice_summary


def test_lucifer_app_supports_api_interface():
    app = LuciferApp(interface_name='api')

    output = app.handle_text('Hei Lucifer')

    assert output.visual_channel == 'api'


def test_lucifer_app_supports_hud_interface():
    app = LuciferApp(interface_name='hud')

    output = app.handle_text('Hei Lucifer')

    assert output.visual_channel == 'hud'


def test_lucifer_app_supports_voice_interface():
    app = LuciferApp(interface_name='voice')

    output = app.handle_text('Hei Lucifer')

    assert output.visual_channel == 'voice'


def test_lucifer_app_passes_provider_name_to_interface_adapter():
    with patch('lucifer_os.providers.factory.OllamaProvider', return_value=OfflineProvider()):
        app = LuciferApp(interface_name='cli', provider_name='ollama')

    output = app.handle_text('Hei Lucifer')

    assert output.visual_channel == 'cli'
    assert 'offline-modus' in output.voice_summary


def test_lucifer_app_passes_session_and_metadata_to_core_audit():
    app = LuciferApp(interface_name='voice')

    output = app.handle_text(
        'Hei Lucifer',
        session_id='session-1',
        metadata={'source': 'test'},
    )

    assert output.visual_channel == 'voice'
    assert output.trace_id


def test_lucifer_app_rejects_unknown_interface():
    with pytest.raises(ValueError, match='Ukjent interface: unknown'):
        LuciferApp(interface_name='unknown')


def test_lucifer_app_status_returns_status_output():
    app = LuciferApp(interface_name='cli')

    output = app.status()

    assert output.visual_channel == 'cli'
    assert 'LuciferOS status' in output.visual_text
    assert 'Active provider: offline' in output.visual_text


def test_lucifer_app_status_uses_app_interface():
    app = LuciferApp(interface_name='hud')

    output = app.status()

    assert output.visual_channel == 'hud'
    assert 'LuciferOS status' in output.visual_text
