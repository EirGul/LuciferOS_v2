from lucifer_os.core.core import CoreRequest, LuciferCore
from lucifer_os.providers.base import Provider
from lucifer_os.registries.provider_registry import ProviderMetadata
from lucifer_os.response.builder import ResponseBuilder
from lucifer_os.response.response import LuciferResponse


class FakeProvider(Provider):
    def __init__(self, message: str):
        self.message = message
        self.response_builder = ResponseBuilder()

    def metadata(self) -> ProviderMetadata:
        return ProviderMetadata(
            name='fake',
            kind='test_provider',
            requires_api_key=False,
            supports_streaming=False,
            supports_tools=False,
        )

    def health(self) -> bool:
        return True

    def answer(self, prompt: str) -> LuciferResponse:
        return self.response_builder.build(
            voice_summary=self.message,
            visual_text=self.message,
            visual_channel='cli',
            requires_confirmation=False,
            risk_level=0,
            action=None,
        )


class FailingProvider(FakeProvider):
    def metadata(self) -> ProviderMetadata:
        return ProviderMetadata(
            name='ollama',
            kind='local_model',
            requires_api_key=False,
            supports_streaming=False,
            supports_tools=False,
        )

    def answer(self, prompt: str) -> LuciferResponse:
        return self.response_builder.build(
            voice_summary='OllamaProvider feilet trygt: offline',
            visual_text='OllamaProvider feilet trygt: offline',
            visual_channel='cli',
            requires_confirmation=False,
            risk_level=0,
            action=None,
        )


def test_core_uses_injected_primary_provider_for_conversation():
    core = LuciferCore(primary_provider=FakeProvider('Svar fra primary provider.'))

    result = core.handle(CoreRequest(text='Hei Lucifer'))

    assert result.response.voice_summary == 'Svar fra primary provider.'
    assert result.response.trace_id == result.trace_id
    assert any(
        event.event_type == 'provider_selected' and event.metadata['provider'] == 'fake'
        for event in result.audit_events
    )


def test_core_falls_back_to_offline_provider_when_primary_provider_fails_safely():
    core = LuciferCore(primary_provider=FailingProvider('unused'))

    result = core.handle(CoreRequest(text='Hei Lucifer'))

    assert result.response.voice_summary == 'Jeg er online i offline-modus. Core fungerer, men ingen AI-provider er aktiv ennå.'
    assert result.response.trace_id == result.trace_id
    assert any(event.event_type == 'provider_fallback' for event in result.audit_events)


def test_core_default_provider_is_offline_provider():
    core = LuciferCore()

    result = core.handle(CoreRequest(text='Hei Lucifer'))

    assert result.response.voice_summary == 'Jeg er online i offline-modus. Core fungerer, men ingen AI-provider er aktiv ennå.'
    assert any(
        event.event_type == 'provider_selected' and event.metadata['provider'] == 'offline'
        for event in result.audit_events
    )
