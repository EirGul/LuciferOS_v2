from lucifer_os.providers.base import Provider
from lucifer_os.registries.provider_registry import ProviderMetadata
from lucifer_os.response.builder import ResponseBuilder
from lucifer_os.response.response import LuciferResponse


class OfflineProvider(Provider):
    def __init__(self):
        self.response_builder = ResponseBuilder()

    def metadata(self) -> ProviderMetadata:
        return ProviderMetadata(
            name='offline',
            kind='local_fallback',
            requires_api_key=False,
            supports_streaming=False,
            supports_tools=False,
        )

    def health(self) -> bool:
        return True

    def answer(self, prompt: str) -> LuciferResponse:
        cleaned_prompt = prompt.strip()

        if not cleaned_prompt:
            message = 'Jeg er online i offline-modus, men jeg fikk ingen tekst å svare på.'
        else:
            message = 'Jeg er online i offline-modus. Core fungerer, men ingen AI-provider er aktiv ennå.'

        return self.response_builder.build(
            voice_summary=message,
            visual_text=message,
            visual_channel='cli',
            requires_confirmation=False,
            risk_level=0,
            action=None,
        )
