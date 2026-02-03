from fastapi.testclient import TestClient

from bot.api import app


client = TestClient(app)


def test_health_endpoint():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_create_order_validation_error():
    # Missing quantity should trigger 422 from FastAPI or 400 from our validation
    payload = {"symbol": "BTCUSDT", "side": "BUY", "type": "MARKET"}
    resp = client.post("/orders", json=payload)
    assert resp.status_code in (400, 422)

