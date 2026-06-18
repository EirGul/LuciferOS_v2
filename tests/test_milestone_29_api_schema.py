from lucifer_os.interfaces.api_schema import (
    ApiChatRequest,
    ApiChatResponse,
    ApiHealthResponse,
    api_chat_response_from_output,
    api_health_response_from_dict,
)
from lucifer_os.interfaces.base import InterfaceOutput


def test_api_chat_request_has_safe_defaults():
    request = ApiChatRequest(text='Hei Lucifer')

    assert request.text == 'Hei Lucifer'
    assert request.session_id is None
    assert request.metadata == {}


def test_api_chat_request_accepts_session_and_metadata():
    request = ApiChatRequest(
        text='Hei Lucifer',
        session_id='session-1',
        metadata={'source': 'api-test'},
    )

    assert request.session_id == 'session-1'
    assert request.metadata == {'source': 'api-test'}


def test_api_chat_response_from_interface_output():
    output = InterfaceOutput(
        voice_summary='kort svar',
        visual_text='langt svar',
        visual_channel='api',
        trace_id='trace-1',
        metadata={'mode': 'test'},
    )

    response = api_chat_response_from_output(output)

    assert isinstance(response, ApiChatResponse)
    assert response.voice_summary == 'kort svar'
    assert response.visual_text == 'langt svar'
    assert response.visual_channel == 'api'
    assert response.trace_id == 'trace-1'
    assert response.metadata == {'mode': 'test'}


def test_api_health_response_from_health_dict_with_provider():
    response = api_health_response_from_dict(
        {
            'app_ready': True,
            'project_root': '.',
            'interface_name': 'api',
            'provider_name': 'offline',
            'adapter_name': 'api',
        }
    )

    assert isinstance(response, ApiHealthResponse)
    assert response.app_ready is True
    assert response.project_root == '.'
    assert response.interface_name == 'api'
    assert response.provider_name == 'offline'
    assert response.adapter_name == 'api'


def test_api_health_response_from_health_dict_with_none_provider():
    response = api_health_response_from_dict(
        {
            'app_ready': True,
            'project_root': '.',
            'interface_name': 'hud',
            'provider_name': None,
            'adapter_name': 'hud',
        }
    )

    assert response.provider_name is None
    assert response.adapter_name == 'hud'
