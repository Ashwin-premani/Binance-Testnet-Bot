from bot.db import get_engine, get_recent_orders, init_db
from bot.orders import build_and_place_order
from bot.validators import ValidationError


class DummyClient:
    """Fake Binance client for tests that avoids real HTTP calls."""

    def __init__(self):
        self.calls = []

    def place_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: float,
        price=None,
        time_in_force=None,
    ):
        self.calls.append(
            {
                "symbol": symbol,
                "side": side,
                "type": order_type,
                "quantity": quantity,
                "price": price,
                "timeInForce": time_in_force,
            }
        )
        # Minimal response similar to Binance
        return {
            "symbol": symbol,
            "side": side,
            "type": order_type,
            "status": "NEW",
            "orderId": 1,
            "origQty": str(quantity),
            "executedQty": "0.000",
        }


def test_build_and_place_order_persists_to_db(tmp_path, monkeypatch):
    # Use a temporary SQLite file for this test
    db_path = tmp_path / "test.db"
    monkeypatch.setenv("TRADING_BOT_DB_URL", f"sqlite:///{db_path}")

    # Re-initialize DB with the temporary URL
    init_db()

    client = DummyClient()
    response = build_and_place_order(
        client=client,
        symbol="BTCUSDT",
        side="BUY",
        order_type="MARKET",
        quantity=0.002,
    )

    assert response["status"] == "NEW"
    recent = get_recent_orders(limit=5)
    assert len(recent) >= 1
    assert recent[0].symbol == "BTCUSDT"


def test_build_and_place_order_validation_error():
    client = DummyClient()
    # Invalid quantity should raise ValidationError before hitting client
    try:
        build_and_place_order(
            client=client,
            symbol="BTCUSDT",
            side="BUY",
            order_type="MARKET",
            quantity=0,
        )
    except ValidationError:
        assert not client.calls
    else:
        assert False, "Expected ValidationError"

