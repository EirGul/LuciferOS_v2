import json

from lucifer_os.core.config import ConfigLoader


def test_config_loader_reads_project_config_file():
    config = ConfigLoader(project_root='.').load()

    assert config.project_name == 'LuciferOS v2'
    assert config.default_provider == 'offline'
    assert config.ollama_model == 'eirik-qwen3:latest'
    assert config.performance_mode == 'instant'
    assert config.audit_enabled is True


def test_config_loader_falls_back_to_defaults_when_file_is_missing(tmp_path):
    config = ConfigLoader(project_root=str(tmp_path)).load()

    assert config.project_name == 'LuciferOS v2'
    assert config.default_provider == 'offline'
    assert config.ollama_model == 'eirik-qwen3:latest'
    assert config.performance_mode == 'instant'
    assert config.audit_enabled is True


def test_config_loader_allows_config_file_overrides(tmp_path):
    config_dir = tmp_path / 'config'
    config_dir.mkdir()
    config_path = config_dir / 'lucifer.json'
    config_path.write_text(
        json.dumps(
            {
                'project_name': 'Test Lucifer',
                'default_provider': 'ollama',
                'ollama_model': 'qwen3.5:4b',
                'performance_mode': 'local_fast',
                'audit_enabled': False,
            }
        ),
        encoding='utf-8',
    )

    config = ConfigLoader(project_root=str(tmp_path)).load()

    assert config.project_name == 'Test Lucifer'
    assert config.default_provider == 'ollama'
    assert config.ollama_model == 'qwen3.5:4b'
    assert config.performance_mode == 'local_fast'
    assert config.audit_enabled is False
