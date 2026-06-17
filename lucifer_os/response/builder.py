from uuid import uuid4

from lucifer_os.response.response import LuciferResponse


class ResponseBuilder:
    def build(
        self,
        voice_summary: str,
        visual_text: str | None = None,
        visual_channel: str = 'cli',
        requires_confirmation: bool = False,
        risk_level: int = 0,
        action: str | None = None,
    ) -> LuciferResponse:
        return LuciferResponse(
            voice_summary=voice_summary,
            visual_text=visual_text or voice_summary,
            visual_channel=visual_channel,
            requires_confirmation=requires_confirmation,
            risk_level=risk_level,
            action=action,
            trace_id=str(uuid4()),
        )
