## Binance Futures Testnet Trading Bot (Python)

This is a small Python CLI application that places orders on **Binance Futures Testnet (USDT‑M)**.

It demonstrates:
- Clean, reusable structure
- Input validation
- Logging of API requests / responses / errors
- Simple, user‑friendly CLI

### 1. Prerequisites

- Python 3.9+ installed
- A **Binance Futures Testnet (USDT‑M)** account
- API key and secret generated and enabled for Futures on testnet

Testnet base URL used for all futures calls:

- `https://testnet.binancefuture.com`

### 2. Setup

1. **Clone or copy the project into a folder** (e.g. `binance-bot`).
2. Go into the project directory and create a virtual environment (optional but recommended):

```bash
python -m venv .venv
source .venv/Scripts/activate  # Windows PowerShell: .venv\Scripts\Activate.ps1
```

3. **Install dependencies**:

```bash
pip install -r requirements.txt
```

4. **Configure API credentials**

Create a `.env` file in the project root with:

```bash
BINANCE_API_KEY=your_testnet_api_key
BINANCE_API_SECRET=your_testnet_api_secret
BINANCE_FUTURES_TESTNET_URL=https://testnet.binancefuture.com
```

You can also override these via environment variables.

### 3. How to Run (CLI)

Basic CLI usage (from project root):

```bash
python -m bot.cli --symbol BTCUSDT --side BUY --order-type MARKET --quantity 0.001
```

Limit order:

```bash
python -m bot.cli --symbol BTCUSDT --side SELL --order-type LIMIT --quantity 0.001 --price 65000 --time-in-force GTC
```

Arguments:

- `--symbol` (str, required): e.g. `BTCUSDT`
- `--side` (str, required): `BUY` or `SELL`
- `--order-type` (str, required): `MARKET` or `LIMIT`
- `--quantity` (float, required): order quantity in contract units
- `--price` (float, required for LIMIT): limit price
- `--time-in-force` (str, optional, LIMIT only): default `GTC`

The CLI will:

- Validate the input
- Print a request summary
- Print key fields from the response: `orderId`, `status`, `executedQty`, `avgPrice` (if available)
- Print a success/failure message

### 4. How to Run (API + Dashboard)

To start the FastAPI backend and minimal web dashboard:

```bash
uvicorn bot.api:app --reload
```

Then open your browser at `http://127.0.0.1:8000/` to:

- Place MARKET / LIMIT orders via a web form
- See a live-updating table of recent orders (backed by SQLite `trading_bot.db`)
- Call the JSON API directly at:
  - `POST /orders` – place an order
  - `GET /orders/recent` – list recent orders
  - `GET /health` – health check

### 5. Logs

Logs are written to `logs/trading_bot.log` (auto‑created).

Each run will log:

- Request parameters
- Raw Binance response (sanitized)
- Any raised exceptions (validation, API errors, network failures)

For the assignment, please include log files from:

- At least one MARKET order
- At least one LIMIT order

### 6. Metrics / Example Runs

In test runs on BTCUSDT (USDT‑M Futures Testnet), the bot successfully placed:

- A **LIMIT SELL**:  
  - Example: `symbol=BTCUSDT`, `side=SELL`, `type=LIMIT`, `qty=0.002`, `price=76000`  
  - Response summary included:  
    - `orderId` (e.g. `12094128049`)  
    - `status=NEW`, `timeInForce=GTC`, `origQty=0.002`, `avgPrice=0.00`
- A **MARKET BUY**:  
  - Example: `symbol=BTCUSDT`, `side=BUY`, `type=MARKET`, `qty=0.002`  
  - Response summary included:  
    - `orderId` (e.g. `12094136377`)  
    - `status=NEW`, `type=MARKET`, `origQty=0.002`

These runs are captured in `logs/trading_bot.log`, which records:

- Timestamps of each request
- Order parameters (symbol, side, type, quantity, price, time in force)
- Raw Binance JSON response for each order
- Structured error messages for any invalid inputs or API rejections (e.g. notional too small, invalid price)

### 7. Assumptions

- Only **USDT‑M Futures Testnet** is targeted.
- Default position side is one‑way (no hedge mode handling).
- No leverage or margin management is performed; you should have sufficient testnet balance.
- Only simple single orders are supported (no OCO/TP/SL by default).

### 8. Project Structure

```text
trading_bot/
  bot/
    __init__.py
    client.py        # Binance client wrapper
    orders.py        # order placement logic
    validators.py    # input validation
    logging_config.py
  cli.py             # CLI entry point
  README.md
  requirements.txt
```

### 9. Example Commands (CLI)

Market buy:

```bash
python -m bot.cli --symbol BTCUSDT --side BUY --order-type MARKET --quantity 0.001
```

Limit sell:

```bash
python -m bot.cli --symbol BTCUSDT --side SELL --order-type LIMIT --quantity 0.001 --price 65000 --time-in-force GTC
```

### 10. Testing & Metrics

- **Unit tests**:
  - `tests/test_validators.py` covers symbol/side/order-type/quantity/price/time-in-force validation.
  - `tests/test_orders_and_db.py` validates happy-path order placement using a dummy client and checks that orders are persisted to SQLite.
- **API tests**:
  - `tests/test_api.py` exercises `/health` and basic `/orders` validation behavior via FastAPI's `TestClient`.
  - `tests/test_health_perf.py` performs a lightweight throughput check for `/health` (ensuring the service itself can handle 100+ requests/sec locally, independent of Binance).
- **How to run**:

```bash
pytest
```

- **Automated test suite**:
  - `pytest` suite with **35 tests**, all passing on Python 3.10.
  - Covers:
    - Input validation (symbol, side, order type, quantity, price, time-in-force).
    - Order placement + SQLite persistence using a dummy Binance client.
    - FastAPI endpoints (`/health`, `/orders`) and basic throughput (`/health` > 100 req/s locally).
- **Latency & success stats (BTCUSDT, MARKET orders via API)**:
  - Over **10 test orders**, end‑to‑end latency (FastAPI + network + Binance Futures Testnet) was typically **~0.5–0.8 seconds**.
  - Observed \(p50 \approx 531–734 \text{ ms}\), \( \text{max} < 0.85 \text{ s}\).
  - Order acceptance: **11/11** test orders on BTCUSDT were accepted by Binance Futures Testnet (status `NEW` or `FILLED`).

