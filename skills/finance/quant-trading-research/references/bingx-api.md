# BingX API Reference

## Endpoints Used

| Endpoint | Purpose | Auth |
|---|---|---|
| `/openApi/swap/v2/quote/klines` | Historical OHLCV data | None |
| `/openApi/swap/v2/quote/depth` | L2 order book | None |
| `/openApi/swap/v2/quote/premiumIndex` | Funding rate | None |
| `/openApi/swap/v2/quote/openInterest` | Open interest | None |
| `/openApi/swap/v2/user/balance` | Account balance | Signed |
| `/openApi/swap/v2/user/positions` | Open positions | Signed |
| `/openApi/swap/v2/trade/order` | Place order | Signed |
| `/openApi/swap/v2/trade/closeAll` | Close all positions | Signed |

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

## Paper Trading Environment

- **Base URL:** `https://open-api-vst.bingx.com`
- **Currency:** VST (Virtual Settlement Token)
- **Starting balance:** 0 VST (need to fund via demo environment)
- **Fees:** Same as live (maker 0.02%, taker 0.05%)

## Rate Limits

- 20 requests/second for public endpoints
- 10 requests/second for signed endpoints
- Max 1000 klines per request

## Kline Intervals

Supported: `1m`, `3m`, `5m`, `15m`, `30m`, `1h`, `4h`, `1d`, `1w`, `1M`

## Order Types

- `MARKET`: Execute immediately at market price
- `LIMIT`: Execute at specified price or better

## Position Sides

- `LONG`: Buy (profit when price goes up)
- `SHORT`: Sell (profit when price goes down)

## Contract Sizes

| Coin | Contract Size |
|---|---|
| BTC | 0.0001 BTC |
| ETH | 0.001 ETH |
| XRP | 0.1 XRP |
| DOGE | 1 DOGE |
| ADA | 1 ADA |
| SOL | 0.01 SOL |
| LTC | 0.01 LTC |
| LINK | 0.1 LINK |

## Common Issues

1. **"Invalid parameters, positionSide"**: Must specify `positionSide` in order
2. **"Invalid API key"**: Check key/secret and ensure paper trading URL is used
3. **"Insufficient balance"**: Demo account needs to be funded first
4. **Klines return empty**: Check date range is within available history
