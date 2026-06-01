from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_strategy_generation():

    response = client.post(
        "/api/strategy/recommend"
    )

    assert response.status_code == 200

    data = response.json()

    assert "recommended_action" in data