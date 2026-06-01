from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_telemetry_ingestion():

    payload = {
        "speed": 210,
        "rpm": 9000,
        "gear": 6,
        "throttle": 0.9,
        "brake": 0.0,
        "steering_angle": 0.1,
        "track_position": 0.02,
        "lap": 12,
        "fuel": 42,
        "tire_wear": 0.3,
        "timestamp": "2026-05-28T10:00:00"
    }

    response = client.post(
        "/api/telemetry/",
        json=payload
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "accepted"