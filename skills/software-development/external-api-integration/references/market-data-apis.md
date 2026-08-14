# Free Market-Data APIs — verified matrix (Aug 2026, Vercel/datacenter + local IPs)

Used by `src/features/investments/market-data.ts` (cashflow-os). Test BEFORE wiring; this space changes yearly.

## Working

| Source | Key | Provides | Notes |
|---|---|---|---|
| **CoinGecko** `api.coingecko.com/api/v3` | none | crypto quotes (`simple/price` + `include_24hr_change=true`), history (`coins/{id}/market_chart?days=N` → `{prices:[[ms,usd],...]}`) | Free tier ~10-30 req/min — fine for a personal portfolio |
| **Finnhub** `finnhub.io/api/v1` | free key (`FINNHUB_API_KEY`) | **real-time** US quotes `/quote?symbol=X&token=K` → `{c:price, dp:dayChange%, ...}` | Free tier has NO candles/history → `{"error":"You don't have access to this resource."}` |
| **Yahoo Finance** `query1.finance.yahoo.com/v8/finance/chart` | none | quotes + daily history (`range=1mo/6mo/1y&interval=1d`) → `chart.result[0].{timestamp[], indicators.quote[0].close[]}` | **REQUIRES a browser User-Agent header** — without it: `Edge: Too Many Requests` (UA-based block, not IP). US + many international tickers |
| **Twelve Data** `api.twelvedata.com/quote?symbol=X&apikey=K` → `{close, percent_change}` | free key (`TWELVEDATA_API_KEY`, 32-hex) | US stocks/ETFs quotes; works from cloud IPs | 8 calls/min, 800/day free. **PSE (`.PS`) = Ultra/Enterprise paid plan only** — free tier returns a plan-tier 404, not an auth error |
| **Frankfurter (ECB)** `api.frankfurter.app` | none | **FX**: `/latest?from=USD&to=PHP` → `{rates:{PHP}}`; daily series `/{from}..{to}?from=USD&to=PHP` (one call = whole window) | Keyless, daily (holiday-safe), 301 http→https (Node follows). Fallbacks: `open.er-api.com/v6/latest/USD`, CoinGecko `tether` vs fiat |

## Blocked from cloud IPs (2026)

- Stooq CSV endpoints — JS proof-of-work challenge page
- CNBC quote webservice — Akamai `Access Denied`
- MSN Finance quotes — "App authentication info not found"
- Yahoo WITHOUT the UA header
- PSE (Philippine) symbols on Yahoo — feed dead: `.PS` returns STALE 2019 MUTUALFUND rows with null currency; SM.PS has zero history points

## Wiring rules (learned the hard way)

1. **Every fetch needs `signal: AbortSignal.timeout(8000)`** — a hanging upstream freezes the page on its loading state with no error path (observed: investments page stuck on skeleton forever).
2. Cache: `{ next: { revalidate: 60 } }` = "real-time enough" without rate-limit pain.
3. **Fallback chain: Finnhub (real-time) → Twelve Data (cloud-friendly) → Yahoo+UA (keyless last resort)** — each layer returns `null` on failure so the chain falls through; keyed layers no-op when their env key is absent. History: Yahoo+UA (stocks/ETF), CoinGecko (crypto) — Finnhub free can't.
4. Keep `getPrices`/`getQuotes`/`getHistories` contracts stable — consumers include the portfolio action and the net-worth asset sync.
5. **FX conversion (BUILT Aug 2026):** prices arrive in USD → multiply by the entity currency rate (`fxToday`); HISTORY converts per-date via the Frankfurter series, falling back to today's rate for missing dates. **Day-change % is rate-agnostic — convert the price, never the percentage.** USD entities skip the fetch (rate = 1). Rate cache: `revalidate: 3600`.
6. Crypto day-change comes from `include_24hr_change=true` (`usd_24h_change`); stock day-change from Finnhub `dp` or Twelve Data `percent_change` or Yahoo `chartPreviousClose`.
7. **.xlsx parsing (SheetJS):** 2MB cap (zip ~1000:1 expansion → OOM on serverless), cap rows via `decode_range(ws['!ref'])` BEFORE `sheet_to_json`, `sheetRows` option on `XLSX.read`. Use the patched tarball (`https://cdn.sheetjs.com/xlsx-0.20.3/xlsx-0.20.3.tgz`) — npm's frozen 0.18.5 has CVE-2023-30533 (prototype pollution/RCE) + CVE-2024-22363 (ReDoS).
8. **Test plan:** curl quote + history per source from the TARGET IP, then one browser E2E with a real holding through the actual UI — verify the FX math exactly (`quote × rate` matches the displayed value to the cent).
