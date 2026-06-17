from lucifer_os.core.config import LuciferConfig
from lucifer_os.providers.base import Provider
from lucifer_os.providers.offline import OfflineProvider
from lucifer_os.providers.ollama import OllamaConfig, OllamaProvider


def create_provider(name: str, config: LuciferConfig) -> Provider:
    provider_name = name.strip().lower()

    if provider_name == 'offline':
        return OfflineProvider()

    if provider_name == 'ollama':
        ollama_config = OllamaConfig(model=config.ollama_model)
        return OllamaProvider(config=ollama_config)

    raise ValueError(f'Ukjent provider: {name}')
