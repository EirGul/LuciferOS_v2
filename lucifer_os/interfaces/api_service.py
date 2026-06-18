from lucifer_os.interfaces.api_schema import (
    ApiChatRequest,
    ApiChatResponse,
    ApiHealthResponse,
    api_chat_response_from_output,
    api_health_response_from_dict,
)
from lucifer_os.runtime.app import LuciferApp


class ApiService:
    def __init__(
        self,
        project_root: str = '.',
        provider_name: str | None = None,
    ):
        self.app = LuciferApp(
            project_root=project_root,
            interface_name='api',
            provider_name=provider_name,
        )

    def chat(self, request: ApiChatRequest) -> ApiChatResponse:
        output = self.app.handle_text(
            request.text,
            session_id=request.session_id,
            metadata=request.metadata,
        )

        return api_chat_response_from_output(output)

    def health(self) -> ApiHealthResponse:
        return api_health_response_from_dict(self.app.health())
