from lucifer_os.interfaces.api_schema import ApiChatResponse, ApiHealthResponse
from lucifer_os.interfaces.hud_client import HudClient


class FakeApiClient:
    def __init__(self):
        self.last_chat = None

    def health(self):
        return ApiHealthResponse(
            app_ready=True,
            project_root='.',
            interface_name='api',
            provider_name=None,
            adapter_name='api',
        )

    def chat(self, text, session_id=None, metadata=None):
        self.last_chat = {
            'text': text,
            'session_id': session_id,
            'metadata': metadata,
        }
        return ApiChatResponse(
            voice_summary='hud kort svar',
            visual_text='hud langt svar',
            visual_channel='api',
            trace_id='trace-hud',
            metadata={'source': 'hud-test'},
        )


def test_hud_client_health_uses_api_client():
    client = HudClient(api_client=FakeApiClient())

    response = client.health()

    assert isinstance(response, ApiHealthResponse)
    assert response.app_ready is True
    assert response.interface_name == 'api'
    assert response.adapter_name == 'api'


def test_hud_client_send_text_uses_api_client():
    fake_api = FakeApiClient()
    client = HudClient(api_client=fake_api)

    response = client.send_text('Hei Lucifer')

    assert isinstance(response, ApiChatResponse)
    assert response.voice_summary == 'hud kort svar'
    assert response.visual_text == 'hud langt svar'
    assert response.trace_id == 'trace-hud'
    assert fake_api.last_chat == {
        'text': 'Hei Lucifer',
        'session_id': None,
        'metadata': None,
    }


def test_hud_client_send_text_passes_session_and_metadata():
    fake_api = FakeApiClient()
    client = HudClient(api_client=fake_api)

    response = client.send_text(
        'Hei Lucifer',
        session_id='hud-session-1',
        metadata={'source': 'hud'},
    )

    assert response.metadata == {'source': 'hud-test'}
    assert fake_api.last_chat == {
        'text': 'Hei Lucifer',
        'session_id': 'hud-session-1',
        'metadata': {'source': 'hud'},
    }


def test_hud_client_can_construct_default_api_client():
    client = HudClient()

    assert client.api_client is not None
