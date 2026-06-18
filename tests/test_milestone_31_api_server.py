from fastapi.testclient import TestClient

from lucifer_os.interfaces.api_server import create_api_app


def test_api_server_health_endpoint():
    client = TestClient(create_api_app())

    response = client.get('/health')

    assert response.status_code == 200
    data = response.json()
    assert data['app_ready'] is True
    assert data['interface_name'] == 'api'
    assert data['adapter_name'] == 'api'


def test_api_server_chat_endpoint():
    client = TestClient(create_api_app())

    response = client.post('/chat', json={'text': 'Hei Lucifer'})

    assert response.status_code == 200
    data = response.json()
    assert data['visual_channel'] == 'api'
    assert data['trace_id']
    assert 'offline-modus' in data['voice_summary']


def test_api_server_chat_endpoint_accepts_session_and_metadata():
    client = TestClient(create_api_app())

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
