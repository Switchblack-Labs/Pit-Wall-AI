from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_simulation():

    payload = {
        "scenario_type": "pit_now",
        "laps_until_action": 0
    }

    response = client.post(
        "/api/simulate/",
        json=payload
    )

    assert response.status_code == 200

    data = response.json()

    assert "projected_position" in data