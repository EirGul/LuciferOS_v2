from lucifer_os.interfaces.api_client import LuciferApiClient
from lucifer_os.interfaces.api_schema import ApiChatResponse, ApiHealthResponse


class HudClient:
    def __init__(
        self,
        api_client: LuciferApiClient | None = None,
    ):
        self.api_client = api_client or LuciferApiClient()

    def health(self) -> ApiHealthResponse:
        return self.api_client.health()

    def send_text(
        self,
        text: str,
        session_id: str | None = None,
        metadata: dict[str, str] | None = None,
    ) -> ApiChatResponse:
        return self.api_client.chat(
            text,
            session_id=session_id,
            metadata=metadata,
        )
