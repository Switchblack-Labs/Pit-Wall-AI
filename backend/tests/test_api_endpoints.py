"""API-level tests for new and changed endpoints (offline via echo provider)."""


def test_rag_query_response_shape(client):
    resp = client.post("/api/rag/query", json={"question": "What is the pit lane speed limit?"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["question"]
    assert "answer" in data
    assert "citations" in data
    assert "grounded" in data
    assert isinstance(data["citations"], list)


def test_explain_never_500s_without_strategy(client):
    resp = client.post("/api/explain/")
    assert resp.status_code == 200


def test_explain_after_strategy(client):
    client.post("/api/strategy/recommend")
    resp = client.post("/api/explain/")
    assert resp.status_code == 200
    assert "explanation" in resp.json()


def test_competitors_post_then_get(client):
    payload = {
        "car_id": "CAR_44",
        "position": 2,
        "gap": 1.3,
        "pit_status": False,
        "pace_delta": -0.2,
        "tire_wear": 0.4,
    }
    post = client.post("/api/competitors/", json=payload)
    assert post.status_code == 200

    get = client.get("/api/competitors/")
    assert get.status_code == 200
    car_ids = [c["car_id"] for c in get.json()]
    assert "CAR_44" in car_ids


def test_torcs_start_and_stop(client):
    start = client.post("/api/torcs/start", json={"mode": "simulated", "total_laps": 3})
    assert start.status_code == 200
    assert start.json()["status"] in {"torcs started", "already running"}

    stop = client.post("/api/torcs/stop")
    assert stop.status_code == 200
    assert stop.json()["status"] == "torcs stopped"


def test_torcs_start_defaults_without_body(client):
    start = client.post("/api/torcs/start")
    assert start.status_code == 200
    client.post("/api/torcs/stop")


def test_websocket_connect_and_receive_broadcast(client):
    with client.websocket_connect("/ws/live") as ws:
        client.post("/api/strategy/recommend")
        msg = ws.receive_json()
        assert "type" in msg
        assert msg["type"] in {"strategy", "telemetry", "simulation", "explanation"}
