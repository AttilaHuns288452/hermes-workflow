# Market-data provider matrix (verified Aug 2026 from a datacenter/cloud IP)

Empirical result: **every keyless quote source tested was blocked from server IPs**. Wire keyed providers from the start.

## Failure signatures (don't confuse with your code being wrong)

| Source | Response seen | Meaning |
|---|---|---|
| Yahoo `query1.finance.yahoo.com/v8/finance/chart/AAPL` | `Edge: Too Many Requests` (plain text, HTTP 429-ish) | IP-level block; cookie/crumb trick does NOT fix it from cloud IPs |
| Stooq `q/l/?s=aapl.us&f=sd2t2ohlcv&h&e=csv` | "page does not exist" HTML, or JS proof-of-work challenge (`/__verify` + SHA-256 loop) | Endpoint dead / bot-wall |
| CNBC quote webservice | Akamai `Access Denied` HTML | WAF block |
| MSN `assets.msn.com/service/Finance/Quotes` | `App authentication info not found` | Requires app auth now |

## Working providers

### CoinGecko (crypto, keyless) — works from servers
- Batch: `GET https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd&include_24hr_change=true`
- Response: `{"bitcoin": {"usd": 64267, "usd_24h_change": 1.2}}`
- Needs a ticker→CoinGecko-ID map (BTC→bitcoin, ETH→ethereum, SOL→solana, …). Unknown ticker → null.
- Rate limits: free tier ~10-30 calls/min; batch everything.

### Finnhub (US stocks/ETFs, keyed) — real-time, free tier
- Signup: finnhub.io/register (free key, 40 chars, e.g. `d9pdufpr01qo4gjd0mfgd9pdufpr01qo4gjd0mg0` style).
- Quote: `GET https://finnhub.io/api/v1/quote?symbol=AAPL&token=<KEY>`
- Response: `{"c":309.38,"d":5.96,"dp":1.9643,"h":310.42,"l":301.32,"o":302.725,"pc":303.42}` — `c`=current, `dp`=day change %, `pc`=prev close.
- Free tier ~60 calls/min. No batch endpoint — loop with Promise.all (portfolios are small).
- Invalid key → `{"error":"Invalid API key."}`.
- **PSE (Philippines) not covered** — PH tickers have no reliable free source from cloud IPs; fall back to manual price.

## Wiring pattern (Next.js server actions)

```ts
const FH_KEY = process.env.FINNHUB_API_KEY || "";
const FETCH_CACHE = { next: { revalidate: 60 } } as const; // 60s = real-time enough

async function stockQuote(ticker: string) {
  if (FH_KEY) {
    const res = await fetch(`https://finnhub.io/api/v1/quote?symbol=${ticker}&token=${FH_KEY}`, FETCH_CACHE);
    if (res.ok) { /* parse c + dp */ }
  }
  // fallback: yahoo chart (works from home IPs, blocked on servers) → null
}
```

- UI contract: enrich holdings with `{ price, changePct }`; render `—` when null (cost basis).
- Currency caveat: Finnhub returns USD; if the app is single-currency (e.g. PHP), prices display in the entity currency by convention — FX conversion is a separate multi-currency feature.
- Env: add key to `.env.local` AND `vercel env add FINNHUB_API_KEY production` (pipe value via stdin), then redeploy. Verify live by adding a real holding in the browser and reading the table cell (should equal the curl result).
