import pytest

from bot.validators import (
    ValidationError,
    validate_order_type,
    validate_price,
    validate_quantity,
    validate_side,
    validate_symbol,
    validate_time_in_force,
)


def test_validate_symbol_ok():
    assert validate_symbol("btcusdt") == "BTCUSDT"


@pytest.mark.parametrize("symbol", ["", " BTCUSDT", "BTC-USDT", " "])
def test_validate_symbol_invalid(symbol):
    with pytest.raises(ValidationError):
        validate_symbol(symbol)


@pytest.mark.parametrize("side", ["BUY", "buy", "SELL", "sell"])
def test_validate_side_ok(side):
    assert validate_side(side) in ("BUY", "SELL")


@pytest.mark.parametrize("side", ["", "LONG", "SHORT"])
def test_validate_side_invalid(side):
    with pytest.raises(ValidationError):
        validate_side(side)


@pytest.mark.parametrize("order_type", ["MARKET", "market", "LIMIT", "limit"])
def test_validate_order_type_ok(order_type):
    assert validate_order_type(order_type) in ("MARKET", "LIMIT")


@pytest.mark.parametrize("order_type", ["", "STOP", "OCO"])
def test_validate_order_type_invalid(order_type):
    with pytest.raises(ValidationError):
        validate_order_type(order_type)


@pytest.mark.parametrize("qty", [0.001, "1"])
def test_validate_quantity_ok(qty):
    assert validate_quantity(qty) > 0


@pytest.mark.parametrize("qty", [0, -1, "abc"])
def test_validate_quantity_invalid(qty):
    with pytest.raises(ValidationError):
        validate_quantity(qty)


def test_validate_price_limit_ok():
    assert validate_price(10.5, "LIMIT") == 10.5


def test_validate_price_limit_missing():
    with pytest.raises(ValidationError):
        validate_price(None, "LIMIT")


def test_validate_price_market_ignored():
    assert validate_price(None, "MARKET") is None


def test_validate_time_in_force_default_gtc():
    assert validate_time_in_force(None, "LIMIT") == "GTC"


def test_validate_time_in_force_invalid():
    with pytest.raises(ValidationError):
        validate_time_in_force("DAY", "LIMIT")


def test_validate_time_in_force_ignored_for_market():
    assert validate_time_in_force("GTC", "MARKET") is None

