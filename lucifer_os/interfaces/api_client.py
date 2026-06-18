import json
from typing import Any
from urllib import request as urllib_request
from urllib.error import URLError

from lucifer_os.interfaces.api_schema import ApiChatResponse, ApiHealthResponse


class LuciferApiClient:
    def __init__(
        self,
        base_url: str = 'http://127.0.0.1:8787',
        timeout: float = 5.0,
    ):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout

    def health(self) -> ApiHealthResponse:
        data = self._request_json('GET', '/health')

        return ApiHealthResponse(
            app_ready=bool(data['app_ready']),
            project_root=str(data['project_root']),
            interface_name=str(data['interface_name']),
            provider_name=None if data['provider_name'] is None else str(data['provider_name']),
            adapter_name=str(data['adapter_name']),
        )

    def chat(
        self,
        text: str,
        session_id: str | None = None,
        metadata: dict[str, str] | None = None,
    ) -> ApiChatResponse:
        data = self._request_json(
            'POST',
            '/chat',
            {
                'text': text,
                'session_id': session_id,
                'metadata': dict(metadata or {}),
            },
        )

        return ApiChatResponse(
            voice_summary=str(data['voice_summary']),
            visual_text=str(data['visual_text']),
            visual_channel=str(data['visual_channel']),
            trace_id=str(data['trace_id']),
            metadata=dict(data.get('metadata') or {}),
        )

    def _request_json(
        self,
        method: str,
        path: str,
        payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        url = f'{self.base_url}{path}'
        body = None
        headers = {}

        if payload is not None:
            body = json.dumps(payload).encode('utf-8')
            headers['Content-Type'] = 'application/json'

        request = urllib_request.Request(
            url=url,
            data=body,
            headers=headers,
            method=method,
        )

        try:
            with urllib_request.urlopen(request, timeout=self.timeout) as response:
                raw = response.read().decode('utf-8')
        except URLError as error:
            raise ConnectionError(f'Kunne ikke kontakte LuciferOS API: {error}') from error

        return json.loads(raw)
