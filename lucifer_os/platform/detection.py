from dataclasses import dataclass
import platform


@dataclass(frozen=True)
class PlatformInfo:
    system: str
    release: str
    machine: str
    python_version: str


def detect_platform() -> PlatformInfo:
    return PlatformInfo(
        system=platform.system().lower(),
        release=platform.release(),
        machine=platform.machine(),
        python_version=platform.python_version(),
    )
