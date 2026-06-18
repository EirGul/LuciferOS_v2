import pytest

from lucifer_os.core.config import ConfigLoader
from lucifer_os.providers.factory import create_provider
from lucifer_os.providers.offline import OfflineProvider
from lucifer_os.providers.ollama import OllamaProvider


def test_provider_factory_creates_offline_provider():
    config = ConfigLoader(project_root='.').load()

    provider = create_provider('offline', config)

    assert isinstance(provider, OfflineProvider)
    assert provider.metadata().name == 'offline'


def test_provider_factory_creates_ollama_provider_with_config_model():
    config = ConfigLoader(project_root='.').load()

    provider = create_provider('ollama', config)

    assert isinstance(provider, OllamaProvider)
    assert provider.metadata().name == 'ollama'
    assert provider.config.model == 'eirik-qwen3:latest'


def test_provider_factory_normalizes_provider_name():
    config = ConfigLoader(project_root='.').load()

    provider = create_provider('  OFFLINE  ', config)

    assert isinstance(provider, OfflineProvider)


def test_provider_factory_rejects_unknown_provider():
    config = ConfigLoader(project_root='.').load()

    with pytest.raises(ValueError, match='Ukjent provider: unknown'):
        create_provider('unknown', config)
