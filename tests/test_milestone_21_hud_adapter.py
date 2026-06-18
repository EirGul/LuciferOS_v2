from unittest.mock import patch

from lucifer_os.interfaces.base import InterfaceInput, InterfaceOutput
from lucifer_os.interfaces.hud_adapter import HudAdapter
from lucifer_os.providers.offline import OfflineProvider


def test_hud_adapter_has_name_hud():
    adapter = HudAdapter()

    assert adapter.name == 'hud'


def test_hud_adapter_wraps_core_and_returns_interface_output():
    adapter = HudAdapter()

    output = adapter.handle_input(
        InterfaceInput(
            text='Hei Lucifer',
            interface='hud',
        )
    )

    assert isinstance(output, InterfaceOutput)
    assert output.visual_channel == 'hud'
    assert output.trace_id
    assert 'offline-modus' in output.voice_summary


def test_hud_adapter_forces_hud_interface_even_if_input_interface_differs():
    adapter = HudAdapter()

    output = adapter.handle_input(
        InterfaceInput(
            text='Hei Lucifer',
            interface='voice',
        )
    )

    assert output.visual_channel == 'hud'


def test_hud_adapter_passes_provider_name_to_core_factory():
    with patch('lucifer_os.providers.factory.OllamaProvider', return_value=OfflineProvider()):
        adapter = HudAdapter(provider_name='ollama')

    output = adapter.handle_input(
        InterfaceInput(
            text='Hei Lucifer',
            interface='hud',
        )
    )

    assert output.visual_channel == 'hud'
    assert 'offline-modus' in output.voice_summary
