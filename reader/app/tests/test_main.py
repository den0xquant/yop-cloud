from fastapi.testclient import TestClient


def test_healthy(client: TestClient):
    response = client.get("/health-check")
    assert response.status_code == 200
    assert response.content == b"true"
