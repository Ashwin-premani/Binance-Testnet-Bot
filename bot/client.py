import logging
import os
from typing import Any, Dict, Optional

from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceRequestException

logger = logging.getLogger(__name__)


class BinanceFuturesClient:
    """
    Lightweight wrapper around python-binance for USDT-M Futures Testnet.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        base_url: Optional[str] = None,
    ) -> None:
        api_key = api_key or os.getenv("BINANCE_API_KEY")
        api_secret = api_secret or os.getenv("BINANCE_API_SECRET")
        if not api_key or not api_secret:
            raise ValueError("BINANCE_API_KEY and BINANCE_API_SECRET must be set.")

        base_url = base_url or os.getenv(
            "BINANCE_FUTURES_TESTNET_URL", "https://testnet.binancefuture.com"
        )

        # python-binance uses FUTURES_URL like "https://fapi.binance.com/fapi".
        # For testnet, base_url is "https://testnet.binancefuture.com", and the client
        # will append "/order", etc. So we add the "/fapi" prefix here.
        futures_url = base_url.rstrip("/") + "/fapi"

        self._client = Client(api_key=api_key, api_secret=api_secret)
        self._client.FUTURES_URL = futures_url  # type: ignore[attr-defined]

        logger.info(
            "Initialized BinanceFuturesClient with base_url=%s futures_url=%s",
            base_url,
            futures_url,
        )

    def place_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: float,
        price: Optional[float] = None,
        time_in_force: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Place a futures order on Binance Futures Testnet.
        """
        logger.info(
            "Placing order: symbol=%s side=%s type=%s qty=%s price=%s tif=%s",
            symbol,
            side,
            order_type,
            quantity,
            price,
            time_in_force,
        )

        try:
            params: Dict[str, Any] = {
                "symbol": symbol,
                "side": side,
                "type": order_type,
                "quantity": quantity,
            }
            if order_type == "LIMIT":
                params["price"] = price
                params["timeInForce"] = time_in_force or "GTC"

            response = self._client.futures_create_order(**params)
            logger.info("Order placed successfully: %s", response)
            return response
        except BinanceAPIException as exc:
            logger.error(
                "Binance API error when placing order: code=%s msg=%s",
                exc.code,
                exc.message,
            )
            raise
        except BinanceRequestException as exc:
            logger.error("Network error when placing order: %s", exc)
            raise
        except Exception as exc:  # pragma: no cover - defensive
            logger.exception("Unexpected error when placing order: %s", exc)
            raise


