from lucifer_os.core.core import CoreRequest, LuciferCore
from lucifer_os.interfaces.base import InterfaceAdapter, InterfaceInput, InterfaceOutput, output_from_core_result


class FakeInterfaceAdapter(InterfaceAdapter):
    def __init__(self):
        self.core = LuciferCore()

    @property
    def name(self) -> str:
        return 'fake'

    def handle_input(self, input_data: InterfaceInput) -> InterfaceOutput:
        result = self.core.handle(
            CoreRequest(
                text=input_data.text,
                interface=input_data.interface,
                session_id=input_data.session_id,
                metadata=input_data.metadata,
            )
        )
        return output_from_core_result(result)


def test_interface_input_has_expected_fields():
    input_data = InterfaceInput(
        text='Hei Lucifer',
        interface='voice',
        session_id='session-1',
        metadata={'source': 'test'},
    )

    assert input_data.text == 'Hei Lucifer'
    assert input_data.interface == 'voice'
    assert input_data.session_id == 'session-1'
    assert input_data.metadata == {'source': 'test'}


def test_interface_output_has_expected_fields():
    output = InterfaceOutput(
        voice_summary='kort svar',
        visual_text='langt svar',
        visual_channel='hud',
        trace_id='trace-1',
        metadata={'mode': 'test'},
    )

    assert output.voice_summary == 'kort svar'
    assert output.visual_text == 'langt svar'
    assert output.visual_channel == 'hud'
    assert output.trace_id == 'trace-1'
    assert output.metadata == {'mode': 'test'}


def test_output_from_core_result_maps_response_fields():
    core = LuciferCore()

    result = core.handle(CoreRequest(text='Hei Lucifer', interface='hud'))
    output = output_from_core_result(result)

    assert output.voice_summary == result.response.voice_summary
    assert output.visual_text == result.response.visual_text
    assert output.visual_channel == 'hud'
    assert output.trace_id == result.trace_id


def test_interface_adapter_contract_can_wrap_core():
    adapter = FakeInterfaceAdapter()

    output = adapter.handle_input(
        InterfaceInput(
            text='Hei Lucifer',
            interface='voice',
            session_id='session-1',
            metadata={'source': 'test'},
        )
    )

    assert adapter.name == 'fake'
    assert output.visual_channel == 'voice'
    assert output.trace_id
