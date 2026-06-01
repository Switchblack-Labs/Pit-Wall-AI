from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_explanation():

    client.post(
        "/api/strategy/recommend"
    )

    response = client.post(
        "/api/explain/"
    )

    assert response.status_code == 200

    data = response.json()

    assert "explanation" in data