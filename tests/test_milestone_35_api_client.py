import json
from urllib.error import URLError

import pytest

from lucifer_os.interfaces.api_client import LuciferApiClient
from lucifer_os.interfaces.api_schema import ApiChatResponse, ApiHealthResponse


class FakeHttpResponse:
    def __init__(self, data):
        self.data = data

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False

    def read(self):
        return json.dumps(self.data).encode('utf-8')


def test_api_client_health_returns_health_response(monkeypatch):
    def fake_urlopen(request, timeout):
        assert request.full_url == 'http://127.0.0.1:8787/health'
        assert request.get_method() == 'GET'
        assert timeout == 5.0
        return FakeHttpResponse(
            {
                'app_ready': True,
                'project_root': '.',
                'interface_name': 'api',
                'provider_name': None,
                'adapter_name': 'api',
            }
        )

    monkeypatch.setattr('urllib.request.urlopen', fake_urlopen)

    response = LuciferApiClient().health()

    assert isinstance(response, ApiHealthResponse)
    assert response.app_ready is True
    assert response.interface_name == 'api'
    assert response.provider_name is None


def test_api_client_chat_returns_chat_response(monkeypatch):
    def fake_urlopen(request, timeout):
        assert request.full_url == 'http://127.0.0.1:8787/chat'
        assert request.get_method() == 'POST'
        assert request.headers['Content-type'] == 'application/json'
        payload = json.loads(request.data.decode('utf-8'))
        assert payload == {
            'text': 'Hei Lucifer',
            'session_id': None,
            'metadata': {},
        }
        return FakeHttpResponse(
            {
                'voice_summary': 'kort svar',
                'visual_text': 'langt svar',
                'visual_channel': 'api',
                'trace_id': 'trace-1',
                'metadata': {'mode': 'test'},
            }
        )

    monkeypatch.setattr('urllib.request.urlopen', fake_urlopen)

    response = LuciferApiClient().chat('Hei Lucifer')

    assert isinstance(response, ApiChatResponse)
    assert response.voice_summary == 'kort svar'
    assert response.visual_text == 'langt svar'
    assert response.visual_channel == 'api'
    assert response.trace_id == 'trace-1'
    assert response.metadata == {'mode': 'test'}


def test_api_client_chat_sends_session_and_metadata(monkeypatch):
    def fake_urlopen(request, timeout):
        payload = json.loads(request.data.decode('utf-8'))
        assert payload['text'] == 'Hei Lucifer'
        assert payload['session_id'] == 'session-1'
        assert payload['metadata'] == {'source': 'client-test'}
        return FakeHttpResponse(
            {
                'voice_summary': 'ok',
                'visual_text': 'ok',
                'visual_channel': 'api',
                'trace_id': 'trace-2',
                'metadata': {},
            }
        )

    monkeypatch.setattr('urllib.request.urlopen', fake_urlopen)

    response = LuciferApiClient().chat(
        'Hei Lucifer',
        session_id='session-1',
        metadata={'source': 'client-test'},
    )

    assert response.trace_id == 'trace-2'


def test_api_client_accepts_custom_base_url_and_timeout(monkeypatch):
    def fake_urlopen(request, timeout):
        assert request.full_url == 'http://localhost:9999/health'
        assert timeout == 1.5
        return FakeHttpResponse(
            {
                'app_ready': True,
                'project_root': '.',
                'interface_name': 'api',
                'provider_name': 'offline',
                'adapter_name': 'api',
            }
        )

    monkeypatch.setattr('urllib.request.urlopen', fake_urlopen)

    response = LuciferApiClient(
        base_url='http://localhost:9999/',
        timeout=1.5,
    ).health()

    assert response.provider_name == 'offline'


def test_api_client_raises_connection_error_when_api_is_unavailable(monkeypatch):
    def fake_urlopen(request, timeout):
        raise URLError('connection refused')

    monkeypatch.setattr('urllib.request.urlopen', fake_urlopen)

    with pytest.raises(ConnectionError):
        LuciferApiClient().health()


def test_api_client_uses_environment_base_url(monkeypatch):
    monkeypatch.setenv('LUCIFER_API_URL', 'http://localhost:7777')

    def fake_urlopen(request, timeout):
        assert request.full_url == 'http://localhost:7777/health'
        return FakeHttpResponse(
            {
                'app_ready': True,
                'project_root': '.',
                'interface_name': 'api',
                'provider_name': None,
                'adapter_name': 'api',
            }
        )

    monkeypatch.setattr('urllib.request.urlopen', fake_urlopen)

    response = LuciferApiClient().health()

    assert response.app_ready is True


def test_api_client_explicit_base_url_overrides_environment(monkeypatch):
    monkeypatch.setenv('LUCIFER_API_URL', 'http://localhost:7777')

    def fake_urlopen(request, timeout):
        assert request.full_url == 'http://localhost:8888/health'
        return FakeHttpResponse(
            {
                'app_ready': True,
                'project_root': '.',
                'interface_name': 'api',
                'provider_name': 'offline',
                'adapter_name': 'api',
            }
        )

    monkeypatch.setattr('urllib.request.urlopen', fake_urlopen)

    response = LuciferApiClient(base_url='http://localhost:8888').health()

    assert response.provider_name == 'offline'
