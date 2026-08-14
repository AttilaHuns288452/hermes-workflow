---
name: finance-api-providers
description: Use when wiring live market prices or FX into an app.
---

# Finance API Providers (server-side, verified 2026)

Use when an app needs real-time or historical market prices, or USD→local FX rates, fetched from server/cloud IPs (Vercel, dev boxes). All endpoints below were curl-verified 2026-08 from a datacenter IP — the free-API landscape shifts yearly; re-verify with a 10s curl before trusting a new provider.

## Verified provider matrix

| Provider | Endpoint | Keyless | Covers | Verified behavior |
|---|---|---|---|---|
| **Finnhub** | `https://finnhub.io/api/v1/quote?symbol=AAPL&token=KEY` | Key (free tier) | US stocks/ETFs real-time | `{"c":309.38,"dp":1.9643,...}` c=price, dp=day %. **Free tier does NOT include candles/history** (`/stock/candle` → `"You don't have access to this resource"`) |
| **Yahoo Finance** | `https://query1.finance.yahoo.com/v8/finance/chart/AAPL?interval=1d&range=1mo` | Yes, but REQUIRES browser User-Agent | Stocks/ETFs + history (1mo/6mo/1y daily) | Without `User-Agent: Mozilla/5.0 ...` header → `Edge: Too Many Requests` (Akamai UA block). With it: full `chart.result[0].timestamp[]` + `indicators.quote[0].close[]`. Both query1/query2 hosts fine |
| **CoinGecko** | `https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd&include_24hr_change=true` + `/coins/{id}/market_chart?vs_currency=usd&days=30` | Yes | Crypto (needs ticker→id map: BTC→bitcoin, etc.) | Prices, 24h change %, 30d history `prices:[[ms,price]]`. Free tier ~10-30 req/min — batch ids comma-joined in ONE call |
| **Frankfurter (ECB)** | `https://api.frankfurter.app/latest?from=USD&to=PHP` + `/2026-07-06..2026-08-05?from=USD&to=PHP` | Yes | FX, daily rates (holiday-safe) | Returns 301 → Node fetch follows redirects natively (curl needs `-L`). Time-series endpoint = all daily rates in ONE call |
| open.er-api | `https://open.er-api.com/v6/latest/USD` | Yes | FX fallback | Same shape as Frankfurter rates |
| Stooq / CNBC / MSN Money | — | — | — | **Blocked from cloud IPs** (JS proof-of-work, Akamai deny, auth required) — don't waste time |

## Pitfalls

- **Every external fetch needs a timeout**: `signal: AbortSignal.timeout(8000)` — a hanging price API freezes the server action → UI stuck on skeleton forever. This bit a real deploy (2026-08).
- **Cache discipline**: quotes 60s (`next: { revalidate: 60 }`), FX hourly. "Real-time" = 60s freshness, not per-request — avoids free-tier rate limits.
- **Never throw from market-data fns** — return `null`/`[]` and let callers fall back (cost basis for prices, today's rate for history).
- **Finnhub keys are 40 chars** — a doubled paste looks like one long key; test the full string first, halves only if it 401s. Wire via `printf '%s' "$KEY" | vercel env add NAME production`.
- **FX conversion pattern** (USD prices → entity currency): quotes multiply by today's rate; HISTORY should convert per-date via one Frankfurter time-series call (rate map keyed by `YYYY-MM-DD`), fallback to today's rate per missing date — curve shape stays honest, only absolutes drift.

## Recipes

- `references/excel-to-supabase-import.md` — importing a spreadsheet ledger into a Supabase app via idempotent SQL.
