from unittest.mock import patch

from lucifer_os.interfaces.api_adapter import ApiAdapter
from lucifer_os.interfaces.base import InterfaceInput, InterfaceOutput
from lucifer_os.providers.offline import OfflineProvider


def test_api_adapter_has_name_api():
    adapter = ApiAdapter()

    assert adapter.name == 'api'


def test_api_adapter_wraps_core_and_returns_interface_output():
    adapter = ApiAdapter()

    output = adapter.handle_input(
        InterfaceInput(
            text='Hei Lucifer',
            interface='api',
        )
    )

    assert isinstance(output, InterfaceOutput)
    assert output.visual_channel == 'api'
    assert output.trace_id
    assert 'offline-modus' in output.voice_summary


def test_api_adapter_forces_api_interface_even_if_input_interface_differs():
    adapter = ApiAdapter()

    output = adapter.handle_input(
        InterfaceInput(
            text='Hei Lucifer',
            interface='voice',
        )
    )

    assert output.visual_channel == 'api'


def test_api_adapter_passes_provider_name_to_core_factory():
    with patch('lucifer_os.providers.factory.OllamaProvider', return_value=OfflineProvider()):
        adapter = ApiAdapter(provider_name='ollama')

    output = adapter.handle_input(
        InterfaceInput(
            text='Hei Lucifer',
            interface='api',
        )
    )

    assert output.visual_channel == 'api'
    assert 'offline-modus' in output.voice_summary
