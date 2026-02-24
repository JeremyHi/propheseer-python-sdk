# Propheseer Python SDK

Official Python SDK for the [Propheseer](https://propheseer.com) prediction markets API. Access normalized data from Polymarket, Kalshi, and Gemini through a single, type-safe interface.

## Installation

```bash
pip install propheseer
```

For WebSocket support (real-time market updates):

```bash
pip install propheseer[websocket]
```

## Quick Start

```python
from propheseer import Propheseer

client = Propheseer(
    api_key="pk_test_...",  # or set PROPHESEER_API_KEY env var
)

# List prediction markets
page = client.markets.list(source="polymarket", limit=10)
for market in page.data:
    print(f"{market.question}: {market.outcomes[0].probability:.0%}")

# Check your API key usage
result = client.keys.me()
print(f"Plan: {result.data.plan}, Daily usage: {result.data.usage.daily}")
```

## Async Support

```python
import asyncio
from propheseer import AsyncPropheseer

async def main():
    async with AsyncPropheseer(api_key="pk_test_...") as client:
        page = await client.markets.list(source="polymarket")
        for market in page.data:
            print(market.question)

asyncio.run(main())
```

## Configuration

```python
client = Propheseer(
    api_key="pk_test_...",                      # Required (or PROPHESEER_API_KEY env var)
    base_url="https://api.propheseer.com",      # Default
    timeout=30.0,                               # Request timeout in seconds (default: 30)
    max_retries=2,                              # Retries on 429/5xx errors (default: 2)
)
```

## Resources

### Markets

```python
# List markets with filters
page = client.markets.list(
    source="polymarket",   # "polymarket" | "kalshi" | "gemini"
    category="politics",   # "politics" | "sports" | "finance" | ...
    status="open",
    q="election",          # search query
    limit=50,
    offset=0,
)

# Get a single market
result = client.markets.get("pm_12345")
market = result.data

# Auto-paginate through all markets
for market in client.markets.list_auto_paginate(source="kalshi"):
    print(market.question)
```

### Categories

```python
result = client.categories.list()
# [Category(id='politics', name='Politics', subcategories=['elections', ...]), ...]
```

### Arbitrage (Pro+)

```python
result = client.arbitrage.find(min_spread=0.05, category="politics")

for opp in result.data:
    print(f"{opp.question}: spread={opp.spread}, return={opp.potential_return}")
```

### Unusual Trades (Pro+)

```python
page = client.unusual_trades.list(
    reason="high_amount",
    since="2025-01-01T00:00:00Z",
    limit=20,
)

for trade in page.data:
    print(f"${trade.trade.usdc_value} {trade.trade.side} on \"{trade.market.question}\"")

# Auto-paginate
for trade in client.unusual_trades.list_auto_paginate():
    print(trade.detection.reason, trade.detection.anomaly_score)
```

### History (Business+)

```python
# Market price history
result = client.history.list(market_id="pm_12345", days=7)

# Available snapshot dates
result = client.history.dates()
```

### Ticker (Public)

```python
# No auth required
result = client.ticker.list(limit=10)
```

## Pagination

Paginated endpoints return a `SyncPage[T]` (or `AsyncPage[T]`) object:

```python
page = client.markets.list(limit=50)
print(page.data)          # list[Market]
print(page.meta.total)    # total matching markets
print(page.has_more())    # bool
print(page.next_offset()) # int | None
```

For automatic pagination:

```python
for market in client.markets.list_auto_paginate(limit=50, max_items=200):
    # yields individual items, fetching new pages as needed
    pass
```

## Error Handling

All API errors are raised as typed exceptions:

```python
from propheseer import PermissionDeniedError, RateLimitError, AuthenticationError

try:
    client.arbitrage.find()
except PermissionDeniedError as err:
    print(f"Upgrade to {err.required_plan} plan")
except RateLimitError as err:
    print(f"Rate limited, retry after {err.retry_after}s")
except AuthenticationError:
    print("Invalid API key")
```

| Error Class | Status | When |
|------------|--------|------|
| `AuthenticationError` | 401 | Missing or invalid API key |
| `InsufficientCreditsError` | 402 | Not enough credits |
| `PermissionDeniedError` | 403 | Plan upgrade required |
| `NotFoundError` | 404 | Resource not found |
| `RateLimitError` | 429 | Rate limit exceeded |
| `InternalServerError` | 5xx | Server error |
| `APIConnectionError` | - | Network/timeout error |

## WebSocket (Real-Time Updates)

```python
from propheseer import PropheseerWebSocket

ws = PropheseerWebSocket(
    api_key="pk_test_...",
    reconnect=True,              # Auto-reconnect (default: True)
    max_reconnect_attempts=5,    # Default: 5
    ping_interval=25.0,          # Keepalive interval (default: 25s)
)

@ws.on("connected")
def on_connected(msg):
    print(f"Connected: {msg['sessionId']} ({msg['plan']})")
    ws.subscribe(["pm_12345", "ks_67890"])

@ws.on("market_update")
def on_update(msg):
    print("Market update:", msg["market"])

@ws.on("error")
def on_error(err):
    print("Error:", err)

ws.connect()

# Later:
ws.unsubscribe(["pm_12345"])
ws.close()
```

### Async WebSocket

```python
import asyncio
from propheseer import AsyncPropheseerWebSocket

async def main():
    ws = AsyncPropheseerWebSocket(api_key="pk_test_...")

    ws.on("connected", lambda msg: print(f"Connected: {msg['sessionId']}"))
    ws.on("market_update", lambda msg: print("Update:", msg))

    await ws.connect()
    ws.subscribe(["pm_12345"])

    await asyncio.sleep(60)
    await ws.close()

asyncio.run(main())
```

## Rate Limit Information

Every API response includes rate limit info:

```python
page = client.markets.list()
print(page.rate_limit)
# RateLimitInfo(
#   plan='pro',
#   billing_type='subscription',
#   limit_day=10000,
#   remaining_day=9950,
#   limit_minute=100,
#   remaining_minute=98,
# )
```

## Requirements

- Python >= 3.9
- httpx >= 0.24.0
- websockets >= 11.0 (optional, for WebSocket support)

## License

MIT
