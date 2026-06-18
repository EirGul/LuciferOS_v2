from unittest.mock import patch

from lucifer_os.interfaces.api_schema import ApiChatRequest, ApiChatResponse, ApiHealthResponse
from lucifer_os.interfaces.api_service import ApiService
from lucifer_os.providers.offline import OfflineProvider


def test_api_service_chat_returns_api_chat_response():
    service = ApiService()

    response = service.chat(ApiChatRequest(text='Hei Lucifer'))

    assert isinstance(response, ApiChatResponse)
    assert response.visual_channel == 'api'
    assert response.trace_id
    assert 'offline-modus' in response.voice_summary


def test_api_service_chat_passes_session_and_metadata():
    service = ApiService()

    response = service.chat(
        ApiChatRequest(
            text='Hei Lucifer',
            session_id='session-1',
            metadata={'source': 'api-test'},
        )
    )

    assert response.visual_channel == 'api'
    assert response.trace_id


def test_api_service_health_returns_api_health_response():
    service = ApiService()

    response = service.health()

    assert isinstance(response, ApiHealthResponse)
    assert response.app_ready is True
    assert response.interface_name == 'api'
    assert response.adapter_name == 'api'


def test_api_service_accepts_provider_name():
    with patch('lucifer_os.providers.factory.OllamaProvider', return_value=OfflineProvider()):
        service = ApiService(provider_name='ollama')

    response = service.chat(ApiChatRequest(text='Hei Lucifer'))

    assert response.visual_channel == 'api'
    assert 'offline-modus' in response.voice_summary


def test_api_service_health_reports_provider_name_when_given():
    service = ApiService(provider_name='offline')

    response = service.health()

    assert response.provider_name == 'offline'
    assert response.interface_name == 'api'
