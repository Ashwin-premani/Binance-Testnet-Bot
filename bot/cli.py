import logging
import sys
from typing import Optional

import typer
from dotenv import load_dotenv
from rich import print
from rich.console import Console
from rich.table import Table

from .client import BinanceFuturesClient
from .logging_config import setup_logging
from .orders import build_and_place_order, summarize_order_response
from .validators import ValidationError

app = typer.Typer(add_completion=False)
console = Console()


@app.command()
def main(
    symbol: str = typer.Option(..., help="Trading symbol, e.g. BTCUSDT"),
    side: str = typer.Option(..., help="Order side: BUY or SELL"),
    order_type: str = typer.Option(..., "--order-type", help="Order type: MARKET or LIMIT"),
    quantity: float = typer.Option(..., help="Order quantity"),
    price: Optional[float] = typer.Option(
        None,
        help="Price for LIMIT orders. Required when --order-type=LIMIT.",
    ),
    time_in_force: Optional[str] = typer.Option(
        None,
        "--time-in-force",
        "-tif",
        help="Time in force for LIMIT orders: GTC, IOC, FOK (default: GTC).",
    ),
) -> None:
    """
    Simple CLI to place MARKET and LIMIT orders on Binance Futures Testnet (USDT-M).
    """
    # Load environment variables from .env (if present)
    load_dotenv()

    setup_logging()
    logger = logging.getLogger(__name__)

    console.rule("[bold green]Binance Futures Testnet Trading Bot")

    print("[bold]Order request summary:[/bold]")
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Field")
    table.add_column("Value")
    table.add_row("Symbol", symbol)
    table.add_row("Side", side)
    table.add_row("Type", order_type)
    table.add_row("Quantity", str(quantity))
    table.add_row("Price", str(price) if price is not None else "-")
    table.add_row("Time in Force", time_in_force or "GTC (default for LIMIT)")
    console.print(table)

    try:
        client = BinanceFuturesClient()
    except Exception as exc:
        logger.exception("Failed to initialize BinanceFuturesClient.")
        print(f"[bold red]Error:[/bold red] {exc}")
        raise typer.Exit(code=1)

    try:
        response = build_and_place_order(
            client=client,
            symbol=symbol,
            side=side,
            order_type=order_type,
            quantity=quantity,
            price=price,
            time_in_force=time_in_force,
        )
    except ValidationError as exc:
        print(f"[bold red]Validation error:[/bold red] {exc}")
        raise typer.Exit(code=1)
    except Exception as exc:  # API / network errors
        logger.exception("Failed to place order.")
        print(f"[bold red]Failed to place order:[/bold red] {exc}")
        raise typer.Exit(code=1)

    summary = summarize_order_response(response)

    print("\n[bold]Order response details:[/bold]")
    resp_table = Table(show_header=True, header_style="bold cyan")
    resp_table.add_column("Field")
    resp_table.add_column("Value")
    for key in [
        "symbol",
        "orderId",
        "clientOrderId",
        "status",
        "type",
        "side",
        "origQty",
        "executedQty",
        "avgPrice",
        "updateTime",
    ]:
        resp_table.add_row(key, str(summary.get(key)))
    console.print(resp_table)

    print("\n[bold green]Order placed successfully (or accepted by Binance).[/bold green]")


if __name__ == "__main__":
    # Allow running as `python -m bot.cli`
    app()


