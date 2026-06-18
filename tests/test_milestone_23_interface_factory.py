import pytest

from lucifer_os.interfaces.api_adapter import ApiAdapter
from lucifer_os.interfaces.cli_adapter import CliAdapter
from lucifer_os.interfaces.factory import create_interface_adapter
from lucifer_os.interfaces.hud_adapter import HudAdapter
from lucifer_os.interfaces.voice_adapter import VoiceAdapter


def test_interface_factory_creates_cli_adapter():
    adapter = create_interface_adapter('cli')

    assert isinstance(adapter, CliAdapter)
    assert adapter.name == 'cli'


def test_interface_factory_creates_api_adapter():
    adapter = create_interface_adapter('api')

    assert isinstance(adapter, ApiAdapter)
    assert adapter.name == 'api'


def test_interface_factory_creates_hud_adapter():
    adapter = create_interface_adapter('hud')

    assert isinstance(adapter, HudAdapter)
    assert adapter.name == 'hud'


def test_interface_factory_creates_voice_adapter():
    adapter = create_interface_adapter('voice')

    assert isinstance(adapter, VoiceAdapter)
    assert adapter.name == 'voice'


def test_interface_factory_normalizes_interface_name():
    adapter = create_interface_adapter('  VOICE  ')

    assert isinstance(adapter, VoiceAdapter)
    assert adapter.name == 'voice'


def test_interface_factory_passes_provider_name_to_adapter():
    adapter = create_interface_adapter('cli', provider_name='offline')

    assert adapter.provider_name == 'offline'


def test_interface_factory_rejects_unknown_interface():
    with pytest.raises(ValueError, match='Ukjent interface: unknown'):
        create_interface_adapter('unknown')
