import logging
from typing import Any, Dict, Optional

from .client import BinanceFuturesClient
from .validators import (
    OrderType,
    Side,
    TimeInForce,
    validate_order_type,
    validate_price,
    validate_quantity,
    validate_side,
    validate_symbol,
    validate_time_in_force,
    ValidationError,
)

logger = logging.getLogger(__name__)


def build_and_place_order(
    client: BinanceFuturesClient,
    symbol: str,
    side: str,
    order_type: str,
    quantity: float,
    price: Optional[float] = None,
    time_in_force: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Validate input and place an order through the BinanceFuturesClient.
    """
    try:
        v_symbol = validate_symbol(symbol)
        v_side: Side = validate_side(side)
        v_type: OrderType = validate_order_type(order_type)
        v_qty = validate_quantity(quantity)
        v_price = validate_price(price, v_type)
        v_tif: Optional[TimeInForce] = validate_time_in_force(time_in_force, v_type)
    except ValidationError:
        logger.exception("Validation failed for order parameters.")
        raise

    response = client.place_order(
        symbol=v_symbol,
        side=v_side,
        order_type=v_type,
        quantity=v_qty,
        price=v_price,
        time_in_force=v_tif,
    )
    return response


def summarize_order_response(response: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract a concise summary from Binance order response.
    """
    return {
        "symbol": response.get("symbol"),
        "orderId": response.get("orderId"),
        "clientOrderId": response.get("clientOrderId"),
        "status": response.get("status"),
        "type": response.get("type"),
        "side": response.get("side"),
        "origQty": response.get("origQty"),
        "executedQty": response.get("executedQty"),
        "avgPrice": response.get("avgPrice") or response.get("avgPrice", None),
        "updateTime": response.get("updateTime") or response.get("transactTime"),
    }


