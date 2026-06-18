from lucifer_os.core.config import ConfigLoader
from lucifer_os.core.diagnostics import DiagnosticsService, DiagnosticsStatus
from lucifer_os.platform.detection import detect_platform
from lucifer_os.providers.offline import OfflineProvider


def test_diagnostics_status_reports_core_runtime_state():
    config = ConfigLoader(project_root='.').load()
    platform = detect_platform()
    provider = OfflineProvider()
    diagnostics = DiagnosticsService(
        config=config,
        platform=platform,
        active_provider=provider,
    )

    status = diagnostics.status()

    assert isinstance(status, DiagnosticsStatus)
    assert status.project_name == 'LuciferOS v2'
    assert status.platform_system in {'windows', 'linux', 'darwin'}
    assert status.platform_release
    assert status.python_version
    assert status.active_provider == 'offline'
    assert status.provider_health is True
    assert status.default_provider == 'offline'
    assert status.ollama_model == 'eirik-qwen3:latest'
    assert status.performance_mode == 'instant'
    assert status.audit_enabled is True


class UnhealthyProvider(OfflineProvider):
    def health(self) -> bool:
        return False


def test_diagnostics_status_reports_provider_health_false():
    config = ConfigLoader(project_root='.').load()
    platform = detect_platform()
    provider = UnhealthyProvider()
    diagnostics = DiagnosticsService(
        config=config,
        platform=platform,
        active_provider=provider,
    )

    status = diagnostics.status()

    assert status.active_provider == 'offline'
    assert status.provider_health is False
    assert status.ollama_model == 'eirik-qwen3:latest'
