from dataclasses import dataclass, field

from lucifer_os.interfaces.base import InterfaceOutput


@dataclass(frozen=True)
class ApiChatRequest:
    text: str
    session_id: str | None = None
    metadata: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class ApiChatResponse:
    voice_summary: str
    visual_text: str
    visual_channel: str
    trace_id: str
    metadata: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class ApiHealthResponse:
    app_ready: bool
    project_root: str
    interface_name: str
    provider_name: str | None
    adapter_name: str


def api_chat_response_from_output(output: InterfaceOutput) -> ApiChatResponse:
    return ApiChatResponse(
        voice_summary=output.voice_summary,
        visual_text=output.visual_text,
        visual_channel=output.visual_channel,
        trace_id=output.trace_id,
        metadata=dict(output.metadata),
    )


def api_health_response_from_dict(health: dict[str, str | bool | None]) -> ApiHealthResponse:
    return ApiHealthResponse(
        app_ready=bool(health['app_ready']),
        project_root=str(health['project_root']),
        interface_name=str(health['interface_name']),
        provider_name=None if health['provider_name'] is None else str(health['provider_name']),
        adapter_name=str(health['adapter_name']),
    )
