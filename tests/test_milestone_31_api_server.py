import warnings

from starlette.exceptions import StarletteDeprecationWarning

with warnings.catch_warnings():
    warnings.simplefilter('ignore', StarletteDeprecationWarning)
    from fastapi.testclient import TestClient

from lucifer_os.interfaces.api_server import create_api_app


def test_api_server_health_endpoint():
    client = TestClient(create_api_app(provider_name='offline'))

    response = client.get('/health')

    assert response.status_code == 200
    data = response.json()
    assert data['app_ready'] is True
    assert data['interface_name'] == 'api'
    assert data['adapter_name'] == 'api'


def test_api_server_chat_endpoint():
    client = TestClient(create_api_app(provider_name='offline'))

    response = client.post('/chat', json={'text': 'Hei Lucifer'})

    assert response.status_code == 200
    data = response.json()
    assert data['visual_channel'] == 'api'
    assert data['trace_id']
    assert 'offline-modus' in data['voice_summary']


def test_api_server_chat_endpoint_accepts_session_and_metadata():
    client = TestClient(create_api_app(provider_name='offline'))

    response = client.post(
        '/chat',
        json={
            'text': 'Hei Lucifer',
            'session_id': 'session-1',
            'metadata': {'source': 'api-test'},
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data['visual_channel'] == 'api'
    assert data['trace_id']


def test_api_server_module_exposes_importable_app():
    from lucifer_os.interfaces.api_server import app

    client = TestClient(app)
    response = client.get('/health')

    assert response.status_code == 200
    assert response.json()['app_ready'] is True


def test_api_server_has_main_entrypoint():
    from lucifer_os.interfaces import api_server

    assert callable(api_server.main)


def test_api_server_allows_cors_preflight_for_chat():
    client = TestClient(create_api_app(provider_name='offline'))

    response = client.options(
        '/chat',
        headers={
            'Origin': 'null',
            'Access-Control-Request-Method': 'POST',
            'Access-Control-Request-Headers': 'content-type',
        },
    )

    assert response.status_code == 200
    assert response.headers['access-control-allow-origin'] == 'null'
    assert 'POST' in response.headers['access-control-allow-methods']
