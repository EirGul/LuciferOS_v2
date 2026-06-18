from lucifer_os.interfaces.api_schema import ApiChatResponse, ApiHealthResponse
from lucifer_os.interfaces.hud_models import (
    HudChatView,
    HudHealthView,
    hud_chat_view_from_api,
    hud_health_view_from_api,
)


def test_hud_health_view_from_online_api_response():
    response = ApiHealthResponse(
        app_ready=True,
        project_root='.',
        interface_name='api',
        provider_name='offline',
        adapter_name='api',
    )

    view = hud_health_view_from_api(response)

    assert isinstance(view, HudHealthView)
    assert view.online is True
    assert view.status_text == 'LuciferOS API online'
    assert view.provider_name == 'offline'
    assert view.adapter_name == 'api'


def test_hud_health_view_from_offline_api_response():
    response = ApiHealthResponse(
        app_ready=False,
        project_root='.',
        interface_name='api',
        provider_name=None,
        adapter_name='api',
    )

    view = hud_health_view_from_api(response)

    assert view.online is False
    assert view.status_text == 'LuciferOS API offline'
    assert view.provider_name is None


def test_hud_chat_view_from_api_response():
    response = ApiChatResponse(
        voice_summary='kort svar',
        visual_text='langt svar',
        visual_channel='api',
        trace_id='trace-hud',
        metadata={'source': 'hud'},
    )

    view = hud_chat_view_from_api(response)

    assert isinstance(view, HudChatView)
    assert view.voice_summary == 'kort svar'
    assert view.visual_text == 'langt svar'
    assert view.trace_id == 'trace-hud'
    assert view.metadata == {'source': 'hud'}
