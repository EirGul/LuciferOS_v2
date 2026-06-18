from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from lucifer_os.core.core import CoreResult


@dataclass(frozen=True)
class InterfaceInput:
    text: str
    interface: str
    session_id: str | None = None
    metadata: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class InterfaceOutput:
    voice_summary: str
    visual_text: str
    visual_channel: str
    trace_id: str
    metadata: dict[str, str] = field(default_factory=dict)


class InterfaceAdapter(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def handle_input(self, input_data: InterfaceInput) -> InterfaceOutput:
        raise NotImplementedError


def output_from_core_result(result: CoreResult) -> InterfaceOutput:
    return InterfaceOutput(
        voice_summary=result.response.voice_summary,
        visual_text=result.response.visual_text,
        visual_channel=result.response.visual_channel,
        trace_id=result.trace_id,
        metadata=dict(result.response.metadata),
    )
