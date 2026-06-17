from dataclasses import dataclass


@dataclass(frozen=True)
class ToolMetadata:
    name: str
    capability: str
    risk_level: int
    requires_confirmation: bool
    supports_dry_run: bool
    platform_support: tuple[str, ...]


class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, ToolMetadata] = {}

    def register(self, metadata: ToolMetadata) -> None:
        if metadata.name in self._tools:
            raise ValueError(f'Tool already registered: {metadata.name}')

        self._tools[metadata.name] = metadata

    def get(self, name: str) -> ToolMetadata:
        return self._tools[name]

    def list(self) -> list[ToolMetadata]:
        return list(self._tools.values())

    def has(self, name: str) -> bool:
        return name in self._tools
