from dataclasses import dataclass


@dataclass(frozen=True)
class AdapterMetadata:
    name: str
    platform: str
    capabilities: tuple[str, ...]


class AdapterRegistry:
    def __init__(self):
        self._adapters: dict[str, AdapterMetadata] = {}

    def register(self, metadata: AdapterMetadata) -> None:
        if metadata.name in self._adapters:
            raise ValueError(f'Adapter already registered: {metadata.name}')

        self._adapters[metadata.name] = metadata

    def get(self, name: str) -> AdapterMetadata:
        return self._adapters[name]

    def list(self) -> list[AdapterMetadata]:
        return list(self._adapters.values())

    def has(self, name: str) -> bool:
        return name in self._adapters
