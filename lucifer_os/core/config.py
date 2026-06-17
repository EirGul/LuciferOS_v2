from dataclasses import dataclass
import json
from pathlib import Path


@dataclass(frozen=True)
class LuciferConfig:
    project_name: str
    default_provider: str
    ollama_model: str
    performance_mode: str
    audit_enabled: bool


class ConfigLoader:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root).resolve()

    def load(self) -> LuciferConfig:
        config_path = self.project_root / 'config' / 'lucifer.json'

        defaults = {
            'project_name': 'LuciferOS v2',
            'default_provider': 'offline',
            'ollama_model': 'qwen3.5:9b',
            'performance_mode': 'instant',
            'audit_enabled': True,
        }

        if config_path.exists():
            with config_path.open('r', encoding='utf-8') as config_file:
                loaded = json.load(config_file)
            defaults.update(loaded)

        return LuciferConfig(
            project_name=str(defaults['project_name']),
            default_provider=str(defaults['default_provider']),
            ollama_model=str(defaults['ollama_model']),
            performance_mode=str(defaults['performance_mode']),
            audit_enabled=bool(defaults['audit_enabled']),
        )
