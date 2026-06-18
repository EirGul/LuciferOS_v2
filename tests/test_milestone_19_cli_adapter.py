from unittest.mock import patch

from lucifer_os.interfaces.base import InterfaceInput, InterfaceOutput
from lucifer_os.interfaces.cli_adapter import CliAdapter
from lucifer_os.providers.offline import OfflineProvider


def test_cli_adapter_has_name_cli():
    adapter = CliAdapter()

    assert adapter.name == 'cli'


def test_cli_adapter_wraps_core_and_returns_interface_output():
    adapter = CliAdapter()

    output = adapter.handle_input(
        InterfaceInput(
            text='Hei Lucifer',
            interface='cli',
        )
    )

    assert isinstance(output, InterfaceOutput)
    assert output.visual_channel == 'cli'
    assert output.trace_id
    assert 'offline-modus' in output.voice_summary


def test_cli_adapter_passes_provider_name_to_core_factory():
    with patch('lucifer_os.providers.factory.OllamaProvider', return_value=OfflineProvider()):
        adapter = CliAdapter(provider_name='ollama')

    output = adapter.handle_input(
        InterfaceInput(
            text='Hei Lucifer',
            interface='cli',
        )
    )

    assert output.visual_channel == 'cli'
    assert 'offline-modus' in output.voice_summary
