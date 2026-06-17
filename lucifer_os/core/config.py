from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class LuciferConfig:
    project_name: str
    default_provider: str
    performance_mode: str
    audit_enabled: bool


class ConfigLoader:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root).resolve()

    def load(self) -> LuciferConfig:
        return LuciferConfig(
            project_name='LuciferOS v2',
            default_provider='offline',
            performance_mode='instant',
            audit_enabled=True,
        )
