import time

from fastapi.testclient import TestClient

from bot.api import app


client = TestClient(app)


def test_health_throughput():
    """Lightweight throughput check for /health (no Binance calls)."""
    n = 200
    t0 = time.perf_counter()
    for _ in range(n):
        resp = client.get("/health")
        assert resp.status_code == 200
    dt = time.perf_counter() - t0
    rps = n / dt

    # Just assert it's not ridiculously slow in local test environment
    assert rps > 100

