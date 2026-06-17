from lucifer_os.providers.offline import OfflineProvider
from lucifer_os.response.builder import ResponseBuilder
from lucifer_os.response.response import LuciferResponse


def test_response_builder_creates_structured_response():
    builder = ResponseBuilder()

    response = builder.build(
        voice_summary='Kort svar',
        visual_text='Lengre visuelt svar',
        visual_channel='cli',
        requires_confirmation=False,
        risk_level=0,
        action=None,
    )

    assert isinstance(response, LuciferResponse)
    assert response.voice_summary == 'Kort svar'
    assert response.visual_text == 'Lengre visuelt svar'
    assert response.visual_channel == 'cli'
    assert response.requires_confirmation is False
    assert response.risk_level == 0
    assert response.action is None
    assert response.trace_id


def test_response_builder_defaults_visual_text_to_voice_summary():
    builder = ResponseBuilder()

    response = builder.build(voice_summary='Samme tekst')

    assert response.visual_text == 'Samme tekst'


def test_offline_provider_metadata_and_health():
    provider = OfflineProvider()
    metadata = provider.metadata()

    assert metadata.name == 'offline'
    assert metadata.kind == 'local_fallback'
    assert metadata.requires_api_key is False
    assert metadata.supports_streaming is False
    assert metadata.supports_tools is False
    assert provider.health() is True


def test_offline_provider_returns_structured_response():
    provider = OfflineProvider()

    response = provider.answer('Hei Lucifer')

    assert isinstance(response, LuciferResponse)
    assert response.voice_summary
    assert response.visual_text
    assert response.visual_channel == 'cli'
    assert response.requires_confirmation is False
    assert response.risk_level == 0
    assert response.action is None
    assert response.trace_id
