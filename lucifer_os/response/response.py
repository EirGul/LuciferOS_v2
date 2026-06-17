from dataclasses import dataclass, field


@dataclass(frozen=True)
class LuciferResponse:
    voice_summary: str
    visual_text: str
    visual_channel: str
    requires_confirmation: bool
    risk_level: int
    action: str | None
    trace_id: str
    metadata: dict[str, str] = field(default_factory=dict)
