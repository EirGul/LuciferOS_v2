from dataclasses import dataclass, field

from lucifer_os.interfaces.api_schema import ApiChatResponse, ApiHealthResponse


@dataclass(frozen=True)
class HudHealthView:
    online: bool
    status_text: str
    provider_name: str | None
    adapter_name: str


@dataclass(frozen=True)
class HudChatView:
    voice_summary: str
    visual_text: str
    trace_id: str
    metadata: dict[str, str] = field(default_factory=dict)


def hud_health_view_from_api(response: ApiHealthResponse) -> HudHealthView:
    status_text = 'LuciferOS API online' if response.app_ready else 'LuciferOS API offline'

    return HudHealthView(
        online=response.app_ready,
        status_text=status_text,
        provider_name=response.provider_name,
        adapter_name=response.adapter_name,
    )


def hud_chat_view_from_api(response: ApiChatResponse) -> HudChatView:
    return HudChatView(
        voice_summary=response.voice_summary,
        visual_text=response.visual_text,
        trace_id=response.trace_id,
        metadata=dict(response.metadata),
    )
