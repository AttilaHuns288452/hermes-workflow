# BingX API Reference

## Endpoints Used

| Endpoint | Purpose | Auth |
|---|---|---|
| `/openApi/swap/v2/quote/klines` | Historical OHLCV data | None |
| `/openApi/swap/v2/quote/depth` | L2 order book (also the only honest spread source) | None |
| `/openApi/swap/v2/quote/price` | Last traded price (cheap sizing fallback) | None |
| `/openApi/swap/v2/quote/contracts` | Contract specs, fee rates, min qty | None |
| `/openApi/swap/v2/quote/premiumIndex` | Funding rate | None |
| `/openApi/swap/v2/quote/openInterest` | Open interest | None |
| `/openApi/swap/v2/server/time` | Server clock (cheapest liveness probe) | None |
| `/openApi/swap/v2/user/balance` | Account balance | Signed |
| `/openApi/swap/v2/user/positions` | Open positions | Signed |
| `/openApi/swap/v2/trade/order` | Place order | Signed |
| `/openApi/swap/v2/trade/allOrders` | Order history — rows under `data.orders`, NOT `data` | Signed |
| `/openApi/swap/v2/trade/closeAllPositions` | Close all positions for a symbol | Signed |

**Paths that do NOT exist** (both answer `100404`, and a client that swallows `code` reads them as an empty success):

| Wrong path | Right path |
|---|---|
| `/openApi/swap/v2/trade/closeAll` | `/openApi/swap/v2/trade/closeAllPositions` |
| `/openApi/swap/v2/trade/orders` | `/openApi/swap/v2/trade/allOrders` (nested under `data.orders`) |

A dead close path is the worst kind: every automated exit silently becomes a no-op while the ledger still logs a SELL row.

## Environments

| | Base URL |
|---|---|
| Live | `https://open-api.bingx.com` |
| Demo / VST | `https://open-api-vst.bingx.com` |

VST = virtual settlement token. Demo orders are real orders on a demo account — real latency, real rejects, no real money.

## Diagnosing: Public Works But Signed Fails

This is the most common false alarm. Separate the two layers before concluding the integration is broken:

```python
# 1. Connectivity + signing code + base URL are all fine if this returns code 0
GET /openApi/swap/v2/server/time           -> {"code": 0, "data": {"serverTime": ...}}

# 2. Credentials are the problem if this returns 100413
GET /openApi/swap/v2/user/balance   (signed) -> {"code": 100413,
                                                "msg": "Incorrect apiKey, please check your valid api key"}
```

`100413` means the HMAC code, timestamp, and endpoint are correct and the **key** is stale, revoked, or from a deleted demo account. Regenerate it in the demo account. Do not debug the signature — a wrong signature returns a different error (usually `100001`/`100400`-family), not "incorrect apiKey".

Run both probes before reporting any auth verdict, and never paste the key while doing it — print only `set`/`len`, never the value.

## Authentication

BingX uses HMAC-SHA256 signatures:

```python
import hmac, hashlib
from urllib.parse import urlencode

def sign_request(params: dict, secret_key: str) -> str:
    query_string = urlencode(sorted(params.items()))
    return hmac.new(
        secret_key.encode("utf-8"),
        query_string.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
```

Signed requests need `timestamp` (ms) and `signature` in the params, with the signature computed over params **sorted** and URL-encoded.

**Sign and transmit the SAME bytes for GET/DELETE.** POST signs the JSON body, so orders work even when signed GETs are broken. A client that sorts params for the signature but lets `requests` re-serialise them produces a different order and fails `100001` on any signed GET with two or more params — while single-param GETs and all POSTs pass, which hides the bug. Build the signed query string once and send it verbatim:

```python
qs = urlencode(sorted(params.items()))
r = requests.get(f"{url}?{qs}", headers=headers, timeout=10)
```

## Coherent failure handling

The host reports rejections in the body under **HTTP 200**. A client that only calls `raise_for_status()` reads a rejected order as success, and `get_positions()` returning `[]` then means "flat **or** rejected" — indistinguishable, and the dangerous one wins. Check `body["code"]` and raise on anything that is not `0`.

## Order-book spreads are 30x wider than the fee on alt pairs

Measured 2026-11-09 from the live VST book, top of book:

| symbol | spread |
|---|---|
| BTC-USDT | **0.7 bps** |
| ETH-USDT | 27.9 bps |
| SOL-USDT | 26.1 bps |
| DOGE-USDT | 29.0 bps |

Fees are 5 bps taker either way, so a round trip is ~10 bps on BTC and **36-39 bps on the alts** — roughly 4x. A cost model with `spread_bps = 0` understates real cost by ~2x on four of five tradable symbols, and a live 1%-sized DOGE round trip confirmed it: 36.1 bps against a modelled 20.

Implications:
- Read the spread from `/quote/depth` per symbol, not from a single global assumption.
- BTC-only backtests are not evidence for an alt-pair strategy. The instrument is part of the hypothesis.
- When you add a measured-scenario, add it as a NEW scenario beside the existing baseline rather than changing the baseline, so prior experiments and promoted parameters stay comparable.

## Position limits: percentage of equity, enforced in the client

A flat dollar cap and a percentage cap are different instruments. The flat cap (`MAX_POSITION_USDT=10`) silently refuses every order on a funded account, because sizing at 20% of 100k asks for 20,000 — the bot runs, logs signals, and places nothing. A percentage cap scales with the account and is what the user usually means by "1% risk per trade".

Enforce BOTH, in `check_order`, so no caller can bypass them:

```python
cap = limits["max_position_usdt"]                       # hard backstop
equity = _equity_for_risk()                             # cached, see below
if limits["max_position_pct"] > 0:
    cap = min(cap, equity * limits["max_position_pct"])  # the working limit
if notional > cap:
    raise RiskLimitError(...)
```

Two traps that make this look broken:

1. **An order sized to exactly the cap gets refused.** Sizing uses the last close; `check_order` re-derives the reference price from the order book. They differ by a few bps, so a 1,000.00 order checks at 1,001.61 and is rejected. Size to **99.5% of the limit** and leave the limit exact — a cap that tolerates overshoot is not a cap.
2. **Reading equity per order bursts the rate limit.** Five orders in a loop produced five signed balance calls and a `429` on the fifth, which the risk check correctly turned into a refusal. Cache equity for ~60s (`_equity_for_risk(ttl=60)`) — one read per cycle is correct and rate-safe — and refuse rather than fall back to the absolute cap when the read fails.

## Rate Limits

- 20 requests/second for public endpoints
- 10 requests/second for signed endpoints
- Max 1000 klines per request
- **Repeated error codes get their own budget**: `over 5 error code:109400 requests within 900000 ms for this api` blocks that endpoint for 15 minutes after five bad requests. A retry loop against a malformed signed request therefore locks you out of the very endpoint you are debugging — fix the request, do not retry it.

## Kline Intervals

Supported: `1m`, `3m`, `5m`, `15m`, `30m`, `1h`, `4h`, `1d`, `1w`, `1M`

## Order Types

- `MARKET`: Execute immediately at market price
- `LIMIT`: Execute at specified price or better

**`place_order`'s 5th positional argument is `price`, not `position_side`.** `place_order(sym, "BUY", qty, "MARKET", "LONG")` sends `price="LONG"`; market orders ignore it so the order still fills, and the recorded call is not the one that ran. Always pass `position_side=` by keyword.

## Position Sides

- `LONG`: Buy (profit when price goes up)
- `SHORT`: Sell (profit when price goes down)

## Contract Sizes

| Coin | Contract Size | Min Notional |
|---|---|---|
| BTC | 0.0001 BTC | 2 USDT |
| ETH | 0.001 ETH | 2 USDT |
| XRP | 0.1 XRP | 2 USDT |
| DOGE | 1 DOGE | 2 USDT |
| ADA | 1 ADA | 2 USDT |
| SOL | 0.01 SOL | 2 USDT |
| LTC | 0.01 LTC | 2 USDT |
| LINK | 0.1 LINK | 2 USDT |

`quantityPrecision` / `pricePrecision` come from `/quote/contracts` — floor to the step, then take `max(step, qty)` so a small target does not round to zero.

## Common Issues

1. **"Invalid parameters, positionSide"**: Must specify `positionSide` in order
2. **`100413` Incorrect apiKey**: stale/revoked key on a working endpoint. Regenerate demo keys; do not touch the signing code.
3. **"Insufficient balance"**: Demo account needs to be funded first
4. **Klines return empty**: Check date range is within available history
5. **`ModuleNotFoundError` on a probe**: the project has no venv of its own and is borrowing another project's interpreter — create its own before diagnosing further
6. **`100404` on close/history**: wrong path, not a permissions problem — see the wrong-path table above
