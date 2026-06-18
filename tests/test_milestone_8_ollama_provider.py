from unittest.mock import MagicMock, patch

from lucifer_os.providers.ollama import OllamaConfig, OllamaProvider
from lucifer_os.response.response import LuciferResponse


def test_ollama_provider_metadata():
    provider = OllamaProvider()
    metadata = provider.metadata()

    assert metadata.name == 'ollama'
    assert metadata.kind == 'local_model'
    assert metadata.requires_api_key is False
    assert metadata.supports_streaming is False
    assert metadata.supports_tools is False


def test_ollama_provider_default_config():
    provider = OllamaProvider()

    assert provider.config.base_url == 'http://127.0.0.1:11434'
    assert provider.config.model == 'eirik-qwen3:latest'
    assert provider.config.timeout_seconds == 120


def test_ollama_provider_accepts_custom_config():
    config = OllamaConfig(
        base_url='http://localhost:11434',
        model='llama3.2',
        timeout_seconds=10,
    )

    provider = OllamaProvider(config=config)

    assert provider.config == config


def test_ollama_provider_answer_returns_empty_prompt_response():
    provider = OllamaProvider()

    response = provider.answer('   ')

    assert isinstance(response, LuciferResponse)
    assert response.voice_summary == 'Jeg fikk ingen tekst å sende til Ollama.'
    assert response.visual_channel == 'cli'
    assert response.requires_confirmation is False
    assert response.risk_level == 0


def test_ollama_provider_health_returns_true_when_tags_endpoint_responds_200():
    provider = OllamaProvider()
    mock_response = MagicMock()
    mock_response.status = 200
    mock_response.__enter__.return_value = mock_response
    mock_response.__exit__.return_value = None

    with patch('lucifer_os.providers.ollama.urlopen', return_value=mock_response):
        assert provider.health() is True


def test_ollama_provider_health_returns_false_when_tags_endpoint_fails():
    provider = OllamaProvider()

    with patch('lucifer_os.providers.ollama.urlopen', side_effect=OSError('offline')):
        assert provider.health() is False


def test_ollama_provider_answer_returns_chat_response():
    provider = OllamaProvider()
    mock_response = MagicMock()
    mock_response.read.return_value = b'{"message": {"content": "Hei, jeg svarer lokalt."}}'
    mock_response.__enter__.return_value = mock_response
    mock_response.__exit__.return_value = None

    with patch('lucifer_os.providers.ollama.urlopen', return_value=mock_response):
        response = provider.answer('Hei Lucifer')

    assert isinstance(response, LuciferResponse)
    assert response.voice_summary == 'Hei, jeg svarer lokalt.'
    assert response.visual_text == 'Hei, jeg svarer lokalt.'
    assert response.visual_channel == 'cli'
    assert response.requires_confirmation is False
    assert response.risk_level == 0
    assert response.action is None
    assert response.trace_id


def test_ollama_provider_answer_fails_safely_when_chat_fails():
    provider = OllamaProvider()

    with patch('lucifer_os.providers.ollama.urlopen', side_effect=OSError('offline')):
        response = provider.answer('Hei Lucifer')

    assert isinstance(response, LuciferResponse)
    assert response.voice_summary.startswith('OllamaProvider feilet trygt:')
    assert response.requires_confirmation is False
    assert response.risk_level == 0
