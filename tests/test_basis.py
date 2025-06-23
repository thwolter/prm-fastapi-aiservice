def test_root(test_client):
    response = test_client.get('/api/_health')
    assert response.status_code == 204
    assert response.content == b''


def test_health_check_returns_ok(test_client):
    response = test_client.get('/health-check')
    assert response.status_code == 200
    assert response.json() == {'status': 'ok'}
