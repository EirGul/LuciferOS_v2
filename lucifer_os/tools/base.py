from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from lucifer_os.registries.tool_registry import ToolMetadata


@dataclass(frozen=True)
class ToolRequest:
    name: str
    arguments: dict[str, str] = field(default_factory=dict)
    dry_run: bool = True


@dataclass(frozen=True)
class ToolResult:
    success: bool
    message: str
    data: dict[str, str] = field(default_factory=dict)
    dry_run: bool = True


class Tool(ABC):
    @abstractmethod
    def metadata(self) -> ToolMetadata:
        raise NotImplementedError

    @abstractmethod
    def run(self, request: ToolRequest) -> ToolResult:
        raise NotImplementedError
