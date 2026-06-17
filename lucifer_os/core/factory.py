from lucifer_os.core.config import ConfigLoader
from lucifer_os.core.core import LuciferCore
from lucifer_os.providers.factory import create_provider


def create_core(project_root: str = '.', provider_name: str | None = None) -> LuciferCore:
    config = ConfigLoader(project_root=project_root).load()
    resolved_provider_name = provider_name or config.default_provider
    provider = create_provider(resolved_provider_name, config)

    return LuciferCore(primary_provider=provider, project_root=project_root)
