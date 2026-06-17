from lucifer_os.core.runtime import LuciferRuntime


def test_runtime_status_contains_config_and_platform():
    runtime = LuciferRuntime(project_root='.')

    status = runtime.status()

    assert status.config.project_name == 'LuciferOS v2'
    assert status.config.default_provider == 'offline'
    assert status.config.performance_mode == 'instant'
    assert status.config.audit_enabled is True
    assert status.platform.system in {'windows', 'linux', 'darwin'}
    assert status.platform.python_version
