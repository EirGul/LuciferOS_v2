from dataclasses import dataclass


@dataclass(frozen=True)
class ProviderMetadata:
    name: str
    kind: str
    requires_api_key: bool
    supports_streaming: bool
    supports_tools: bool


class ProviderRegistry:
    def __init__(self):
        self._providers: dict[str, ProviderMetadata] = {}

    def register(self, metadata: ProviderMetadata) -> None:
        if metadata.name in self._providers:
            raise ValueError(f'Provider already registered: {metadata.name}')

        self._providers[metadata.name] = metadata

    def get(self, name: str) -> ProviderMetadata:
        return self._providers[name]

    def list(self) -> list[ProviderMetadata]:
        return list(self._providers.values())

    def has(self, name: str) -> bool:
        return name in self._providers
