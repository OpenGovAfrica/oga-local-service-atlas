import json


def test_health_check(client):
    response = client.get("/api/v1/health/")
    assert response.status_code == 200
    data = json.loads(response.content.decode())
    assert data.get("status") == "healthy"
