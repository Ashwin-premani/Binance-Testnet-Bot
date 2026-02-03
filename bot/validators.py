from typing import Literal, Optional


Side = Literal["BUY", "SELL"]
OrderType = Literal["MARKET", "LIMIT"]
TimeInForce = Literal["GTC", "IOC", "FOK"]


class ValidationError(ValueError):
    """Raised when user input is invalid."""


def validate_symbol(symbol: str) -> str:
    if not symbol or not symbol.isalnum():
        raise ValidationError("Symbol must be a non-empty alphanumeric string, e.g. BTCUSDT.")
    return symbol.upper()


def validate_side(side: str) -> Side:
    side_upper = side.upper()
    if side_upper not in ("BUY", "SELL"):
        raise ValidationError("Side must be BUY or SELL.")
    return side_upper  # type: ignore[return-value]


def validate_order_type(order_type: str) -> OrderType:
    ot_upper = order_type.upper()
    if ot_upper not in ("MARKET", "LIMIT"):
        raise ValidationError("Order type must be MARKET or LIMIT.")
    return ot_upper  # type: ignore[return-value]


def validate_quantity(qty: float) -> float:
    try:
        value = float(qty)
    except (TypeError, ValueError) as exc:
        raise ValidationError("Quantity must be a number.") from exc
    if value <= 0:
        raise ValidationError("Quantity must be greater than 0.")
    return value


def validate_price(price: Optional[float], order_type: OrderType) -> Optional[float]:
    if order_type == "LIMIT":
        if price is None:
            raise ValidationError("Price is required for LIMIT orders.")
        try:
            value = float(price)
        except (TypeError, ValueError) as exc:
            raise ValidationError("Price must be a number.") from exc
        if value <= 0:
            raise ValidationError("Price must be greater than 0.")
        return value
    return None


def validate_time_in_force(tif: Optional[str], order_type: OrderType) -> Optional[TimeInForce]:
    if order_type != "LIMIT":
        return None

    if tif is None:
        return "GTC"

    tif_upper = tif.upper()
    if tif_upper not in ("GTC", "IOC", "FOK"):
        raise ValidationError("time-in-force must be one of GTC, IOC, FOK for LIMIT orders.")
    return tif_upper  # type: ignore[return-value]


