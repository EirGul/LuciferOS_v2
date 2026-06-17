from dataclasses import dataclass

from lucifer_os.core.config import LuciferConfig
from lucifer_os.platform.detection import PlatformInfo
from lucifer_os.providers.base import Provider


@dataclass(frozen=True)
class DiagnosticsStatus:
    project_name: str
    platform_system: str
    platform_release: str
    python_version: str
    active_provider: str
    provider_health: bool
    default_provider: str
    ollama_model: str
    performance_mode: str
    audit_enabled: bool


class DiagnosticsService:
    def __init__(
        self,
        config: LuciferConfig,
        platform: PlatformInfo,
        active_provider: Provider,
    ):
        self.config = config
        self.platform = platform
        self.active_provider = active_provider

    def status(self) -> DiagnosticsStatus:
        return DiagnosticsStatus(
            project_name=self.config.project_name,
            platform_system=self.platform.system,
            platform_release=self.platform.release,
            python_version=self.platform.python_version,
            active_provider=self.active_provider.metadata().name,
            provider_health=self.active_provider.health(),
            default_provider=self.config.default_provider,
            ollama_model=self.config.ollama_model,
            performance_mode=self.config.performance_mode,
            audit_enabled=self.config.audit_enabled,
        )
