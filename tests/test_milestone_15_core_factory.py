import pytest

from lucifer_os.core.core import LuciferCore
from lucifer_os.core.factory import create_core


def test_core_factory_creates_core_with_config_default_provider():
    core = create_core(project_root='.')

    assert isinstance(core, LuciferCore)
    assert core.primary_provider.metadata().name == 'offline'


def test_core_factory_creates_core_with_explicit_offline_provider():
    core = create_core(project_root='.', provider_name='offline')

    assert isinstance(core, LuciferCore)
    assert core.primary_provider.metadata().name == 'offline'


def test_core_factory_creates_core_with_explicit_ollama_provider():
    core = create_core(project_root='.', provider_name='ollama')

    assert isinstance(core, LuciferCore)
    assert core.primary_provider.metadata().name == 'ollama'
    assert core.primary_provider.config.model == 'qwen3.5:9b'


def test_core_factory_rejects_unknown_provider():
    with pytest.raises(ValueError, match='Ukjent provider: unknown'):
        create_core(project_root='.', provider_name='unknown')
