from dataclasses import dataclass

from lucifer_os.core.config import ConfigLoader, LuciferConfig
from lucifer_os.platform.detection import PlatformInfo, detect_platform


@dataclass(frozen=True)
class RuntimeStatus:
    config: LuciferConfig
    platform: PlatformInfo


class LuciferRuntime:
    def __init__(self, project_root: str):
        self.project_root = project_root
        self.config_loader = ConfigLoader(project_root)

    def status(self) -> RuntimeStatus:
        return RuntimeStatus(
            config=self.config_loader.load(),
            platform=detect_platform(),
        )
