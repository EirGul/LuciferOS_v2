from unittest.mock import patch

from lucifer_os.interfaces.base import InterfaceInput, InterfaceOutput
from lucifer_os.interfaces.voice_adapter import VoiceAdapter
from lucifer_os.providers.offline import OfflineProvider


def test_voice_adapter_has_name_voice():
    adapter = VoiceAdapter()

    assert adapter.name == 'voice'


def test_voice_adapter_wraps_core_and_returns_interface_output():
    adapter = VoiceAdapter()

    output = adapter.handle_input(
        InterfaceInput(
            text='Hei Lucifer',
            interface='voice',
        )
    )

    assert isinstance(output, InterfaceOutput)
    assert output.visual_channel == 'voice'
    assert output.trace_id
    assert 'offline-modus' in output.voice_summary


def test_voice_adapter_forces_voice_interface_even_if_input_interface_differs():
    adapter = VoiceAdapter()

    output = adapter.handle_input(
        InterfaceInput(
            text='Hei Lucifer',
            interface='hud',
        )
    )

    assert output.visual_channel == 'voice'


def test_voice_adapter_passes_provider_name_to_core_factory():
    with patch('lucifer_os.providers.factory.OllamaProvider', return_value=OfflineProvider()):
        adapter = VoiceAdapter(provider_name='ollama')

    output = adapter.handle_input(
        InterfaceInput(
            text='Hei Lucifer',
            interface='voice',
        )
    )

    assert output.visual_channel == 'voice'
    assert 'offline-modus' in output.voice_summary
