from lucifer_os.interfaces.api_schema import ApiChatResponse, ApiHealthResponse
from lucifer_os.interfaces.hud_controller import HudController
from lucifer_os.interfaces.hud_models import HudChatView, HudHealthView


class FakeHudClient:
    def __init__(self):
        self.last_text = None
        self.last_session_id = None
        self.last_metadata = None

    def health(self):
        return ApiHealthResponse(
            app_ready=True,
            project_root='.',
            interface_name='api',
            provider_name='offline',
            adapter_name='api',
        )

    def send_text(self, text, session_id=None, metadata=None):
        self.last_text = text
        self.last_session_id = session_id
        self.last_metadata = metadata
        return ApiChatResponse(
            voice_summary='hud kort svar',
            visual_text='hud langt svar',
            visual_channel='api',
            trace_id='trace-controller',
            metadata={'source': 'controller-test'},
        )


def test_hud_controller_health_view_returns_hud_health_view():
    controller = HudController(client=FakeHudClient())

    view = controller.health_view()

    assert isinstance(view, HudHealthView)
    assert view.online is True
    assert view.status_text == 'LuciferOS API online'
    assert view.provider_name == 'offline'
    assert view.adapter_name == 'api'


def test_hud_controller_send_text_view_returns_hud_chat_view():
    fake_client = FakeHudClient()
    controller = HudController(client=fake_client)

    view = controller.send_text_view('Hei Lucifer')

    assert isinstance(view, HudChatView)
    assert view.voice_summary == 'hud kort svar'
    assert view.visual_text == 'hud langt svar'
    assert view.trace_id == 'trace-controller'
    assert view.metadata == {'source': 'controller-test'}
    assert fake_client.last_text == 'Hei Lucifer'
    assert fake_client.last_session_id is None
    assert fake_client.last_metadata is None


def test_hud_controller_send_text_view_passes_session_and_metadata():
    fake_client = FakeHudClient()
    controller = HudController(client=fake_client)

    view = controller.send_text_view(
        'Hei Lucifer',
        session_id='hud-session-1',
        metadata={'source': 'hud'},
    )

    assert view.trace_id == 'trace-controller'
    assert fake_client.last_text == 'Hei Lucifer'
    assert fake_client.last_session_id == 'hud-session-1'
    assert fake_client.last_metadata == {'source': 'hud'}


def test_hud_controller_can_construct_default_client():
    controller = HudController()

    assert controller.client is not None
