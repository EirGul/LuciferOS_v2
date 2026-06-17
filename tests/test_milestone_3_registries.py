import pytest

from lucifer_os.registries.provider_registry import ProviderMetadata, ProviderRegistry
from lucifer_os.registries.tool_registry import ToolMetadata, ToolRegistry
from lucifer_os.registries.adapter_registry import AdapterMetadata, AdapterRegistry


def test_provider_registry_registers_metadata():
    registry = ProviderRegistry()
    metadata = ProviderMetadata(
        name='offline',
        kind='local',
        requires_api_key=False,
        supports_streaming=False,
        supports_tools=False,
    )

    registry.register(metadata)

    assert registry.has('offline') is True
    assert registry.get('offline') == metadata
    assert registry.list() == [metadata]


def test_provider_registry_rejects_duplicate_names():
    registry = ProviderRegistry()
    metadata = ProviderMetadata(
        name='offline',
        kind='local',
        requires_api_key=False,
        supports_streaming=False,
        supports_tools=False,
    )

    registry.register(metadata)

    with pytest.raises(ValueError):
        registry.register(metadata)


def test_tool_registry_registers_metadata():
    registry = ToolRegistry()
    metadata = ToolMetadata(
        name='git.status',
        capability='development',
        risk_level=1,
        requires_confirmation=False,
        supports_dry_run=True,
        platform_support=('windows', 'linux', 'darwin'),
    )

    registry.register(metadata)

    assert registry.has('git.status') is True
    assert registry.get('git.status') == metadata
    assert registry.list() == [metadata]


def test_adapter_registry_registers_metadata():
    registry = AdapterRegistry()
    metadata = AdapterMetadata(
        name='windows-default',
        platform='windows',
        capabilities=('app.open', 'file.open'),
    )

    registry.register(metadata)

    assert registry.has('windows-default') is True
    assert registry.get('windows-default') == metadata
    assert registry.list() == [metadata]
