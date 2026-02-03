import logging
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from .client import BinanceFuturesClient
from .db import get_recent_orders, init_db
from .logging_config import setup_logging
from .orders import build_and_place_order, summarize_order_response
from .validators import ValidationError

logger = logging.getLogger(__name__)

app = FastAPI(title="Binance Futures Testnet Bot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class OrderRequest(BaseModel):
    symbol: str = Field(..., example="BTCUSDT")
    side: str = Field(..., example="BUY")
    order_type: str = Field(..., alias="type", example="MARKET")
    quantity: float = Field(..., gt=0)
    price: Optional[float] = Field(None, gt=0)
    time_in_force: Optional[str] = Field(None, alias="timeInForce", example="GTC")

    class Config:
        populate_by_name = True


@app.on_event("startup")
def on_startup() -> None:
    # Load environment variables for API process
    load_dotenv()
    setup_logging()
    init_db()
    logger.info("API startup complete.")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/orders")
def create_order(payload: OrderRequest):
    try:
        client = BinanceFuturesClient()
    except Exception as exc:
        logger.exception("Failed to initialize BinanceFuturesClient in API.")
        raise HTTPException(status_code=500, detail=str(exc))

    try:
        response = build_and_place_order(
            client=client,
            symbol=payload.symbol,
            side=payload.side,
            order_type=payload.order_type,
            quantity=payload.quantity,
            price=payload.price,
            time_in_force=payload.time_in_force,
        )
    except ValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        logger.exception("Failed to place order via API.")
        raise HTTPException(status_code=502, detail=str(exc))

    return summarize_order_response(response)


@app.get("/orders/recent")
def recent_orders(limit: int = 20):
    records = get_recent_orders(limit=limit)
    return [
        {
            "id": r.id,
            "created_at": r.created_at,
            "symbol": r.symbol,
            "side": r.side,
            "type": r.type,
            "status": r.status,
            "order_id": r.order_id,
        }
        for r in records
    ]


@app.get("/", response_class=HTMLResponse)
def dashboard() -> str:
    # Minimal inline HTML dashboard for quick visualization
    return """
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <title>Binance Futures Bot Dashboard</title>
    <style>
      body { font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; margin: 2rem; background: #0b1120; color: #e5e7eb; }
      h1 { color: #38bdf8; }
      .card { background: #020617; padding: 1.5rem; border-radius: 0.75rem; margin-bottom: 1.5rem; box-shadow: 0 10px 15px -3px rgba(15,23,42,0.5); }
      label { display: block; margin-top: 0.5rem; font-size: 0.9rem; color: #9ca3af; }
      input, select { width: 100%; padding: 0.4rem 0.6rem; margin-top: 0.15rem; border-radius: 0.4rem; border: 1px solid #1f2937; background: #020617; color: #e5e7eb; }
      button { margin-top: 0.75rem; padding: 0.45rem 0.9rem; border-radius: 0.5rem; border: none; background: #22c55e; color: #022c22; font-weight: 600; cursor: pointer; }
      button:disabled { opacity: 0.6; cursor: wait; }
      table { width: 100%; border-collapse: collapse; margin-top: 0.75rem; font-size: 0.85rem; }
      th, td { padding: 0.4rem 0.5rem; border-bottom: 1px solid #111827; text-align: left; }
      th { background: #020617; color: #9ca3af; }
      tr:nth-child(even) { background: #020617; }
      .badge { display: inline-block; padding: 0.1rem 0.45rem; border-radius: 999px; font-size: 0.7rem; }
      .badge-buy { background: #064e3b; color: #6ee7b7; }
      .badge-sell { background: #7f1d1d; color: #fecaca; }
    </style>
  </head>
  <body>
    <h1>Binance Futures Testnet Bot</h1>
    <div class="card">
      <h2>Place Order</h2>
      <form id="order-form">
        <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:0.75rem;">
          <div>
            <label>Symbol</label>
            <input name="symbol" value="BTCUSDT" />
          </div>
          <div>
            <label>Side</label>
            <select name="side">
              <option>BUY</option>
              <option>SELL</option>
            </select>
          </div>
          <div>
            <label>Type</label>
            <select name="type">
              <option>MARKET</option>
              <option>LIMIT</option>
            </select>
          </div>
          <div>
            <label>Quantity</label>
            <input name="quantity" type="number" step="0.001" value="0.002" />
          </div>
          <div>
            <label>Price (for LIMIT)</label>
            <input name="price" type="number" step="0.1" />
          </div>
          <div>
            <label>Time in Force</label>
            <select name="timeInForce">
              <option value="">(default)</option>
              <option>GTC</option>
              <option>IOC</option>
              <option>FOK</option>
            </select>
          </div>
        </div>
        <button id="submit-btn" type="submit">Place Order</button>
      </form>
      <pre id="order-result" style="margin-top:0.75rem;font-size:0.8rem;white-space:pre-wrap;"></pre>
    </div>

    <div class="card">
      <h2>Recent Orders</h2>
      <table id="orders-table">
        <thead>
          <tr>
            <th>Time</th>
            <th>Symbol</th>
            <th>Side</th>
            <th>Type</th>
            <th>Status</th>
            <th>Order ID</th>
          </tr>
        </thead>
        <tbody></tbody>
      </table>
    </div>

    <script>
      async function loadOrders() {
        const res = await fetch('/orders/recent?limit=25');
        const data = await res.json();
        const tbody = document.querySelector('#orders-table tbody');
        tbody.innerHTML = '';
        for (const row of data) {
          const tr = document.createElement('tr');
          const sideBadgeClass = row.side === 'BUY' ? 'badge badge-buy' : 'badge badge-sell';
          tr.innerHTML = `
            <td>${new Date(row.created_at).toLocaleTimeString()}</td>
            <td>${row.symbol}</td>
            <td><span class="${sideBadgeClass}">${row.side}</span></td>
            <td>${row.type}</td>
            <td>${row.status}</td>
            <td>${row.order_id}</td>
          `;
          tbody.appendChild(tr);
        }
      }

      document.getElementById('order-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const btn = document.getElementById('submit-btn');
        btn.disabled = true;
        const form = new FormData(e.target);
        const payload = {
          symbol: form.get('symbol'),
          side: form.get('side'),
          type: form.get('type'),
          quantity: parseFloat(form.get('quantity')),
        };
        const price = form.get('price');
        if (price) payload.price = parseFloat(price);
        const tif = form.get('timeInForce');
        if (tif) payload.timeInForce = tif;

        try {
          const res = await fetch('/orders', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
          });
          const data = await res.json();
          if (!res.ok) {
            document.getElementById('order-result').textContent = 'Error: ' + (data.detail || JSON.stringify(data));
          } else {
            document.getElementById('order-result').textContent = JSON.stringify(data, null, 2);
            await loadOrders();
          }
        } catch (err) {
          document.getElementById('order-result').textContent = 'Request failed: ' + err;
        } finally {
          btn.disabled = false;
        }
      });

      loadOrders();
      setInterval(loadOrders, 15000);
    </script>
  </body>
</html>
    """

