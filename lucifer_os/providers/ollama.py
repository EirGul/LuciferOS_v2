from dataclasses import dataclass
import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from lucifer_os.providers.base import Provider
from lucifer_os.registries.provider_registry import ProviderMetadata
from lucifer_os.response.builder import ResponseBuilder
from lucifer_os.response.response import LuciferResponse


@dataclass(frozen=True)
class OllamaConfig:
    base_url: str = 'http://127.0.0.1:11434'
    model: str = 'qwen3.5:9b'
    timeout_seconds: int = 120


class OllamaProvider(Provider):
    def __init__(self, config: OllamaConfig | None = None):
        self.config = config or OllamaConfig()
        self.response_builder = ResponseBuilder()

    def metadata(self) -> ProviderMetadata:
        return ProviderMetadata(
            name='ollama',
            kind='local_model',
            requires_api_key=False,
            supports_streaming=False,
            supports_tools=False,
        )

    def health(self) -> bool:
        try:
            request = Request(f'{self.config.base_url}/api/tags', method='GET')
            with urlopen(request, timeout=self.config.timeout_seconds) as response:
                return response.status == 200
        except (HTTPError, URLError, TimeoutError, OSError):
            return False

    def answer(self, prompt: str) -> LuciferResponse:
        cleaned_prompt = prompt.strip()

        if not cleaned_prompt:
            return self.response_builder.build(
                voice_summary='Jeg fikk ingen tekst å sende til Ollama.',
                visual_text='Jeg fikk ingen tekst å sende til Ollama.',
                visual_channel='cli',
                requires_confirmation=False,
                risk_level=0,
                action=None,
            )

        payload = {
            'model': self.config.model,
            'messages': [
                {
                    'role': 'system',
                    'content': (
                        'Du er LuciferOS, en lokal-first personlig AI-assistent under utvikling. '
                        'Når brukeren spør om Core, mener de LuciferOS Core i dette prosjektet, ikke Microsoft eller andre produkter. '
                        'Svar kort, tydelig og direkte på norsk. '
                        'Ikke vis resonnement. Ikke forklar hva Ollama CLI er med mindre brukeren spør spesifikt om Ollama CLI. '
                        'Hvis brukeren spør om du fungerer, svar som LuciferOS-runtime, ikke som en generell chatbot.'
                    ),
                },
                {
                    'role': 'user',
                    'content': cleaned_prompt,
                },
            ],
            'stream': False,
            'think': False,
            'options': {'num_predict': 256},
        }

        try:
            request = Request(
                f'{self.config.base_url}/api/chat',
                data=json.dumps(payload).encode('utf-8'),
                headers={'Content-Type': 'application/json'},
                method='POST',
            )
            with urlopen(request, timeout=self.config.timeout_seconds) as response:
                body = response.read().decode('utf-8')
                data = json.loads(body)
                message = data.get('message', {})
                answer_text = str(message.get('content', '')).strip()

            if not answer_text:
                answer_text = 'Ollama svarte, men responsen var tom.'

            return self.response_builder.build(
                voice_summary=answer_text,
                visual_text=answer_text,
                visual_channel='cli',
                requires_confirmation=False,
                risk_level=0,
                action=None,
            )
        except (HTTPError, URLError, TimeoutError, OSError, json.JSONDecodeError) as error:
            message = f'OllamaProvider feilet trygt: {error}'
            return self.response_builder.build(
                voice_summary=message,
                visual_text=message,
                visual_channel='cli',
                requires_confirmation=False,
                risk_level=0,
                action=None,
                metadata={'provider_error': 'true', 'provider': 'ollama'},
            )
