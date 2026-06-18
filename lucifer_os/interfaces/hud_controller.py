from lucifer_os.interfaces.hud_client import HudClient
from lucifer_os.interfaces.hud_models import (
    HudChatView,
    HudHealthView,
    hud_chat_view_from_api,
    hud_health_view_from_api,
)


class HudController:
    def __init__(
        self,
        client: HudClient | None = None,
    ):
        self.client = client or HudClient()

    def health_view(self) -> HudHealthView:
        response = self.client.health()
        return hud_health_view_from_api(response)

    def send_text_view(
        self,
        text: str,
        session_id: str | None = None,
        metadata: dict[str, str] | None = None,
    ) -> HudChatView:
        response = self.client.send_text(
            text,
            session_id=session_id,
            metadata=metadata,
        )
        return hud_chat_view_from_api(response)
